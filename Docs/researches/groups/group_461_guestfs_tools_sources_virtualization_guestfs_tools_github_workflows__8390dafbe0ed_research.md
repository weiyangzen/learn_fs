# Group Research: group_461_guestfs_tools_sources_virtualization_guestfs_tools_github_workflows__8390dafbe0ed

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/virtualization/guestfs-tools` files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/.github/workflows/main.yml -->
# File Research: sources/virtualization/guestfs-tools/.github/workflows/main.yml

## Scope

GitHub Actions CI for `guestfs-tools`, triggered on pushes to `master`, `ci/**`, pull requests to `master`, and manual dispatch.

## Behavior

- The active job is Fedora 43 running inside a privileged `quay.io/fedora/fedora` container on `ubuntu-latest`.
- Installs build dependencies with `dnf builddep guestfs-tools libguestfs`, adds `git`, `kernel`, and `sqlite`, and removes OCaml libguestfs packages to avoid multiple-definition warnings.
- Checks out `guestfs-tools`, clones and builds current `libguestfs`, then configures/builds `guestfs-tools` through `./libguestfs/run`.
- Runs `make check`, printing any `test-suite.log` files on failure.
- Contains a fully commented Ubuntu job showing a similar source-package build-dependency path.

## Dependencies And Risks

- Requires Fedora builddep metadata and network access to clone libguestfs.
- Privileged container is needed for libguestfs-style appliance/KVM tests.
- Tracks latest libguestfs `master` by shallow clone, so CI may fail from upstream incompatibilities not pinned to a commit.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/.github/workflows/main.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/Makefile.am

## Scope

Top-level Automake file for guestfs-tools. It orders common libraries, C tools, OCaml tools, Perl/bash tools, docs, translations, distribution files, clean rules, tests, and maintainer helpers.

## Build Structure

- Includes `common-rules.mk` and sets `ACLOCAL_AMFLAGS`.
- Builds shared common components first, with OCaml-only common libraries guarded by `HAVE_OCAML`.
- Adds C tools unconditionally: `align`, `cat`, `diff`, `df`, `edit`, `filesystems`, `format`, `inspector`, `log`, `ls`, `make-fs`, and `tail`.
- Adds OCaml tools only when available: `customize`, `builder`, `drivers`, `get-kernel`, `resize`, `sparsify`, and `sysprep`.
- Adds bash completion, Perl `win-reg` if enabled, docs, gettext catalogs, and optional po4a docs.

## Generated/Distribution Logic

- `EXTRA_DIST` includes repository metadata, maintainer scripts, internal headers, and support files.
- `dist-hook` regenerates translation input lists and docs POT files.
- `po/POTFILES` and `po/POTFILES-ml` are generated from source discovery with exclusions for generated, dummy, and test files.
- Builds `podwrapper.1` from `podwrapper.pl`.

## Tests And Maintenance

- Default top-level `TESTS` runs `check-mli.sh`.
- `build-test-guests` prepares phony guests.
- `check-valgrind` and `check-slow` discover subdirectories with matching targets and run them.
- Maintainer targets commit/tag the current version and check `EXTRA_DIST` completeness against git files.

## Risks And Invariants

- `SUBDIRS` ordering matters because OCaml tools depend on common OCaml libraries and customize code.
- Translation file generation depends on stable grep exclusions.
- Maintainer distribution checks assume git submodule layout and generated-file exclusions remain accurate.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/align/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/align/Makefile.am

## Scope

Automake rules for the C-based `virt-alignment-scan` tool.

## Build And Install

- Builds `bin_PROGRAMS = virt-alignment-scan` from `scan.c`.
- Includes common options, parallel, structs, utils, libguestfs headers, and gnulib.
- Links common options/parallel/structs/utils libraries, libguestfs, libxml2, libvirt, gettext, gnulib, pthread, and math support.
- Generates `virt-alignment-scan.1` and website HTML through `PODWRAPPER`.

## Tests

- Runs docs check and a direct image scan test.
- Adds libvirt guest scan test only under `HAVE_LIBVIRT`.
- Provides `check-valgrind` by rerunning check with `VG`.

## Risks And Invariants

- The binary always builds read-only partition alignment logic, while all-domain scanning depends on libvirt availability.
- The test environment uses `$(top_builddir)/run --test`, so generated library paths and test variables come from the repository wrapper.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/align/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/align/scan.c -->
# File Research: sources/virtualization/guestfs-tools/align/scan.c

## Scope

Implements `virt-alignment-scan`, a read-only tool that reports partition start alignment for supplied disk images/domains or all libvirt domains.

## CLI And Modes

- Supports `-a`, `-d`, `-c`, `--format`, `--blocksize`, `-P`, `--quiet`, `--uuid`, `-v`, `-V`, and trace/help/list-options flags.
- Uses shared `options.c` globals with fixed invariants: `read_only = 1`, `inspector = 0`.
- If no drives are specified, it enumerates all libvirt domains and scans them in parallel with `start_threads`.
- If drives/domains are specified, it treats them as one guest, launches one libguestfs handle, and scans locally.
- `--uuid` is valid only for all-libvirt-domain mode.

## Alignment Logic

- Lists devices, calls `guestfs_part_list` for each, and skips devices with unrecognized disk labels.
- Canonicalizes device names before printing.
- For each partition, reads `part_start` in bytes and computes the power-of-two alignment by counting trailing zero bits.
- Tracks the smallest alignment seen in global `worst_alignment`, protected by a pthread mutex.
- Reports `<4K` as bad, `<64K` as bad for NetApp-style alignment, otherwise OK.
- Exit codes encode worst alignment: `3` for under 4K, `2` for under 64K, `0` otherwise.

## Dependencies And Risks

- Depends on libguestfs partition inspection and optional libvirt domain enumeration.
- Shared global worst alignment must remain mutex-protected because all-domain mode is threaded.
- Partition start of zero is treated as highly aligned, though the comment notes it is unlikely.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/align/scan.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan-docs.sh

## Scope

Documentation consistency test for `virt-alignment-scan`.

## Behavior

- Sources common test functions, enables strict shell execution and tracing, then honors skip configuration.
- Runs `podcheck.pl` against `virt-alignment-scan.pod`, passing the common options path.

## Dependencies And Risks

- Requires `podcheck.pl` and the POD file to match the executable option surface.
- Only validates documentation/options, not runtime alignment scanning.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan-guests.sh -->
# File Research: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan-guests.sh

## Scope

Libvirt-backed integration smoke test for `virt-alignment-scan`.

## Behavior

- Uses the phony guest libvirt XML through `test://$abs_top_builddir/test-data/phony-guests/guests-all-good.xml`.
- Runs `virt-alignment-scan -c "$libvirt_uri"`.
- Accepts exit codes `0`, `2`, and `3` because those are semantic alignment results, not execution failures.

## Dependencies And Risks

- Depends on libvirt test driver support and generated phony guest metadata.
- Does not assert exact output, only that the tool completes with a valid alignment-result code.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan-guests.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan.sh -->
# File Research: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan.sh

## Scope

Direct-image smoke test for `virt-alignment-scan`.

## Behavior

- Runs the tool on `../test-data/phony-guests/fedora.img` with `--format=raw`.
- Accepts alignment-result exit codes `0`, `2`, and `3`.

## Dependencies And Risks

- Requires the Fedora phony guest image.
- Does not validate exact partition alignment text, only successful execution and recognized result codes.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/bash/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/bash/Makefile.am

## Scope

Build/install rules for bash completion scripts.

## Behavior

- Maintains real completion scripts for `virt-alignment-scan` and `virt-win-reg`.
- Creates symlinked completion entries for many tools that share the common completion script behavior.
- Under `HAVE_BASH_COMPLETION`, installs scripts and symlinks into `$(BASH_COMPLETIONS_DIR)`.
- Copies real scripts into the build directory for out-of-tree builds.
- Cleans generated symlinks and copied scripts.

## Tests

- Runs `test-complete-in-script.sh` with environment variables listing scripts, symlinks, and commands.

## Risks And Invariants

- Symlink targets must stay consistent with tools that support common `--short-options`/`--long-options`.
- The `symlinks="$(scripts)"` assignment in `TESTS_ENVIRONMENT` appears intentional or legacy but means the test’s command list is the main coverage signal.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/bash/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/bash/test-complete-in-script.sh -->
# File Research: sources/virtualization/guestfs-tools/bash/test-complete-in-script.sh

## Scope

Test ensuring each bash completion script or symlink contains a matching `complete` command.

## Behavior

- Requires the `commands` environment variable, normally supplied by `make check`.
- For each command, verifies the script/symlink exists and contains a `complete` rule ending with that command name.
- Fails with diagnostic messages for missing files or mismatched completion declarations.

## Dependencies And Risks

- Depends on generated symlinks being present in the build directory.
- Uses grep against shell completion text, so format changes in completion scripts must preserve recognizable `complete ... command` lines.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/bash/test-complete-in-script.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/bugs-in-changelog.sh -->
# File Research: sources/virtualization/guestfs-tools/bugs-in-changelog.sh

## Scope

Maintainer release-note helper that extracts referenced bugs/issues from git history for a supplied commit range.

## Behavior

- Requires one argument: a git commit range.
- Extracts Red Hat Bugzilla IDs and URLs from `git log`, normalizes to numeric IDs, sorts uniquely, and queries Bugzilla.
- Filters Bugzilla results to post-NEW/ASSIGNED states and emits POD `=item` entries with bug links and descriptions.
- Extracts Jira IDs matching `RHEL-[0-9]+` and GitHub guestfs-tools issue URLs, emitting placeholder `XXX` entries because it cannot fetch titles.

## Dependencies And Risks

- Requires `git`, `bugzilla` CLI, and Bugzilla login/API key.
- Empty bug sets or unauthenticated Bugzilla can cause misleading/truncated output.
- Output is POD fragment text intended for manual release note preparation.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/bugs-in-changelog.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/build-aux/guestfs-test-driver -->
# File Research: sources/virtualization/guestfs-tools/build-aux/guestfs-test-driver

## Scope

Automake-style test driver customized to record guestfs test duration.

## Behavior

- Parses standard Automake test-driver options: test name, log file, TRS file, expected failure, color, and hard-error behavior.
- Runs the supplied test script, capturing stdout/stderr to the log file.
- Maps exit status to `PASS`, `FAIL`, `SKIP`, `ERROR`, `XFAIL`, or `XPASS`.
- Writes result metadata to `.trs`, including `:guestfs-time:` measured in seconds.
- Removes log/TRS files on signal traps.

## Dependencies And Risks

- Maintained as an Automake-derived script with guestfs-specific timing metadata.
- Uses shell `set -u`, so missing mandatory option handling is strict.
- Color output uses terminal escape sequences only when enabled.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/build-aux/guestfs-test-driver -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/builder/Makefile.am

## Scope

Automake rules for `virt-builder`, `virt-builder-repository`, the C `virt-index-validate` validator, parser tests, repository config, templates, docs, and builder test images.

## Build Structure

- Lists OCaml interfaces/implementations for builder, cache, downloader, index parsing, sources, Simplestreams, list output, and command-line handling.
- Lists C parser/support sources: flex scanner, bison parser, structure ownership, OCaml parser bridge, pxzcat bridge, and setlocale bridge.
- Under `HAVE_OCAML`, builds `virt-builder`, `virt-builder-repository`, and `index_parser_tests` with `ocaml-link.sh`.
- Links shared OCaml archives from common utility, gettext, XML, guestfs, tools, and customize libraries.
- Generates `osinfo_config.ml` from the configured libosinfo database path.

## Data And Docs

- Installs default repo config files and GPG keys under `virt-builder/repos.d`.
- Generates man pages and website HTML for `virt-builder`, `virt-builder-repository`, and `virt-index-validate`.
- Builds compressed/qcow2 phony guest artifacts for tests when source images exist.

## Tests

- Standard tests cover docs, cache-all, list output, index validation, Simplestreams list output, core virt-builder behavior, and parser tests.
- Slow tests cover serial console boot checks, planner combinations, and repository generation/update behavior.
- Console wrapper scripts are generated from a common `test-console.sh`.

## Risks And Invariants

- Parser-generated files are built but removed from the distribution by `dist-hook`.
- OCaml link ordering and common library archives are significant.
- Many tests depend on generated phony guests, qemu-img, xz, libguestfs runtime wrappers, and optional OCaml/native compiler availability.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-parse.y -->
# File Research: sources/virtualization/guestfs-tools/builder/index-parse.y

## Scope

Bison grammar for virt-builder index files, including optional clear-signed PGP wrappers.

## Grammar And Behavior

- Parses an empty index, plain section list, or PGP prologue + section list + epilogue.
- A section is `[name]` followed by zero or more fields.
- Fields may have continuation lines; continuations are concatenated with newline separators.
- Builds linked `struct section` and `struct field` lists from scanner tokens.
- Uses destructors to free partially parsed sections/fields on parse errors.

## Interfaces

- Exposes `do_parse(struct parse_context *, FILE *)`.
- Uses `scanner_init`, `scanner_destroy`, and reentrant `yylex`.
- Reports syntax errors with optional program name, input file, line number, and configured suffix.

## Risks And Invariants

- Memory ownership transfers from scanner token values into linked parser structures.
- `concat_newline` allocates merged strings and must be paired with freeing old values.
- Parser is pure/reentrant and depends on `YY_EXTRA_TYPE` carrying parse context through the scanner.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-parse.y -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-parser-c.c -->
# File Research: sources/virtualization/guestfs-tools/builder/index-parser-c.c

## Scope

C/OCaml bridge for the flex/bison virt-builder index parser.

## Behavior

- Exposes `virt_builder_parse_index` to OCaml.
- Initializes `parse_context` with program name, input filename, and error suffix.
- Opens the index file, runs `do_parse`, converts parse errors into OCaml invalid-argument exceptions, and maps close errors to Unix exceptions.
- Converts linked C sections into OCaml arrays of `(section_name, fields)` tuples.
- Converts each field into `(key, subkey option, value)`.
- Frees the C parse tree after conversion.

## Dependencies And Risks

- Uses OCaml runtime allocation macros and must keep values rooted through `CAMLparam`/`CAMLlocal`.
- Assumes parser output remains valid until copied into OCaml strings.
- File I/O failures surface through OCaml Unix exceptions.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-parser-c.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-scan.l -->
# File Research: sources/virtualization/guestfs-tools/builder/index-scan.l

## Scope

Flex scanner for virt-builder index syntax.

## Tokens And Behavior

- Ignores comments beginning with `#` at the start of a line and increments `seen_comments`.
- Ignores blank lines.
- Recognizes section headers of the form `[A-Za-z0-9._-]`.
- Recognizes fields `key=value` and `key[subkey]=value`, allocating `struct field`.
- Recognizes indented continuation lines and strips the leading whitespace and trailing newline.
- Special-cases PGP signed-message prologue by consuming headers through the first blank line.
- Special-cases PGP signature epilogue by consuming to EOF.
- Returns `UNKNOWN_LINE` for otherwise invalid input.

## Interfaces

- Reentrant scanner with bison bridge and location tracking.
- Provides `scanner_init` and `scanner_destroy`.

## Risks And Invariants

- Scanner intentionally processes line-by-line except for PGP wrapper hacks.
- Comments are only comments at column zero.
- PGP prologue/epilogue consumption affects compatibility validation because comments are counted separately.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-scan.l -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-struct.c -->
# File Research: sources/virtualization/guestfs-tools/builder/index-struct.c

## Scope

Memory management helpers for virt-builder parsed-index data structures.

## Behavior

- `parse_context_init` zeroes the context.
- `parse_context_free` frees the parsed index tree.
- `section_free` recursively frees a section list, section names, and fields.
- `field_free` recursively frees field lists, keys, subkeys, and values.

## Risks And Invariants

- Recursion follows linked-list `next` pointers, so parser-created chains must be acyclic.
- The functions free structure contents and nodes reachable from them; `parse_context_free` does not free the context pointer itself.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-struct.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-struct.h -->
# File Research: sources/virtualization/guestfs-tools/builder/index-struct.h

## Scope

Header defining the C structures produced by the virt-builder index parser.

## Data Structures

- `struct section`: linked list node with section name and field list.
- `struct field`: linked list node with key, optional subkey, and value.
- `struct parse_context`: parser result, comment detection flag, input file, program name, and error suffix.

## APIs

- Declares context initialization/freeing.
- Declares recursive section and field free helpers.

## Risks And Invariants

- `seen_comments` is part of validator compatibility checks for old virt-builder versions.
- Ownership is heap-based C strings and linked nodes; callers must use the declared cleanup helpers.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-struct.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-validate.c -->
# File Research: sources/virtualization/guestfs-tools/builder/index-validate.c

## Scope

Standalone C validator for virt-builder index files.

## CLI And Behavior

- Accepts one index file plus `--version`, `--help`, and compatibility flags `--compat-1.24.0` / `--compat-1.24.1`.
- Parses the file through the shared flex/bison parser.
- Reports parse failures as validation errors after closing input.
- Under `--compat-1.24.1`, rejects indexes containing comments.
- Under `--compat-1.24.0`, rejects section names with underscores and requires every section to contain `sig`.
- Under `--compat-1.24.1`, rejects field keys containing `.` or `,`.
- Prints `<input> validated OK` on success.

## Dependencies And Risks

- Shares parser structures with OCaml builder code.
- Compatibility checks are semantic post-parse checks, not scanner-level restrictions.
- Close errors are reported but ignored after parsing.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/index-validate.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/libguestfs.conf.in -->
# File Research: sources/virtualization/guestfs-tools/builder/libguestfs.conf.in

## Scope

Default virt-builder repository configuration template for libguestfs-hosted indexes.

## Contents

- Defines `[libguestfs.org]` using `https://builder.libguestfs.org/index.asc`.
- Defines `[archive.libguestfs.org]` using `http://archive.libguestfs.org/builder/index.asc`.
- Both entries reference the installed `libguestfs.gpg` key under `@SYSCONFDIR@/virt-builder/repos.d`.

## Risks And Invariants

- `@SYSCONFDIR@` is substituted by configure.
- These repositories are network-backed and signature-checked through the configured GPG key.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/libguestfs.conf.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/opensuse.conf.in -->
# File Research: sources/virtualization/guestfs-tools/builder/opensuse.conf.in

## Scope

Default virt-builder repository configuration template for openSUSE images.

## Contents

- Defines `[opensuse.org]` with an openSUSE Virtualization repository image index URL.
- References the installed `opensuse.gpg` key under `@SYSCONFDIR@/virt-builder/repos.d`.

## Risks And Invariants

- Uses HTTP for the repository URI while relying on GPG key verification for integrity.
- Configure substitutes `@SYSCONFDIR@`.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/opensuse.conf.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/pxzcat-c.c -->
# File Research: sources/virtualization/guestfs-tools/builder/pxzcat-c.c

## Scope

OCaml C stub implementing virt-builder decompression of xz templates, with optional parallel liblzma support and fallback to external `xzcat`.

## Public OCaml Stubs

- `virt_builder_using_parallel_xzcat` reports whether parallel liblzma support was compiled in.
- `virt_builder_pxzcat` decompresses an input xz file into an output file.

## Fallback Behavior

- Opens/truncates the output file, forks, redirects child stdout to the output, and execs configured `XZCAT`.
- Parent waits and raises OCaml failure if `xzcat` exits abnormally or nonzero.

## Parallel Behavior

- Enabled only when liblzma and needed index APIs are available.
- Determines thread count from online CPUs.
- Validates xz header magic.
- Parses xz stream indexes backward from the file end, handling stream padding, stream headers/footers, and combined multi-stream indexes.
- Preallocates output to the total uncompressed size, using careful truncation/write sequencing to avoid ext4 `auto_da_alloc` flush behavior.
- Iterates xz blocks across worker threads. A mutex protects the shared `lzma_index_iter`; workers use `pread`/`pwrite` to avoid shared file offset races.
- Each worker decodes block headers, verifies compressed size against the index, decompresses block data, and writes nonzero output buffers to preserve sparseness.

## Dependencies And Risks

- Uses OCaml exception APIs from C; error paths may not return normally.
- Thread workers return status pointers in per-thread state and aggregate failures after joins.
- Parallel path depends on correct xz indexes; corrupt footer/header/index data becomes OCaml invalid-argument errors.
- Sparse preservation depends on `is_zero` checks before `pwrite`.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/pxzcat-c.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/setlocale-c.c -->
# File Research: sources/virtualization/guestfs-tools/builder/setlocale-c.c

## Scope

OCaml C stub exposing `setlocale` for virt-builder.

## Behavior

- Maps OCaml category indexes to `LC_ALL`, `LC_CTYPE`, `LC_NUMERIC`, `LC_TIME`, `LC_COLLATE`, `LC_MONETARY`, and `LC_MESSAGES`.
- Accepts an OCaml optional locale string; `None` maps to `NULL`.
- Calls C `setlocale`.
- Returns `Some locale_string` on success or `None` on failure.

## Risks And Invariants

- The OCaml-side enum ordering must match `lc_string_table`.
- Returned `setlocale` storage is copied immediately into an OCaml string.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/setlocale-c.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/templates/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/builder/templates/Makefile.am

## Scope

Automake rules for virt-builder template fragments and kickstart/preseed generation data.

## Behavior

- Collects `*.index-fragment` files into a generated `index`.
- Distributes fragments, kickstarts, virt-install command files, preseed files, `make-template.ml`, and `validate.sh`.
- Concatenates fragments with `LANG=C` and reminds maintainers to update `index.asc` via GPG clearsigning.
- Runs `validate.sh` under the repository test wrapper.

## Risks And Invariants

- Generated unsigned `index` and signed `index.asc` must stay aligned manually.
- Concatenation order follows shell wildcard collation under `LANG=C`.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/templates/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/templates/validate.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/templates/validate.sh

## Scope

Validation test for virt-builder template indexes.

## Behavior

- Forces `LANG=C` and exits on errors.
- Creates an empty temporary file.
- Runs `virt-index-validate index`.
- If `index.asc` exists, validates it too.
- Validates the empty temporary file, then removes it.

## Dependencies And Risks

- Requires the `virt-index-validate` binary.
- Empty-file validation confirms parser acceptance of empty indexes.
- Does not verify that `index.asc` cryptographically matches `index`.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/templates/validate.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-config/virt-builder/repos.d/test-index.conf.in -->
# File Research: sources/virtualization/guestfs-tools/builder/test-config/virt-builder/repos.d/test-index.conf.in

## Scope

Test repository configuration template for native virt-builder index tests.

## Contents

- Defines `[test-index]`.
- Points `uri` to `file://@abs_top_builddir@/builder/test-index`.

## Risks And Invariants

- Configure substitutes the absolute build directory.
- The referenced `test-index` file must exist in the builder build directory for list/build tests.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-config/virt-builder/repos.d/test-index.conf.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-console.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/test-console.sh

## Scope

Slow integration test checking that virt-builder templates boot with a functional serial console.

## Behavior

- Intended to be invoked through generated `test-console-GUEST.sh` wrappers.
- Requires slow-test mode, a known virt-builder guest, x86_64 host, and `qemu-system-x86_64`.
- Unsets `VIRT_BUILDER_DIRS` to use public templates.
- Applies guest-specific fixes for Debian/Ubuntu serial console setup.
- Builds a guest disk with `virt-builder`, boots it under qemu with `-serial stdio`, sleeps 180 seconds, then kills qemu.
- Checks captured serial output for GRUB, kernel/systemd, login banner, and login prompt patterns depending on distro family.
- Removes generated disk and output on success.

## Dependencies And Risks

- Requires qemu/KVM or TCG fallback and public template availability.
- Fixed sleep/kill timing can be sensitive to host speed.
- Pattern expectations are distro-specific and may need updates as templates change.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-console.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/test-docs.sh

## Scope

Documentation consistency test for builder tools.

## Behavior

- Runs `podcheck.pl` on `virt-builder.pod`, inserting common customize synopsis/options POD fragments and ignoring signature options.
- Runs `podcheck.pl` on `virt-builder-repository.pod`.

## Dependencies And Risks

- Depends on common customize POD fragment paths.
- Only checks documentation/option consistency, not runtime builder behavior.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-simplestreams/streams/v1/index.json -->
# File Research: sources/virtualization/guestfs-tools/builder/test-simplestreams/streams/v1/index.json

## Scope

Simplestreams index fixture for virt-builder tests.

## Contents

- Declares `format: index:1.0`.
- Points to one product stream, `net.cirros-cloud:released:download`.
- Lists product IDs for CirrOS standard 0.3 on i386, x86_64, powerpc, and arm.
- References product metadata path `streams/v1/net.cirros-cloud_released_download.json`.

## Risks And Invariants

- Tests expect this fixture to resolve into the supported templates listed by `test-virt-builder-list-simplestreams.sh`.
- The arm product lacks disk image data in the companion fixture, so list output intentionally covers only usable disk images.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-simplestreams/streams/v1/index.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-simplestreams/streams/v1/net.cirros-cloud_released_download.json -->
# File Research: sources/virtualization/guestfs-tools/builder/test-simplestreams/streams/v1/net.cirros-cloud_released_download.json

## Scope

Simplestreams product metadata fixture for CirrOS image-download tests.

## Contents

- Declares products under `net.cirros-cloud:standard:0.3` for i386, x86_64, powerpc, and arm.
- Provides versioned items with `ftype`, `md5`, `sha256`, `size`, and `path`.
- i386 and x86_64 include multiple dated versions from CirrOS 0.3.0 through 0.3.4 with `disk.img`, `lxc.tar.gz`, and `uec.tar.gz`.
- powerpc includes 0.3.4 disk image metadata.
- arm contains LXC/UEC items but no `disk.img`, which makes it unsuitable as a virt-builder disk template.
- Includes top-level `datatype: image-downloads`, `format: products:1.0`, update timestamp, and content ID.

## Test Role

- Drives Simplestreams parsing and filtering.
- Expected list output selects latest usable disk images for powerpc, x86_64, and i386.

## Risks And Invariants

- Exact sizes, names, and architecture ordering are asserted by tests.
- Changes to Simplestreams selection logic can alter which product versions appear.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-simplestreams/streams/v1/net.cirros-cloud_released_download.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-simplestreams/virt-builder/repos.d/cirros.conf.in -->
# File Research: sources/virtualization/guestfs-tools/builder/test-simplestreams/virt-builder/repos.d/cirros.conf.in

## Scope

Repository configuration template for Simplestreams tests.

## Contents

- Defines `[test-cirros]`.
- Points `uri` to `file://@abs_top_builddir@/builder/test-simplestreams`.
- Sets `format=simplestreams`.

## Risks And Invariants

- Configure substitutes the build directory.
- The format flag is required so virt-builder uses the Simplestreams parser instead of native index parsing.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-simplestreams/virt-builder/repos.d/cirros.conf.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-cacheall.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-cacheall.sh

## Scope

Test for `virt-builder --cache-all-templates`.

## Behavior

- Creates temporary repo, config, and cache directories.
- Creates fake raw and qcow2 images with `qemu-img`.
- Computes checksums and writes a minimal native index with two entries and revisions.
- Configures `VIRT_BUILDER_DIRS` and `XDG_CACHE_HOME`.
- Verifies `virt-builder --list` exact output.
- Runs `virt-builder --cache-all-templates` and checks cached template filenames include OS, arch, and revision.

## Dependencies And Risks

- Requires `qemu-img`, checksum helper, and local filesystem URI support.
- Exact `--list` formatting is part of the test contract.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-cacheall.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-list-simplestreams.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-list-simplestreams.sh

## Scope

List-output regression test for Simplestreams-backed virt-builder sources.

## Behavior

- Points `VIRT_BUILDER_DIRS` at the Simplestreams fixture.
- Checks exact short `--list` output for CirrOS powerpc, x86_64, and i386 templates.
- Checks exact `--list --long` output, including source URI, names, arches, sizes, and aliases.
- Checks exact JSON list output and schema version.

## Dependencies And Risks

- Highly sensitive to output formatting, ordering, size formatting, and Simplestreams selection rules.
- Uses local file URI fixture and disables cache/signature checks.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-list-simplestreams.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-list.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-list.sh

## Scope

List-output regression test for native virt-builder index sources.

## Behavior

- Points `VIRT_BUILDER_DIRS` at `builder/test-config`.
- Checks exact short `--list` output for phony Debian, Fedora, Fedora qcow2 variants, Ubuntu, and Windows.
- Checks exact long output, including notes and multiline notes.
- Checks exact JSON output including `notes` objects and hidden flags.

## Dependencies And Risks

- Exact text comparison makes this a strict output-format contract.
- Relies on generated `test-index.conf` pointing at the local test index.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-list.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-planner.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-planner.sh

## Scope

Slow planner/regression test for virt-builder output format and size combinations.

## Behavior

- Requires slow-test mode and local Fedora compressed/qcow2 artifacts.
- Iterates four Fedora template variants, four size choices, and three output format choices.
- Runs `virt-builder` for every combination with no cache and no signature check.
- Writes to a common `planner-output` file and removes it at the end.

## Dependencies And Risks

- Requires generated `fedora.xz`, `fedora.qcow2`, and `fedora.qcow2.xz`.
- Test is broad smoke coverage; it does not inspect each output beyond command success.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-planner.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-repository.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-repository.sh

## Scope

Slow integration test for `virt-builder-repository`.

## Behavior

- Creates a temporary repository test directory.
- Copies a Fedora phony image and writes a minimal index entry.
- Runs `virt-builder-repository` interactively with no compression, feeding architecture, name, osinfo, and expand device answers.
- Verifies generated index fields: revision, arch, name, osinfo, checksum, format, size, compressed size, and expand path.
- Adds a Debian image and reruns repository generation, ensuring new image metadata is added without changing Fedora revision.
- Modifies Fedora image via `virt-edit`, reruns with compression, and verifies revision increments, file becomes `.xz`, compressed image exists, and original raw image is removed.

## Dependencies And Risks

- Requires phony images, `virt-builder-repository`, `virt-edit`, and compression support.
- Interactive prompts are tested by piped input, so prompt ordering is part of the behavioral contract.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder-repository.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder.sh

## Scope

Core virt-builder customization integration test using a phony Fedora template.

## Behavior

- Requires `fedora.xz` in the build directory.
- Builds `phony-fedora` into qcow2 output with size, format, arch, hostname, timezone, root password, directory creation, writes, uploads, edits, deletes, symlinks, appended lines, ownership change, firstboot script, and firstboot package list.
- Uses `guestfish` to verify resulting guest content and metadata.
- Compares full expected output, including hostname, timezone symlink, shadow hash prefix, appended file contents, symlinks, and uid/gid.

## Dependencies And Risks

- Avoids `$VG` for the main `virt-builder` invocation because libtool has trouble with multiline parameters.
- Strongly asserts behavior of common customize operations.
- Uses a phony guest, so package install/run-command behavior is intentionally not covered.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-builder.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-index-validate.sh -->
# File Research: sources/virtualization/guestfs-tools/builder/test-virt-index-validate.sh

## Scope

Regression test for `virt-index-validate`.

## Behavior

- Forces `LANG=C`.
- Expects two bad index fixtures to fail validation.
- Expects four good index fixtures to pass validation.

## Dependencies And Risks

- Validates parser/validator acceptance and rejection behavior through fixture files.
- Does not inspect exact error messages.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-virt-index-validate.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-website/virt-builder/repos.d/libguestfs.conf.in -->
# File Research: sources/virtualization/guestfs-tools/builder/test-website/virt-builder/repos.d/libguestfs.conf.in

## Scope

Test repository config for website/template list checks.

## Contents

- Defines `[libguestfs.org]`.
- Points to the signed local template index under `@abs_top_srcdir@/builder/templates/index.asc`.
- References the local `libguestfs.gpg` key.
- Notes it is only enough for commands like `--list` and does not contain installable templates.

## Risks And Invariants

- Configure substitutes the absolute source directory.
- Intended for metadata/listing tests, not actual template builds.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/builder/test-website/virt-builder/repos.d/libguestfs.conf.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/cat/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/cat/Makefile.am

## Scope

Automake rules for the C-based `virt-cat` tool.

## Build And Docs

- Builds `virt-cat` from `cat.c`.
- Includes common utils, structs, options, Windows path helpers, libguestfs, and gnulib.
- Links options, windows, structs, utils, libguestfs, libxml2, libvirt, gettext, and gnulib.
- Generates `virt-cat.1` and website HTML from POD.

## Tests

- Runs docs check and `test-virt-cat.sh`.
- Supports valgrind by rerunning check with `VG`.

## Risks And Invariants

- Windows helper linkage is required because runtime path conversion is in `cat.c`.
- Tests rely on phony Fedora guest content.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/cat/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/cat/cat.c -->
# File Research: sources/virtualization/guestfs-tools/cat/cat.c

## Scope

Implements `virt-cat`, a read-only tool that prints files from virtual machine disk images or domains.

## CLI And Mounting

- Supports `-a`, `-d`, `-c`, `--format`, `--blocksize`, LUKS key options, `-m`, verbose/version/trace/help, and long/short option discovery.
- Defaults to inspector mode and read-only operation.
- Supports old-style syntax by inferring disk images or domain names from positional arguments before the final file path.
- If `-m` is supplied, disables inspector and uses explicit mountpoints.
- Adds drives, enables network if key store requires it, launches libguestfs, then either mounts explicit mountpoints or auto-inspects/mounts the guest.

## File Output

- Requires at least one guest file path.
- In inspector mode, obtains the single root and detects Windows.
- For Windows guests, converts requested paths through `windows_path`.
- Streams each requested file to stdout via `guestfs_download(filename, "/dev/stdout")`.
- Returns failure if any requested file cannot be converted or downloaded.

## Dependencies And Risks

- Assumes inspector finds exactly one root when used.
- Windows path conversion is read-only.
- Output is raw file content; multiple requested files are concatenated without delimiters.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/cat/cat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/cat/test-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/cat/test-docs.sh

## Scope

Documentation consistency test for `virt-cat`.

## Behavior

- Sources common test functions and honors skip configuration.
- Runs `podcheck.pl` against `virt-cat.pod` with the common options path.

## Dependencies And Risks

- Verifies docs/options consistency only.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/cat/test-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/cat/test-virt-cat.sh -->
# File Research: sources/virtualization/guestfs-tools/cat/test-virt-cat.sh

## Scope

Runtime test for `virt-cat` against a phony Fedora guest.

## Behavior

- Reads `/etc/test1` from `fedora.img` and expects `abcdefg`.
- Reads `/etc/test2` and expects an empty string.
- Fails with diagnostics on mismatches.

## Dependencies And Risks

- Requires the phony Fedora image and exact fixture contents.
- Covers raw image mode and auto-inspection.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/cat/test-virt-cat.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/check-mli.sh -->
# File Research: sources/virtualization/guestfs-tools/check-mli.sh

## Scope

Repository consistency test requiring OCaml implementation files to have matching interfaces.

## Behavior

- Finds `*.ml` files, excluding builder templates, contrib, OCaml examples/tests, bindtests, and `_tests.ml`.
- For each remaining `.ml`, checks for a sibling `.mli`.
- Reports missing interface files and exits nonzero if any are missing.

## Dependencies And Risks

- The rule exists because Makefile dependency generation is difficult without `.mli` files.
- Exclusion list must track intentional implementation-only OCaml files.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/check-mli.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/common-rules.mk -->
# File Research: sources/virtualization/guestfs-tools/common-rules.mk

## Scope

Top-level shared Automake fragment included by `Makefile.am`.

## Behavior

- Optionally includes `$(top_builddir)/localenv`.
- Defines `NULL` as a list terminator helper.
- Initializes common `CLEANFILES` for editor backups, patch rejects/originals, OCaml build artifacts, generated man pages, POD stamp files, and bindtests temp files.
- Initializes `DISTCLEANFILES` for `.depend` and `stamp-*`.
- Adds OCaml and PO suffixes.

## Risks And Invariants

- Intended for top-level inclusion; comments distinguish it from `subdir-rules.mk`.
- Broad clean patterns assume no subdirectory has files matching these patterns that must survive `make clean`.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/common-rules.mk -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/config.sh.in -->
# File Research: sources/virtualization/guestfs-tools/config.sh.in

## Scope

Configure-generated shell fragment exposing selected tool checks to shell scripts.

## Contents

- Preserves configure substitution marker.
- Exports `XMLLINT`.
- Exports `PYCODESTYLE`.

## Risks And Invariants

- Values are substituted by configure.
- Intended for test/support scripts that need configured tool paths.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/config.sh.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/configure.ac -->
# File Research: sources/virtualization/guestfs-tools/configure.ac

## Scope

Autoconf entry point for guestfs-tools.

## Configure Flow

- Initializes package `guestfs-tools` version `1.55.8`.
- Defines `PACKAGE_VERSION_FULL`.
- Sets colored heading helpers for readable configure output.
- Configures auxiliary directory and requires `guestfs-test-driver`.
- Initializes Automake, silent rules, macro directory, and libtool.
- Includes m4 checks for external programs, C compiler environment, guestfs libraries, OCaml/gettext/libguestfs bindings, Perl, miscellaneous libraries, and bash completion.
- Computes substituted `SYSCONFDIR`.
- Sets compatibility conditionals required by shared common makefiles.

## Generated Outputs

- Generates `config.h`, wrapper scripts (`ocaml-dep.sh`, `ocaml-link.sh`, `podwrapper.pl`, `run`, tests functions, `virt-win-reg`), all Makefiles, repo config files, test config files, and generated OCaml config files.

## Summary

- Prints optional component summary for C tools, gettext, liblzma, OCaml tools/gettext, Perl tools, bash completion, and completion directory.

## Risks And Invariants

- Many shared `common/` Makefiles are generated from this smaller standalone project, so compatibility conditionals are defined even when disabled.
- Optional tools and tests depend heavily on configure-detected OCaml, Perl, libvirt, liblzma, libosinfo, and bash-completion support.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/configure.ac -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/customize/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/customize/Makefile.am

## Scope

Automake rules for the OCaml-based `virt-customize` tool and its tests.

## Build And Docs

- Distributes OCaml source/interface, dummy C source, tests, and POD.
- Under `HAVE_OCAML`, builds `virt-customize` using `dummy.c` plus OCaml object files linked through `ocaml-link.sh`.
- Links common OCaml utility, guestfs, gettext, PCRE, XML, tools, and customize archives.
- Generates `virt-customize.1` and website HTML with inserted common customize synopsis/options.

## Tests

- Standard tests cover docs and phony guest customization.
- Slow tests are generated wrappers for password and settings tests across many distro templates.
- `check-slow` runs only slow tests with `SLOW=1`.

## Risks And Invariants

- `dummy.c` is needed because Automake expects a C source for the linked program.
- Generated slow-test wrappers and cleanup patterns must stay aligned with script naming.
- OCaml dependency generation uses `.depend`.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/customize/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/customize/dummy.c -->
# File Research: sources/virtualization/guestfs-tools/customize/dummy.c

## Scope

Dummy C source for OCaml-based tools with no real C implementation file.

## Behavior

- Defines a trivial enum constant so the file is valid C.

## Risks And Invariants

- Exists for build-system mechanics, not runtime behavior.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/customize/dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/customize/test-password.pl -->
# File Research: sources/virtualization/guestfs-tools/customize/test-password.pl

## Scope

Slow Perl/Expect integration test for virt-builder root password customization.

## Behavior

- Requires `SLOW=1`, Perl `Expect`, one guest name argument, x86_64 host, qemu, and a known public virt-builder template.
- Unsets `VIRT_BUILDER_DIRS` to use public templates.
- Applies serial-console fixes for selected Debian/Ubuntu guests.
- Generates a random root password.
- Builds a guest with `virt-builder --root-password password:<password>`.
- Boots it in qemu with serial stdio, waits for login prompt, logs in as root, runs `ls -1 /`, and expects `home` in output.
- Removes disk and log on success.

## Dependencies And Risks

- Highly environment-dependent: public templates, qemu, host architecture, boot timing, and Expect availability.
- Password/login behavior is tested through actual guest boot, not static image inspection.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/customize/test-password.pl -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/customize/test-settings.sh -->
# File Research: sources/virtualization/guestfs-tools/customize/test-settings.sh

## Scope

Slow integration test for virt-builder hostname, timezone, and firstboot settings.

## Behavior

- Requires slow-test mode, one guest name argument, x86_64 host, qemu, and a known public template.
- Builds a guest with hostname `test-set.example.com`, timezone `Japan`, and a generated firstboot script.
- Firstboot script records hostname, FQDN, timezone offset where supported, syncs, and powers off.
- Boots the guest under qemu.
- Uses `guestfish` to download `/firstboot.out` and print debug files.
- Verifies observed hostname/FQDN/timezone fields when present.
- Cleans disk and firstboot artifacts.

## Dependencies And Risks

- Guest-family conditionals handle differences in hostname/FQDN/timezone support.
- Requires firstboot to run to completion inside the guest.
- Public template behavior can change over time.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/customize/test-settings.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/customize/test-virt-customize-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/customize/test-virt-customize-docs.sh

## Scope

Documentation consistency test for `virt-customize`.

## Behavior

- Runs `podcheck.pl` on `virt-customize.pod`.
- Supplies common options path and inserts common customize synopsis/options POD fragments.
- Ignores `--dryrun`.

## Dependencies And Risks

- Documentation must remain aligned with generated/common option fragments.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/customize/test-virt-customize-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/customize/test-virt-customize.sh -->
# File Research: sources/virtualization/guestfs-tools/customize/test-virt-customize.sh

## Scope

Basic runtime test for `virt-customize` using a qcow2 overlay of a phony Fedora guest.

## Behavior

- Requires the phony Fedora guest.
- Creates a qcow2 image backed by the raw Fedora fixture.
- Runs `virt-customize` to write `/etc/motd`, write `/etc/motd2`, write then delete `/etc/motd3`.
- Uses `guestfish` to verify motd contents and that `/etc/motd3` is absent.
- Removes generated files on success.

## Dependencies And Risks

- Covers write/delete customization operations on qcow2.
- Depends on qemu-img and guestfish.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/customize/test-virt-customize.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/df/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/df/Makefile.am

## Scope

Automake rules for the C-based `virt-df` tool.

## Build And Docs

- Builds `virt-df` from `virt-df.h`, `df.c`, `main.c`, and `output.c`.
- Includes common options, parallel, structs, utils, libguestfs, and gnulib headers.
- Links common libraries, libguestfs, libxml2, libvirt, gettext, gnulib, pthread, and math.
- Generates man page and website HTML from POD.

## Tests

- Runs docs and direct image tests.
- Adds libvirt guest test under `HAVE_LIBVIRT`.
- Provides valgrind targets, including one for local libvirt guests.

## Risks And Invariants

- Parallel and libvirt libraries are needed for all-domain scanning.
- Output formatting is separately implemented in `output.c` and verified by tests.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/df/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/df/df.c -->
# File Research: sources/virtualization/guestfs-tools/df/df.c

## Scope

Core filesystem stat collection for `virt-df`.

## Behavior

- `df_on_handle` lists devices and filesystems from an already launched guestfs handle.
- Skips empty, swap, and unknown filesystem types.
- For each candidate filesystem, suppresses libguestfs errors, attempts read-only mount at `/`, calls `statvfs`, unmounts all, then prints stats if successful.
- Avoids exiting on individual guestfs failures to stay robust against bad guests.
- Under libvirt, `df_work` adds domain disks read-only, launches the handle, and delegates to `df_on_handle`.

## Dependencies And Risks

- Read-only mount failures are expected and silently ignored.
- `df_work` traditionally ignores errors adding libvirt disks but treats launch failures as errors.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/df/df.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/df/main.c -->
# File Research: sources/virtualization/guestfs-tools/df/main.c

## Scope

Command-line front end and guest selection logic for `virt-df`.

## CLI And Modes

- Supports disk/domain selection, libvirt URI, format/blocksize, CSV, human-readable, inode mode, UUID output, thread count, verbosity/version/trace, and legacy `--one-per-guest`.
- Supports old-style syntax by inferring disk paths or domain names from positional arguments when no `-a`/`-d` was given.
- Rejects extra arguments and `-h` combined with `--csv`.
- If no drives are specified, enumerates all libvirt domains and runs `df_work` through `start_threads`.
- If drives are specified, treats them as one guest, launches a single handle, synthesizes a display name, and calls `df_on_handle`.

## Display Name Logic

- Single drive names come from basename, URI final path element, or domain name.
- Multiple drives use the last list item’s name plus one `+` per additional disk.

## Dependencies And Risks

- All-domain mode requires libvirt.
- Single `-d` mode lacks UUID because the libvirt domain handle is hidden inside guestfs add-domain.
- Shared globals are consumed by options and output code.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/df/main.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/df/output.c -->
# File Research: sources/virtualization/guestfs-tools/df/output.c

## Scope

Output formatting for `virt-df`.

## Behavior

- `print_title` emits text or CSV headers for block or inode mode.
- `print_stat` canonicalizes device names, computes block/inode totals, used/free values, and percentages.
- Non-human block mode scales filesystem block counts to 1K units.
- Human mode uses gnulib `human_readable` with base-1024 SI formatting.
- Text mode combines guest name and filesystem as `name:dev`, aligning or wrapping long names.
- CSV mode writes name, device, and four stat columns as separate escaped fields.
- UUID mode replaces name with UUID when available.
- Percentages emulate `df` with ceil in text mode and one decimal in CSV mode.

## Dependencies And Risks

- Exits on failure to canonicalize device name or write output.
- CSV escaping is local and handles spaces, quotes, newlines, and commas.
- `human` and `csv` are expected to be mutually exclusive, enforced by `main.c`.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/df/output.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/df/test-virt-df-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/df/test-virt-df-docs.sh

## Scope

Documentation consistency test for `virt-df`.

## Behavior

- Runs `podcheck.pl` against `virt-df.pod` with common options path after honoring skips.

## Dependencies And Risks

- Checks documentation/options consistency only.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/df/test-virt-df-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/df/test-virt-df-guests.sh -->
# File Research: sources/virtualization/guestfs-tools/df/test-virt-df-guests.sh

## Scope

Libvirt-backed smoke test for `virt-df`.

## Behavior

- Uses the phony guest libvirt XML via `test://.../guests.xml`.
- Runs `virt-df -c "$libvirt_uri"`.

## Dependencies And Risks

- Requires libvirt test driver and generated phony guest XML.
- Does not assert exact output; command success is the check.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/df/test-virt-df-guests.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/df/test-virt-df.sh -->
# File Research: sources/virtualization/guestfs-tools/df/test-virt-df.sh

## Scope

Direct-image regression test for `virt-df`.

## Behavior

- Runs `virt-df --format=raw -a fedora.img`.
- Verifies the output starts with a title line.
- Verifies exactly six lines: header plus five filesystems.
- Checks that `/dev/VG/LV1`, `/dev/VG/LV2`, `/dev/VG/LV3`, `/dev/VG/Root`, and `/dev/[hsv]da1` appear.
- Contains disabled detailed numeric comparisons documenting expected `df`/`df -h`/`df -i` values.

## Dependencies And Risks

- Depends on the phony Fedora filesystem layout.
- Detailed space accounting is intentionally disabled due historical mismatch concerns.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/df/test-virt-df.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/df/virt-df.h -->
# File Research: sources/virtualization/guestfs-tools/df/virt-df.h

## Scope

Shared header for `virt-df`.

## APIs And Globals

- Declares output mode globals: `csv`, `human`, `inodes`, and `uuid`.
- Declares `df_on_handle`.
- Declares libvirt worker `df_work` when `HAVE_LIBVIRT`.
- Declares output functions `print_title` and `print_stat`.

## Risks And Invariants

- Shared globals are set by `main.c` and consumed by `output.c`.
- Header assumes `guestfs_h` and `guestfs_statvfs` are visible through included libguestfs headers in implementation files.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/df/virt-df.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/diff/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/diff/Makefile.am

## Scope

Automake rules for the C-based `virt-diff` tool.

## Build And Docs

- Builds `virt-diff` from `diff.c`.
- Includes common utils, visit traversal, options, cat/fish headers, libguestfs, and gnulib.
- Links options, visit, structs, utils, libguestfs, libxml2, libvirt, gettext, and gnulib.
- Generates man page and website HTML from POD.

## Tests

- Runs docs check and `test-virt-diff.sh`.
- Provides valgrind check wrapper.

## Risks And Invariants

- Depends on the common visit library for recursive guest traversal.
- Runtime content diffs also depend on the external `diff` command.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/diff/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/diff/diff.c -->
# File Research: sources/virtualization/guestfs-tools/diff/diff.c

## Scope

Implements `virt-diff`, comparing filesystems of two virtual machines or disk sets.

## CLI And Setup

- Uses two libguestfs handles, `g` for the first guest and `g2` for the second.
- Supports first guest `-a`/`-d`, second guest `-A`/`-D`, libvirt URI, format/blocksize, key options, CSV, human-readable, checksum, metadata detail flags, time formatting flags, and verbose/trace/version/help.
- Requires at least one source for each guest and rejects extra arguments.
- Enforces read-only inspector mode and rejects human-readable CSV.
- Mounts and inspects each guest independently before traversal.

## Tree Collection

- `visit_guest` recursively traverses `/` using common `visit`.
- Each entry is copied into an in-memory `tree` as path, `statns`, xattrs, and optional checksum.
- If `--checksum` is set and the entry is a regular file, computes a guestfs checksum.
- Unless enabled by flags, normalizes access time, directory link counts, and directory times to avoid noisy diffs.
- Stores entries in visit order, relying on sorted traversal for merge-style comparison.

## Diff Logic

- `diff_guests` walks both sorted file lists.
- Paths only in the first guest are deleted (`-`); paths only in the second are added (`+`).
- Matching paths compare statns and xattrs; matching regular files may compare checksums or mtime/ctime/size as content-change indicators.
- Content changes emit `=` plus metadata, then in non-CSV mode download both files to a temp directory and run external `diff -u`, omitting the first two diff header lines.
- Metadata-only changes emit old and new rows and a `# changed:` row naming changed fields/xattrs.

## Output

- Outputs file type, octal permissions, size, optional uid/gid, optional times, optional extra stat fields, optional checksum, path, symlink target, and optional xattrs.
- Text mode separates fields with spaces and right-aligns sizes; CSV mode escapes strings/binary fields locally.
- Time output supports formatted local time, raw time_t, seconds relative to now, or days relative to now.
- Device numbers are printed as major:minor.

## Dependencies And Risks

- External `diff` command is required for content display.
- Temporary file paths are created under guestfs tmpdir and cleaned after use.
- Comparisons intentionally ignore `st_dev` and `st_ino` in changed-field reporting.
- Large guests can consume substantial memory because all entries and selected checksums are stored before comparison.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/diff/diff.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/diff/test-virt-diff-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/diff/test-virt-diff-docs.sh

## Scope

Documentation consistency test for `virt-diff`.

## Behavior

- Runs `podcheck.pl` against `virt-diff.pod`.
- Supplies common options path.
- Ignores documented aliases/options that map to internal canonical options.

## Dependencies And Risks

- Covers docs/options consistency only.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/diff/test-virt-diff-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/diff/test-virt-diff.sh -->
# File Research: sources/virtualization/guestfs-tools/diff/test-virt-diff.sh

## Scope

Runtime regression test for `virt-diff`.

## Behavior

- Requires phony Fedora guest.
- Creates a qcow2 overlay backed by the raw Fedora image.
- Modifies the overlay by touching `/diff` and appending text to `/etc/motd`.
- Runs `virt-diff` between the raw base and qcow2 overlay.
- Compares exact expected output, including added file row, changed file row, unified diff hunk, and end marker.
- Removes generated qcow2 file.

## Dependencies And Risks

- Depends on guestfish qcow2 overlay creation and exact phony guest `/etc/motd` contents.
- Exact output comparison covers both metadata row formatting and external diff output.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/diff/test-virt-diff.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/drivers/Makefile.am

## Scope

Automake rules for the OCaml-based `virt-drivers` tool.

## Build And Docs

- Distributes OCaml sources/interfaces, dummy C source, expected XML outputs, tests, and POD.
- Under `HAVE_OCAML`, builds `virt-drivers` from OCaml objects linked through `ocaml-link.sh`.
- Links common OCaml stdutils, guestfs, gettext, PCRE, utils, tools, and mldrivers archives.
- Generates `virt-drivers.1` and website HTML from POD.
- Generates OCaml dependencies into `.depend`.

## Tests

- Runs docs, Linux output, and Windows output tests under the test wrapper.

## Risks And Invariants

- `hwdata_config.ml` is configure-generated and determines optional PCI/USB IDs lookup paths.
- Expected XML tests ignore generated-by comments and normalize optional hwdata names.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/dummy.c -->
# File Research: sources/virtualization/guestfs-tools/drivers/dummy.c

## Scope

Dummy C source for the OCaml-based `virt-drivers` binary.

## Behavior

- Defines a trivial enum constant so Automake has a valid C source.

## Risks And Invariants

- Build-system shim only; no runtime behavior.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/expected-fedora.xml -->
# File Research: sources/virtualization/guestfs-tools/drivers/expected-fedora.xml

## Scope

Expected XML output fixture for `virt-drivers` on the phony Fedora guest.

## Contents

- Describes one BIOS firmware Linux operating system rooted at `/dev/VG/Root`.
- Includes Fedora release metadata, x86_64 arch, RPM/yum package metadata, and osinfo `fedora14`.
- Includes grub1 bootloader config path and one kernel entry.
- Kernel entry includes version, architecture, vmlinuz/initrd/modules paths, module `virtio_blk`, and `supports_virtio_blk`.

## Risks And Invariants

- Tests ignore the generated-by version comment.
- Any virt-drivers XML schema or phony Fedora kernel/module fixture change must update this expected file.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/expected-fedora.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/expected-windows.xml -->
# File Research: sources/virtualization/guestfs-tools/drivers/expected-windows.xml

## Scope

Expected XML output fixture for `virt-drivers` on the phony Windows guest.

## Contents

- Describes one BIOS firmware Windows operating system rooted at `/dev/sda2`.
- Includes i386 arch, Windows distro/product metadata, client variant, version 6.1, and osinfo `win7`.
- Lists detected drivers:
  - `machine` with PCI vendor `8086` device `0008`.
  - `mshdc` with PCI class `000101`.

## Risks And Invariants

- Test strips optional `vendorname` and `devicename` attributes before comparison because hwdata availability varies.
- Generated-by version comment is ignored during diff.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/expected-windows.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/hwdata_config.ml.in -->
# File Research: sources/virtualization/guestfs-tools/drivers/hwdata_config.ml.in

## Scope

Configure-generated OCaml configuration for virt-drivers hwdata paths.

## Behavior

- Defines `dir` from substituted `@HWDATA_PKGDATADIR@`.
- Converts empty directory string to `None`, otherwise `Some dir`.
- Defines optional `pci_ids` and `usb_ids` paths by appending `pci.ids` and `usb.ids`.

## Dependencies And Risks

- Depends on `Std_utils.(//)` path join helper.
- If hwdata directory is absent, driver output omits vendor/device names.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/hwdata_config.ml.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-docs.sh

## Scope

Documentation consistency test for `virt-drivers`.

## Behavior

- Runs `podcheck.pl` on `virt-drivers.pod` with the common options path after honoring skips.

## Dependencies And Risks

- Checks docs/options consistency only.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-linux.sh -->
# File Research: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-linux.sh

## Scope

Runtime output regression test for `virt-drivers` on the phony Fedora guest.

## Behavior

- Requires the Fedora phony guest.
- Runs `virt-drivers --format=raw -a fedora.img` into `actual-fedora.xml`.
- Diffs against `expected-fedora.xml`, ignoring generated-by lines.
- Removes actual output afterward.

## Dependencies And Risks

- Exact XML structure is asserted aside from generated version comment.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-linux.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-windows.sh -->
# File Research: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-windows.sh

## Scope

Runtime output regression test for `virt-drivers` on the phony Windows guest.

## Behavior

- Requires the Windows phony guest.
- Runs `virt-drivers --format=raw -a windows.img` into XML.
- Strips optional `vendorname` and `devicename` attributes because hwdata may vary by environment.
- Diffs normalized output against `expected-windows.xml`, ignoring generated-by lines.
- Removes temporary XML files.

## Dependencies And Risks

- Tests stable driver detection while allowing environment-dependent hwdata enrichment.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-windows.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/edit/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/edit/Makefile.am

## Scope

Automake rules for the C-based `virt-edit` tool.

## Build And Docs

- Builds `virt-edit` from `edit.c`.
- Includes common edit, options, Windows path helpers, utils, libguestfs, and gnulib headers.
- Links common edit/options/windows/utils libraries, libguestfs, libxml2, libvirt, gettext, and gnulib.
- Generates `virt-edit.1` and website HTML from POD with general warnings.

## Tests

- Runs docs and runtime `virt-edit` tests under the repository test wrapper.

## Risks And Invariants

- Links both common edit logic and Windows path support because editing must handle guest path translation.
- This file only defines build/test wiring; tool behavior lives in `edit.c`, outside this group.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/edit/Makefile.am -->