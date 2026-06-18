# Group Research: subset-b-000244

This grouped report covers the exact source files assigned to work item `subset-b-000244`. Each section is delimited for deterministic reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result.h -->
# sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result.h

## Purpose
This public header declares the `OstreeGpgVerifyResult` boxed/GObject-style result API used by libostree callers to inspect GPG signature verification outcomes. It defines the signature attribute enum, formatting flags, validation helpers, and the GPG error domain.

## Important APIs, Types, and Control Flow
The central opaque type is `OstreeGpgVerifyResult`. Callers count signatures with `ostree_gpg_verify_result_count_all()` and `ostree_gpg_verify_result_count_valid()`, locate a signature by key id with `ostree_gpg_verify_result_lookup()`, and extract typed attributes with `ostree_gpg_verify_result_get()` or `ostree_gpg_verify_result_get_all()`. `OstreeGpgSignatureAttr` fixes the schema for validity, expired/revoked/missing-key status, fingerprints, timestamps, algorithm names, and user identity strings. Human-readable output flows through `ostree_gpg_verify_result_describe()` and `ostree_gpg_verify_result_describe_variant()`. `ostree_gpg_verify_result_require_valid_signature()` converts a result object into a boolean security gate.

## State, Dependencies, Integration, Risks, and Tests
The header stores no state itself; persistence is in the result object produced by GPG verification code elsewhere. It depends on GLib/GIO and `ostree-types.h`, exports `_OSTREE_PUBLIC` symbols, and integrates with repository pull/commit/signature verification paths. Risks concentrate around keeping `OstreeGpgSignatureAttr` ordering and `GVariant` typing compatible with implementations and bindings. Test signals should cover no signatures, invalid signatures, missing/expired/revoked keys, lookup by key id, and stable describe output.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-impl-system-generator.c -->
# sources/cloud-native/ostree/src/libostree/ostree-impl-system-generator.c

## Purpose
This file implements the ostree systemd generator. At boot or soft reboot it detects an OSTree boot, ensures internal OSTree services are required, and synthesizes mount units/drop-ins for `/sysroot`, `/boot`, and `/var` so deployment mounts remain correct without rerunning the initramfs.

## Important APIs and Control Flow
The entry point is `_ostree_impl_system_generator(normal_dir, early_dir, late_dir, error)`. It first removes the initramfs handoff marker `INITRAMFS_MOUNT_VAR`; under static prepare-root builds it touches `/run/ostree-booted`, otherwise it no-ops unless `OTCORE_RUN_OSTREE` exists. It reads `/proc/cmdline`, extracts `ostree=` with `otcore_get_ostree_target()`, then runs `require_internal_units()`, `sysroot_mount_generator()`, `boot_mount_generator()`, and `fstab_generator()`. `require_internal_units()` creates symlinks for `ostree-remount.service` and `ostree-boot-complete.service`. `generate_mount_unit_dropin()` writes `DefaultDependencies=no` drop-ins. `boot_mount_generator()` emits a bind `boot.mount` only when `/sysroot/boot/loader` is a symlink and `/boot` exists. `fstab_generator()` parses the deployment stateroot, scans `/etc/fstab` with libmount for an existing `/var`, and if absent writes a bind `var.mount`.

## State, Dependencies, Integration, Risks, and Tests
Persistent output is generated systemd unit files and symlinks under `normal_dir`; runtime input comes from `/run`, `/proc/cmdline`, `/etc/fstab`, `/sysroot`, and `/boot`. Dependencies include libglnx, GIO streams, libmount when enabled, mount utilities, sysroot parsing helpers, and systemd unit path macros. Key risks are boot ordering regressions, duplicate generated files causing hard failures, libmount-disabled builds returning "Not implemented", and subtle soft-reboot dependency cycles. Test signals should exercise OSTree and non-OSTree cmdlines, aboot bootlinks, existing `/var` fstab entries, same-partition `/boot`, generated unit contents, and missing macro/libmount build configurations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-impl-system-generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-kernel-args-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-kernel-args-private.h

## Purpose
This private header exposes the internal representation helpers for `OstreeKernelArgs` to libostree implementation files and tests. It is not a stable public API; it exists to inspect and manipulate the ordered multimap backing kernel argument handling.

## Important APIs, State, and Integration
It forward declares `OstreeKernelArgsEntry` and exposes accessors for the hash table (`_ostree_kernel_arg_get_kargs_table()`), ordered array (`_ostree_kernel_arg_get_key_array()`), entry key/value getters and setters, indexed key/value lookup, entry allocation, value cleanup, and `_ostree_kernel_args_equal()`. These functions mirror the concrete structures in `ostree-kernel-args.c`: a `GHashTable` from key to entry arrays and a `GPtrArray` preserving argument order.

## Dependencies, Risks, and Tests
The header depends only on `ostree-kernel-args.h` and GLib declarations. Integration points are tests, deployment code needing equality checks, and internals that preserve ordering while replacing/deleting entries. Risk is representation leakage: callers can observe or mutate structures in ways that break ownership invariants if used outside controlled code. Test signals should include duplicate keys, NULL values, order-sensitive equality, and mutation through public APIs rather than direct private mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-kernel-args-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-kernel-args.c -->
# sources/cloud-native/ostree/src/libostree/ostree-kernel-args.c

## Purpose
This file implements `OstreeKernelArgs`, an ordered multimap for Linux kernel command-line arguments. It supports appending duplicate keys, replacing values, deleting specific key/value entries, parsing strings while preserving quoted spaces, filtering current `/proc/cmdline`, and serializing back to `strv` or a command-line string.

## Important APIs and Control Flow
`ostree_kernel_args_new()` creates the table and order array; `ostree_kernel_args_free()` releases both. `split_kernel_args()` tokenizes on spaces outside quotes. `split_keyeq()` mutates an argument buffer into key and value pieces. `ostree_kernel_args_append()` adds one or more parsed entries, preserving every duplicate in `order` and appending to the key's value array. `ostree_kernel_args_replace_take()` replaces all values for an existing key at its old order position or inserts a new key. `ostree_kernel_args_new_replace()` handles the advanced `key`, `key=new`, and `key=old=new` replacement forms and errors on ambiguous duplicate keys. `ostree_kernel_args_delete()` removes by key or key/value, while `ostree_kernel_args_delete_key_entry()` removes all entries for a key. Serialization walks `order`, and `ostree_kernel_args_get_last_value()` returns the final value for a key.

## State, Dependencies, Integration, Risks, and Tests
State is entirely in memory: `table` owns key strings and per-key `GPtrArray`s, while `order` references the same entries for deterministic output. `/proc/cmdline` is read only by `ostree_kernel_args_append_proc_cmdline()`, filtering `BOOT_IMAGE=` and `initrd=`. Dependencies are GLib, libglnx, `otutil`, and private helpers. Risks include ownership coupling between table and order, quote parsing asserting on unterminated quotes, `ostree_kernel_args_contains()` checking only keys despite accepting key/value text, and ambiguous duplicate-key edits. Test signals should cover duplicate keys, NULL versus empty values, quoted arguments, delete ambiguity, replace old/new syntax, `/proc/cmdline` filters, and order-preserving serialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-kernel-args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-kernel-args.h -->
# sources/cloud-native/ostree/src/libostree/ostree-kernel-args.h

## Purpose
This public header declares the `OstreeKernelArgs` API for constructing, mutating, parsing, querying, and serializing kernel command-line argument sets used during deployment and bootloader configuration.

## Important APIs and Behavior
The lifecycle surface is `ostree_kernel_args_new()`, `ostree_kernel_args_free()`, and `ostree_kernel_args_cleanup()`. Mutation APIs include `replace_take()`, `replace()`, `replace_argv()`, `append()`, `append_argv()`, `append_argv_filtered()`, `new_replace()`, `delete()`, `delete_key_entry()`, `append_if_missing()`, and `delete_if_present()`. Data import/export APIs include `append_proc_cmdline()`, `parse_append()`, `from_string()`, `to_strv()`, and `to_string()`. Query APIs are `get_last_value()` and `contains()`.

## State, Dependencies, Integration, Risks, and Tests
The type is opaque in the public header, so callers rely on documented ownership transfer and GLib allocation conventions. It depends on `ostree-types.h`, GLib, GObject, and GIO. Integration points include admin deployment commands, bootloader configuration, and tests referenced by the `/proc/cmdline` filter comment. Risks are semantic ambiguity around duplicate keys and whether a key/value argument to `contains()` should imply value matching. Tests should assert API-level behavior without relying on private structures except in dedicated internal tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-kernel-args.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-libarchive-input-stream.c -->
# sources/cloud-native/ostree/src/libostree/ostree-libarchive-input-stream.c

## Purpose
This file adapts libarchive entry data into a `GInputStream`. It lets OSTree code consume archive member contents through GLib stream APIs while libarchive remains the underlying reader.

## Important APIs and Control Flow
`G_DEFINE_TYPE_WITH_PRIVATE` defines `OstreeLibarchiveInputStream` as a `GInputStream` subclass with a construct-only pointer property `archive`. `_ostree_libarchive_input_stream_new(struct archive *a)` creates the stream. `ostree_libarchive_input_stream_read()` first honors `GCancellable`, then calls `archive_read_data()`, returning bytes read or mapping libarchive errors into `G_IO_ERROR_FAILED`. `close_fn` is intentionally a no-op returning TRUE; the stream does not own or close the archive.

## State, Dependencies, Integration, Risks, and Tests
State is one borrowed `struct archive *` stored in private data. Dependencies are GObject, GIO, and libarchive. The stream integrates with archive import paths that expect `GInputStream` content sources. Risks are lifetime-sensitive: callers must keep the archive valid and positioned on an entry while the stream is used. The close no-op means archive cleanup belongs to the surrounding archive reader. Test signals should cover successful reads, cancellation, libarchive read errors, and ownership/lifetime behavior when the stream is closed before the archive.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-libarchive-input-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-libarchive-input-stream.h -->
# sources/cloud-native/ostree/src/libostree/ostree-libarchive-input-stream.h

## Purpose
This private header declares the `OstreeLibarchiveInputStream` GType and constructor used to expose a libarchive reader as a `GInputStream`.

## Important APIs, State, and Integration
It defines type-checking macros, the instance/class structs, the private pointer slot, `_ostree_libarchive_input_stream_get_type()`, and `_ostree_libarchive_input_stream_new(struct archive *a)`. The instance embeds `GInputStream` and stores private state allocated by the implementation. The class includes reserved slots for ABI padding inside the private libostree boundary.

## Dependencies, Risks, and Tests
The header depends on `ostree-libarchive-private.h` and GIO. It is an internal integration bridge between libarchive import logic and GLib stream consumers. Risks are mostly compile-time and ownership-related: the archive pointer is not refcounted by the stream and the header assumes libarchive declarations are available through the private header. Tests should confirm the constructor returns a readable `GInputStream` and that closing it does not destroy the archive.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-libarchive-input-stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-libarchive-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-libarchive-private.h

## Purpose
This private header centralizes libarchive cleanup typedefs and small archive-opening helpers for OSTree archive import/export code. It is hidden from GObject introspection.

## Important APIs and Control Flow
When `HAVE_LIBARCHIVE` is enabled, it defines autoptr cleanup aliases for `struct archive` readers/writers and `archive_entry`. `ot_archive_read_new()` allocates a reader, enables all filters or legacy compression support depending on libarchive feature macros, and enables all formats. `ot_open_archive_read(path, error)` and `ot_open_archive_read_fd(fd, error)` create readers and open them with an 8192-byte block size, mapping libarchive failures to `G_IO_ERROR_FAILED`.

## State, Dependencies, Integration, Risks, and Tests
State is owned by returned libarchive objects and cleaned by `archive_read_free()` or related cleanup functions. Dependencies include `config.h`, `otutil`, GIO, and libarchive headers behind feature guards. Integration points include archive import commands and `OstreeLibarchiveInputStream`. Risks are build-configuration drift, all-format/all-filter attack surface, and caller responsibility to handle archive entry iteration safely. Test signals should include opening by path and fd, unsupported/corrupt archives, feature-macro builds, and cleanup on early error.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-libarchive-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-linuxfsutil.c -->
# sources/cloud-native/ostree/src/libostree/ostree-linuxfsutil.c

## Purpose
This file wraps Linux filesystem ioctls used by OSTree while isolating problematic kernel header includes. It supports toggling the immutable flag and freezing/thawing filesystems.

## Important APIs and Control Flow
`_ostree_linuxfs_fd_alter_immutable_flag(fd, new_immutable_state, cancellable, error)` uses `EXT2_IOC_GETFLAGS` and `EXT2_IOC_SETFLAGS` to read and change `EXT2_IMMUTABLE_FL`. A static atomic `no_alter_immutable` disables future attempts after `EPERM`; unsupported filesystems (`EOPNOTSUPP`, `ENOTTY`) are silently ignored. `_ostree_linuxfs_filesystem_freeze(fd)` and `_ostree_linuxfs_filesystem_thaw(fd)` wrap `FIFREEZE` and `FITHAW` with `TEMP_FAILURE_RETRY`.

## State, Dependencies, Integration, Risks, and Tests
Persistent state changes occur on the target inode or mounted filesystem. Process state includes the global atomic capability-disable flag. Dependencies include `ext2fs/ext2_fs.h`, `linux/fs.h`, `sys/ioctl.h`, libglnx error helpers, and `ostree-linuxfsutil.h`. Integration points include commit/deployment code that protects files or coordinates filesystem snapshots. Risks are silently skipped protection on unsupported/unprivileged systems, process-wide disable after one `EPERM`, and freeze/thaw deadlocks if callers fail to pair operations. Tests need privilege-aware coverage and should include unsupported filesystem behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-linuxfsutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-linuxfsutil.h -->
# sources/cloud-native/ostree/src/libostree/ostree-linuxfsutil.h

## Purpose
This private header declares Linux-specific filesystem utility wrappers used elsewhere in libostree.

## Important APIs, State, and Integration
It exports `_ostree_linuxfs_fd_alter_immutable_flag()`, `_ostree_linuxfs_filesystem_freeze()`, and `_ostree_linuxfs_filesystem_thaw()`. The header keeps callers away from direct `linux/fs.h` inclusion, matching the implementation comment about glibc/kernel header conflicts. It depends on `ostree-types.h` for GLib/GIO types.

## Risks and Tests
The API is intentionally low-level and fd-based, so misuse can affect live filesystems. Callers must handle integer errno returns from freeze/thaw and boolean/GError returns from immutable changes consistently. Tests should verify compile isolation, error propagation for unexpected ioctls, and graceful success on unsupported immutable flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-linuxfsutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-common.c -->
# sources/cloud-native/ostree/src/libostree/ostree-lzma-common.c

## Purpose
This file translates liblzma return codes into GLib `GConverterResult` values and `GError`s shared by OSTree's LZMA compressor and decompressor.

## Important APIs and Control Flow
`_ostree_lzma_return(lzma_ret res, GError **error)` maps `LZMA_OK` to `G_CONVERTER_CONVERTED`, `LZMA_STREAM_END` to `G_CONVERTER_FINISHED`, and every known error to `G_CONVERTER_ERROR` with a specific `G_IO_ERROR` message. `LZMA_BUF_ERROR` is mapped to `G_IO_ERROR_PARTIAL_INPUT`; memory, format, options, data, and check errors are mapped to failed converter errors.

## State, Dependencies, Integration, Risks, and Tests
The function is stateless. Dependencies are liblzma, GLib/GIO, errno/string headers, and the shared header. Compressor/decompressor implementations rely on this mapping for all terminal results. Risks are semantic mismatch between liblzma's `LZMA_BUF_ERROR` and GLib callers' expectations, and loss of numeric lzma code details. Test signals should exercise each mapped error, stream end, and normal converted return.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-common.h -->
# sources/cloud-native/ostree/src/libostree/ostree-lzma-common.h

## Purpose
This private header declares the common liblzma-to-GIO converter result helper used by OSTree LZMA converters.

## Important API, Dependencies, and Integration
It includes GIO and liblzma and declares `GConverterResult _ostree_lzma_return(lzma_ret value, GError **error)`. Both compressor and decompressor call it after initializing or running an `lzma_stream`.

## Risks and Tests
The header exposes a narrow error-conversion contract. Any change in mapping affects all LZMA stream consumers. Compile tests should cover liblzma availability, and behavior tests should ensure converter users receive consistent `G_IO_ERROR` domains and converter result values.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-compressor.c -->
# sources/cloud-native/ostree/src/libostree/ostree-lzma-compressor.c

## Purpose
This file implements `OstreeLzmaCompressor`, a `GConverter` that compresses data using liblzma. It is a GObject wrapper around `lzma_stream` for use in GLib converter streams.

## Important APIs and Control Flow
The type stores optional construct-only `params`, an `lzma_stream`, and an `initialized` flag. `_ostree_lzma_compressor_new(params)` constructs it. The converter `reset` method calls `lzma_end()`, restores `LZMA_STREAM_INIT`, and clears initialization. `_ostree_lzma_compressor_convert()` rejects non-empty input with zero output space, lazily initializes `lzma_easy_encoder()` at preset 8 with `LZMA_CHECK_CRC64`, wires input/output buffers into the stream, maps GLib flags to `LZMA_RUN`, `LZMA_SYNC_FLUSH`, or `LZMA_FINISH`, then calls `lzma_code()`. Bytes read/written are computed from remaining stream availability, and results flow through `_ostree_lzma_return()`.

## State, Dependencies, Integration, Risks, and Tests
State is per-object stream state plus the unused/stored params variant. Dependencies are GObject, GIO converter interfaces, liblzma, and the common mapper. Integration points are archive/object compression paths that need streaming XZ/LZMA output. Risks include hard-coded compression level/check despite the `params` property, incomplete handling of no-progress buffer conditions, and correct finalization after partial conversions. Tests should cover streaming chunks, flush, finish, reset/reuse, small output buffers, and corrupt/unsupported initialization errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-compressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-compressor.h -->
# sources/cloud-native/ostree/src/libostree/ostree-lzma-compressor.h

## Purpose
This private header declares the `OstreeLzmaCompressor` GType and constructor.

## Important APIs, State, and Integration
It defines the standard GObject type macros, forward declares the instance and class, declares `_ostree_lzma_compressor_get_type()`, and exposes `_ostree_lzma_compressor_new(GVariant *params)`. The class derives from `GObject`; the converter interface is attached in the implementation.

## Dependencies, Risks, and Tests
The header depends on GIO for converter/GObject declarations. It is used by code that wraps compression in `GConverterInputStream` or `GConverterOutputStream`. Risk is mostly API expectation drift around `params`, since construction accepts it but current implementation does not interpret it. Tests should verify type registration and constructor behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-compressor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-decompressor.c -->
# sources/cloud-native/ostree/src/libostree/ostree-lzma-decompressor.c

## Purpose
This file implements `OstreeLzmaDecompressor`, a `GConverter` wrapper around liblzma stream decoding.

## Important APIs and Control Flow
`_ostree_lzma_decompressor_new()` constructs the object. The instance owns an `lzma_stream` and an `initialized` flag. `reset` ends any active stream and restores `LZMA_STREAM_INIT`. `_ostree_lzma_decompressor_convert()` rejects non-empty input with zero output space, lazily initializes `lzma_stream_decoder()` with unlimited memory and no flags, sets input/output buffer pointers, runs `lzma_code(..., LZMA_RUN)`, records bytes consumed/produced for `LZMA_OK` and `LZMA_STREAM_END`, and delegates final result/error mapping to `_ostree_lzma_return()`.

## State, Dependencies, Integration, Risks, and Tests
State is per-object decompression progress. Dependencies are GObject, GIO, liblzma, and the common mapper. Integration points are OSTree object/archive decompression and any GLib converter stream that needs LZMA input. Risks include unlimited decoder memory, no explicit handling of `G_CONVERTER_INPUT_AT_END` flags, and partial-input semantics depending entirely on liblzma return codes. Tests should cover chunked decompression, stream end, reset/reuse, zero output buffer errors, corrupt input, and memory-limit expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-decompressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-decompressor.h -->
# sources/cloud-native/ostree/src/libostree/ostree-lzma-decompressor.h

## Purpose
This private header declares the `OstreeLzmaDecompressor` GType and constructor.

## Important APIs, State, and Integration
It defines GObject type macros, forward declares the instance/class, declares `_ostree_lzma_decompressor_get_type()`, and exposes `_ostree_lzma_decompressor_new()`. The class derives from `GObject`; the implementation supplies the `GConverter` interface.

## Dependencies, Risks, and Tests
The header depends on GIO. It integrates with GLib converter streams used by object and archive readers. Risks are low at the declaration layer, but ABI/type macro correctness matters for casts and introspection-like internal use. Tests should ensure type registration, constructor success, and converter interface availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-lzma-decompressor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-metalink.c -->
# sources/cloud-native/ostree/src/libostree/ostree-metalink.c

## Purpose
This file implements synchronous Metalink fetching for OSTree. It downloads a metalink document, parses the requested file entry, validates size and SHA-256/SHA-512 checksums, and tries listed HTTP(S) target URLs until one succeeds.

## Important APIs and Control Flow
`_ostree_metalink_new(fetcher, requested_file, max_size, uri, n_network_retries)` stores a fetcher, requested filename, metalink URI, maximum size, and retry count. `_ostree_metalink_request_sync()` creates a private main context, downloads the metalink into memory with `_ostree_fetcher_request_uri_to_membuf()`, parses it with `GMarkupParseContext`, then calls `try_metalink_targets()`. The parser is a state machine over `metalink/files/file/size/verification/hash/resources/url`, with passthrough state for unknown or ignored elements. Only URLs with `protocol` `http` or `https` are collected. `try_one_url()` downloads a candidate target, checks exact byte size, and verifies SHA-512 preferentially, then SHA-256.

## State, Dependencies, Integration, Risks, and Tests
Persistent state is none; request state includes parsed size, hashes, URL array, last error, and parser state. Dependencies include `OstreeFetcher`, fetcher URI helpers, GMarkup, GBytes, and GChecksum. Integration points are summary or content fetch paths using metalink indirection. Risks include strict XML shape assumptions, lowercase-only hex validation, collecting URLs in document order without preference sorting, full in-memory downloads capped only by `max_size`, and parser text callbacks overwriting hash text if split unexpectedly. Tests should cover missing file entries, unknown elements, bad sizes, invalid hash length/characters, multiple URLs with fallback, checksum mismatch, non-HTTP filtering, and max-size enforcement.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-metalink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-metalink.h -->
# sources/cloud-native/ostree/src/libostree/ostree-metalink.h

## Purpose
This private header declares the `OstreeMetalink` GObject wrapper and synchronous request API for Metalink resolution. It is hidden from GObject introspection.

## Important APIs, State, and Integration
It defines GObject type macros, `OstreeMetalinkClass`, an autoptr cleanup function, `_ostree_metalink_get_type()`, `_ostree_metalink_new()`, and `_ostree_metalink_request_sync()`. The constructor binds an `OstreeFetcher`, requested filename, max size, metalink URI, and network retry count; the request API returns the selected target URI and/or downloaded bytes.

## Dependencies, Risks, and Tests
The header depends on `ostree-fetcher.h` and GLib/GObject. It integrates with fetch code that can use Metalink metadata as a mirror list and verification envelope. Risks are internal ownership conventions for returned `OstreeFetcherURI` and `GBytes`. Tests should verify constructor/ref cleanup and request output ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-metalink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-mutable-tree.c -->
# sources/cloud-native/ostree/src/libostree/ostree-mutable-tree.c

## Purpose
This file implements `OstreeMutableTree`, the in-memory modifiable directory tree used to compose commits. It tracks file checksums, child trees, metadata checksum, dirtree checksum, and a lazy-loading state backed by an `OstreeRepo`.

## Important APIs and Control Flow
The object has `WHOLE` and `LAZY` states. `ostree_mutable_tree_new()` creates an empty whole tree; `new_from_checksum()` and `new_from_commit()` create lazy trees from repo object checksums. `_ostree_mutable_tree_make_whole()` loads a lazy dirtree variant, fills `files` and `subdirs`, creates lazy children, drops the repo ref, and switches to whole. Mutation APIs (`replace_file()`, `remove()`, `ensure_dir()`, `ensure_parent_dirs()`) validate filenames, force whole state, enforce file-vs-directory conflicts, and call `invalidate_contents_checksum()` up the parent chain. Lookup and walk APIs traverse loaded trees. `fill_empty_from_dirtree()` optimizes composition by converting empty or compatible trees to lazy references instead of loading them. Non-throwing getters cache lazy-load errors in `cached_error`; `check_error()` reports them later.

## State, Dependencies, Integration, Risks, and Tests
State includes parent back-pointers, cached checksums, optional repo ref, cached error, and hash tables for files/subdirs. Child ownership is shared by the parent hash table; `remove_child_mtree()` clears stale parent pointers before unref. Dependencies include OSTree core variant formats, filename validation, repo object loading, GObject, and GLib hash tables. Risks include checksum invalidation invariants partly enforced by callers, cached errors from getter paths, recursive walk depth, and subtle parent lifetime handling. Test signals should cover lazy load, mutation invalidation up ancestors, file/dir conflict errors, noent handling, empty-tree fill optimization, new-from-commit checksum extraction, and child lifetime after parent destruction.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-mutable-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-mutable-tree.h -->
# sources/cloud-native/ostree/src/libostree/ostree-mutable-tree.h

## Purpose
This public header declares the `OstreeMutableTree` API used to build and edit commit trees before writing them to an `OstreeRepo`.

## Important APIs, State, and Integration
The header defines type macros, `OstreeMutableTreeClass`, and an iterator helper struct. Constructors include `ostree_mutable_tree_new()`, `new_from_commit()`, and `new_from_checksum()`. Checksum APIs get/set metadata and contents checksums. Mutation and traversal APIs include `replace_file()`, `remove()`, `ensure_dir()`, `lookup()`, `ensure_parent_dirs()`, `walk()`, `fill_empty_from_dirtree()`, `check_error()`, `get_subdirs()`, and `get_files()`.

## Dependencies, Risks, and Tests
It depends on `ostree-types.h` and exposes GLib containers by transfer-none getters, so callers must not free returned hash tables. Integration points include commit writers and import code. Risks include public access to mutable hash-table contents through getters and lazy-load errors surfaced only by `check_error()` after legacy getter calls. Tests should verify documented transfer semantics and error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-mutable-tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-ref.c -->
# sources/cloud-native/ostree/src/libostree/ostree-ref.c

## Purpose
This file implements `OstreeCollectionRef`, a boxed value representing `(collection_id, ref_name)`. It gives OSTree a globally unique ref identity for peer-to-peer and collection-aware operations, while allowing `NULL` collection IDs for legacy plain refs.

## Important APIs and Control Flow
`ostree_collection_ref_new()` validates a non-NULL ref name and optional collection ID, then deep-copies both strings. `ostree_collection_ref_dup()` uses the constructor to copy. `ostree_collection_ref_free()` releases strings and the struct. `ostree_collection_ref_hash()` XORs collection and ref hashes when a collection exists, otherwise hashes only the ref name. `ostree_collection_ref_equal()` compares both fields with `g_strcmp0()`. `dupv()` and `freev()` deep-copy and free NULL-terminated arrays; `dupv()` uses `g_strv_length()` as a pointer-array length hack.

## State, Dependencies, Integration, Risks, and Tests
State is the allocated pair of strings. Dependencies include validation helpers from `ostree-core`, GLib boxed types, and libglnx headers. Integration points include ref maps, summary/pull code, and APIs that accept collection-ref vectors. Risks are hash collisions from XOR being acceptable but simple, `dupv()` assuming a NULL-terminated pointer array compatible with string-vector length scanning, and constructor validation returning NULL rather than setting `GError`. Tests should cover NULL collection IDs, invalid collection/ref names, equality/hash table behavior, and vector ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-ref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-ref.h -->
# sources/cloud-native/ostree/src/libostree/ostree-ref.h

## Purpose
This public header defines `OstreeCollectionRef`, the tuple type for globally identifying refs by optional collection ID plus ref name.

## Important APIs, State, and Integration
The struct exposes `gchar *collection_id` and `gchar *ref_name`. The API declares boxed type registration, constructor, duplication/free functions, hash/equality callbacks, vector duplication/free helpers, and the `OstreeCollectionRefv` auto-cleanup-friendly typedef. It integrates with collection-aware pull, summary, and ref APIs where a plain ref string is insufficient.

## Risks and Tests
Because fields are public, callers can mutate them after construction and bypass validation; hash-table users must treat keys as immutable. Tests should assert construction validation, transfer ownership, hash/equality consistency, and vector cleanup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-ref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-remote-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-remote-private.h

## Purpose
This private header defines the concrete `OstreeRemote` structure and internal constructors used by repository configuration code.

## Important APIs, State, and Integration
`struct OstreeRemote` contains an atomic `ref_count`, display `name`, optional `refspec_name` for dynamic remotes inheriting from a static remote, keyfile `group`, keyring filename, optional config `GFile`, and `GKeyFile *options`. Internal constructors are `ostree_remote_new()`, `ostree_remote_new_dynamic()`, and `ostree_remote_new_from_keyfile()`.

## Dependencies, Risks, and Tests
The header depends on GLib/GIO, libglnx, public `ostree-remote.h`, and `ostree-types.h`. Integration points are repo remote loading, dynamic remote creation, keyring selection, and URL lookup. Risks are representation leakage inside libostree, especially around whether `name` or `refspec_name` should be used for config groups and keyrings. Tests should cover static and dynamic remote construction and keyfile group parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-remote-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-remote.c -->
# sources/cloud-native/ostree/src/libostree/ostree-remote.c

## Purpose
This file implements the `OstreeRemote` boxed/reference-counted configuration object. It represents a remote repository's configured name, keyfile group, keyring filename, backing config file, and options.

## Important APIs and Control Flow
`ostree_remote_new(name)` delegates to `ostree_remote_new_dynamic(name, NULL)`. Dynamic construction asserts non-empty names, initializes `ref_count` to 1, stores `name` and optional `refspec_name`, builds the keyfile group `remote "..."`, derives `$name.trustedkeys.gpg` or `$refspec_name.trustedkeys.gpg`, and creates an empty `GKeyFile`. `ostree_remote_new_from_keyfile()` validates a group with regex `^remote \"(.+)\"$`, extracts the name, constructs a remote, and copies that group into the remote options. `ostree_remote_ref()` and `ostree_remote_unref()` provide atomic refcounting; unref releases strings, file, keyfile, and slice memory. Public getters expose name and duplicate the configured `url`.

## State, Dependencies, Integration, Risks, and Tests
State persists only in memory unless associated with the repository config/keyfile. Dependencies are GLib/GIO, regex, `ot-keyfile-utils`, and the private struct header. Integration points include repo remote management, pull/fetch configuration, keyring lookup, and bindings via boxed type. Risks include regex acceptance of broad group names, assertions rather than recoverable errors for invalid dynamic construction, and split identity between dynamic remote display name and refspec/keyring name. Tests should cover refcount lifetime, group parsing failures, option copying, URL getter NULL behavior, and dynamic remote naming.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-remote.h -->
# sources/cloud-native/ostree/src/libostree/ostree-remote.h

## Purpose
This public header declares the opaque `OstreeRemote` API for passing remote configuration handles around libostree and bindings.

## Important APIs, State, and Integration
It declares boxed type registration, `ostree_remote_ref()`, `ostree_remote_unref()`, `ostree_remote_get_name()`, and `ostree_remote_get_url()`. The concrete state remains private, so external callers can only hold references and query basic identity/URL information.

## Risks and Tests
The limited public surface keeps configuration mutation internal, but callers must follow transfer rules: `get_name()` is borrowed and `get_url()` is newly allocated or NULL. Tests should cover boxed type behavior, NULL/invalid remote guard behavior, and memory ownership in bindings.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-remote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-checkout.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-checkout.c

## Purpose
This large implementation materializes OSTree commits or subpaths into a filesystem checkout. It handles directory recursion, hardlink and copy strategies, uncompressed cache population and GC, xattrs, ownership, SELinux labels, whiteouts, overwrite modes, fsync, composefs image generation, and dev/inode checksum caching.

## Important APIs and Control Flow
Public entry points are `ostree_repo_checkout_tree()`, deprecated `ostree_repo_checkout_tree_at()`, `ostree_repo_checkout_at()`, `ostree_repo_checkout_composefs()`, `ostree_repo_checkout_at_options_set_devino()`, `ostree_repo_devino_cache_new()`, and `ostree_repo_checkout_gc()`. `ostree_repo_checkout_at()` canonicalizes options, resolves a commit/subpath to an `OstreeRepoFile`, queries info, and delegates to `checkout_tree_at()`. `checkout_tree_at()` initializes path buffers for filters and SELinux labeling, opens the uncompressed cache if enabled, special-cases single-file checkouts, and recurses through directory metadata via `checkout_tree_at_recurse()`. File checkout first validates names, loads object info/xattrs, applies filters and whiteout handling, tries hardlinking from bare repos or uncompressed cache, may unpack archive objects into the cache, and falls back to copy through tempfiles. Copy paths set content, ownership, xattrs, mode, fsync, and atomic link replacement according to overwrite mode.

## State and Persistence
Persistent output is the destination tree, hardlinks to repo objects, optional `uncompressed-objects-cache` entries, composefs images, and overlayfs whiteout device nodes. Runtime state includes `CheckoutState` path buffers, option structs, repo cache locks, `updated_uncompressed_dirs`, and optional devino cache entries mapping checked-out hardlinks to checksums. Directory metadata is applied after children are created to avoid exposing partial directories.

## Dependencies, Integration, Risks, and Tests
Dependencies include GIO file/stream APIs, libglnx fd/tempfile helpers, xattrs, OSTree repo/core/private APIs, sepolicy helpers, composefs when enabled, and Unix syscalls. Integration points are deployment checkout, admin commands, rpm-ostree layering, container whiteout processing, composefs generation, and later commit detection through devino caches. Risks include path traversal prevention relying on filename validation, complex overwrite semantics, hardlink fallback behavior across devices, xattr/SELinux differences by repo mode, whiteout destructive deletes, uncompressed cache GC correctness, and option bugs such as legacy fsync polarity. Test signals should cover all overwrite modes, hardlink versus copy, archive cache creation and GC, user/bare-user-only modes, whiteouts and passthrough whiteouts, filters, SELinux labeling, fsync toggles, subpath and single-file checkout, composefs digest validation, and cross-device no-copy failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-checkout.c -->
