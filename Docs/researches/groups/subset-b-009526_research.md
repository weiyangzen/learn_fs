# Group Research: subset-b-009526

This grouped report covers the requested e2fsprogs-libs build, packaging, install-helper, and bundled GNU gettext runtime files. Each section is delimited for source-tree-aligned reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure.in

## Purpose
This is the Autoconf input for the embedded e2fsprogs library tree used by xfstests-bld. It derives the e2fsprogs version/date from `version.h`, detects host/build capabilities, exposes many build toggles, and emits the configured `MCONFIG`, Makefiles, pkg-config files, headers, and RPM spec input needed to build e2fsprogs tools and libraries.

## Important APIs, Types, and Functions
The file is macro-driven rather than function-oriented. Key Autoconf interfaces include `AC_INIT`, `AC_PREREQ`, `AC_CANONICAL_HOST`, `AC_PROG_CC`, `AC_PROG_CPP`, `AC_CHECK_HEADERS`, `AC_CHECK_FUNCS`, `AC_CHECK_LIB`, `AC_SEARCH_LIBS`, `AC_CHECK_SIZEOF`, `AC_CHECK_DECL`, `AC_CHECK_TYPE`, `AC_SUBST`, `AC_SUBST_FILE`, and `AC_OUTPUT`. It also uses project macros such as `PKG_PROG_PKG_CONFIG`, `CHECK_GNU_MAKE`, `AX_TLS`, and `AM_GNU_GETTEXT`. Important substituted variables include `E2FSPROGS_VERSION`, `E2FSPROGS_PKGVER`, `LIB_EXT`, `LDFLAG_STATIC`, `LDFLAG_DYNAMIC`, `*_CMT` build comments, root install directories, `INTL_FLAGS`, `DO_TEST_SUITE`, and per-library dependency variables for uuid and blkid.

## Control Flow
The script first parses version metadata and normalizes release/package versions, including WIP/pre-release handling. It then sets toolchain defaults, processes legacy and current `--with`/`--enable` options, chooses static/shared/profile/checker library modes, and decides whether private or external `libuuid`/`libblkid` are used. Later phases probe programs, headers, functions, types, byte order, struct fields, socket/sem libraries, OS-specific defaults, static-link support, gettext setup, and cross-build behavior. The final phase creates build directories, builds an `outlist` only for outputs whose source directories exist, and calls `AC_OUTPUT($outlist)`.

## State and Persistence
The generated `configure` script persists build decisions in `config.status`, configured Makefiles, `MCONFIG`, `public_config.h`, `asm_types.h`, pkg-config files, and `e2fsprogs.spec`. It also creates build directories such as `lib`, `include`, `include/linux`, and `include/asm`. Runtime state is not stored here, but many compile-time defines such as `ENABLE_HTREE`, `CONFIG_TESTIO_DEBUG`, `CONFIG_BUILD_FINDFS`, `USE_UUIDD`, and `HAVE_EXT2_IOCTLS` shape compiled binaries.

## Dependencies and Integration Points
It integrates with e2fsprogs make fragments (`lib/Makefile.*`), gettext (`intl/Makefile`, `po/Makefile.in`, `libgnuintl.h`), type-generation helper `config/parse-types.sh`, Linux fallback headers under `include`, pkg-config for external uuid/blkid, and OS facilities such as `ldconfig`, `sem_init`, `socket`, `dlopen`, and ext2 ioctls. It directly controls whether downstream directories like `misc`, `e2fsck`, `debugfs`, `resize`, `doc`, and `intl` are included in the configured build.

## Risks
The template is legacy Autoconf syntax with many shell snippets, so quoting bugs can leak into generated configure behavior. Cross-compiling relies on a separate `BUILD_CC` and disables the test suite, which can hide target-only failures. The gettext section sets `VERSION="$E2FSPROGS_VERSION"` and then overwrites it with `VERSION=0.14.1`, a surprising compatibility artifact that can confuse package metadata readers. Feature toggles create many comment variables, so Makefile rules must keep using the matching `*_CMT` variables consistently. External `libuuid`/`libblkid` modes require working `pkg-config` and library probes.

## Test Signals
Useful validation signals are successful `autoconf` generation, `./configure` on Linux and at least one non-Linux host profile, `make`, `make check` when not cross-compiling, expected generated `MCONFIG` substitutions, correct `public_config.h`, correct selection of shared/static library extensions, and verifying that generated `e2fsprogs.spec` has the normalized package version.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/depfix.sed -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/depfix.sed

## Purpose
This sed program post-processes generated dependency lines before appending them to `Makefile.in` files. It inserts a marker header, joins continuation lines, normalizes whitespace, and removes dependencies that point at system or generated headers that should not make the distributed Makefile depend on local machine paths.

## Important APIs, Types, and Functions
The script uses sed commands only: `1i` inserts the dependency-section header, label `:FIRST` and `bFIRST` loop over continued lines, `N` appends the next physical line, `y` translates tabs to spaces, `s` normalizes/removes paths, and `$a` adds a final newline. There are no exported functions or persistent data structures.

## Control Flow
For each input dependency block, the script removes leading whitespace and repeatedly joins lines ending in backslash. Once a logical dependency line is assembled, it collapses spaces and strips `/usr/include`, `/usr/lib`, `/mit/cygnus`, generated blkid dependency paths, and uuid header references. It emits a clean dependency section with a final blank line.

## State and Persistence
There is no runtime state. Persistence is the transformed dependency text in the receiving Makefile or dependency file.

## Dependencies and Integration Points
It depends on POSIX sed behavior and the dependency-generation conventions used by e2fsprogs make rules. It is integrated wherever maintainer rules regenerate Makefile dependency sections.

## Risks
The path-stripping regexes are broad and can remove real dependencies if a source path resembles one of the filtered system/generated paths. Because it flattens continuation lines before stripping, malformed backslashes can merge unrelated lines. It also assumes dependency paths are space-delimited.

## Test Signals
Run it against compiler-generated `.d` output containing continuations, tabs, system include paths, and project uuid/blkid paths. The expected signal is a final dependency block without local machine system paths and without broken target/dependency syntax.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/depfix.sed -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/doc/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/doc/Makefile.in

## Purpose
This make template builds and installs libext2fs documentation from Texinfo sources. It produces Info and DVI outputs by default, can generate split HTML, installs compressed Info files, and defines cleanup targets for generated documentation artifacts.

## Important APIs, Types, and Functions
Important make targets are `all`, `install-doc-libs`, `uninstall-doc-libs`, `libext2fs.info`, `libext2fs.dvi`, `libext2fs_abt.html`, `distclean`, `clean`, `clean-all`, `clean-final`, `clean-tex`, `clean-backup`, `clean-tarfiles`, and `clean-html`. It consumes `@MCONFIG@` for common install variables and `@MAKEINFO@` from configure.

## Control Flow
`all` depends on Info and DVI generation. Install removes old `libext2fs.info*`, creates `$(infodir)`, copies matching Info files, and gzips them. Individual document targets invoke `makeinfo`, `texi2dvi`, or `texi2html`; failures are prefixed with `-`, making documentation generation non-fatal in many paths.

## State and Persistence
Generated files persist in the doc build directory: `.info`, `.dvi`, `.html`, Texinfo auxiliary files, archives, and backups. Install persists compressed Info files under `$(DESTDIR)$(infodir)`.

## Dependencies and Integration Points
The template depends on `libext2fs.texinfo`, configured install tools from `MCONFIG`, `makeinfo`, `texi2dvi`, `texi2html`, `gzip`, and directory creation via `MKINSTALLDIRS`. It is emitted by `configure.in` as `doc/Makefile` when the source doc directory exists.

## Risks
Documentation generation is often non-fatal, so missing or broken tools may produce a successful build without docs. The HTML target assumes `texi2html -split_chapter` creates a `libext2fs` subdirectory. Cleanup rules are broad within the doc directory and remove generated artifacts by extension.

## Test Signals
Signals include `make -C doc all` producing Info/DVI when tools exist, `make install-doc-libs DESTDIR=...` creating gzipped Info files, and cleanup targets removing only expected generated documentation files.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/doc/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/e2fsprogs.spec.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/e2fsprogs.spec.in

## Purpose
This RPM spec template packages e2fsprogs into the main utilities package, a development package, and a `uuidd` daemon package. Configure substitutes the e2fsprogs package version before RPM build processing.

## Important APIs, Types, and Functions
RPM sections include package metadata, `%description`, `%package devel`, `%package -n uuidd`, `%prep`, `%build`, `%install`, `%clean`, scriptlets `%post`, `%postun`, `%post devel`, `%postun devel`, `%pre -n uuidd`, and `%files` lists. RPM macros define root install directories and use standard macros such as `%configure`, `%find_lang`, `%defattr`, `%doc`, `%attr`, and `%dir`.

## Control Flow
The build runs `%configure --enable-elf-shlibs --enable-nls`, then `make` and `make check`. Install runs `make install install-libs` with root-specific sbindir/libdir overrides, calls `ldconfig -n` in the build root, creates `/var/lib/libuuid`, and collects translations via `%find_lang`. Scriptlets refresh ldconfig, maintain Info directory entries, and create the `uuidd` user/group before installing daemon-owned files.

## State and Persistence
Installed state includes filesystem utilities in root sbin, shared libraries under root libdir, helper tools and headers under standard development paths, man pages, Info docs, pkg-config files, translation catalogs, and `uuidd` state directory `/var/lib/libuuid`. RPM scriptlets modify system user/group databases and Info indexes.

## Dependencies and Integration Points
It integrates with the configured build system, `ldconfig`, `install-info`, `shadow-utils`, `%find_lang`, and RPM ownership/permission handling. It assumes the e2fsprogs make install targets install files matching the explicit `%files` lists.

## Risks
The file list is static and can drift from build outputs, causing RPM unpackaged-file or missing-file failures. Scriptlets assume legacy locations such as `/sbin/install-info` and `/sbin/nologin`. `make check` in `%build` can make RPM builds environment-sensitive. The spec packages static libraries and many shared libraries together, so ABI/layout changes must update multiple file lists.

## Test Signals
Primary signals are successful `rpmbuild -ba` after configure substitution, no unpackaged/missing files, `%find_lang` producing the expected language file, scriptlet linting, and install/erase tests confirming ldconfig, Info, and uuidd user handling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/e2fsprogs.spec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/compile_manpages -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/compile_manpages

## Purpose
This shell helper warms or compiles preformatted man-page caches for selected e2fsprogs commands by invoking `man` for section 8 and section 1 pages.

## Important APIs, Types, and Functions
The script defines `MAN8` and `MAN1` command lists, loops over them, and runs `man -S 8 $i` or `man -S 1 $i` with output discarded. It exits zero unconditionally after the loops if `man` calls do not abort under shell settings.

## Control Flow
It iterates section 8 commands (`debugfs`, `badblocks`, `e2fsck`, `mke2fs`, `dumpe2fs`, `mklost+found`, `fsck`, `tune2fs`) and then section 1 commands (`lsattr`, `chattr`). Each `man` invocation resolves and formats the page, usually causing legacy man systems to populate cat-page caches.

## State and Persistence
The script itself stores no state, but the system man implementation may persist formatted cat pages under its configured cache directories.

## Dependencies and Integration Points
It depends on `/bin/sh`, `man`, and a man implementation that supports `-S`. It pairs with `remove_preformat_manpages`, which deletes preformatted cache entries.

## Risks
The command list is incomplete relative to modern e2fsprogs utilities. On systems where `man -S` is unsupported, the helper fails or does nothing useful. Running it during package install may be slow or undesirable on systems with read-only man caches.

## Test Signals
Run in a staging environment with installed man pages and confirm `man -S` resolves each listed page. If the target man implementation uses cat-page caches, check that cache files are created or refreshed.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/compile_manpages -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/convfstab -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/convfstab

## Purpose
This legacy shell script rewrites `/etc/fstab` into a form with six fields by adding default mount options, dump frequency, and fsck pass numbers where they are missing.

## Important APIs, Types, and Functions
The script uses shell variables `ROOT_PASS`, `NON_ROOT_PASS`, `DEF_FLAGS`, and `DEF_DUMP`, reads `/etc/fstab` line by line, uses positional parameters via `set -- $LINE`, and writes transformed output to `/tmp/newfstab.$$`. It then renames `/etc/fstab` to `/etc/fstab.bak` and moves the temporary file into place.

## Control Flow
Blank lines are omitted with a warning. Lines starting with `#` or `!` are echoed back with warnings even though comments are described as non-standard. For non-comment entries, the script rejects lines with fewer than three or more than six fields. It sets pass `1` for root, `0` for `none`, `2` otherwise, then overrides dump/pass to zero for ignored, CD-ROM, DOS, network, proc, and swap-like filesystems. Depending on whether the line has three, four, five, or six fields, it appends the missing trailing fields.

## State and Persistence
This script directly mutates host state: it overwrites `/etc/fstab`, backs up the previous file to `/etc/fstab.bak`, and uses a PID-suffixed temporary file in `/tmp`.

## Dependencies and Integration Points
It depends on `/bin/sh`, root permissions, `/etc/fstab`, `/tmp`, and `mv`. It is an install utility rather than build-time code, and it assumes whitespace-delimited fstab fields without escaped spaces.

## Risks
This is high risk because it rewrites a critical boot configuration file in place, does not preserve ownership/mode explicitly, does not use atomic rename with validation, and can mishandle comments, escaped spaces, labels with spaces, or modern fstab conventions. A failed second `mv` after backing up `/etc/fstab` can leave no active fstab. The temp path is predictable modulo PID.

## Test Signals
Only test against temporary fixture files or a chroot/container. Useful fixtures include root, swap, proc, network, comments, blank lines, malformed entries, and already-six-field lines. Verify output fields, warnings, backup behavior, and failure handling when the destination cannot be replaced.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/convfstab -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/remove_preformat_manpages -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/remove_preformat_manpages

## Purpose
This shell helper removes legacy preformatted cat-page cache files for selected e2fsprogs man pages.

## Important APIs, Types, and Functions
It defines `PREFORMAT_ROOT=/usr/man/preformat`, `COMPILED_ROOT=/usr/man`, `MAN8`, and `MAN1`, then loops over each page name and runs `rm -f` for uncompressed and `.gz` cat-page paths in section-specific directories.

## Control Flow
The section 8 loop removes matching files under `cat8`, then the section 1 loop removes matching files under `cat1`. Missing files are ignored because `rm -f` is used.

## State and Persistence
The script deletes persistent system man-cache files. It does not alter source man pages, only preformatted copies in legacy directories.

## Dependencies and Integration Points
It depends on `/bin/sh` and `rm`. It complements `compile_manpages` and assumes older `/usr/man` cache layouts.

## Risks
The hard-coded `/usr/man` paths may be wrong on modern systems. The command list is static and incomplete for newer utilities. Because deletion is unconditional, a packaging script using this on a shared man-cache tree could remove cat pages generated by another package if names collide.

## Test Signals
Create a temporary `/usr/man`-like fixture by overriding via a patched test copy or container, populate listed and unlisted cache names, run the script, and confirm only the listed section 1/8 cache files and their `.gz` variants disappear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/remove_preformat_manpages -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/Makefile.in

## Purpose
This is the generated GNU gettext `intl` directory make template. It builds either included `libintl`/`libgnuintl`, generates headers and alias sed scripts, installs runtime support files when appropriate, and handles distribution/cleanup for the embedded gettext runtime.

## Important APIs, Types, and Functions
Important variables include `PACKAGE`, `VERSION`, `USE_INCLUDED_LIBINTL`, `BUILD_INCLUDED_LIBINTL`, `LTV_CURRENT`, `LTV_REVISION`, `LTV_AGE`, `OBJECTS`, `HEADERS`, `SOURCES`, `DISTFILES.*`, `DEFS`, `COMPILE`, and `INCLUDES`. Important targets include `all-yes`, `all-no-yes`, `libintl.$la`, `libgnuintl.$la`, object `.lo` rules, `libgnuintl.h`, `libintl.h`, `charset.alias`, `install`, `uninstall`, `dist`, `clean`, `distclean`, and tag/id targets.

## Control Flow
`all` dispatches based on configure substitutions. If included libintl is used, it builds `libintl`, generated headers, charset aliases, and sed scripts. If not, but gettext tools need an included helper, it builds `libgnuintl`. Install logic is heavily conditional on `PACKAGE` and `USE_INCLUDED_LIBINTL`: runtime installs headers/libraries, updates `charset.alias` and `locale.alias` via `ref-add.sed`, and gettext-tools installs source support files. Uninstall reverses alias references via `ref-del.sed`.

## State and Persistence
Build products include `.lo`, `.la`, static archives, `libgnuintl.h`, `libintl.h`, `charset.alias`, `ref-add.sed`, `ref-del.sed`, `.libs`, and tag/index files. Install persists libraries, headers, alias files, and optional gettext source support files under configured `libdir`, `includedir`, `localedir`, and `gettextsrcdir`.

## Dependencies and Integration Points
It depends on libtool, compiler/linker tools, `config.charset`, `ref-add.sin`, `ref-del.sin`, generated `plural.c`, and the C sources in this `intl` directory. It is configured by `configure.in` through gettext macros and is consumed by the top-level build when `AM_GNU_GETTEXT` selects included libintl.

## Risks
The template contains many legacy compatibility branches and generated substitutions, so stale configure values can break library naming or install behavior. Alias-file edits are global to install roots and must be reference-counted correctly. The target list includes `.c` files inside `HEADERS` for printf helpers, which is unusual but intentional for distribution dependencies.

## Test Signals
Build with included and system gettext modes, verify the selected library target is built, ensure `libgnuintl.h` substitutions remove `@HAVE_*@` placeholders, run `make install DESTDIR=...` and `make uninstall DESTDIR=...`, and confirm alias files are added/removed idempotently.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/bindtextdom.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/bindtextdom.c

## Purpose
This file implements GNU gettext domain binding APIs: `bindtextdomain` and `bind_textdomain_codeset` under either libc names or `libintl_`-prefixed standalone names.

## Important APIs, Types, and Functions
The central helper is `set_binding_values(domainname, dirnamep, codesetp)`. Public entry points are `BINDTEXTDOMAIN` and `BIND_TEXTDOMAIN_CODESET`, mapped to `__bindtextdomain`/`__bind_textdomain_codeset` in libc or `libintl_bindtextdomain`/`libintl_bind_textdomain_codeset` outside libc. It manipulates `struct binding` from `gettextP.h`, `_nl_domain_bindings`, `_nl_default_dirname`, `_nl_msg_cat_cntr`, and `_nl_state_lock`.

## Control Flow
Invalid empty domain names return `NULL`. Otherwise the helper locks global gettext state, searches the sorted binding list, returns current values for query calls, replaces changed directory/codeset strings for existing bindings, or allocates and inserts a new sorted binding. Codeset changes increment `codeset_cntr`; any binding modification increments `_nl_msg_cat_cntr` to invalidate cached translations.

## State and Persistence
State is in the process-global `_nl_domain_bindings` linked list. Directory and codeset strings may be dynamically allocated and later reused by lookup code in `dcigettext.c`. No filesystem persistence occurs.

## Dependencies and Integration Points
It depends on `gettextP.h`, `libgnuintl.h` or system `libintl.h`, libc lock macros in glibc builds, and the central lookup/cache code that watches `_nl_msg_cat_cntr` and `codeset_cntr`.

## Risks
Standalone builds use dummy locks, so the included libintl is not truly thread-safe outside glibc. Allocation failure returns `NULL` through output pointers without errno-specific reporting. Pointer comparison against `_nl_default_dirname` is used to decide whether to free directory strings, so callers must not mutate returned pointers.

## Test Signals
Test binding creation, querying, rebinding to the same value, rebinding to a new directory, setting/changing codesets, invalid domains, and confirming `_nl_msg_cat_cntr` changes only on real modifications.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/bindtextdom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcgettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcgettext.c

## Purpose
This is the `dcgettext` wrapper. It looks up a singular message in a named domain for a caller-provided locale category.

## Important APIs, Types, and Functions
The public function is `DCGETTEXT(domainname, msgid, category)`, mapped to libc or `libintl_dcgettext` names. It delegates to `DCIGETTEXT(domainname, msgid, NULL, 0, 0, category)`.

## Control Flow
There is no local lookup logic. The wrapper passes `plural=0` and no plural fallback to the internal resolver, then returns its result.

## State and Persistence
No local state is stored. It reads all translation state indirectly through `dcigettext.c`.

## Dependencies and Integration Points
It depends on `gettextP.h`, `libgnuintl.h`/`libintl.h`, and `libintl_dcigettext`. It is part of the public gettext API surface exported by the included library.

## Risks
Behavioral risks are inherited from `dcigettext.c`: invalid categories, missing catalogs, cache invalidation, and charset conversion. The wrapper itself has minimal risk.

## Test Signals
Use a fixture domain and category to confirm it returns translated strings when catalogs exist and the original `msgid` when no catalog or entry exists.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcgettext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcigettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcigettext.c

## Purpose
This is the central runtime resolver for GNU gettext lookups. It implements domain/category/locale selection, catalog loading, known-translation caching, plural selection, secure-mode filtering, charset conversion lookup, and fallback to untranslated strings.

## Important APIs, Types, and Functions
The exported internal entry is `DCIGETTEXT(domainname, msgid1, msgid2, plural, n, category)`, mapped to `__dcigettext` or `libintl_dcigettext`. Important helpers and data include `struct known_translation_t`, `transcmp`, `_nl_current_default_domain`, `_nl_default_dirname`, `_nl_domain_bindings`, `_nl_find_msg`, `plural_lookup`, `guess_category_value`, `category_to_name`, `_nl_msg_cat_cntr`, `_nl_state_lock`, and optional `tsearch` cache root.

## Control Flow
The resolver rejects `NULL` `msgid1`, substitutes the current default domain when none is provided, checks the known-translation cache, preserves errno, determines secure/SUID mode, finds the domain binding, resolves relative bindings against `getcwd`, determines the locale category name and value, and builds an `LC_CATEGORY/domain.mo` suffix. It iterates colon-separated locale candidates, skipping path-containing locale names in secure mode and returning untranslated strings for `C` or `POSIX`. For each candidate it calls `_nl_find_domain`, then `_nl_find_msg` on the chosen domain and successors. Found translations are cached with the current catalog counter and optionally reduced to the plural variant via `plural_lookup`.

## State and Persistence
Process-global state includes the current default domain, domain bindings, known-translation tree, catalog counter, secure-mode flag, and conversion memory cache. No direct filesystem writes occur; the code reads catalogs through downstream loaders.

## Dependencies and Integration Points
It depends on locale APIs, environment variables `LANGUAGE`, `LC_*`, and `LANG`, filesystem path handling, `_nl_find_domain` in `finddomain.c`, `_nl_find_msg` and catalog structures in `loadmsgcat.c`, plural expression support from `eval-plural.h`, and hash support from `hash-string.h`. It is the target for `gettext`, `dgettext`, `dcgettext`, `ngettext`, `dngettext`, and `dcngettext` wrappers.

## Risks
Standalone locking macros are no-ops, so global caches and bindings are not protected in non-glibc builds. Relative domain directories depend on `getcwd` and can fail back to untranslated text. Secure-mode filtering must remain correct because locale values can otherwise include paths. Cache invalidation relies on `_nl_msg_cat_cntr` and binding `codeset_cntr`. Plural expression division by zero intentionally raises `SIGFPE` on platforms where integer divide-by-zero does not.

## Test Signals
Exercise default and named domains, category-specific lookup, `LANGUAGE` chains, secure-mode path rejection, relative and absolute bind paths, C/POSIX fallback, tsearch cache hits after repeated calls, cache invalidation after rebind, plural lookup bounds, errno preservation, and iconv conversion when a catalog charset differs from output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcigettext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcngettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcngettext.c

## Purpose
This wrapper implements plural lookup for a specified domain and locale category.

## Important APIs, Types, and Functions
The public entry is `DCNGETTEXT(domainname, msgid1, msgid2, n, category)`, mapped to libc or `libintl_dcngettext`. It delegates to `DCIGETTEXT(domainname, msgid1, msgid2, 1, n, category)`.

## Control Flow
The wrapper marks the lookup as plural and forwards both singular/plural fallback strings plus the count to the central resolver. All catalog search and plural expression evaluation happens in `dcigettext.c`.

## State and Persistence
No local state; it uses the resolver's global state and loaded catalogs.

## Dependencies and Integration Points
It depends on `gettextP.h`, public libintl headers, and `libintl_dcigettext`. `dngettext` delegates to this wrapper with `LC_MESSAGES`.

## Risks
Risks are inherited from plural metadata in catalogs and `plural_lookup`. If no catalog entry exists, fallback uses the Germanic rule `n == 1 ? msgid1 : msgid2`.

## Test Signals
Test with a plural-capable catalog, out-of-range plural expressions, missing translations, and non-`LC_MESSAGES` categories.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcngettext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dgettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dgettext.c

## Purpose
This wrapper implements singular lookup for a specified domain using the `LC_MESSAGES` category.

## Important APIs, Types, and Functions
The public entry is `DGETTEXT(domainname, msgid)`, mapped to libc or `libintl_dgettext`. It calls `DCGETTEXT(domainname, msgid, LC_MESSAGES)`.

## Control Flow
The wrapper simply fixes the category to `LC_MESSAGES` and delegates to `dcgettext`.

## State and Persistence
No local state is stored. All binding, cache, and catalog state lives in shared gettext internals.

## Dependencies and Integration Points
It depends on `locale.h`, `gettextP.h`, `libgnuintl.h`/`libintl.h`, and `dcgettext`.

## Risks
The wrapper depends on `LC_MESSAGES` availability or a configured fallback in the public header. Otherwise risks are inherited from the central resolver.

## Test Signals
Bind a test domain and locale, call `dgettext`, and confirm `LC_MESSAGES` catalogs are searched rather than other categories.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dgettext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dngettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dngettext.c

## Purpose
This wrapper implements plural lookup for a specified domain using `LC_MESSAGES`.

## Important APIs, Types, and Functions
The public entry is `DNGETTEXT(domainname, msgid1, msgid2, n)`, mapped to libc or `libintl_dngettext`. It calls `DCNGETTEXT(domainname, msgid1, msgid2, n, LC_MESSAGES)`.

## Control Flow
It fixes the category and delegates plural handling to `dcngettext` and ultimately `dcigettext`.

## State and Persistence
No local state is stored.

## Dependencies and Integration Points
It depends on `locale.h`, `gettextP.h`, `libgnuintl.h`/`libintl.h`, and `dcngettext`.

## Risks
The main risk is incorrect plural fallback if catalog plural metadata is missing or malformed; actual behavior is inherited from `dcigettext.c` and `eval-plural.h`.

## Test Signals
Test counts across plural boundaries for a bound domain with a known plural expression, plus missing-catalog fallback for `n == 1` and `n != 1`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dngettext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/eval-plural.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/eval-plural.h

## Purpose
This header provides the recursive evaluator for parsed gettext plural expressions. It converts a `struct expression` tree and count `n` into a plural-form index.

## Important APIs, Types, and Functions
The key function is `plural_eval(struct expression *pexp, unsigned long int n)`, optionally declared `static` through `STATIC`. It operates on expression operations such as `var`, `num`, `lnot`, `lor`, `land`, arithmetic, comparisons, and ternary `qmop` from `plural-exp.h`.

## Control Flow
Evaluation dispatches by `pexp->nargs`: zero-argument nodes return `n` or numeric constants, one-argument nodes compute logical not, two-argument nodes short-circuit `||` and `&&` or evaluate arithmetic/comparison operations, and three-argument nodes implement the conditional operator. Division and modulo explicitly raise `SIGFPE` when configured for platforms where integer divide-by-zero does not.

## State and Persistence
There is no stored state. The evaluator is pure except for possible `SIGFPE` raising on divide/modulo by zero.

## Dependencies and Integration Points
It depends on the plural expression tree produced by gettext plural parsing/extraction and is included directly by `dcigettext.c` for `plural_lookup`.

## Risks
Deep or malformed expression trees can recurse heavily. Invalid operations fall through to return zero. Divide-by-zero behavior can terminate or signal the process. Bounds checking for the returned index is performed by `plural_lookup`, not this evaluator.

## Test Signals
Evaluate fixture expressions for common languages, ternary expressions, logical short-circuiting, arithmetic precedence from parsed trees, out-of-range values, and divide/modulo by zero behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/eval-plural.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/explodename.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/explodename.c

## Purpose
This file splits locale names into language, territory, codeset, normalized codeset, modifier, and CEN-specific components for catalog fallback generation.

## Important APIs, Types, and Functions
Exports are `_nl_find_language(name)` and `_nl_explode_name(name, language, modifier, territory, codeset, normalized_codeset, special, sponsor, revision)`. It returns a bitmask using flags from `loadinfo.h`, including `TERRITORY`, `XPG_CODESET`, `XPG_NORM_CODESET`, `XPG_MODIFIER`, `CEN_AUDIENCE`, `CEN_SPECIAL`, `CEN_SPONSOR`, and `CEN_REVISION`.

## Control Flow
`_nl_find_language` scans to the first locale separator. `_nl_explode_name` destructively inserts NUL terminators into the input string, first parsing XPG syntax (`language[_territory[.codeset]][@modifier]`) and then CEN syntax (`language[_territory][+audience][+special][,sponsor][_revision]`). It normalizes non-empty codesets and clears empty XPG components from the mask.

## State and Persistence
The input locale string is modified in place. A normalized codeset may be dynamically allocated and must be freed by the caller when the returned mask includes `XPG_NORM_CODESET`.

## Dependencies and Integration Points
It depends on `_nl_normalize_codeset` from `l10nflist.c` and the bit flags in `loadinfo.h`. `finddomain.c` uses it before creating catalog fallback lists.

## Risks
Callers must pass mutable storage, not a string literal. The parser is legacy and may not understand every modern locale naming convention. Incorrect mask bits change fallback search order and catalog file names.

## Test Signals
Use locale strings such as `de_DE.UTF-8`, `sr_RS@latin`, `en+audience+special,sponsor_revision`, aliases without language, empty components, and normalized codesets like `ISO-8859-1`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/explodename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/finddomain.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/finddomain.c

## Purpose
This file finds or creates the `loaded_l10nfile` structure for a domain, locale, and directory binding, then triggers catalog loading for the best available fallback candidate.

## Important APIs, Types, and Functions
The main function is `_nl_find_domain(dirname, locale, domainname, domainbinding)`. It owns the static `_nl_loaded_domains` list. It calls `_nl_make_l10nflist`, `_nl_expand_alias`, `_nl_explode_name`, `_nl_load_domain`, and optionally `_nl_unload_domain` in libc cleanup.

## Control Flow
The function first checks whether the exact locale/domain entry is already in `_nl_loaded_domains`; if found, it loads undecided entries and scans successors until a loaded catalog is found. For new locales, it expands aliases, destructively splits locale components, builds a fallback list through `_nl_make_l10nflist`, loads the primary candidate, then walks successors until a catalog with data is available.

## State and Persistence
State persists in the process-global `_nl_loaded_domains` linked list and its successor graph. Loaded catalog data is attached to `loaded_l10nfile->data`.

## Dependencies and Integration Points
It is called by `dcigettext.c` and delegates file creation/path fallback logic to `l10nflist.c` and actual `.mo` loading to `loadmsgcat.c`.

## Risks
The global loaded-domain cache is never freed in standalone builds. Alias expansion can allocate a replacement locale, so cleanup paths must free it correctly. The return logic returns the top-level `retval` even when a successor contains the data, so callers must also check successors as `dcigettext.c` does.

## Test Signals
Test exact cache hits, alias expansion, fallback from specific to generic locale, missing catalogs, and repeated lookups confirming no duplicate loaded-domain entries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/finddomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettext.c

## Purpose
This wrapper implements the basic `gettext(msgid)` API for the current default domain and `LC_MESSAGES`.

## Important APIs, Types, and Functions
The public entry is `GETTEXT(msgid)`, mapped to libc or `libintl_gettext`. It calls `DCGETTEXT(NULL, msgid, LC_MESSAGES)`.

## Control Flow
The wrapper passes a `NULL` domain to mean "use current default domain" and delegates all lookup work to `dcgettext`/`dcigettext`.

## State and Persistence
No local state. The current default domain is stored in `dcigettext.c` and set by `textdomain.c`.

## Dependencies and Integration Points
It depends on `gettextP.h`, `libgnuintl.h`/`libintl.h`, `LC_MESSAGES`, and `dcgettext`.

## Risks
Behavior depends on current process-global textdomain and locale. The wrapper itself is intentionally thin.

## Test Signals
Set a textdomain and locale, call `gettext`, and verify translated and untranslated fallback behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettextP.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettextP.h

## Purpose
This private header defines the internal ABI and data structures for the embedded libintl implementation.

## Important APIs, Types, and Functions
Important macros include `internal_function`, `attribute_hidden`, `__builtin_expect`, `W`, `SWAP`, and `ZERO`. Core types are `struct sysdep_string_desc`, `struct loaded_domain`, and `struct binding`. It declares `_nl_msg_cat_cntr`, `_nl_locale_name`, `_nl_find_domain`, `_nl_load_domain`, `_nl_unload_domain`, `_nl_init_domain_conv`, `_nl_free_domain_conv`, and `_nl_find_msg`, plus public/internal gettext function prototypes.

## Control Flow
As a header, it does not execute. It selects libc versus standalone declarations, includes iconv/gconv support when available, and includes `libgnuintl.h` with redirection macros disabled so internal code can call real `libintl_*` names.

## State and Persistence
It describes process-global state rather than owning it. `struct loaded_domain` stores mapped catalog data, byte-swap flags, original/translated string tables, sysdep tables, hash tables, conversion state, and plural expression metadata. `struct binding` stores domain-specific directory and codeset state.

## Dependencies and Integration Points
It depends on `loadinfo.h`, `gmo.h`, optional iconv/gconv headers, and `libgnuintl.h`. Nearly every C file in `intl` includes it.

## Risks
Because this is private ABI, changes can break all gettext internals. The `ZERO` flexible-array compatibility macro relies on careful allocation sizing. Byte swapping and conversion fields must stay aligned with loader and lookup expectations.

## Test Signals
Compile the entire `intl` directory across standalone and libc-like configurations, with and without iconv, and run catalog lookup tests that exercise loaded-domain fields, bindings, sysdep strings, and plural metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettextP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gmo.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gmo.h

## Purpose
This header describes the binary GNU `.mo` message catalog file format used by the loader.

## Important APIs, Types, and Functions
It defines magic values `_MAGIC` and `_MAGIC_SWAPPED`, revision constants, the 32-bit unsigned type `nls_uint32`, `struct mo_file_header`, `struct string_desc`, `struct sysdep_segment`, `struct sysdep_string`, nested `struct segment_pair`, and `SEGMENTS_END`.

## Control Flow
No runtime flow exists in the header. Preprocessor logic chooses an unsigned 32-bit type from `unsigned`, `unsigned short`, or `unsigned long`, intentionally producing a compile-time error if none fits.

## State and Persistence
It models persistent on-disk `.mo` catalog state: header fields, string descriptor tables, hash table offsets, and optional system-dependent string metadata.

## Dependencies and Integration Points
`loadmsgcat.c` reads these structures directly from mapped or malloced `.mo` files, while `gettextP.h` uses `nls_uint32` and descriptor types in loaded-domain structures.

## Risks
The structs mirror file layout and assume 32-bit fields. Any packing/alignment mismatch or unsupported revision can invalidate catalog loading. Offsets from untrusted catalog files must be validated by loader logic.

## Test Signals
Load little-endian and swapped-endian `.mo` fixtures, revision 0 catalogs, minor revision 1 sysdep catalogs, and invalid headers with wrong magic or unsupported major revision.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gmo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/hash-string.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/hash-string.h

## Purpose
This header implements GNU gettext's string hash function for `.mo` hash-table lookup.

## Important APIs, Types, and Functions
The single key function is `hash_string(const char *str_param)`, a static inline implementation of the PJW hash over unsigned bytes with `HASHWORDBITS` fixed to 32.

## Control Flow
The function initializes `hval` to zero, shifts it four bits per byte, adds the byte, extracts high bits into `g`, and folds those bits back into the hash. It stops at NUL and returns an unsigned long hash value.

## State and Persistence
There is no state. The returned hash is used transiently to probe `.mo` hash tables and build augmented sysdep hash tables.

## Dependencies and Integration Points
Used by `dcigettext.c` for message lookup and `loadmsgcat.c` while constructing in-memory hash entries for system-dependent strings.

## Risks
Correctness must match the hash used by GNU `.mo` generation tools. Changing it breaks catalog lookups. It assumes `unsigned long int` has at least 32 bits.

## Test Signals
Compare hash values for known strings against GNU gettext fixtures and verify hash-table lookup finds translations in catalogs with hash sections.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/hash-string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/intl-compat.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/intl-compat.c

## Purpose
This compatibility file exports unprefixed gettext symbols that forward to the `libintl_`-prefixed implementations, preserving compatibility with older gettext tests and allowing preload-style usage.

## Important APIs, Types, and Functions
It defines forwarding functions for `gettext`, `dgettext`, `dcgettext`, `ngettext`, `dngettext`, `dcngettext`, `textdomain`, `bindtextdomain`, and `bind_textdomain_codeset`. On MSVC DLL builds, `DLL_EXPORTED` marks them for export.

## Control Flow
The file undefines possible macro redirections, then each function directly returns the corresponding `libintl_*` call result.

## State and Persistence
No local state. All behavior is delegated to shared libintl internals.

## Dependencies and Integration Points
It depends on `gettextP.h`, which exposes the prefixed functions. It is compiled into `libintl`/`libgnuintl` by `intl/Makefile.in`.

## Risks
Exporting unprefixed symbols can collide with libc or platform libintl implementations if linking is not controlled. The file exists specifically for compatibility, so removing it can break old Autoconf gettext probes.

## Test Signals
Link a small program against the included library using unprefixed gettext calls and confirm the symbols resolve to the same behavior as prefixed calls.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/intl-compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/l10nflist.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/l10nflist.c

## Purpose
This file constructs and caches candidate localized catalog filenames, including fallback successor lists for less-specific locale variants.

## Important APIs, Types, and Functions
Exports are `_nl_make_l10nflist(...)` and `_nl_normalize_codeset(codeset, name_len)`. Helpers include fallback implementations for `__argz_count`, `__argz_stringify`, `__argz_next`, `pop`, and `stpcpy`. It uses `struct loaded_l10nfile` from `loadinfo.h`.

## Control Flow
`_nl_make_l10nflist` builds an absolute or relative candidate path from directory list, locale components, and filename suffix. It searches the sorted cache list for an existing filename. If allocation is requested and no entry exists, it allocates a `loaded_l10nfile`, inserts it, marks some synthetic entries as already decided, and recursively builds successors by dropping locale mask bits and iterating directory-list elements. `_nl_normalize_codeset` lowercases alphanumeric codeset names and prefixes digit-only names with `iso`.

## State and Persistence
State persists in the caller-provided `l10nfile_list`. Each entry owns an allocated filename and successor pointers. There is no filesystem write.

## Dependencies and Integration Points
It is used by `finddomain.c` to build the catalog fallback graph. It depends on locale mask semantics from `loadinfo.h` and argz-like handling for directory lists.

## Risks
The recursive successor construction can allocate many entries for complex masks and multi-directory paths. It stores entries in sorted order but relies on string comparison direction matching callers. Locale fallback order is encoded in mask iteration and comments, so subtle changes can alter translation precedence.

## Test Signals
Test filename generation for XPG and CEN locale parts, multi-directory alias paths, absolute language paths, normalized versus original codesets, and fallback successor ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/l10nflist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/libgettext.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/libgettext.h

## Purpose
This older public gettext header declares gettext APIs and macro fallbacks for projects using the bundled implementation or systems with catgets/gettext variants.

## Important APIs, Types, and Functions
It defines `__USE_GNU_GETTEXT`, fallback `LC_MESSAGES`, `struct _msg_ent`, `gettext_noop`, prototypes for `gettext`, `dgettext`, `dcgettext`, `textdomain`, and `bindtextdomain`, plus double-underscore suffixed variants. Under `ENABLE_NLS`, macros may map `gettext` to `dgettext` and `dgettext` to `dcgettext`. Without NLS, macros return original strings or arguments.

## Control Flow
There is no runtime flow. Preprocessor branches select system gettext/catgets behavior and may define a GCC constant-string caching macro for `dcgettext` using `_nl_msg_cat_cntr`.

## State and Persistence
No state is stored in the header, but the caching macro introduces static per-call-site variables in compiled code when enabled.

## Dependencies and Integration Points
It depends on `sys/types.h`, optional `locale.h`, `ENABLE_NLS`, `HAVE_CATGETS`, `HAVE_GETTEXT`, `HAVE_DCGETTEXT`, and `_nl_msg_cat_cntr`. It is marked obsolete in newer gettext distribution lists but still present for compatibility.

## Risks
Macro redirection can surprise callers taking function addresses or defining identifiers with the same names. The old GCC caching extension embeds static state at call sites and relies on `_nl_msg_cat_cntr` invalidation.

## Test Signals
Compile consumers with `ENABLE_NLS` on/off, with and without `HAVE_GETTEXT`/`HAVE_DCGETTEXT`, and verify macros and prototypes do not conflict with system `<libintl.h>`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/libgettext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/libgnuintl.h.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/libgnuintl.h.in

## Purpose
This is the public GNU libintl header template generated into `libgnuintl.h`. It declares gettext APIs, redirects public names to `libintl_`-prefixed symbols, optionally exposes printf replacements, and declares relocation support.

## Important APIs, Types, and Functions
It defines `_LIBINTL_H`, `__USE_GNU_GETTEXT`, `__GNU_GETTEXT_SUPPORTED_REVISION`, fallback `LC_MESSAGES`, redirection modes `_INTL_REDIRECT_ASM`, `_INTL_REDIRECT_INLINE`, and `_INTL_REDIRECT_MACROS`, and declarations for `gettext`, `dgettext`, `dcgettext`, `ngettext`, `dngettext`, `dcngettext`, `textdomain`, `bindtextdomain`, `bind_textdomain_codeset`, and `libintl_set_relocation_prefix`. Template variables include `@HAVE_POSIX_PRINTF@`, `@HAVE_ASPRINTF@`, `@HAVE_SNPRINTF@`, and `@HAVE_WPRINTF@`.

## Control Flow
The header uses preprocessor decisions to choose asm aliases, C macros, or C++ inline wrappers so public calls land on `libintl_*` symbols. If POSIX positional printf is unavailable, it remaps printf-family APIs to libintl implementations. It also handles platform conflicts such as DJGPP `gettext` and Apple GCC asm redirection limitations.

## State and Persistence
The header has no storage except through inline/macro side effects in consumers. The generated file persists configured feature substitutions made by `intl/Makefile.in`.

## Dependencies and Integration Points
It is generated by the `libgnuintl.h` make target and included by standalone gettext source files and consumers. It integrates with the compiled prefixed symbols and optional `printf.c` replacement implementation.

## Risks
Symbol redirection is delicate and platform/compiler-specific. Macro redirection can interfere with code that has methods, fields, or variables named like gettext APIs, which is why C++ inline mode exists. Incorrect substitution of `@HAVE_*@` placeholders can produce invalid headers.

## Test Signals
Generate `libgnuintl.h`, compile C and C++ consumers, verify public calls resolve to prefixed symbols, test address-taking of `gettext`, and build with printf replacement branches both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/libgnuintl.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadinfo.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadinfo.h

## Purpose
This header declares locale-dependent catalog lookup support shared by alias expansion, locale name parsing, fallback filename construction, and domain loading.

## Important APIs, Types, and Functions
It defines `PATH_SEPARATOR`, locale component flags (`CEN_REVISION`, `CEN_SPONSOR`, `CEN_SPECIAL`, `XPG_NORM_CODESET`, `XPG_CODESET`, `TERRITORY`, `CEN_AUDIENCE`, `XPG_MODIFIER`), combined masks, and `struct loaded_l10nfile`. It declares `_nl_normalize_codeset`, `_nl_make_l10nflist`, `_nl_expand_alias`, `_nl_explode_name`, and `_nl_find_language`.

## Control Flow
No runtime flow is present. The header documents the contract: `_nl_explode_name` destructively splits mutable locale names and `_nl_make_l10nflist` creates cached lookup results and successor lists.

## State and Persistence
It defines the shape of cached lookup state: filename, decided flag, loaded data pointer, next link, and flexible successor array.

## Dependencies and Integration Points
Included by `gettextP.h`, `explodename.c`, `l10nflist.c`, and related domain lookup code. It bridges locale parsing and catalog loading.

## Risks
The bitmask constants encode fallback semantics, so changes must stay synchronized across parser and fallback builder. `successor[1]` is a flexible-array idiom requiring exact allocation sizing.

## Test Signals
Compile and run lookup tests that cover all mask bits, successor array allocation, and path separator handling on Unix and Windows-like platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadmsgcat.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadmsgcat.c

## Purpose
This file loads GNU `.mo` message catalogs into memory, validates file format revisions, sets up hash/sysdep tables, initializes charset conversion, extracts plural expressions, and frees loaded domains in libc builds.

## Important APIs, Types, and Functions
Important functions are `_nl_load_domain`, `_nl_init_domain_conv`, `_nl_free_domain_conv`, `_nl_unload_domain`, and static `get_sysdep_segment_value`. It defines global `_nl_msg_cat_cntr`. It uses `struct mo_file_header`, `struct loaded_domain`, `struct loaded_l10nfile`, `struct binding`, `struct sysdep_*`, `EXTRACT_PLURAL_EXPRESSION`, iconv/gconv handles, and optional mmap.

## Control Flow
`_nl_load_domain` marks the l10n file decided, opens the filename, stats it, maps or reads it, validates magic and supported major revision, allocates `loaded_domain`, sets byte-swap flags and string/hash table pointers, and handles minor revision sysdep strings by resolving supported system-dependent format fragments and building in-memory descriptor/hash tables. It then initializes charset conversion from the header entry and extracts plural metadata. Invalid files unwind allocated/mapped memory and leave `domain_file->data` null.

## State and Persistence
Loaded catalog state persists in `domain_file->data` as a `loaded_domain`. It may reference mmaped file data, malloced file data, extra sysdep memory, conversion tables, and plural expression trees. No files are written.

## Dependencies and Integration Points
It depends on filesystem APIs (`open`, `read`, `fstat`, `mmap`), `.mo` layout from `gmo.h`, private structures from `gettextP.h`, hashing from `hash-string.h`, plural parsing from `plural-exp.h`, locale charset from `localcharset.c`, and optional iconv/gconv conversion. `dcigettext.c` calls `_nl_find_msg`, which uses data initialized here.

## Risks
The loader reads binary catalog files and must defend against malformed offsets, unsupported revisions, and allocation failures. Some paths allocate data before later validation. Charset conversion caches can be invalidated by `bind_textdomain_codeset`. Sysdep string support is complex and depends on exact hash-table behavior. Standalone builds may leak loaded catalogs until process exit.

## Test Signals
Load valid and invalid `.mo` fixtures, swapped-endian files, revision 0 and revision 1 sysdep catalogs, catalogs with and without hash tables, malformed sysdep references, charset headers requiring iconv, missing charset headers, and plural headers with multiple `nplurals` values.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadmsgcat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.c

## Purpose
This file determines a canonical character set name for the current locale, using platform APIs, environment variables, and `charset.alias` mappings.

## Important APIs, Types, and Functions
The public function is `locale_charset(void)`. Static helper `get_charset_aliases()` lazily reads or constructs alias mappings. Important state is static volatile `charset_aliases`.

## Control Flow
On Unix-like systems, it prefers `nl_langinfo(CODESET)` when available, otherwise falls back to locale environment variables. On Windows it builds `CP<ACP>` from `GetACP`; on OS/2 it uses locale overrides or `DosQueryCp`. It then scans alias pairs from `charset.alias` or built-in VMS/Windows tables, substitutes canonical names, and returns `ASCII` instead of an empty result.

## State and Persistence
The alias table is cached in process memory after first load. It reads `LIBDIR/charset.alias` through `relocate()` when relocatable support is enabled. It does not write files.

## Dependencies and Integration Points
It depends on `localcharset.h`, optional `langinfo.h`, `locale.h`, Windows/OS2 APIs, `relocatable.h`, and `config.charset`-generated `charset.alias`. `loadmsgcat.c` uses `locale_charset()` to choose output conversion when no binding codeset or `OUTPUT_CHARSET` is set.

## Risks
The static cache is only weakly protected with `volatile`, not real locking, so concurrent first-use can race in standalone builds. Missing alias files degrade to raw platform names or ASCII fallback. Environment-derived encodings may be non-canonical until alias mapping succeeds.

## Test Signals
Test with `nl_langinfo`, without `nl_langinfo`, with `LC_ALL`/`LC_CTYPE`/`LANG`, with custom `charset.alias`, missing alias file, Windows/OS2 codepage branches where possible, and empty/unknown codeset fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.h

## Purpose
This small public header declares the charset-detection API implemented by `localcharset.c`.

## Important APIs, Types, and Functions
It declares `extern const char * locale_charset(void);` inside an `extern "C"` block for C++ compatibility and uses include guards.

## Control Flow
No runtime flow; it is a declaration-only header.

## State and Persistence
No state is stored here. The returned pointer contract says callers must not free it because it is statically allocated or cached by the implementation.

## Dependencies and Integration Points
Included by `localcharset.c` and any code needing the current locale's canonical encoding. In this tree, catalog conversion setup uses it indirectly through `loadmsgcat.c`.

## Risks
Callers might incorrectly free or mutate the returned string. The API returns a non-canonical name when canonicalization fails, so users must tolerate unknown encodings.

## Test Signals
Compile C and C++ consumers and verify they can call `locale_charset()` and treat the result as read-only.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localealias.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localealias.c

## Purpose
This file implements locale alias expansion for gettext catalog lookup. It reads `locale.alias` files from configured alias paths, stores alias-value pairs, and performs case-insensitive lookup.

## Important APIs, Types, and Functions
The exported function is `_nl_expand_alias(const char *name)`. Static helpers are `read_alias_file(fname, fname_len)`, `extend_alias_table()`, and `alias_compare()`. Important data includes `struct alias_map`, `string_space`, `map`, `nmap`, `maxmap`, and static `locale_alias_path`.

## Control Flow
`_nl_expand_alias` initializes `locale_alias_path` from `LOCALE_ALIAS_PATH`, searches the sorted alias map with `bsearch`, and lazily reads additional `PATH_SEPARATOR`-delimited alias directories until a match is found or paths are exhausted. `read_alias_file` opens `<dir>/locale.alias`, parses two whitespace-delimited fields per non-comment line into pooled storage, grows the alias table as needed, ignores long trailing line fragments, and sorts the map after adding entries.

## State and Persistence
Alias mappings persist in process-global heap storage. In libc builds a lock protects map initialization and lookup. No files are written.

## Dependencies and Integration Points
It depends on `LOCALE_ALIAS_PATH`, optional `relocatable.h`, stdio, ctype, allocation, and `gettextP.h`. `finddomain.c` calls `_nl_expand_alias` before exploding locale names.

## Risks
Standalone builds lack real locking. Alias file parsing uses a fixed 400-byte line buffer and only reads the first two fields, which is intentional but can ignore unusual files. Allocation failure silently leaves partial alias data. Because alias values are returned from internal storage, callers must not free them.

## Test Signals
Use alias path fixtures with comments, blank lines, mixed-case aliases, duplicate aliases, long lines, multiple directories, missing files, and relocatable paths. Confirm bsearch lookup works after lazy loading and sorting.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localealias.c -->
