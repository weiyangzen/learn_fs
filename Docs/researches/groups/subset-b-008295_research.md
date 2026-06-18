# subset-b-008295 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/parse.c -->
## sources/security-integrity/acl/tools/parse.c

Purpose: ACL command and restore-file parser for `setfacl`. It converts textual ACL entries, comma lists, and `getfacl` comment blocks into `cmd_t` records stored in a `seq_t`.

Important functions are `parse_acl_cmd`, `parse_acl_seq`, `read_acl_comments`, and `read_acl_seq`; helpers `skip_tag_name` and `get_token` implement tolerant ACL token parsing. Control flow recognizes user/group/other/mask/default entries, resolves user and group names through libacl helpers, supports numeric and symbolic permissions including conditional `X`, and reports parse offsets through `which`. State is caller-owned except temporary tokens and parsed comment outputs. Dependencies include `sequence.h`, `misc.h` line/quote helpers, `sys/acl.h`, pwd/group lookup wrappers, and mode flag constants. Risks include permissive fallback to `user:` parsing, static line buffers from `__acl_next_line`, duplicate restore comments causing `-EINVAL`, and fragile pointer-offset diagnostics after parse failure. Test signals come indirectly from `setfacl --restore`, modify/remove-file tests, and ACL text compatibility cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/parse.h -->
## sources/security-integrity/acl/tools/parse.h

Purpose: public parser contract for ACL tool command sequences.

It defines parse-mode bits `SEQ_PARSE_WITH_PERM`, `SEQ_PARSE_NO_PERM`, `SEQ_PARSE_MULTI`, `SEQ_PARSE_DEFAULT`, and `SEQ_PROMOTE_ACL`, then declares the text and stream parsers used by `setfacl.c`. The API integrates with `sequence.h` by returning or appending `cmd_t` objects and with restore logic by exposing comment metadata outputs for path, uid, gid, and mode flags. State is owned by callers except allocated `path_p` from `read_acl_comments`. Risks are mode-bit combinations that can make permissions optional and the need for callers to free comment paths. Tests should exercise both inline CLI ACL strings and multi-line restore input.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/sequence.c -->
## sources/security-integrity/acl/tools/sequence.c

Purpose: minimal linked-list implementation for ACL edit commands.

`cmd_init`/`cmd_free` allocate command records, `seq_init`/`seq_free` own list lifetime, `seq_append` and `seq_append_cmd` add operations, `seq_get_cmd` iterates with `SEQ_FIRST_CMD`/`SEQ_NEXT_CMD`, and `seq_delete_cmd` removes a command. Control flow is simple append-only except cleanup and deletion of set-operation preambles in `setfacl.c`. State is heap-backed `struct seq_obj` plus heap-backed `struct cmd_obj` nodes. Dependencies are only libc allocation and `sequence.h`. Risks include no null-guard in `seq_free`, stale `s_last` when deleting the first and only entry, and caller reliance on list internals (`seq->s_last`) elsewhere. Tests should validate append/delete/iteration and empty-list behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/sequence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/sequence.h -->
## sources/security-integrity/acl/tools/sequence.h

Purpose: data model and command constants for `setfacl` edit sequences.

It defines `struct cmd_obj` fields for command kind, ACL type/tag/id/permissions, and next pointer, plus `struct seq_obj` head/tail pointers. Constants describe replace, remove-entry, remove-extended, and remove-ACL actions and permission bits including conditional execute. This header is the integration point between parsing, CLI construction, and the lower-level `do_set` executor. State/persistence is in-memory only. Risks are exposed struct internals that encourage cross-module mutation and numeric command values coupled to executor assumptions. Tests should cover every command constant through actual `setfacl` operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/sequence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/setfacl.c -->
## sources/security-integrity/acl/tools/setfacl.c

Purpose: CLI front end for setting, modifying, deleting, and restoring POSIX ACLs.

Important functions are `main`, `restore`, `next_file`, `help`, `has_any_of_type`, and `xquote`. Control flow builds a `seq_t` from options (`-m/-M/-x/-X/-b/-k`, plus non-POSIX `--set`, `--restore`, recursion and test mode), then applies it to file arguments through `walk_tree` and `do_set`. Restore mode reads `getfacl` comment headers, clears existing ACLs, parses replacement entries, then restores owner/group and setuid/setgid/sticky flags when needed. State includes global options for walk mode, mask recalculation, default ACL promotion, POSIX compatibility, and test mode. Dependencies include parser/sequence modules, `do_set`, `walk_tree`, gettext, getopt, stat/chown/chmod. Risks include global mutable option state, ACL restore ordering around `chown` clearing mode bits, parse-mode differences under `POSIXLY_CORRECT`, stdin-driven file lists, and symlink recursion semantics. Test signals are CLI exit statuses, restore round trips from `getfacl -R`, recursive traversal, and mask recalculation cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/setfacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/user_group.c -->
## sources/security-integrity/acl/tools/user_group.c

Purpose: UID/GID display helpers for ACL tools.

`user_name` resolves a UID with `getpwuid` unless numeric output is requested, otherwise formats a decimal string; `group_name` mirrors this with `getgrgid`. State is two static 22-byte buffers used for numeric fallback, so return values are overwritten by later calls and are not thread-safe. Dependencies are libc passwd/group databases and `snprintf`. Risks include static storage reuse and `"?"` fallback if formatting somehow fails. Tests should cover numeric and symbolic modes with missing users/groups.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/user_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/user_group.h -->
## sources/security-integrity/acl/tools/user_group.h

Purpose: declares ACL tool user/group name formatting helpers.

The header includes `sys/types.h`, `pwd.h`, and `grp.h`, and exposes `user_name(uid_t,int)` and `group_name(gid_t,int)`. It is consumed by display-oriented ACL tools such as `getfacl`. There is no persistent state in the header, but callers must treat returned pointers as borrowed static or libc-owned storage. Risks are missing include guards and the typo-like parameter name `gid_t uid` for `group_name`. Tests are through ACL output formatting with `--numeric`.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/user_group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/Makefile.am -->
## sources/security-integrity/attr/Makefile.am

Purpose: top-level Automake aggregation for the attr project.

It sets include paths, locale/sysconf defines, pkg-config install location, initializes program/library/header/man/doc variables, installs `xattr.conf`, and includes all module fragments. State is build-system metadata only; persistence is generated Makefiles and installed artifacts. Dependencies are Automake, gettext `po`, libtool fragments, and module files. Risks are module-order coupling because fragments append to shared variables. Test signals are `autoreconf`, `make`, `make install`, and `make check`.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/autogen.sh -->
## sources/security-integrity/attr/autogen.sh

Purpose: bootstrap script for regenerating autotools files.

It updates gettext POTFILES, runs `autopoint --force`, copies Automake's `INSTALL` into `doc/`, and executes `autoreconf -f -i`. State changes are generated autotools files and documentation support files. Dependencies are shell, gettext/autopoint, automake, and autoreconf. Risks are forceful regeneration causing broad metadata churn and dependency-version sensitivity. Test signal is successful configure script generation from a clean checkout.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/configure.ac -->
## sources/security-integrity/attr/configure.ac

Purpose: Autoconf configuration for libattr/tools.

It declares package `attr` 2.5.2, config headers, compiler/libtool/gettext setup, debug flags, calculated libtool revision, Linux conditional, GCC symbol-version attribute detection, and generated files. It also creates an `include/attr` symlink for in-tree include compatibility. State is configure-time substitutions and conditionals. Dependencies include Autoconf 2.69, Automake 1.15, Libtool, gettext, C compiler feature probes, and Linux host checks. Risks include fragile version parsing for `LT_REVISION`, symlink creation behavior on unusual filesystems, and Linux-only syscall wrappers behind `OS_LINUX`. Tests are `autoreconf`, `./configure` on target hosts, and symbol-version build checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/doc/Makemodule.am -->
## sources/security-integrity/attr/doc/Makemodule.am

Purpose: documentation distribution fragment.

It adds `CHANGES`, `COPYING`, and `COPYING.LGPL` to installed distributed docs, and includes generated `INSTALL` in extra distribution. There is no runtime state. Dependencies are Automake variables from the top-level file. Risks are missing `doc/INSTALL` if bootstrap did not copy it. Test signal is `make distcheck` or distribution tarball inspection.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/doc/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/examples/Makefile -->
## sources/security-integrity/attr/examples/Makefile

Purpose: standalone example build file for `copyattr`.

It compiles with debug/warnings, includes `../include`, links `-lattr`, and supports `all` and `clean`. State is the produced `copyattr` binary. Dependencies are a compiler and installed or findable libattr. Risks include assuming library search paths and not using the main build system variables. Test signal is building the example manually.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/examples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/examples/Makemodule.am -->
## sources/security-integrity/attr/examples/Makemodule.am

Purpose: distribution fragment for attr examples.

It ships `copyattr.c` and the standalone example `Makefile`. No runtime state. Dependencies are the top-level Automake `EXTRA_DIST`. Risks are examples drifting from installed headers if not compiled in regular CI. Test signal is `make dist` coverage and optional manual example build.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/examples/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/examples/copyattr.c -->
## sources/security-integrity/attr/examples/copyattr.c

Purpose: sample file-manager style extended-attribute copy program.

It defines an `error_context`, simplistic quote/free callbacks, a filter `is_user_attr` that allows only `user.*`, and `main` that calls `attr_copy_file(from,to,...)` when available. State is local process state only. Dependencies are public `attr/error_context.h` and `attr/libattr.h`, locale setup, and libc allocation. Risks include a leak/bug in `quote` where `pathname` is duplicated twice and the first duplicate is lost, minimal i18n, and compile-time feature guards that can disable the copy call. Test signal is manual copying of user xattrs and error callback behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/examples/copyattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/include/Makemodule.am -->
## sources/security-integrity/attr/include/Makemodule.am

Purpose: Automake install logic for public and private attr headers.

It lists headers, defines `SUBST_INSTALL_HEADER` to replace `EXPORT` with `extern` into temporary generated headers, installs public `attributes.h`, `error_context.h`, and `libattr.h`, and removes them on uninstall. State is generated `include/*.t` during install and installed header files. Dependencies are `sed`, install helpers, and top-level `pkgincludedir`. Risks include regex portability for `\<EXPORT\>` and install-time temporary-file cleanup. Test signals are `make install` and inspecting installed headers for correct `extern` declarations.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/include/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/include/attributes.h -->
## sources/security-integrity/attr/include/attributes.h

Purpose: deprecated IRIX-compatible extended-attributes API.

It defines namespace and operation flags, maximum value length, list result structures (`attrlist_t`, `attrlist_ent_t`, cursor), multi-operation structures, opcodes, and exported functions `attr_get`, `attr_set`, `attr_remove`, `attr_list`, `attr_multi` and fd variants. Control/integration is implemented in `libattr.c` by mapping IRIX names to Linux xattr namespaces. State is caller-owned buffers and cursors. Dependencies are `stdint.h`, errno values, and install-time replacement of `EXPORT`. Risks include deprecated API use, fixed ABI structures, cursor semantics over mutable xattr lists, and `ATTR_ROOT` privilege requirements. Tests should cover namespace mapping, list packing, multi-op error reporting, and fd/path variants.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/include/attributes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/include/error_context.h -->
## sources/security-integrity/attr/include/error_context.h

Purpose: callback interface for libattr error reporting and quoting.

`struct error_context` contains `error`, `quote`, and `quote_free` function pointers, with optional macros that null-check callbacks. State is supplied by callers, allowing tools to integrate localized or structured diagnostics. Dependencies are variadic printf contracts. Risks include callback lifetime and varargs format correctness; macro names can shadow other `error` or `quote` symbols when `ERROR_CONTEXT_MACROS` is defined. Test signals are xattr copy failures with and without context callbacks.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/include/error_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/include/libattr.h -->
## sources/security-integrity/attr/include/libattr.h

Purpose: public libattr copy-helper API.

It declares `attr_copy_file`, `attr_copy_fd`, backwards-compatible `attr_copy_check_permissions`, action constants `ATTR_ACTION_SKIP` and `ATTR_ACTION_PERMISSIONS`, and `attr_copy_action`. Control flows into xattr enumeration/copy functions and `/etc/xattr.conf` action lookup. State is caller-provided check callback and error context. Dependencies are `error_context` and installed `EXPORT` handling. Risks include ambiguous callback semantics where zero skips an attribute and default behavior intentionally excludes ACL-related attributes. Tests should cover default action filtering and explicit custom filters.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/include/libattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/include/misc.h -->
## sources/security-integrity/attr/include/misc.h

Purpose: private utility declarations shared by attr tools and libmisc.

It declares high-water allocation, quote/unquote, and line reading helpers. State is mostly static buffers inside implementations. Dependencies are standard `FILE`/`size_t` definitions from including translation units. Risks include no include guard and static-buffer APIs that are not thread-safe. Tests are indirect through CLI encoding, restore parsing, and long-line handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/include/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/include/nls.h -->
## sources/security-integrity/attr/include/nls.h

Purpose: gettext compatibility wrapper.

It includes locale support, maps `_()` to `gettext` when NLS is enabled, and provides no-op `textdomain`/`bindtextdomain` otherwise. State is process locale/textdomain. Dependencies are `ENABLE_NLS` and libintl. Risks are global locale effects and macro substitution in all tools. Test signals are translated and `LC_MESSAGES=C` test runs.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/include/nls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/include/walk_tree.h -->
## sources/security-integrity/attr/include/walk_tree.h

Purpose: recursive filesystem traversal API for attr tools.

It defines traversal mode flags, callback condition flags, and `walk_tree(path, flags, num_handles, callback, arg)`. Runtime behavior is implemented in `libmisc/walk_tree.c`. State is traversal-local. Dependencies are `struct stat` and callbacks. Risks are flag combinations around symlinks and one-filesystem traversal. Tests should cover recursive, logical, physical, top-level symlink, and failure callbacks.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/include/walk_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libattr.pc.in -->
## sources/security-integrity/attr/libattr.pc.in

Purpose: pkg-config template for libattr consumers.

It substitutes prefix, libdir, includedir, version, and emits `Cflags` plus `Libs: -lattr`. State is installed `libattr.pc`. Dependencies are configure substitutions. Risks are missing private libraries if link requirements change. Test signal is `pkg-config --cflags --libs libattr` after install.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libattr.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libattr/Makemodule.am -->
## sources/security-integrity/attr/libattr/Makemodule.am

Purpose: build fragment for `libattr.la`.

It defines libtool versioning, gettext linkage, exports dependency, source list, Linux-only syscall compatibility wrappers, compile injection of `libattr/libattr.h`, and linker version script flags. State is library ABI metadata and built shared/static artifacts. Dependencies include libtool, `exports`, gettext, and Linux conditional. Risks include ABI/version-script coupling and forced include behavior affecting every source. Test signals are library link, symbol version inspection, and downstream tool linkage.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libattr/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libattr/attr_copy_action.c -->
## sources/security-integrity/attr/libattr/attr_copy_action.c

Purpose: parse and apply `/etc/xattr.conf` copy policy.

It defines a linked list of `attr_action` patterns, lazy-loads `SYSCONFDIR/xattr.conf`, supports `skip` and `permissions` actions, and returns the first `fnmatch` action for an xattr name. State persists globally in `attr_actions` until parse failure or process exit. Dependencies are stdio allocation, `fnmatch`, `error_context`, and install-time `SYSCONFDIR`. Risks include global non-thread-safe lazy initialization, entire-file read with doubling size, reverse order because new actions prepend, parse strictness around whitespace/comments, and generic error messages that quote only the config path. Tests should cover missing config, malformed lines, wildcard precedence, and action lookups.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libattr/attr_copy_action.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libattr/attr_copy_check.c -->
## sources/security-integrity/attr/libattr/attr_copy_check.c

Purpose: default xattr copy filter.

`attr_copy_check_permissions` returns true only when `attr_copy_action(name, ctx)` returns zero, preserving backwards-compatible behavior of skipping configured ACL/security metadata unless explicitly allowed elsewhere. State is delegated to `attr_copy_action`'s cached config. Dependencies are public libattr and error context headers. Risks are the name: it returns false for any configured nonzero action, including `permissions`, which may surprise callers. Test signal is default `attr_copy_file` behavior against `xattr.conf`.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libattr/attr_copy_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libattr/attr_copy_fd.c -->
## sources/security-integrity/attr/libattr/attr_copy_fd.c

Purpose: copy extended attributes between open file descriptors.

`attr_copy_fd` lists source fd xattrs, grows name/value buffers on `ERANGE`, filters each name, gets values, and writes them to the destination fd. It reports per-attribute errors through `error_context` and tolerates unavailable xattr support on listing. State is local buffers with stack defaults and heap growth. Dependencies are `flistxattr`, `fgetxattr`, `fsetxattr`, gettext, and `attr_copy_check_permissions`. Risks include partial-copy semantics, delayed aggregate ENOTSUP reporting, no rollback, large xattr memory growth, and check callback side effects. Tests should cover small/large values, unsupported destination filesystems, ACL filtering, and ENOSYS/ENOTSUP handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libattr/attr_copy_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libattr/attr_copy_file.c -->
## sources/security-integrity/attr/libattr/attr_copy_file.c

Purpose: copy extended attributes between pathnames without following symlinks.

`attr_copy_file` mirrors fd copy logic using `llistxattr`, `lgetxattr`, and `lsetxattr`, preserving link-object xattrs where supported. It filters via caller callback or the default permissions checker, grows buffers on `ERANGE`, and reports source/destination/name failures. State is local and freed before return. Dependencies are Linux xattr syscalls, gettext, and `error_context`. Risks are partial copies, default exclusion of ACL metadata, symlink xattr portability, and continuing after individual get/set failures. Tests should cover symlink behavior, unsupported xattrs, and custom filter callbacks.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libattr/attr_copy_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libattr/libattr.c -->
## sources/security-integrity/attr/libattr/libattr.c

Purpose: implementation of the deprecated IRIX-style `attr_*` API over Linux xattr syscalls.

Important functions include namespace converters `api_convert`/`api_unconvert`, simple get/set/remove/list path and fd variants, list packing into `attrlist_t`, and userspace `attr_multi` decomposition. Control flow maps bare names into `user.`, `security.`, `trusted.`, or legacy `xfsroot.` namespaces, retries compatibility namespaces, handles `ERANGE` as `E2BIG` with required size, and tracks list cursor position in `cursor->opaque[0]`. State is caller buffers/cursors only. Dependencies are `<sys/xattr.h>`, public `attributes.h`, errno names, and Linux namespace semantics. Risks include fixed 64 KiB list buffer, cursor instability if xattrs mutate, no `ATTR_SECURE`/`ATTR_ROOT` checks beyond namespace filtering, deprecated ABI expectations, and `attr_multi` returning aggregate failure while per-op errors live in errno indirectly. Tests should cover namespace flags, compatibility fallback, list packing overflow, and multi-op invalid flags.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libattr/libattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libattr/libattr.h -->
## sources/security-integrity/attr/libattr/libattr.h

Purpose: forced internal feature header for libattr builds.

It defines `HAVE_ATTR_LIBATTR_H`, `HAVE_CONFIG_H`, and the xattr syscall feature macros so library sources compile desired code paths. State is compile-time only. Dependencies are inclusion through `-include libattr/libattr.h` in the build fragment. Risks are divergence from Autoconf probes and forcing code paths on unsupported platforms if misused. Test signal is successful Linux build and expected xattr-copy symbols.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libattr/libattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libattr/syscalls.c -->
## sources/security-integrity/attr/libattr/syscalls.c

Purpose: backwards-compatible symbol-versioned syscall wrappers for historical libattr exports.

It implements `libattr_*xattr` wrappers using `syscall(__NR_*)`, then assigns old symbol versions such as `setxattr@ATTR_1.0` using GCC symver attributes or `.symver` assembly. State is ABI/symbol table only. Dependencies are Linux syscall numbers, compiler symbol-version support, optional visibility attributes, and linker versioning. Risks include LTO/compiler quirks, syscall ABI portability, and maintaining old symbols that libc now normally provides. Tests should inspect exported symbol versions and run old binaries if available.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libattr/syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libmisc/Makemodule.am -->
## sources/security-integrity/attr/libmisc/Makemodule.am

Purpose: build fragment for private utility library `libmisc.la`.

It collects allocation, line reading, quoting, unquoting, and traversal helpers used by attr tools. State is build artifacts only. Dependencies are top-level Automake and source files. Risks are all helpers sharing one private library without independent tests. Test signal is successful linking of `attr`, `getfattr`, and `setfattr`.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libmisc/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libmisc/high_water_alloc.c -->
## sources/security-integrity/attr/libmisc/high_water_alloc.c

Purpose: reusable growing-buffer allocator.

`high_water_alloc` reallocates only when requested size exceeds current capacity, rounding up to 256-byte chunks and updating caller pointers. State is caller-owned buffer pointer and size. Dependencies are `realloc`. Risks include returning `1` while preserving the old buffer, integer rounding assumptions, and no shrink behavior. Tests are indirect through long line/value/encoding paths in attr tools.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libmisc/high_water_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libmisc/next_line.c -->
## sources/security-integrity/attr/libmisc/next_line.c

Purpose: line reader that supports long lines and strips CR/LF.

`next_line` uses a static buffer grown by `high_water_alloc`, repeatedly reads with `fgets`, trims line terminators, and returns the shared buffer. State is static and reused across calls, so it is not thread-safe and only one returned line remains valid. Dependencies are `getpagesize`, stdio, and `misc.h`. Risks include indistinguishable EOF vs allocation failure without checking stream state, static storage, and behavior on final unterminated lines. Tests are restore-file and transcript test inputs with long lines.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libmisc/next_line.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libmisc/quote.c -->
## sources/security-integrity/attr/libmisc/quote.c

Purpose: quote selected characters and backslashes using octal escapes.

`quote` scans for backslash or caller-specified quote characters, returns the original string if no quoting is needed, or a static grown buffer containing escaped text. State is static and reused. Dependencies are `high_water_alloc` and C string functions. Risks are non-thread-safe return storage, caller must handle `NULL` on allocation failure, and only selected characters are escaped, not all non-printables. Tests are output path/name quoting in `getfattr` and `setfattr` restore files.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libmisc/quote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libmisc/unquote.c -->
## sources/security-integrity/attr/libmisc/unquote.c

Purpose: in-place decoder for backslash-octal sequences.

`unquote` scans for `\NNN` octal escapes and compacts decoded bytes into the input buffer, leaving other backslash sequences mostly unchanged. State is caller-owned mutable string. Dependencies are only libc. Risks include modifying argv or static strings if callers pass non-writable data, accepting partial non-octal escapes literally, and embedded NUL effects after decode. Tests are restore parsing for quoted filenames and names.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libmisc/unquote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/libmisc/walk_tree.c -->
## sources/security-integrity/attr/libmisc/walk_tree.c

Purpose: recursive tree walker with symlink, one-filesystem, and file-descriptor-pressure handling.

It tracks visited directories by dev/inode to avoid loops, uses `lstat`/`stat` according to flags, calls the user callback for every path and failures, limits open directory handles based on `RLIMIT_NOFILE`, and reopens closed handles with saved `telldir` positions. State is traversal-local `walk_tree_args`, linked directory handles, mutable path buffer, and callback accumulator return values. Dependencies are POSIX directory/stat APIs. Risks include fixed `FILENAME_MAX` path buffer, complex symlink flag interactions, directory mutation during traversal, and callback error aggregation by addition. Tests should cover recursive symlink loops, ENAMETOOLONG, one-filesystem skipping, and low fd limits.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/libmisc/walk_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/man/Makemodule.am -->
## sources/security-integrity/attr/man/Makemodule.am

Purpose: manpage aggregation and symlink installation logic.

It includes man1/man3 fragments and adds an install hook that parses `.Nm` names from installed pages to create same-section symlinks for multi-interface manpages. State is installed manpage symlinks. Dependencies are `awk`, `sed`, shell, and `ln -s`. Risks include fragile roff parsing and duplicate symlink handling. Test signal is `make install` into a DESTDIR and manpage symlink inspection.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/man/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/man/man1/Makemodule.am -->
## sources/security-integrity/attr/man/man1/Makemodule.am

Purpose: declares command manpages for distribution/install.

It adds `attr.1`, `getfattr.1`, and `setfattr.1` to `dist_man_MANS`. State is packaging metadata only. Dependencies are top-level man aggregation. Risks are CLI behavior drifting from documentation. Tests are distribution/install checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/man/man1/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/man/man3/Makemodule.am -->
## sources/security-integrity/attr/man/man3/Makemodule.am

Purpose: declares library API manpages.

It adds man3 pages for `attr_get`, `attr_list`, `attr_multi`, `attr_remove`, and `attr_set`. Integration with the parent install hook creates aliases for multi-function pages. Risks are deprecated API documentation drift. Test signal is `make distcheck` and installed manpage alias coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/man/man3/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/po/update-potfiles -->
## sources/security-integrity/attr/po/update-potfiles

Purpose: regenerate gettext source file list.

The script writes `po/POTFILES.in` with a generated header and sorted `*.[ch]` files under include, libattr, libmisc, and tools, excluding generated `include/config.h`. State is the updated POTFILES file. Dependencies are shell, `find`, `grep`, `sort`, and locale sorting. Risks include excluding non-C translatable files and overwriting manual POTFILES edits. Test signal is running before gettext extraction and ensuring all `_()` call sites are included.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/po/update-potfiles -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/test/Makemodule.am -->
## sources/security-integrity/attr/test/Makemodule.am

Purpose: Automake test integration for attr CLI transcripts.

It lists test scripts/data, forces `LC_MESSAGES=C`, puts build and test helper directories on `PATH`, and uses `test/run` as `TEST_LOG_COMPILER`. State is test execution environment. Dependencies are Automake test harness and Perl runner. Risks are path-order assumptions and locale-only normalization, leaving filesystem xattr support as an external prerequisite. Test signal is `make check`.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/test/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/test/run -->
## sources/security-integrity/attr/test/run

Purpose: Perl transcript test runner.

It reads test files with `$` commands plus `<` stdin and `>` expected output lines, substitutes environment variables, runs each command in a per-test temp directory, captures combined stdout/stderr, supports regex expected lines with `~`, and implements built-ins like `cd`, `umask`, `su`, `sg`, `require_root`, `export`, and `unset`. State includes temp directories, environment changes, effective uid/gid changes, and pass/fail counters. Dependencies are Perl, POSIX privilege APIs, fork/pipe/exec, and shell fallback for metacharacters. Risks include taint disabled, combined stderr/stdout hiding stream differences, privilege mutation complexity, and shell quoting in fallback mode. Test signal is the runner’s command count and failed count.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/test/run -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/test/sort-getfattr-output -->
## sources/security-integrity/attr/test/sort-getfattr-output

Purpose: normalize `getfattr` multi-file output for tests.

It reads all input as one string, splits records on blank lines, sorts them, and prints records separated by blank lines. State is stream content only. Dependencies are Perl. Risks are assuming blank-line record separators and potentially reordering meaningful output if a value contains the same separator format. Test signal is stable transcript comparisons across filesystem traversal order.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/test/sort-getfattr-output -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/tools/Makemodule.am -->
## sources/security-integrity/attr/tools/Makemodule.am

Purpose: build fragment for attr command-line tools.

It defines common link dependencies on `libattr.la`, `libmisc.la`, and gettext, then builds `attr`, `getfattr`, and `setfattr`. State is built binaries. Dependencies are attr private/public libraries and top-level toolchain variables. Risks are all tools sharing private helper semantics and static buffers. Test signal is `make check` transcript coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/tools/Makemodule.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/tools/attr.c -->
## sources/security-integrity/attr/tools/attr.c

Purpose: legacy IRIX-style CLI for get/set/remove/list extended attributes.

`main` parses one of `-s/-g/-r/-l`, namespace flags `-R/-S`, follow flag `-L`, quiet mode, and optional `-V` value. It calls deprecated `attr_set`, `attr_get`, `attr_remove`, and cursor-based `attr_list`, reading set values from stdin when omitted and writing get values to stdout. State is process-local buffers and attrlist cursor. Dependencies are `attr/attributes.h`, gettext, and libmisc i18n. Risks include fixed max value size, deprecated API warnings suppressed, only one pathname allowed, root/security namespace privilege requirements, and verbose mode mixing binary values with text. Tests should cover all operations, stdin values, namespace flags, and quiet listing.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/tools/attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/tools/getfattr.c -->
## sources/security-integrity/attr/tools/getfattr.c

Purpose: modern CLI for listing and dumping Linux xattrs.

Important functions include `encode`, `print_attribute`, `list_attributes`, `do_print`, and `main`. Control flow compiles a name regex, walks paths with symlink/recursive flags, lists xattrs, filters/sorts names, optionally fetches values, encodes as text/hex/base64, strips leading slashes by default, and formats restore-compatible output. State includes global options, warning/error flags, static growing buffers, and compiled regex. Dependencies are Linux xattr syscalls, `walk_tree`, `quote`, `high_water_alloc`, getopt, regex, and gettext. Risks include heuristic text/base64 choice, static buffers, absolute-path warning side effects, regex errors, path mutation display logic, and no retry if xattr list grows between size and fetch. Tests should cover dump/only-values, encodings, recursive walks, symlink handling, regex filtering, and restore round trip with `setfattr`.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/tools/getfattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/tools/setfattr.c -->
## sources/security-integrity/attr/tools/setfattr.c

Purpose: modern CLI for setting/removing/restoring Linux xattrs.

It parses `-n/-v` set, `-x` remove, `-h` no-dereference, `--restore`, `--raw`, version/help, then applies `setxattr/lsetxattr` or remove variants. Restore mode consumes `getfattr -d` style `# file:` blocks, unquotes paths/names, decodes text/hex/base64 values unless raw, and sets/removes attributes. State includes global operation flags, static decode/path buffers, and error counters. Dependencies are libmisc quote/unquote/line/allocation helpers, Linux xattr syscalls, getopt, gettext. Risks include in-place unquote of option strings, complex base64 validation, restore status overwritten by later attributes, no create/replace flags, and following symlinks by default. Tests should cover all encodings, raw mode, restore files, deletion, symlink mode, and malformed input.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/tools/setfattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/attr/xattr.conf -->
## sources/security-integrity/attr/xattr.conf

Purpose: default policy for xattr copy helpers.

It maps attribute-name patterns to `permissions` or `skip`, marking POSIX/NFS ACLs as permission-related and excluding kernel/security/indexing/filesystem-specific metadata such as SGI, EVM, AFS, and Beagle attributes. State is installed system configuration read lazily by `attr_copy_action`. Dependencies are `fnmatch` pattern semantics. Risks include policy order/precedence because parser prepends entries, local admin edits affecting library behavior process-wide, and stale defaults for new security xattrs. Test signal is `attr_copy_file` behavior against representative names.
<!-- END_FILE_RESEARCH: sources/security-integrity/attr/xattr.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/.github/workflows/ci.yml -->
## sources/security-integrity/audit-userspace/.github/workflows/ci.yml

Purpose: GitHub Actions CI matrix for audit-userspace.

It runs on pushes and pull requests to master, builds in Ubuntu and Fedora containers with gcc and clang, installs distro-specific dependencies, runs `autoreconf`, configures with Python3, Kerberos, libcap-ng, LDAP, z/OS remote, experimental plugins, and io_uring enabled, then runs `make -j` and `make check`. State is CI environment only. Dependencies are container packages and Actions checkout. Risks include `latest` distro drift, broad feature flags increasing dependency fragility, and no sanitizer/static-analysis lane. Test signal is the matrix build/test result.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/Makefile.am -->
## sources/security-integrity/audit-userspace/Makefile.am

Purpose: top-level Automake layout for audit-userspace.

It orders subdirectories for common libraries, libaudit, auparse, dispatcher, plugins, tools, bindings, docs, and rules, lists distribution extras, and defines cleanup for generated artifacts. State is build-system metadata. Dependencies are all submodule Makefile fragments. Risks are subdir order coupling because dispatcher plugins depend on libraries built earlier. Test signal is full `make` and `make distcheck`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/Makefile.am -->
## sources/security-integrity/audit-userspace/audisp/Makefile.am

Purpose: build fragment for audit dispatcher static libraries.

It builds `libdisp.la` from dispatcher/config/list sources and `libqueue.la` from queue sources, links against common/libaudit and pthread, includes plugin tests, and exports internal headers. State is static noinst libraries. Dependencies are top-level libaudit/common, queue implementation, pthread, and compiler flags. Risks include static library boundaries hiding ABI issues and plugin headers consumed across directories. Test signal is dispatcher tests under `audisp/test` and full build.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-config.h -->
## sources/security-integrity/audit-userspace/audisp/audispd-config.h

Purpose: dispatcher daemon configuration structure.

`daemon_conf_t` stores queue depth, overflow action, max plugin restarts, and plugin directory. It extends auditd config types by including `auditd-config.h`. State is copied and owned by dispatcher runtime in `audispd.c`. Risks include string ownership around `plugin_dir` during reload and queue-depth changes requiring live queue resizing. Tests should cover dispatcher init/reconfigure with changed q_depth and plugin_dir.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-llist.c -->
## sources/security-integrity/audit-userspace/audisp/audispd-llist.c

Purpose: simple linked list for plugin configurations.

It initializes lists, appends copied `plugin_conf_t` records, iterates with current pointer, counts active plugins, clears memory, marks entries unchecked, and finds unchecked/name matches for reload reconciliation. State is heap nodes and shallow-copied plugin configs; `free_pconfig` must later release fields inside copied configs. Dependencies are allocation, string compare, and `audispd-pconfig.h`. Risks include shallow struct copy ownership assumptions, append requiring `cur` to point at the tail for nonempty lists, no internal locking, and current-pointer iteration invalidation during mutation. Tests should cover reload matching, duplicate names, and clear/free behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-llist.h -->
## sources/security-integrity/audit-userspace/audisp/audispd-llist.h

Purpose: list data structures and helpers for dispatcher plugin configs.

It defines `lnode` wrapping `plugin_conf_t *`, `conf_llist` with head/current/count, inline `plist_first`, `plist_count`, and `plist_get_cur`, plus list operations. State is external to callers. Dependencies are `audispd-pconfig.h` and compiler attribute macros. Risks are exposed mutable list internals and single-cursor design unsuitable for nested iteration. Test signals are pconfig/list unit tests in the audit dispatcher test directory.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-llist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-pconfig.c -->
## sources/security-integrity/audit-userspace/audisp/audispd-pconfig.c

Purpose: parser and validator for audisp plugin `.conf` files.

`load_pconfig` opens config files relative to a directory fd, verifies root ownership, non-world-writability, and regular-file target, then parses `key = value...` lines through keyword-specific parsers for active, direction, path, type, args, and format. It normalizes obsolete builtin paths/types, reverses args into stored order for later exec handling, records plugin basename, and validates active plugin executable ownership/permissions/inode. State is a populated `plugin_conf_t` with owned strings/arrays, pipes initialized to `-1`, restart counters, and inode for reload detection. Dependencies include `audit_msg`, `private.h`, file descriptor APIs, `dirname`/`basename`. Risks include whitespace-only tokenizer with no quoting, symlinked configs allowed after target checks, args reversal coupling with `safe_exec`, PATH_MAX formatting, and partial allocation cleanup correctness. Tests should cover malformed keywords, permissions failures, obsolete builtin config, arg ordering, and active executable validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-pconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-pconfig.h -->
## sources/security-integrity/audit-userspace/audisp/audispd-pconfig.h

Purpose: plugin configuration model for audisp dispatcher.

It defines active/type/format enums and `plugin_conf_t` fields for executable path, argv array, format, socketpair fds, child pid, inode, reload checked flag, config name, and restart count. Lifecycle APIs are `clear_pconfig`, `load_pconfig`, and `free_pconfig`. State is runtime-owned by dispatcher list nodes. Dependencies are libaudit types and attribute macros. Risks include ownership of `const char *path` despite allocation/free, pipe fd lifecycle, and restart counter preservation across reloads. Tests should validate clear/free idempotence and reload replacement.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd-pconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd.c -->
## sources/security-integrity/audit-userspace/audisp/audispd.c

Purpose: audit dispatcher library that queues audit events and fans them out to configured plugins.

Important APIs are `libdisp_init`, `libdisp_enqueue`, `libdisp_reconfigure`, `libdisp_shutdown`, `libdisp_resume`, `libdisp_write_queue_state`, and `plugin_child_handler`. Control flow loads plugin configs, starts active plugins through `socketpair`/`fork`/`execve`, creates a detached outbound thread, dequeues events, formats protocol v1/v2 records, writes string or binary payloads to child sockets, restarts plugins on `EPIPE` up to `max_restarts`, and handles HUP by loading a temp config list, matching old/new plugin names, restarting changed binaries, and terminating removed services. State includes atomic stop/HUP flags, daemon config snapshots for rollback, plugin list, queue state in `queue.c`, child pipes/pids, restart counts, and a static format buffer. Dependencies are libaudit, common atomics, queue library, pconfig/list modules, pthreads, signals, and syslog via `audit_msg`. Risks include no lock around `plugin_conf` when `plugin_child_handler` can run concurrently, detached thread lifetime during shutdown, partial writes not retried for short positive writes, execve with empty environment, and reload rollback complexity. Tests should cover no-plugin init, plugin lifecycle, EPIPE restart, HUP reload with bad config rollback, binary/string formats, and queue overflow behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/audispd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/libdisp.h -->
## sources/security-integrity/audit-userspace/audisp/libdisp.h

Purpose: internal public interface for audit dispatcher integration with auditd.

It defines `event_t` as an audit dispatcher header plus maximum audit message buffer and declares dispatcher lifecycle, enqueue, reconfigure, child handling, queue state, and resume APIs. State is hidden in `audispd.c` and queue implementation. Dependencies are `libaudit.h` and `auditd-config.h`. Risks include fixed data buffer size and callers needing to respect header size/protocol fields. Test signals are auditd dispatcher integration and queue state output.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/libdisp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/Makefile.am -->
## sources/security-integrity/audit-userspace/audisp/plugins/Makefile.am

Purpose: plugin subdirectory selection for audit dispatcher plugins.

It always builds af_unix, remote, syslog, and filter, adds ids/statsd under `ENABLE_EXPERIMENTAL`, and z/OS remote under `ENABLE_ZOS_REMOTE`. State is build traversal only. Dependencies are configure conditionals. Risks are feature-gated plugins missing regular build coverage unless CI enables flags. Test signal is CI configure enabling experimental and z/OS remote.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/Makefile.am -->
## sources/security-integrity/audit-userspace/audisp/plugins/af_unix/Makefile.am

Purpose: build/install fragment for `audisp-af_unix`.

It builds the PIE plugin from `audisp-af_unix.c` and local queue, links libaudit/auplugin/cap-ng, installs `af_unix.conf` under audit plugins.d with mode 640, and installs manpage metadata. State is installed binary and config. Dependencies include libaudit, libauplugin, optional libcap-ng, and hardening flags. Risks include install path assumptions (`/sbin`) matching config defaults and config file mode/dir ownership outside Automake. Test signals are build, install DESTDIR, and plugin runtime socket tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/af_unix.conf -->
## sources/security-integrity/audit-userspace/audisp/plugins/af_unix/af_unix.conf

Purpose: default audisp plugin config for AF_UNIX event socket forwarding.

It is inactive by default, runs `/sbin/audisp-af_unix`, type `always`, passes mode/path/format args (`0640 /run/audit/audispd_events string`) with optional queue depth, and receives binary dispatcher format. State is installed under plugins.d and parsed by `audispd-pconfig.c`. Risks include default path/binary mismatch on usr-merged systems and inactive default hiding test coverage. Test signal is enabling config and connecting a client to the socket.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/af_unix.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/audisp-af_unix.c -->
## sources/security-integrity/audit-userspace/audisp/plugins/af_unix/audisp-af_unix.c

Purpose: audisp plugin that relays audit events to one nonblocking Unix-domain socket client.

Important functions include signal handlers, `setup_socket`, `create_af_unix_socket`, `event_to_string`, `read_binary_record`, `read_audit_record`, `accept_connection`, `send_queue`, `event_loop`, and `main`. Control flow parses mode/path/output-format/queue-depth args, creates a stream socket, detects inbound protocol from stdin, reads binary or string audit records, converts formats as needed, queues output while a client is connected, accepts only one client, handles partial writes with `out_off`, writes state on SIGUSR1, and exits only on parent-origin SIGTERM or auditd EOF. State includes global socket/client fds, path/mode/format, inbound protocol, in-memory queue, pending output offset, flags, and optional malloc metrics. Dependencies are libaudit, auplugin framing helpers, local queue, poll/socket APIs, syslog, and optional libcap-ng. Risks include global non-threaded state, truncating oversized binary records, fcntl mixing file and fd flags for `FD_CLOEXEC`, dropped events when queue full, single-client semantics, and unlinking configured socket path on exit. Tests should cover protocol detection, string/binary conversion, queue backpressure, disconnect/reconnect, SIGUSR1 state, and parent-only SIGTERM.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/audisp-af_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/queue.c -->
## sources/security-integrity/audit-userspace/audisp/plugins/af_unix/queue.c

Purpose: simple fixed-capacity FIFO for AF_UNIX plugin output buffers.

`q_open` allocates queue metadata and slots, `q_append` copies or takes ownership of data, `q_peek` returns head pointer/length, `q_drop_head` frees and advances, and stats functions expose current/max/capacity. State is heap-backed circular buffer with per-entry data ownership. Dependencies are libc allocation and errno. Risks include no thread safety, overwrite leak if appending into a non-empty slot would occur due to logic bugs, caller must not mutate borrowed `q_peek` data, and fixed entry size rejects large records. Tests should cover full queue, oversized append, take-memory ownership, wraparound, and close cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/queue.h -->
## sources/security-integrity/audit-userspace/audisp/plugins/af_unix/queue.h

Purpose: queue API for `audisp-af_unix`.

It declares opaque `struct queue`, open/close, append/peek/drop, length/max/capacity, and empty checks, with compiler allocation/access annotations. State is hidden in queue implementation. Dependencies are `stdbool.h`, `sys/types.h`, and common attribute macros. Risks are ownership semantics controlled by `take_memory` and no concurrency contract. Tests are local queue unit-style cases or plugin backpressure tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/af_unix/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/filter/Makefile.am -->
## sources/security-integrity/audit-userspace/audisp/plugins/filter/Makefile.am

Purpose: build/install fragment for `audisp-filter`.

It builds a hardening-enabled PIE plugin, links common, auparse, auplugin, and optional cap-ng, installs the plugin config in plugins.d and rule config in audit sysconf, and ships a manpage. State is installed binary/config. Dependencies are auparse expression support and configured install paths. Risks include default config launching `/sbin/audisp-syslog` and requiring both plugin and rule configs to be present. Test signal is build plus `audisp-filter --check`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/filter/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/filter/audisp-filter.c -->
## sources/security-integrity/audit-userspace/audisp/plugins/filter/audisp-filter.c

Purpose: generic audit event filter that forwards matching or non-matching events to a child plugin.

It parses either `--check config` or `allowlist|blocklist config binary args...`, loads root-owned/non-world-writable regular rule files, validates ausearch expressions, forks a child with filtered stdin, uses `auplugin_event_feed` to receive complete events, and applies all expressions with event-level semantics. State includes global rule list, config, child pid, pipe fds, stop/HUP flags, and error count. On SIGHUP it reloads rules and clears the auparse search state; on SIGTERM from parent it forwards signal to the child and stops. Dependencies are auparse search APIs, auplugin, syslog, fork/pipe/execve, and optional cap-ng. Risks include no quoting in command arguments beyond argv, pipe write partials not fully handled, rule reload retaining old rules on syntax failure, child death stopping filter, execve with empty environment, and allowlist/blocklist semantics being easy to invert. Tests should cover `--check`, invalid expressions, HUP reload, multi-record event forwarding, and child failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/filter/audisp-filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/filter/audisp-filter.conf -->
## sources/security-integrity/audit-userspace/audisp/plugins/filter/audisp-filter.conf

Purpose: default rule file for audisp-filter.

It contains comments documenting ausearch-expression syntax, allowlist/blocklist behavior, event-based matching, and intended chaining with downstream plugins, but no active rules. State is installed under `/etc/audit/audisp-filter.conf`. Dependencies are auparse expression parser. Risks are empty rule set semantics depending on selected mode, and users needing to understand event-level forwarding. Test signal is `audisp-filter --check` on this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/filter/audisp-filter.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/filter/filter.conf -->
## sources/security-integrity/audit-userspace/audisp/plugins/filter/filter.conf

Purpose: audisp plugin config for the filter plugin.

It is inactive by default, runs `/sbin/audisp-filter`, passes `allowlist /etc/audit/audisp-filter.conf /sbin/audisp-syslog LOG_USER LOG_INFO interpret`, and expects string input. State is parsed by dispatcher pconfig and determines child plugin chain. Risks include inactive default, hard-coded downstream syslog path, and allowlist mode with empty rules forwarding all events. Test signal is enabling the plugin with a rule file and confirming downstream output.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/filter/filter.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/Makefile.am -->
## sources/security-integrity/audit-userspace/audisp/plugins/ids/Makefile.am

Purpose: experimental IDS plugin build/install fragment.

It builds `audisp-ids` from account, AVL, config, models, reactions, session, and timer sources, links libaudit/auparse/common/auplugin, installs plugin and IDS configs, and includes rules subdir. State is installed experimental binary/config. Dependencies are `ENABLE_EXPERIMENTAL`, auparse normalization, audit logging, and model modules not all in this subset. Risks include broad module coupling and experimental status requiring explicit CI flags. Test signal is CI with `--enable-experimental` and plugin model tests if present.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/account.c -->
## sources/security-integrity/audit-userspace/audisp/plugins/ids/account.c

Purpose: IDS account-state index keyed by account name.

It wraps an AVL tree in `accounts`, tracks count and current account, and provides init/destroy/new/add/find/delete/traverse/score APIs. Each `account_data_t` embeds `avl_t` first, owns a duplicated name, and carries a `karma` score. State persists in memory for the life of `audisp-ids` and is dumped via `traverse_accounts`. Dependencies are `avl`, IDS debug logging, and reactions hooks. Risks include global singleton state, no thread safety, allocation failure silently dropping new accounts, and score reaction placeholder currently doing nothing above threshold. Tests should cover duplicate add, delete, traversal, and karma increments.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/account.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/account.h -->
## sources/security-integrity/audit-userspace/audisp/plugins/ids/account.h

Purpose: account model API for audisp-ids.

It defines `account_data_t` with embedded AVL node, immutable name pointer, and karma, then declares lifecycle, lookup, mutation, traversal, and scoring functions. State is managed by `account.c`'s global index. Dependencies are `avl.h` and stdio for dumps. Risks are requiring `avl` as the first struct member and exposing mutable account pointers. Tests should validate callers do not stack-allocate transient names without duplication.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/account.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/audisp-ids.conf -->
## sources/security-integrity/audit-userspace/audisp/plugins/ids/audisp-ids.conf

Purpose: audisp plugin config for the experimental IDS.

It is inactive by default, runs `/usr/sbin/audisp-ids`, type `always`, passes one argument, and receives string format. State is parsed by dispatcher pconfig. Risks include path mismatch with install prefix/sbin settings and inactive default hiding runtime issues. Test signal is enabling with `ids.conf` and sending audit events through auplugin.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/audisp-ids.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/avl.c -->
## sources/security-integrity/audit-userspace/audisp/plugins/ids/avl.c

Purpose: allocation-free AVL tree implementation for IDS indexes.

It provides `avl_init`, `avl_search`, `avl_insert`, `avl_remove`, in-order traversal, iterator first/next, and tree intersection. Control flow links caller-embedded `avl_t` nodes directly, maintains balance factors, and uses fixed-height stacks sized by `AVL_MAX_HEIGHT`. State is entirely caller-owned tree/node links. Dependencies are comparison callbacks and `avl.h`; no pthread locking by design. Risks include complex rotation correctness, no assertions in production, stack height assumptions, intrusive node requirement, and no duplicate ownership management beyond returning existing node. Tests should cover insert/delete rotation cases, duplicates, iteration order, and intersection.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/avl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/avl.h -->
## sources/security-integrity/audit-userspace/audisp/plugins/ids/avl.h

Purpose: intrusive AVL tree types and APIs for IDS models.

It defines `avl_t`, `avl_tree_t`, iterator stack, maximum height, and public insert/remove/search/traverse/iterator/intersection functions. State is caller-owned, with `avl_t` embedded in containing records. Dependencies are compiler warning attributes. Risks include callers needing stable node memory and a comparison function consistent over node lifetime. Test signal is all IDS indexes that embed AVL nodes.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/avl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.c -->
## sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.c

Purpose: main process for experimental audit IDS plugin.

It configures signals, loads IDS config, opens an audit connection for reaction logging, initializes origin/account/session models, starts `auplugin_event_feed` with a timer callback, normalizes each complete event, and dispatches it to bad-event and behavior models. State includes global debug/mode, log file, stop/HUP/dump flags, current auparse state for metrics, audit fd, config, model indexes, and timer services. SIGUSR1 writes state to `AUDIT_RUN_DIR/ids-state`; SIGHUP reloads config; parent-origin SIGTERM stops auplugin. Dependencies are auparse normalization, libaudit logging, auplugin, IDS model modules, timer services, and config/reaction code outside this subset. Risks include debug default enabled, global singleton state, audit connection failure exits, no locking around signal flags, config reload while models are live, and incomplete reaction code in adjacent modules. Tests should cover config load failure, signal handling, state dump, normalized event model dispatch, and timer cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.conf -->
## sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.conf

Purpose: default IDS policy configuration.

It sets thresholds/reactions for failed logins by origin, session badness, service login/root login permissions and weights, bad login weight, and reaction durations for block-address and lock-account actions. State is read by IDS config parser outside this subset and drives model/reaction behavior. Risks include aggressive defaults if enabled without tuning, duration parsing dependency, and policy semantics split across config/model/reaction modules. Test signal is loading/dumping config and exercising events that cross thresholds.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.h -->
## sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.h

Purpose: shared IDS globals and service APIs.

It defines daemon session/unset constants, exposes debug logging, audit event logging, HUP/state-dump flags, and reload/output functions. State is defined in `ids.c` and consumed by model/reaction modules. Dependencies are libaudit event type constants. Risks include global mutable flags shared across modules and no encapsulation of debug/mode behavior. Test signals are module behavior under reload and state dump.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.h -->
