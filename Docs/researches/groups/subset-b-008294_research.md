# Research Report: subset-b-008294

This grouped report covers the requested RustFS ZIP helper and Linux ACL package build, library, tool, example, and test files. Each section is source-tree-aligned and delimited for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/zip/src/lib.rs -->
# sources/object-store/rustfs/crates/zip/src/lib.rs

Purpose: Implements RustFS archive and compression helpers for gzip, bzip2, xz, zlib, zstd, tar-family streams, and ZIP files. It defines the public error model, archive/codec enums, entry metadata, extraction limit policy, ZIP write options, streaming tar iteration, blocking ZIP extraction/creation, and convenience compressor/decompressor wrappers. The file is 1666 lines and includes in-module async tests for both stream and ZIP workflows.

Important APIs and types: Key symbols include `Result`, `ZipError`, `CompressionCodec`, `ArchiveKind`, `ArchiveFormat`, `CompressionFormat`, `CompressionLevel`, `ZipEntry`, `ZipExtractSummary`, `ArchiveLimits`, `ZipWriteOptions`, `SharedBuffer`, `read_archive_entries`, `read_archive_entries_with_limits`. `ZipError` models unsupported formats, unsafe paths, entry count/size/path limits, I/O, ZIP, and Tokio join failures. `CompressionFormat` and `ArchiveFormat` map extensions and paths to codecs/kinds. `ArchiveLimits` is the zip-slip/resource-exhaustion control surface, `ZipEntry`/`ZipExtractSummary` report extracted metadata, and `Compressor`/`Decompressor` provide byte-buffer and file-level convenience APIs.

Control flow: Stream readers call `get_decoder`, wrap the decoded byte stream in `tokio_tar::Archive`, iterate entries asynchronously, validate path/count/size/total limits before invoking the caller callback, and reject ZIP for stream decoding. ZIP extraction moves blocking `zip::ZipArchive` work to `spawn_blocking`, validates `enclosed_name`, creates parents through a directory cache, uses an 8 KiB fast path for small files, copies larger entries to disk, and optionally collects `ZipEntry` metadata. ZIP creation normalizes every name, optionally emits parent directory records, starts files with stored or deflated options based on `CompressionLevel`, and finishes the writer in the blocking pool.

State and persistence: There is no long-lived service state. Persistent effects are filesystem writes for extracted files/directories and created ZIP archives. Temporary state includes `SharedBuffer` with an `Arc<Mutex<Vec<u8>>>` for async in-memory compression, directory and entry `HashSet`s, extraction counters, and per-operation `ArchiveLimits` enforcement.

Dependencies and integration points: Integrates `async_compression`, Tokio I/O, `tokio_tar`, `tokio_stream`, `zip`, `thiserror`, and `spawn_blocking` for CPU/blocking archive work. Higher RustFS object-store code can use it to inspect archives, unpack ZIPs, create ZIP payloads, or compress/decompress object data without owning codec-specific plumbing.

Risks: Archive extraction is security-sensitive: any relaxation of `normalize_zip_entry_name`, `ZipArchive::enclosed_name`, or limit checks can reintroduce path traversal or decompression bomb risk. Compression-level `Level(u32)` only rejects overflow at encoder construction and does not normalize codec-specific level ranges. Tests show suspicious duplicated lines in this local source snapshot, so compile/test execution is important before treating edits as build-clean.

Test signals: Existing tests cover extension/path detection, encoder overflow, gzip/zstd round trips, stream iteration for tar.gz/tar.bz2/tar.xz/tar.zst, ZIP stream rejection, corrupt/truncated stream errors, entry count/size/total/path limit failures, ZIP create/extract round trips, directory entries, stored-vs-deflated metadata, unsafe create paths, and file decompression.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/zip/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/Makefile.am -->
# sources/security-integrity/acl/Makefile.am

Purpose: Top-level Automake include file that defines the distribution root, `SUBDIRS = po`, common compiler flags, placeholder build variables, and includes module fragments for docs, headers, libraries, tools, tests, examples, and man pages. The file is 36 lines.

Important APIs and targets: Important declarations or variables include `ACLOCAL_AMFLAGS`, `EXTRA_DIST`, `SUBDIRS`, `AM_CPPFLAGS`, `pkgconfdir`, `sysincludedir`, `pkgconf_DATA`, `pkginclude_HEADERS`, `sysinclude_HEADERS`, `bin_PROGRAMS`, `lib_LTLIBRARIES`, `noinst_HEADERS`, `noinst_LTLIBRARIES`, `dist_doc_DATA`. These names form build-system contracts rather than runtime C APIs.

Control flow: Automake reads this file first, initializes empty aggregate variables such as `bin_PROGRAMS`, `noinst_HEADERS`, `dist_doc_DATA`, and `dist_man_MANS`, then each included `Makemodule.am` appends targets and source lists.

State and persistence: State is persisted in generated build artifacts, installed files, distribution tarballs, symlinked include directories, or pkg-config metadata. The file itself does not maintain runtime process state.

Dependencies and integration points: Depends on GNU Autoconf/Automake/Libtool/Gettext conventions, the local module include layout, libattr/xattr probes, and package install variables. It integrates source files into the library, tool, documentation, test, or packaging surfaces.

Risks: Small target-list mistakes can silently omit files from builds, releases, installed docs, or tests. Versioning and dependency changes in libacl metadata affect ABI consumers and downstream pkg-config builds. Bootstrap/configure files are also sensitive to host portability and macro availability.

Test signals: Useful checks are `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, generated `libacl.pc` inspection, and verifying installed headers/manpages/tools match the module lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/autogen.sh -->
# sources/security-integrity/acl/autogen.sh

Purpose: Bootstrap helper that reruns the GNU build-system generator stack for a checkout. The file is 6 lines.

Important APIs and targets: Important declarations or variables include No exported code symbols; the file is declarative or script-oriented.. These names form build-system contracts rather than runtime C APIs.

Control flow: The script exits on errors and `exec`s `autoreconf -f -i`, replacing itself with autoreconf so generated aux files, macros, and Makefile templates are refreshed.

State and persistence: State is persisted in generated build artifacts, installed files, distribution tarballs, symlinked include directories, or pkg-config metadata. The file itself does not maintain runtime process state.

Dependencies and integration points: Depends on GNU Autoconf/Automake/Libtool/Gettext conventions, the local module include layout, libattr/xattr probes, and package install variables. It integrates source files into the library, tool, documentation, test, or packaging surfaces.

Risks: Small target-list mistakes can silently omit files from builds, releases, installed docs, or tests. Versioning and dependency changes in libacl metadata affect ABI consumers and downstream pkg-config builds. Bootstrap/configure files are also sensitive to host portability and macro availability.

Test signals: Useful checks are `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, generated `libacl.pc` inspection, and verifying installed headers/manpages/tools match the module lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/configure.ac -->
# sources/security-integrity/acl/configure.ac

Purpose: Autoconf entry point for the acl package, declaring package metadata, compiler/libtool/gettext setup, debug flags, large-file and endian checks, libattr/xattr dependency probes, generated include symlinks, and configured files. The file is 74 lines.

Important APIs and targets: Important declarations or variables include No exported code symbols; the file is declarative or script-oriented.. These names form build-system contracts rather than runtime C APIs.

Control flow: `autoreconf` expands macros, `configure` probes the host, substitutes `LT_REVISION`, creates `include/config.h`, arranges `include/acl` and `include/sys` symlinks, emits `Makefile`, `po/Makefile.in`, and `libacl.pc`.

State and persistence: State is persisted in generated build artifacts, installed files, distribution tarballs, symlinked include directories, or pkg-config metadata. The file itself does not maintain runtime process state.

Dependencies and integration points: Depends on GNU Autoconf/Automake/Libtool/Gettext conventions, the local module include layout, libattr/xattr probes, and package install variables. It integrates source files into the library, tool, documentation, test, or packaging surfaces.

Risks: Small target-list mistakes can silently omit files from builds, releases, installed docs, or tests. Versioning and dependency changes in libacl metadata affect ABI consumers and downstream pkg-config builds. Bootstrap/configure files are also sensitive to host portability and macro availability.

Test signals: Useful checks are `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, generated `libacl.pc` inspection, and verifying installed headers/manpages/tools match the module lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/doc/Makemodule.am -->
# sources/security-integrity/acl/doc/Makemodule.am

Purpose: Automake module that installs primary documentation (`CHANGES`, `COPYING`, LGPL notice, `INSTALL`, extension and library notes) and ships supplemental old/TODO documents in release archives. The file is 10 lines.

Important APIs and targets: Important declarations or variables include `dist_doc_DATA`, `EXTRA_DIST`. These names are build-system contracts rather than runtime C APIs.

Control flow: `dist_doc_DATA` and `EXTRA_DIST` are appended when the top-level `Makefile.am` includes this fragment, so `make install` and `make dist` carry the expected documentation set.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/doc/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/Makefile -->
# sources/security-integrity/acl/examples/Makefile

Purpose: Example build/distribution metadata for sample ACL programs and the generated examples Makefile. The file is 9 lines.

Important APIs and targets: Important declarations or variables include `CFLAGS`, `LDFLAGS`, `PROGS`, `all`, `clean`. These names form build-system contracts rather than runtime C APIs.

Control flow: The module marks examples for distribution; the concrete examples Makefile invokes compiler and linker commands against installed or built libacl/libattr objects.

State and persistence: State is persisted in generated build artifacts, installed files, distribution tarballs, symlinked include directories, or pkg-config metadata. The file itself does not maintain runtime process state.

Dependencies and integration points: Depends on GNU Autoconf/Automake/Libtool/Gettext conventions, the local module include layout, libattr/xattr probes, and package install variables. It integrates source files into the library, tool, documentation, test, or packaging surfaces.

Risks: Small target-list mistakes can silently omit files from builds, releases, installed docs, or tests. Versioning and dependency changes in libacl metadata affect ABI consumers and downstream pkg-config builds. Bootstrap/configure files are also sensitive to host portability and macro availability.

Test signals: Useful checks are `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, generated `libacl.pc` inspection, and verifying installed headers/manpages/tools match the module lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/Makemodule.am -->
# sources/security-integrity/acl/examples/Makemodule.am

Purpose: Automake module that ships example programs and example README material with distribution archives without making them installed tools. The file is 7 lines.

Important APIs and targets: Important declarations or variables include `EXTRA_DIST`. These names are build-system contracts rather than runtime C APIs.

Control flow: The top-level makefile includes this fragment and `EXTRA_DIST` picks up example C sources, README, and example-local make metadata for release packaging.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/copy-acl.c -->
# sources/security-integrity/acl/examples/copy-acl.c

Purpose: Example program copying access and default ACLs from one source path to one or more destination paths. The file is 70 lines and is intended as sample code rather than the primary installed tool implementation.

Important APIs and functions: Key symbols include `main`.

Control flow: Parses argv, reads source access/default ACLs with `acl_get_file`, loops over destinations applying both with `acl_set_file`, reports per-destination failures, and frees both ACL handles.

State and persistence: Runtime state is argv-derived paths, transient `acl_t` handles, text buffers, and return status. Persistence occurs only when the example calls `acl_set_file` or permission-copy helpers against destination files.

Dependencies and integration points: Depends on public `sys/acl.h` and/or `acl/libacl.h`, libc diagnostics, optional libattr error-context support, and the installed libacl ABI that downstream users are expected to call similarly.

Risks: The examples have intentionally simple error handling and do not cover every production edge case, such as non-directory default ACL behavior or partial destination failures. They still exercise real filesystem ACL writes, so they should be run only on disposable files.

Test signals: Compile examples against installed headers, run them on temporary files/directories with base and extended ACLs, verify output with `getfacl`, and check failure handling for invalid ACL text or unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/copy-acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/copyperm.c -->
# sources/security-integrity/acl/examples/copyperm.c

Purpose: Example program showing cp-style permission preservation through libacl's `perm_copy_file` API and libattr error context callbacks. The file is 61 lines and is intended as sample code rather than the primary installed tool implementation.

Important APIs and functions: Key symbols include `error`, `main`.

Control flow: Initializes locale, validates `from to` arguments, provides an `error_context` printer, calls `perm_copy_file`, and exits by the helper's status.

State and persistence: Runtime state is argv-derived paths, transient `acl_t` handles, text buffers, and return status. Persistence occurs only when the example calls `acl_set_file` or permission-copy helpers against destination files.

Dependencies and integration points: Depends on public `sys/acl.h` and/or `acl/libacl.h`, libc diagnostics, optional libattr error-context support, and the installed libacl ABI that downstream users are expected to call similarly.

Risks: The examples have intentionally simple error handling and do not cover every production edge case, such as non-directory default ACL behavior or partial destination failures. They still exercise real filesystem ACL writes, so they should be run only on disposable files.

Test signals: Compile examples against installed headers, run them on temporary files/directories with base and extended ACLs, verify output with `getfacl`, and check failure handling for invalid ACL text or unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/copyperm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/get-acl.c -->
# sources/security-integrity/acl/examples/get-acl.c

Purpose: Example implementation of a small getfacl-like reader. The file is 96 lines and is intended as sample code rather than the primary installed tool implementation.

Important APIs and functions: Key symbols include `main`.

Control flow: Stats each path, reads access ACL text, conditionally reads directory default ACLs, prints file/owner/group headers and default-prefixed entries, then frees all allocated ACL text/handles.

State and persistence: Runtime state is argv-derived paths, transient `acl_t` handles, text buffers, and return status. Persistence occurs only when the example calls `acl_set_file` or permission-copy helpers against destination files.

Dependencies and integration points: Depends on public `sys/acl.h` and/or `acl/libacl.h`, libc diagnostics, optional libattr error-context support, and the installed libacl ABI that downstream users are expected to call similarly.

Risks: The examples have intentionally simple error handling and do not cover every production edge case, such as non-directory default ACL behavior or partial destination failures. They still exercise real filesystem ACL writes, so they should be run only on disposable files.

Test signals: Compile examples against installed headers, run them on temporary files/directories with base and extended ACLs, verify output with `getfacl`, and check failure handling for invalid ACL text or unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/get-acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/set-acl.c -->
# sources/security-integrity/acl/examples/set-acl.c

Purpose: Example implementation of a small setfacl-like writer for access ACLs. The file is 64 lines and is intended as sample code rather than the primary installed tool implementation.

Important APIs and functions: Key symbols include `main`.

Control flow: Parses an ACL text argument, validates it with `acl_valid`, applies it to each remaining path with `acl_set_file`, reports failures, and frees the ACL.

State and persistence: Runtime state is argv-derived paths, transient `acl_t` handles, text buffers, and return status. Persistence occurs only when the example calls `acl_set_file` or permission-copy helpers against destination files.

Dependencies and integration points: Depends on public `sys/acl.h` and/or `acl/libacl.h`, libc diagnostics, optional libattr error-context support, and the installed libacl ABI that downstream users are expected to call similarly.

Risks: The examples have intentionally simple error handling and do not cover every production edge case, such as non-directory default ACL behavior or partial destination failures. They still exercise real filesystem ACL writes, so they should be run only on disposable files.

Test signals: Compile examples against installed headers, run them on temporary files/directories with base and extended ACLs, verify output with `getfacl`, and check failure handling for invalid ACL text or unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/set-acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/Makemodule.am -->
# sources/security-integrity/acl/include/Makemodule.am

Purpose: Automake module listing public and private headers for distribution and installation under the generated `include/sys` and `include/acl` compatibility directories. The file is 24 lines.

Important APIs and targets: Important declarations or variables include module variables listed in the file. These names are build-system contracts rather than runtime C APIs.

Control flow: The header variables are consumed after `configure` creates include-directory symlinks, ensuring installed `sys/acl.h`, `acl/libacl.h`, and internal helper headers are available to library/tool builds.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/acl.h -->
# sources/security-integrity/acl/include/acl.h

Purpose: Public POSIX.1e-style `sys/acl.h` compatibility API defining opaque ACL handle types, ACL tag/permission/type constants, and the core entry, permission, text, external-copy, file, and fd manipulation functions. The file is 127 lines.

Important APIs and types: Key declarations include `acl_init`, `acl_dup`, `acl_free`, `acl_valid`, `acl_copy_entry`, `acl_create_entry`, `acl_delete_entry`, `acl_get_entry`, `acl_add_perm`, `acl_calc_mask`, `acl_clear_perms`, `acl_delete_perm`, `acl_get_permset`, `acl_set_permset`.

Control flow: Callers allocate an `acl_t`, create or iterate entries, manipulate tag/qualifier/permission fields, validate or serialize it, then apply it to paths or file descriptors.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: This header is a public ABI: numeric constants, opaque pointer typedefs, and exported prototypes must remain compatible with existing applications. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/acl_ea.h -->
# sources/security-integrity/acl/include/acl_ea.h

Purpose: Defines the Linux extended-attribute wire format for POSIX ACLs, including xattr names, version, little-endian header/entry layout, and size calculation helpers. The file is 52 lines.

Important APIs and types: Key declarations include `acl_ea_size`, `acl_ea_count`, `ACL_EA_ACCESS`, `ACL_EA_DEFAULT`, `ACL_EA_VERSION`.

Control flow: `acl_get_*` reads bytes from `system.posix_acl_access` or `system.posix_acl_default`, serializers translate between this layout and internal ACL entries, and setters write it back.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Endianness, packed layout, and xattr names are kernel/user-space interoperability contracts; any drift corrupts stored ACLs. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/acl_ea.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/libacl.h -->
# sources/security-integrity/acl/include/libacl.h

Purpose: Public libacl extension header layered on `sys/acl.h`, adding text formatting flags, ACL validation error codes, comparison/check/equiv/extended-file helpers, and permission-copy APIs. The file is 80 lines.

Important APIs and types: Key declarations include `acl_cmp`, `acl_check`, `acl_from_mode`, `acl_equiv_mode`, `acl_extended_file`, `acl_extended_file_nofollow`, `acl_extended_fd`, `acl_entries`, `acl_get_perm`, `perm_copy_file`, `perm_copy_fd`, `__ACL_LIBACL_H`, `TEXT_SOME_EFFECTIVE`, `TEXT_ALL_EFFECTIVE`.

Control flow: Command-line tools and downstream applications use these helpers for richer ACL display, validation diagnostics, mode equivalence, extended ACL checks, and cp-style permission preservation.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: The extension API is public; exported names and error-code meanings are consumed by tools such as `getfacl`, `setfacl`, and external programs. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/libacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/misc.h -->
# sources/security-integrity/acl/include/misc.h

Purpose: Internal helper header for allocation growth, line reading, quoting/unquoting, and user/group id-name lookup used by libacl and tools. The file is 51 lines.

Important APIs and types: Key declarations include `__acl_high_water_alloc`, `__acl_get_uid`, `__acl_get_gid`, `__MISC_H`.

Control flow: Tools call quote and lookup helpers while parsers/text emitters call unquote and uid/gid resolution; buffers grow through high-water allocation.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Lookup and quoting behavior directly affects text ACL parsing, display stability, and shell/test expectations. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/walk_tree.h -->
# sources/security-integrity/acl/include/walk_tree.h

Purpose: Internal directory traversal contract defining recursive, logical/physical symlink, top-level dereference, one-filesystem, failure, and callback flags. The file is 42 lines.

Important APIs and types: Key declarations include `walk_tree`, `__WALK_TREE_H`, `WALK_TREE_RECURSIVE`, `WALK_TREE_PHYSICAL`, `WALK_TREE_LOGICAL`, `WALK_TREE_DEREFERENCE`, `WALK_TREE_DEREFERENCE_TOPLEVEL`, `WALK_TREE_ONE_FILESYSTEM`, `WALK_TREE_TOPLEVEL`, `WALK_TREE_SYMLINK`, `WALK_TREE_FAILED`.

Control flow: Tools pass a path, flag set, optional fd budget, and callback; `walk_tree.c` reports each node with stat data and walk flags.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Flag semantics are user-visible through `getfacl -R/-L/-P` and `setfacl`; regressions can follow or skip symlinks incorrectly. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/walk_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl.pc.in -->
# sources/security-integrity/acl/libacl.pc.in

Purpose: pkg-config template advertising libacl include paths, linker flags, version, and the libattr private dependency. The file is 11 lines.

Important APIs and targets: Important declarations or variables include `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Description`, `Version`, `License`, `Cflags`, `Libs`. These names form build-system contracts rather than runtime C APIs.

Control flow: `configure` substitutes prefix/libdir/includedir/version fields and installs the result as `libacl.pc` for downstream builds.

State and persistence: State is persisted in generated build artifacts, installed files, distribution tarballs, symlinked include directories, or pkg-config metadata. The file itself does not maintain runtime process state.

Dependencies and integration points: Depends on GNU Autoconf/Automake/Libtool/Gettext conventions, the local module include layout, libattr/xattr probes, and package install variables. It integrates source files into the library, tool, documentation, test, or packaging surfaces.

Risks: Small target-list mistakes can silently omit files from builds, releases, installed docs, or tests. Versioning and dependency changes in libacl metadata affect ABI consumers and downstream pkg-config builds. Bootstrap/configure files are also sensitive to host portability and macro availability.

Test signals: Useful checks are `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, generated `libacl.pc` inspection, and verifying installed headers/manpages/tools match the module lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/Makemodule.am -->
# sources/security-integrity/acl/libacl/Makemodule.am

Purpose: Source file participating in the ACL package. The file is 83 lines.

Important APIs and functions: Key symbols include `lib_LTLIBRARIES`, `LT_CURRENT`, `LT_AGE`, `LTVERSION`, `CFILES`, `HFILES`, `POSIX_CFILES`, `LIBACL_CFILES`, `INTERNAL_CFILES`, `libacl_la_DEPENDENCIES`, `libacl_la_SOURCES`, `libacl_la_LIBADD`, `libacl_la_CFLAGS`, `libacl_la_LDFLAGS`.

Control flow: The file contributes declarative or helper behavior used by the surrounding ACL build, library, tool, or test subsystem.

State and persistence: State is local to the consuming subsystem and is persisted only through generated build/test artifacts or filesystem ACL operations performed by callers.

Dependencies and integration points: Integrates with the acl source tree's Autotools build, libacl/libmisc internals, public ACL headers, tools, or tests depending on its directory.

Risks: Drift from adjacent module contracts can break builds, tests, or command behavior.

Test signals: Build the package, run `make check`, and exercise the relevant public tool or API path.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_extended_file.c -->
# sources/security-integrity/acl/libacl/__acl_extended_file.c

Purpose: Hidden helper that decides whether a path has an extended access/default ACL by probing xattr value sizes. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 49 lines.

Important APIs and functions: Key symbols include `__acl_extended_file`.

Control flow: Calls a supplied xattr-size function for access and default ACL names, compares sizes with the three-entry base ACL threshold, and returns 1 for extended ACLs, 0 for base/no ACL, or -1 for real errors.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_extended_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_extended_file.h -->
# sources/security-integrity/acl/libacl/__acl_extended_file.h

Purpose: Private helper prototype header for one hidden libacl routine used across xattr or extended-ACL implementation files. The file is 3 lines.

Important APIs and types: Key declarations include `__acl_extended_file`.

Control flow: Implementation files include it to share hidden helper signatures without exposing them in public headers.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Prototype drift causes build warnings or ABI-internal mismatches. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_extended_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_from_xattr.c -->
# sources/security-integrity/acl/libacl/__acl_from_xattr.c

Purpose: Hidden deserializer from Linux POSIX ACL xattr bytes into libacl internal objects. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 93 lines.

Important APIs and functions: Key symbols include `__acl_from_xattr`.

Control flow: Validates header size, version, entry-size alignment, creates entries, converts little-endian tag/perm/id values, rejects unknown tags, and canonicalizes ordering.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_from_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_from_xattr.h -->
# sources/security-integrity/acl/libacl/__acl_from_xattr.h

Purpose: Private helper prototype header for one hidden libacl routine used across xattr or extended-ACL implementation files. The file is 1 lines.

Important APIs and types: Key declarations include `__acl_from_xattr`.

Control flow: Implementation files include it to share hidden helper signatures without exposing them in public headers.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Prototype drift causes build warnings or ABI-internal mismatches. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_from_xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_reorder_obj_p.c -->
# sources/security-integrity/acl/libacl/__acl_reorder_obj_p.c

Purpose: Canonical ordering engine for ACL entry objects. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 134 lines.

Important APIs and functions: Key symbols include `__acl_entry_p_compare`, `__acl_entry_pp_compare`, `__acl_reorder_entry_obj_p`, `__acl_reorder_obj_p`.

Control flow: Reorders individual entries or whole ACL rings so entries sort by required POSIX ACL order and qualifier ids, which later validation and comparison assume.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_reorder_obj_p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_to_any_text.c -->
# sources/security-integrity/acl/libacl/__acl_to_any_text.c

Purpose: Hidden formatter for ACLs with prefixes, separators, suffixes, effective-right comments, numeric/name lookup, smart indentation, and abbreviation modes. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 349 lines.

Important APIs and functions: Key symbols include `acl_entry_to_any_str`, `snprint_uint`, `__acl_to_any_text`, `user_name`, `group_name`, `ADVANCE`, `ABBREV`, `EFFECTIVE_STR`.

Control flow: Walks entries, resolves qualifiers to names unless numeric output is requested, applies mask-aware effective comments, measures output, allocates a string object, and renders the final text.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_to_any_text.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_to_xattr.c -->
# sources/security-integrity/acl/libacl/__acl_to_xattr.c

Purpose: Hidden serializer from canonical internal ACL objects to Linux POSIX ACL xattr bytes. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 62 lines.

Important APIs and functions: Key symbols include `__acl_to_xattr`.

Control flow: Allocates an xattr header plus one entry per ACL entry, writes version, little-endian tag/perm/id fields, and uses undefined ids for non-qualified tags.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_to_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_to_xattr.h -->
# sources/security-integrity/acl/libacl/__acl_to_xattr.h

Purpose: Private helper prototype header for one hidden libacl routine used across xattr or extended-ACL implementation files. The file is 1 lines.

Important APIs and types: Key declarations include No exported code symbols; the file is declarative or script-oriented..

Control flow: Implementation files include it to share hidden helper signatures without exposing them in public headers.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Prototype drift causes build warnings or ABI-internal mismatches. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_to_xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__apply_mask_to_mode.c -->
# sources/security-integrity/acl/libacl/__apply_mask_to_mode.c

Purpose: Internal helper that folds ACL mask semantics into mode bits for fallback chmod behavior. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 67 lines.

Important APIs and functions: Key symbols include `__acl_apply_mask_to_mode`.

Control flow: Finds mask/group entries and updates group permission bits so chmod fallback preserves effective group permissions when full ACL setting is unavailable.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__apply_mask_to_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__libobj.c -->
# sources/security-integrity/acl/libacl/__libobj.c

Purpose: Implementation of the private tagged-object allocator and validator used by all opaque ACL handles. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 93 lines.

Important APIs and functions: Key symbols include `__acl_new_var_obj_p`, `__acl_new_obj_p_here`, `__acl_free_obj_p`, `__acl_check_obj_p`.

Control flow: Allocates variable-size objects with magic prefixes, supports in-place object initialization, validates external-to-internal conversions, and frees only heap-owned objects.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__libobj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_add_perm.c -->
# sources/security-integrity/acl/libacl/acl_add_perm.c

Purpose: Public permission mutator that adds read/write/execute bits to an ACL permset. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 35 lines.

Important APIs and functions: Key symbols include `acl_add_perm`.

Control flow: Validates the permset handle and rejects unknown permission bits before OR-ing the requested bits into the internal `sperm` mask.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_add_perm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_calc_mask.c -->
# sources/security-integrity/acl/libacl/acl_calc_mask.c

Purpose: Public mask recalculation helper for ACLs with named users/groups or group object entries. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 67 lines.

Important APIs and functions: Key symbols include `acl_calc_mask`.

Control flow: Aggregates permissions from `ACL_USER`, `ACL_GROUP_OBJ`, and `ACL_GROUP`, creates an `ACL_MASK` entry if absent, reorders it, and stores the aggregate mask.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_calc_mask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_check.c -->
# sources/security-integrity/acl/libacl/acl_check.c

Purpose: Public validator for canonical ACL shape and required entries. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 127 lines.

Important APIs and functions: Key symbols include `acl_check`, `FAIL_CHECK`.

Control flow: Walks entries as a state machine through user_obj, named users, group_obj, named groups, optional/required mask, and other, returning ACL error codes and last-valid index.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_clear_perms.c -->
# sources/security-integrity/acl/libacl/acl_clear_perms.c

Purpose: Public helper that clears all permissions from a permset. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 35 lines.

Important APIs and functions: Key symbols include `acl_clear_perms`.

Control flow: Validates the permset handle and sets the internal permission mask to `ACL_PERM_NONE`.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_clear_perms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_cmp.c -->
# sources/security-integrity/acl/libacl/acl_cmp.c

Purpose: Public ACL comparison routine. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 53 lines.

Important APIs and functions: Key symbols include `acl_cmp`.

Control flow: Checks handle validity, entry counts, tags, permission masks, and qualifiers for named user/group entries in canonical order.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_cmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_copy_entry.c -->
# sources/security-integrity/acl/libacl/acl_copy_entry.c

Purpose: Public entry-copy routine. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 40 lines.

Important APIs and functions: Key symbols include `acl_copy_entry`.

Control flow: Copies tag, qualifier, and permset fields from source to destination and reorders the destination entry inside its containing ACL.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_copy_entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_copy_ext.c -->
# sources/security-integrity/acl/libacl/acl_copy_ext.c

Purpose: Public serializer to the draft POSIX external in-memory representation. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 52 lines.

Important APIs and functions: Key symbols include `acl_copy_ext`.

Control flow: Checks the destination buffer size, writes total size, and copies each internal `__acl_entry` into the caller buffer.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_copy_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_copy_int.c -->
# sources/security-integrity/acl/libacl/acl_copy_int.c

Purpose: Public parser from the draft POSIX external in-memory representation. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 65 lines.

Important APIs and functions: Key symbols include `acl_copy_int`.

Control flow: Validates size fields and entry alignment, allocates a new ACL, copies external entries in, and canonicalizes order.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_copy_int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_create_entry.c -->
# sources/security-integrity/acl/libacl/acl_create_entry.c

Purpose: Public and hidden entry allocation implementation. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 74 lines.

Important APIs and functions: Key symbols include `__acl_create_entry_obj`, `acl_create_entry`.

Control flow: Allocates from a preallocated entry range when available or heap-allocates a new entry, links it at the tail of the ACL ring, initializes defaults, and returns an external handle.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_create_entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_delete_def_file.c -->
# sources/security-integrity/acl/libacl/acl_delete_def_file.c

Purpose: Public helper for removing a directory default ACL xattr. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 39 lines.

Important APIs and functions: Key symbols include `acl_delete_def_file`.

Control flow: Calls `removexattr` for `system.posix_acl_default` and treats absent xattrs as success-compatible filesystem state.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_delete_def_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_delete_entry.c -->
# sources/security-integrity/acl/libacl/acl_delete_entry.c

Purpose: Public entry deletion helper. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 44 lines.

Important APIs and functions: Key symbols include `acl_delete_entry`.

Control flow: Validates ACL and entry handles, backs up the current iterator if needed, unlinks the entry from the ring, frees it, and decrements the used count.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_delete_entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_delete_perm.c -->
# sources/security-integrity/acl/libacl/acl_delete_perm.c

Purpose: Public permission mutator that removes read/write/execute bits. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 35 lines.

Important APIs and functions: Key symbols include `acl_delete_perm`.

Control flow: Validates the permset and requested mask, then clears those bits from internal permissions.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_delete_perm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_dup.c -->
# sources/security-integrity/acl/libacl/acl_dup.c

Purpose: Public deep-copy helper for ACL objects. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 54 lines.

Important APIs and functions: Key symbols include `acl_dup`.

Control flow: Allocates a new ACL sized like the source and recreates each entry with copied tag, qualifier, and permission state.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_dup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_entries.c -->
# sources/security-integrity/acl/libacl/acl_entries.c

Purpose: Public count helper. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 33 lines.

Important APIs and functions: Key symbols include `acl_entries`.

Control flow: Validates an ACL handle and returns the internal used-entry count.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_entries.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_equiv_mode.c -->
# sources/security-integrity/acl/libacl/acl_equiv_mode.c

Purpose: Public helper determining whether an ACL is equivalent to traditional mode bits. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 71 lines.

Important APIs and functions: Key symbols include `acl_equiv_mode`.

Control flow: Builds mode bits from user/group/other entries, notes named entries or mask as non-equivalent, and applies mask bits to group mode output when requested.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_equiv_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_error.c -->
# sources/security-integrity/acl/libacl/acl_error.c

Purpose: Public diagnostic mapper for `acl_check` error codes. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 43 lines.

Important APIs and functions: Key symbols include `acl_error`.

Control flow: Returns translated strings for multiple-entry, duplicate, missing-entry, and wrong-entry-type validation failures.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_extended_fd.c -->
# sources/security-integrity/acl/libacl/acl_extended_fd.c

Purpose: Public fd-based extended ACL check. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 47 lines.

Important APIs and functions: Key symbols include `acl_extended_fd`.

Control flow: Delegates to xattr probing on `/proc/self/fd`-style fd support or fd xattr APIs to distinguish base mode ACLs from extended ACLs.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_extended_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_extended_file.c -->
# sources/security-integrity/acl/libacl/acl_extended_file.c

Purpose: Public path-based extended ACL check following symlinks. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 34 lines.

Important APIs and functions: Key symbols include `acl_extended_file`.

Control flow: Calls the hidden extended-file helper with `getxattr` so access/default ACL xattr sizes decide whether the file has non-base ACL state.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_extended_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_extended_file_nofollow.c -->
# sources/security-integrity/acl/libacl/acl_extended_file_nofollow.c

Purpose: Public path-based extended ACL check that does not follow symlinks. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 33 lines.

Important APIs and functions: Key symbols include `acl_extended_file_nofollow`.

Control flow: Calls the hidden extended-file helper with `lgetxattr`, preserving symlink traversal semantics for tools.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_extended_file_nofollow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_free.c -->
# sources/security-integrity/acl/libacl/acl_free.c

Purpose: Public object/string/ACL free routine plus hidden ACL-object destructor. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 76 lines.

Important APIs and functions: Key symbols include `__acl_free_acl_obj`, `acl_free`.

Control flow: Frees all entries in an ACL ring or dispatches generic object free for strings/qualifiers while preserving libobj magic checks.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_free.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_from_mode.c -->
# sources/security-integrity/acl/libacl/acl_from_mode.c

Purpose: Public constructor creating a base three-entry ACL from Unix mode bits. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 72 lines.

Important APIs and functions: Key symbols include `acl_from_mode`.

Control flow: Allocates an ACL with user_obj, group_obj, and other entries and maps owner/group/other `rwx` bits into ACL permissions.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_from_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_from_text.c -->
# sources/security-integrity/acl/libacl/acl_from_text.c

Purpose: Public text parser for ACL entries. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 259 lines.

Important APIs and functions: Key symbols include `parse_acl_entry`, `acl_from_text`, `skip_tag_name`, `get_token`, `SKIP_WS`.

Control flow: Skips whitespace/comments, parses user/group/mask/other tags and optional qualifiers, resolves names or ids, decodes rwx permission text, creates entries, and copies parsed state into the ACL.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_from_text.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_entry.c -->
# sources/security-integrity/acl/libacl/acl_get_entry.c

Purpose: Public ACL iterator. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 59 lines.

Important APIs and functions: Key symbols include `acl_get_entry`.

Control flow: Supports `ACL_FIRST_ENTRY` and `ACL_NEXT_ENTRY`, tracks the current entry in the ACL object, and returns 1/0 for found/end.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_fd.c -->
# sources/security-integrity/acl/libacl/acl_get_fd.c

Purpose: Public fd-based ACL reader. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 66 lines.

Important APIs and functions: Key symbols include `acl_get_fd`.

Control flow: Reads the access ACL xattr from a file descriptor, resizes buffers on `ERANGE`, converts xattr bytes to internal ACLs, and falls back to mode-derived ACLs when no xattr exists.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_file.c -->
# sources/security-integrity/acl/libacl/acl_get_file.c

Purpose: Public path-based ACL reader. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 87 lines.

Important APIs and functions: Key symbols include `acl_get_file`.

Control flow: Selects access/default xattr names, reads and resizes buffers, deserializes positive-size xattrs, and falls back to mode-derived access ACLs or empty directory default ACLs.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_perm.c -->
# sources/security-integrity/acl/libacl/acl_get_perm.c

Purpose: Public permission membership test. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 33 lines.

Important APIs and functions: Key symbols include `acl_get_perm`.

Control flow: Validates the permset and returns whether the requested read/write/execute bit is present.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_perm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_permset.c -->
# sources/security-integrity/acl/libacl/acl_get_permset.c

Purpose: Public entry permission accessor. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 42 lines.

Important APIs and functions: Key symbols include `acl_get_permset`.

Control flow: Validates an entry handle and returns an external handle to its embedded permset object.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_permset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_qualifier.c -->
# sources/security-integrity/acl/libacl/acl_get_qualifier.c

Purpose: Public qualifier copier. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 48 lines.

Important APIs and functions: Key symbols include `acl_get_qualifier`.

Control flow: Returns a newly allocated `id_t` copy for named user/group entries and rejects unqualified tags.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_qualifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_tag_type.c -->
# sources/security-integrity/acl/libacl/acl_get_tag_type.c

Purpose: Public tag accessor. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 39 lines.

Important APIs and functions: Key symbols include `acl_get_tag_type`.

Control flow: Validates an entry handle and writes its ACL tag into the caller-supplied pointer.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_get_tag_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_init.c -->
# sources/security-integrity/acl/libacl/acl_init.c

Purpose: Public ACL allocator and hidden object initializer. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 69 lines.

Important APIs and functions: Key symbols include `__acl_init_obj`, `acl_init`.

Control flow: Allocates an ACL object with optional preallocated entry storage, initializes the sentinel ring, current pointer, used count, and preallocation bounds.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_fd.c -->
# sources/security-integrity/acl/libacl/acl_set_fd.c

Purpose: Public fd-based ACL setter. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 50 lines.

Important APIs and functions: Key symbols include `acl_set_fd`.

Control flow: Serializes a validated internal ACL to xattr bytes and writes it to the access ACL xattr for the file descriptor.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_file.c -->
# sources/security-integrity/acl/libacl/acl_set_file.c

Purpose: Public path-based ACL setter. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 64 lines.

Important APIs and functions: Key symbols include `acl_set_file`.

Control flow: Maps access/default ACL type to xattr name, serializes the internal ACL, writes it with `setxattr`, and frees the temporary xattr buffer.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_permset.c -->
# sources/security-integrity/acl/libacl/acl_set_permset.c

Purpose: Public permission-set setter. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 36 lines.

Important APIs and functions: Key symbols include `acl_set_permset`.

Control flow: Validates entry and permset handles and copies the permission mask into the entry embedded permset.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_permset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_qualifier.c -->
# sources/security-integrity/acl/libacl/acl_set_qualifier.c

Purpose: Public qualifier setter. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 48 lines.

Important APIs and functions: Key symbols include `acl_set_qualifier`.

Control flow: Validates the entry, copies an `id_t` qualifier for named user/group tags, and reorders the entry after qualifier changes.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_qualifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_tag_type.c -->
# sources/security-integrity/acl/libacl/acl_set_tag_type.c

Purpose: Public tag setter. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 47 lines.

Important APIs and functions: Key symbols include `acl_set_tag_type`.

Control flow: Validates the entry and tag value, updates the tag, resets or preserves qualifier expectations, and reorders the entry.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_set_tag_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_size.c -->
# sources/security-integrity/acl/libacl/acl_size.c

Purpose: Public external-size calculator. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 35 lines.

Important APIs and functions: Key symbols include `acl_size`.

Control flow: Returns the byte count needed for `acl_copy_ext` based on the ACL object header plus one external entry per ACL entry.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_to_any_text.c -->
# sources/security-integrity/acl/libacl/acl_to_any_text.c

Purpose: Public formatting wrapper with custom prefix/separator/options. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 33 lines.

Important APIs and functions: Key symbols include `acl_to_any_text`.

Control flow: Delegates to hidden `__acl_to_any_text` using no suffix and returns an allocated string for callers to free with `acl_free`.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_to_any_text.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_to_text.c -->
# sources/security-integrity/acl/libacl/acl_to_text.c

Purpose: Public POSIX text formatter. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 32 lines.

Important APIs and functions: Key symbols include `acl_to_text`.

Control flow: Delegates to hidden `__acl_to_any_text` with newline separators and standard text behavior, returning string length when requested.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_to_text.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_valid.c -->
# sources/security-integrity/acl/libacl/acl_valid.c

Purpose: Public ACL validity boolean wrapper. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 41 lines.

Important APIs and functions: Key symbols include `acl_valid`.

Control flow: Calls `acl_check` and maps successful validation to 0 while invalid ACLs become `EINVAL` failures.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_valid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/byteorder.h -->
# sources/security-integrity/acl/libacl/byteorder.h

Purpose: Endian-conversion compatibility layer for ACL xattr serialization, selecting host-to/from little-endian conversion helpers based on configure results. The file is 33 lines.

Important APIs and types: Key declarations include No exported code symbols; the file is declarative or script-oriented..

Control flow: xattr readers and writers call `cpu_to_le16/32` and `le16/32_to_cpu` through this header when translating kernel ACL bytes.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Incorrect endian branches make cross-architecture ACL xattrs unreadable or misinterpreted. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/libacl.h -->
# sources/security-integrity/acl/libacl/libacl.h

Purpose: Private libacl implementation header mapping public opaque handles to tagged internal objects, defining ACL entry/qualifier/permset containers, object macros, canonical iteration, and hidden helper prototypes. The file is 150 lines.

Important APIs and types: Key declarations include `ACL_PERM_NONE`, `sperm`, `oprefix`, `permset_obj_equal`, `qid`, `qualifier_obj_id`, `econtainer`, `eprev`, `enext`, `eentry`.

Control flow: All libacl C files convert external handles through `ext2int`, mutate linked-list ACL objects, and return handles through `int2ext`.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Pointer-prefix and magic-check macros are central memory-safety guards; layout changes affect every API implementation. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/libacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/libobj.h -->
# sources/security-integrity/acl/libacl/libobj.h

Purpose: Private object-system header that prepends magic/flag metadata to allocated libacl objects and provides checked allocation, conversion, and free macros. The file is 96 lines.

Important APIs and types: Key declarations include `__LIBOBJ_H`, `int2ext`, `new_var_obj_p`, `realloc_var_obj_p`, `new_obj_p`, `new_obj_p_here`, `check_obj_p`, `free_obj_p`, `pmagic`, `pflags`.

Control flow: Allocation creates tagged objects, public handles point into embedded external structs, and API entry points validate handles before mutation.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: The conversion macros are intentionally low-level pointer manipulation; misuse can cause invalid frees or false handle validation. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/libobj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy.h -->
# sources/security-integrity/acl/libacl/perm_copy.h

Purpose: Compatibility feature-detection shim forced into libacl permission-copy compilation to declare which ACL/libattr APIs are available in this package build. The file is 40 lines.

Important APIs and types: Key declarations include `HAVE_ACL_LIBACL_H`, `HAVE_CONFIG_H`, `HAVE_SYS_ACL_H`, `HAVE_LIBACL_LIBACL_H`, `HAVE_ACL_DELETE_DEF_FILE`, `HAVE_ACL_ENTRIES`, `HAVE_ACL_FREE`, `HAVE_ACL_FROM_MODE`, `HAVE_ACL_FROM_TEXT`, `HAVE_ACL_GET_ENTRY`.

Control flow: `perm_copy_file.c` and `perm_copy_fd.c` use these macros to select native ACL preservation or chmod-only fallbacks.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Wrong feature macros change error handling and may drop extended ACLs silently. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy_fd.c -->
# sources/security-integrity/acl/libacl/perm_copy_fd.c

Purpose: fd-to-fd permission preservation helper used by cp-like callers. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 203 lines.

Important APIs and functions: Key symbols include `acl_free`, `acl_entries`, `acl_from_mode`, `set_acl_fd`, `perm_copy_fd`, `ERROR_CONTEXT_MACROS`.

Control flow: Stats the source fd, reads its ACL when available, applies it to the destination fd, falls back through mask-adjusted `fchmod` for base ACLs or unsupported ACL filesystems, and reports errors through `error_context`.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy_file.c -->
# sources/security-integrity/acl/libacl/perm_copy_file.c

Purpose: path-to-path permission preservation helper used by examples and downstream copy tools. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 240 lines.

Important APIs and functions: Key symbols include `acl_free`, `acl_entries`, `acl_from_mode`, `set_acl`, `perm_copy_file`, `ERROR_CONTEXT_MACROS`.

Control flow: Stats the source path, copies access ACLs with fallback chmod behavior, then copies or deletes directory default ACLs when the source is a directory.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/Makemodule.am -->
# sources/security-integrity/acl/libmisc/Makemodule.am

Purpose: Automake module that builds the internal `libmisc.la` convenience library used by libacl and command-line tools. The file is 9 lines.

Important APIs and targets: Important declarations or variables include `noinst_LTLIBRARIES`, `libmisc_la_SOURCES`. These names are build-system contracts rather than runtime C APIs.

Control flow: It appends `libmisc.la` to non-installed libtool libraries and lists helper sources for allocation growth, line parsing, quoting, uid/gid lookup, unquoting, and directory traversal.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/high_water_alloc.c -->
# sources/security-integrity/acl/libmisc/high_water_alloc.c

Purpose: Implements a reusable high-water buffer allocator for callers that grow scratch buffers. The file is 45 lines.

Important APIs and functions: Key symbols include `__acl_high_water_alloc`, `CHUNK_SIZE`.

Control flow: Rounds requested sizes to chunks, reallocates only when the requested size exceeds the current allocation, and updates caller-owned buffer/size pointers.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/high_water_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/next_line.c -->
# sources/security-integrity/acl/libmisc/next_line.c

Purpose: Reads logical lines from a stream into dynamically managed memory for tool stdin/test parsing. The file is 58 lines.

Important APIs and functions: Key symbols include `LINE_SIZE`.

Control flow: Consumes input until newline or EOF, grows storage with the high-water allocator, strips the trailing newline, and returns NULL on EOF/error.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/next_line.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/quote.c -->
# sources/security-integrity/acl/libmisc/quote.c

Purpose: Quotes strings for ACL text and diagnostics so control/special characters remain parseable. The file is 62 lines.

Important APIs and functions: Key symbols include No exported code symbols; the file is declarative or script-oriented..

Control flow: Scans for characters requiring escaping, allocates a string object, and emits backslash/octal escape sequences for unsafe bytes.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/quote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/uid_gid_lookup.c -->
# sources/security-integrity/acl/libmisc/uid_gid_lookup.c

Purpose: Resolves textual ACL user/group qualifiers to numeric ids with robust buffer growth around reentrant passwd/group APIs. The file is 128 lines.

Important APIs and functions: Key symbols include `get_id`, `grow_buffer`, `__acl_get_uid`, `__acl_get_gid`.

Control flow: Handles numeric strings directly, calls `getpwnam_r`/`getgrnam_r`, retries on `ERANGE`, and returns ACL-style errors on misses.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/uid_gid_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/unquote.c -->
# sources/security-integrity/acl/libmisc/unquote.c

Purpose: In-place unquoter for ACL text qualifiers. The file is 57 lines.

Important APIs and functions: Key symbols include `isoctal`.

Control flow: Walks quoted strings, decodes backslash escapes and octal byte forms, compacts the result in the same buffer, and returns the unquoted pointer.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/unquote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/walk_tree.c -->
# sources/security-integrity/acl/libmisc/walk_tree.c

Purpose: Recursive traversal engine shared by `getfacl` and `setfacl`. The file is 258 lines.

Important APIs and functions: Key symbols include `walk_tree_visited`, `walk_tree_rec`, `walk_tree`.

Control flow: Uses lstat/stat according to logical/physical flags, tracks visited `(dev, ino)` directories to break cycles, enforces one-filesystem mode, manages a limited pool of directory handles, and calls a user callback for each path or failure.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/walk_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/man/Makemodule.am -->
# sources/security-integrity/acl/man/Makemodule.am

Purpose: Top-level manpage Automake dispatcher that includes section-specific manpage fragments. The file is 3 lines.

Important APIs and targets: Important declarations or variables include No exported code symbols; the file is declarative or script-oriented.. These names are build-system contracts rather than runtime C APIs.

Control flow: The top-level makefile includes this fragment, which then includes `man1`, `man3`, and `man5` modules so CLI, library API, and ACL format documentation are installed together.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/man/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/man/man1/Makemodule.am -->
# sources/security-integrity/acl/man/man1/Makemodule.am

Purpose: Automake module adding command manual pages for installed ACL tools. The file is 4 lines.

Important APIs and targets: Important declarations or variables include `dist_man_MANS`. These names are build-system contracts rather than runtime C APIs.

Control flow: It appends `chacl.1`, `getfacl.1`, and `setfacl.1` to manpage distribution/install variables so tool documentation follows tool installation.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/man/man1/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/man/man3/Makemodule.am -->
# sources/security-integrity/acl/man/man3/Makemodule.am

Purpose: Automake module adding section 3 API manual pages for libacl functions. The file is 40 lines.

Important APIs and targets: Important declarations or variables include `dist_man_MANS`. These names are build-system contracts rather than runtime C APIs.

Control flow: It enumerates public ACL API pages for permissions, entries, serialization, file/fd access, validation, text formatting, and extension helpers, keeping installed API docs aligned with exported symbols.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/man/man3/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/man/man5/Makemodule.am -->
# sources/security-integrity/acl/man/man5/Makemodule.am

Purpose: Automake module adding the section 5 ACL format manual page. The file is 2 lines.

Important APIs and targets: Important declarations or variables include `dist_man_MANS`. These names are build-system contracts rather than runtime C APIs.

Control flow: It appends `acl.5` to distribution/install metadata so the ACL model and file format documentation is packaged with the library.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/man/man5/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/po/update-potfiles -->
# sources/security-integrity/acl/po/update-potfiles

Purpose: Maintenance script regenerating `po/POTFILES.in` from translatable C/header sources under include, libacl, libmisc, and tools. The file is 13 lines.

Important APIs and functions: Key symbols include No exported code symbols; the file is declarative or script-oriented..

Control flow: Runs `find`, filters out generated `include/config.h`, sorts paths in the C locale, and overwrites the gettext input manifest.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/po/update-potfiles -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/Makemodule.am -->
# sources/security-integrity/acl/test/Makemodule.am

Purpose: Automake test module wiring ACL functional tests, fixture files, and the deterministic passwd/group preload library into `make check`. The file is 38 lines.

Important APIs and targets: Important declarations or variables include `XFAIL_TESTS`, `TESTS`, `EXTRA_DIST`, `check_LTLIBRARIES`, `libtestlookup_la_SOURCES`, `libtestlookup_la_CFLAGS`, `libtestlookup_la_LDFLAGS`, `AM_TESTS_ENVIRONMENT`, `TEST_LOG_COMPILER`. These names are build-system contracts rather than runtime C APIs.

Control flow: It defines `TESTS`, ships `.test` scripts and helper scripts, builds `libtestlookup.la` from passwd/group shims, and sets test environment variables such as PATH and locale.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/make-tree -->
# sources/security-integrity/acl/test/make-tree

Purpose: Developer helper script for generating a synthetic directory tree for traversal/performance experiments. The file is 45 lines.

Important APIs and functions: Key symbols include `random_dir`, `random_file`, `create`.

Control flow: Recursively creates directories and files according to level/dir/file parameters; commented setfacl lines show how randomized ACLs can be added.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/make-tree -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/run -->
# sources/security-integrity/acl/test/run

Purpose: Perl test harness for ACL scenario files used by `make check`. The file is 375 lines.

Important APIs and functions: Key symbols include `exec_test`, `process_test`, `su`, `sg`.

Control flow: Creates an isolated temp directory, sets TESTDIR/PATH/TUSER/TGROUP, parses `$` command lines with `<` stdin and `>` expected output records, executes commands, compares exact or regex-prefixed output, reports colored status, supports line limits/verbose mode, and cleans up.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/run -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/runwrapper -->
# sources/security-integrity/acl/test/runwrapper

Purpose: Shell wrapper that injects the deterministic passwd/group lookup library before invoking the Perl harness. The file is 7 lines.

Important APIs and functions: Key symbols include No exported code symbols; the file is declarative or script-oriented..

Control flow: If `.libs/libtestlookup.so` exists, exports it through `LD_PRELOAD`, then executes `test/run` from `srcdir` or the current directory.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/runwrapper -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/sort-getfacl-output -->
# sources/security-integrity/acl/test/sort-getfacl-output

Purpose: Perl filter that sorts blank-line-separated `getfacl` output records for stable recursive-output comparisons. The file is 4 lines.

Important APIs and functions: Key symbols include No exported code symbols; the file is declarative or script-oriented..

Control flow: Reads all stdin at once, splits records on double newlines, sorts them, and prints records separated by blank lines.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/sort-getfacl-output -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/test_group.c -->
# sources/security-integrity/acl/test/test_group.c

Purpose: LD_PRELOAD group database shim used by tests for deterministic group-name/group-id lookups and ERANGE retry behavior. The file is 165 lines.

Important APIs and functions: Key symbols include `test_getgrent_r`, `test_getgr_match`, `match_name`, `getgrnam_r`, `match_gid`, `getgrgid_r`, `TEST_GROUP`, `ALIGN_MASK`, `ALIGN`.

Control flow: Parses `test/test.group`, implements `getgrnam_r`, `getgrgid_r`, and non-reentrant wrappers, deliberately forces large-buffer retries for name lookups, and returns fixture-backed records.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/test_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/test_passwd.c -->
# sources/security-integrity/acl/test/test_passwd.c

Purpose: LD_PRELOAD passwd database shim used by tests for deterministic user-name/user-id lookups and ERANGE retry behavior. The file is 158 lines.

Important APIs and functions: Key symbols include `test_getpwent_r`, `test_getpw_match`, `match_name`, `getpwnam_r`, `match_uid`, `getpwuid_r`, `TEST_PASSWD`, `ALIGN_MASK`, `ALIGN`.

Control flow: Parses `test/test.passwd`, implements `getpwnam_r`, `getpwuid_r`, and wrappers, forces growing-buffer paths for name lookups, and returns fixture-backed passwd records.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/test_passwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/Makemodule.am -->
# sources/security-integrity/acl/tools/Makemodule.am

Purpose: Automake module building installed ACL tools `chacl`, `getfacl`, and `setfacl` plus parser/sequence/set helper code. The file is 23 lines.

Important APIs and targets: Important declarations or variables include `tools_ldadd`, `bin_PROGRAMS`, `chacl_SOURCES`, `chacl_LDADD`, `getfacl_SOURCES`, `getfacl_LDADD`, `setfacl_SOURCES`, `setfacl_LDADD`. These names are build-system contracts rather than runtime C APIs.

Control flow: It appends programs to `bin_PROGRAMS`, enumerates per-tool source lists, and links tools with libacl/libmisc/gettext dependencies inherited from the top-level build.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/chacl.c -->
# sources/security-integrity/acl/tools/chacl.c

Purpose: Installed IRIX-compatible `chacl` tool for setting, removing, listing, and recursively applying access/default ACLs. The file is 354 lines.

Important APIs and functions: Key symbols include `acl_delete_file`, `list_acl`, `set_acl`, `walk_dir`, `usage`, `main`.

Control flow: Allows one mode flag, parses ACL text with `acl_from_text`, validates with `acl_check`, removes access/default ACLs by deleting extended entries or default xattrs, lists compact ACL text, and applies ACLs directly or through its recursive directory walker.

State and persistence: Tool state is process-global option flags, parsed command sequences, traversal flags, current path/stat data, transient ACL handles, and accumulated exit status. Persistent effects occur when setters/delete helpers update ACL xattrs or chmod-compatible mode bits on visited files.

Dependencies and integration points: Integrates public libacl APIs, private libmisc quoting/lookup/walk helpers, gettext/locale, libc option parsing, `walk_tree` recursion semantics, and generated build rules from `tools/Makemodule.am`.

Risks: CLI behavior is user-visible and historically compatible: POSIXLY_CORRECT modes, symlink traversal, default ACL handling, mask recalculation, absolute-path stripping, and partial-error exit codes must remain stable. Mutation paths can broaden or narrow permissions if mask/default ACL logic regresses.

Test signals: Run `make check` tool cases plus manual `getfacl`/`setfacl`/`chacl` scenarios on files, directories, symlinks, recursive trees, named users/groups, numeric ids, stdin path lists, base-vs-extended ACLs, unsupported filesystems, and dry-run/test output.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/chacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/do_set.c -->
# sources/security-integrity/acl/tools/do_set.c

Purpose: Core ACL mutation engine used by `setfacl` after command parsing. The file is 529 lines.

Important APIs and functions: Key symbols include `find_entry`, `has_execute_perms`, `clone_entry`, `print_test`, `set_perm`, `retrieve_acl`, `remove_extended_entries`, `do_set`, `RETRIEVE_ACL`.

Control flow: As a `walk_tree` callback, lazily retrieves access/default ACLs, applies command sequences, handles conditional execute `X`, replaces/removes entries, removes extended/default ACLs, clones base entries for default ACL creation, recalculates masks unless suppressed, validates results, prints test output or persists with `acl_set_file`/`acl_delete_def_file`.

State and persistence: Tool state is process-global option flags, parsed command sequences, traversal flags, current path/stat data, transient ACL handles, and accumulated exit status. Persistent effects occur when setters/delete helpers update ACL xattrs or chmod-compatible mode bits on visited files.

Dependencies and integration points: Integrates public libacl APIs, private libmisc quoting/lookup/walk helpers, gettext/locale, libc option parsing, `walk_tree` recursion semantics, and generated build rules from `tools/Makemodule.am`.

Risks: CLI behavior is user-visible and historically compatible: POSIXLY_CORRECT modes, symlink traversal, default ACL handling, mask recalculation, absolute-path stripping, and partial-error exit codes must remain stable. Mutation paths can broaden or narrow permissions if mask/default ACL logic regresses.

Test signals: Run `make check` tool cases plus manual `getfacl`/`setfacl`/`chacl` scenarios on files, directories, symlinks, recursive trees, named users/groups, numeric ids, stdin path lists, base-vs-extended ACLs, unsupported filesystems, and dry-run/test output.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/do_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/do_set.h -->
# sources/security-integrity/acl/tools/do_set.h

Purpose: Tool-private interface for `setfacl` application logic, declaring command execution state shared between parser/main code and `do_set.c`. The file is 40 lines.

Important APIs and types: Key declarations include `do_set`, `__DO_SET_H`.

Control flow: `setfacl.c` constructs a sequence of ACL commands, fills `do_set_args`, and passes `do_set` as the tree-walk callback.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Field semantics must remain aligned with parser command flags or setfacl may modify the wrong ACL type. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/do_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/getfacl.c -->
# sources/security-integrity/acl/tools/getfacl.c

Purpose: Installed `getfacl` command implementation for printing access/default ACLs, headers, effective-right comments, tabular output, recursion, symlink policy, numeric ids, and POSIXLY_CORRECT behavior. The file is 762 lines.

Important APIs and functions: Key symbols include `free_list`, `max_name_length`, `acl_perm_str`, `acl_mask_perm_str`, `apply_mask`, `show_line`, `do_show`, `acl_get_file_mode`, `flagstr`, `do_print`, `help`, `main`, `POSIXLY_CORRECT_STR`, `POSIXLY_CMD_LINE_OPTIONS`.

Control flow: Parses options, configures walk flags and output modes, walks command-line or stdin paths via `walk_tree`, reads access/default ACLs with fallback to mode-derived ACLs on unsupported filesystems, skips base ACLs when requested, strips leading slashes unless disabled, and formats output through `acl_to_any_text` or its tabular renderer.

State and persistence: Tool state is process-global option flags, parsed command sequences, traversal flags, current path/stat data, transient ACL handles, and accumulated exit status. Persistent effects occur when setters/delete helpers update ACL xattrs or chmod-compatible mode bits on visited files.

Dependencies and integration points: Integrates public libacl APIs, private libmisc quoting/lookup/walk helpers, gettext/locale, libc option parsing, `walk_tree` recursion semantics, and generated build rules from `tools/Makemodule.am`.

Risks: CLI behavior is user-visible and historically compatible: POSIXLY_CORRECT modes, symlink traversal, default ACL handling, mask recalculation, absolute-path stripping, and partial-error exit codes must remain stable. Mutation paths can broaden or narrow permissions if mask/default ACL logic regresses.

Test signals: Run `make check` tool cases plus manual `getfacl`/`setfacl`/`chacl` scenarios on files, directories, symlinks, recursive trees, named users/groups, numeric ids, stdin path lists, base-vs-extended ACLs, unsupported filesystems, and dry-run/test output.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/getfacl.c -->
