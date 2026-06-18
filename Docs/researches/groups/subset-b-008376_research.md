# subset-b-008376 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secil2conf.c -->
# sources/security-integrity/selinux/secilc/secil2conf.c

Purpose: `secil2conf` is a small command-line converter from one or more SELinux CIL files to textual `policy.conf`. It configures a `cil_db`, adds each input file, compiles the database, and emits the result through `cil_write_policy_conf`.

Important APIs and flow: `usage` documents `-o`, `-M`, `-P`, `-Q`, `-v`, and `-h`. `main` parses options with `getopt_long`, maps MLS strings to `cil_set_mls`, toggles tunable and qualified-name handling, and disables generated attribute expansion with `cil_set_attrs_expand_generated(db, 0)` and size expansion with `cil_set_attrs_expand_size(db, 0)`. Each file is read via `fopen`, `stat`, `malloc`, `fread`, then passed to `cil_add_file`; after all files are added, `cil_compile` runs before opening `policy.conf` or the requested output file.

State and persistence: the only persistent output is the generated policy.conf text; all CIL state is transient inside `cil_db`. Dependencies are libc, `getopt`, `stat`, and libsepol/libcil headers. Risks: whole-file `uint32_t file_size` truncates very large inputs, empty files cause `malloc(0)`/`fread(..., 0, 1)` edge behavior unlike `secilc.c`, and `strdup` results are not checked. Test signals should validate option parsing, multiple input ordering, qualified-name mode, MLS override, output-path failures, and empty-file behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secil2conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secil2tree.8.xml -->
# sources/security-integrity/selinux/secilc/secil2tree.8.xml

Purpose: this DocBook manpage documents the `secil2tree(8)` CIL AST writer. It describes the command as invoking the CIL AST writer for a supplied CIL file and outputting an AST representation.

Important surface: options include `-o/--output`, `-P/--preserve-tunables`, `-Q/--qualified-names`, `-A/--ast-phase`, `-v/--verbose`, and `-h/--help`. Integration points are the generated manpage installation pipeline and cross references to `secilc(8)` and `secil2conf(8)`. It also points users to CIL HTML and PDF reference documentation.

State and persistence: the file is static XML input to manpage tooling; runtime state is represented only as documented command-line flags. Risks: the option list says AST phase must be `parse`, `build`, or `resolve`, while `secil2tree.c` also accepts `post`; documentation can therefore under-specify a real supported mode. It also shows only one plain `file` argument, while the implementation accepts repeated input files. Test signals are documentation build validation, generated manpage inspection, and cross-checks against `secil2tree.c` option parsing.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secil2tree.8.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secil2tree.c -->
# sources/security-integrity/selinux/secilc/secil2tree.c

Purpose: `secil2tree` loads CIL source files into a libcil database and writes one of several AST views. It is a diagnostic/developer utility rather than a binary policy compiler.

Important APIs and flow: `enum write_ast_phase` models parse, build, resolve, and post phases. Option parsing supports `-o`, `-P`, `-Q`, `-A`, `-v`, and `-h`; phase names are parsed with `strcasecmp`. The program initializes `cil_db`, sets tunable and qualified-name behavior, disables attribute expansion, reads every input into memory, adds it via `cil_add_file`, then chooses `cil_write_parse_ast`, `cil_write_build_ast`, `cil_write_resolve_ast`, or `cil_write_post_ast`. Unlike `secilc`, it does not explicitly call `cil_compile`; the selected writer drives the relevant internal CIL phases.

State and persistence: output is stdout by default or the path passed to `-o`; CIL state is transient. Dependencies are libsepol/libcil and standard file APIs. Risks: repeated `-o` leaks earlier `output` strings, empty files have the same `malloc(0)`/`fread` edge risk as `secil2conf`, and the manpage omits the `post` phase. Test signals should cover all AST phases, repeated input files, stdout versus file output, invalid phase names, and option/manpage parity.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secil2tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secilc.8.xml -->
# sources/security-integrity/selinux/secilc/secilc.8.xml

Purpose: this DocBook manpage documents `secilc(8)`, the SELinux CIL compiler that builds a kernel binary policy and a `file_contexts` file from CIL input.

Important surface: it documents output selection (`-o`, `-f`), target platform (`-t selinux|xen`), MLS override, binary policy version, unknown-class handling, dontaudit suppression, tunable preservation, qualified names, multiple declarations, neverallow disabling, generated-attribute expansion, size-based attribute expansion, optimization, verbosity, and help. It integrates with generated manpage installation and references `file_contexts(5)`, `sestatus(8)`, CIL reference docs, and the CIL design wiki.

State and persistence: the documented outputs are the binary policy and file-contexts file. Risks: option spelling in the XML says `--filecontext`, while `secilc.c` registers the long option as `--filecontexts`; it says default policy version depends on the system, but the code defaults to `POLICYDB_VERSION_MAX`. These mismatches can mislead automation and users. Test signals should compare generated manpage options with `getopt_long` definitions and verify documented defaults against actual compiler behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secilc.8.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secilc.c -->
# sources/security-integrity/selinux/secilc/secilc.c

Purpose: `secilc` is the main CIL-to-binary-policy compiler. It reads CIL files, configures libcil compilation behavior, builds a `sepol_policydb_t`, optionally optimizes it, writes a binary policy, and emits file contexts.

Important APIs and flow: command-line parsing maps target to `SEPOL_TARGET_SELINUX` or `SEPOL_TARGET_XEN`, MLS to `cil_set_mls`, policy version through `strtol` bounded by `POLICYDB_VERSION_MIN/MAX`, unknown handling to `SEPOL_DENY/ALLOW/REJECT_UNKNOWN`, and flags to CIL setters such as `cil_set_disable_dontaudit`, `cil_set_multiple_decls`, and `cil_set_disable_neverallow`. Input files are read completely and added with `cil_add_file`; zero-length files are skipped. The compile path is `cil_compile` -> `cil_build_policydb` -> optional `sepol_policydb_optimize` -> `sepol_policydb_write`. File contexts come from `cil_filecons_to_string` and are written separately.

State and persistence: persistent artifacts are `policy.<version>` or `-o` output plus `file_contexts` or `-f` output. Dependencies include libsepol policydb, CIL APIs, and filesystem writes. Risks: some `strdup` and default-output allocations are checked inconsistently, binary output uses text-mode `"w"`, and failures can leave partial output files. Test signals should include policy version bounds, unknown action overrides, empty inputs, file_context generation, optimization, neverallow disabling, and target-platform differences.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secilc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secilcheck.8.xml -->
# sources/security-integrity/selinux/secilc/secilcheck.8.xml

Purpose: this DocBook manpage documents `secilcheck(8)`, a utility for checking a binary SELinux policy against CIL neverallow files.

Important surface: the synopsis requires one binary policy followed by one or more CIL files. Options are `-Q/--qualified-names`, `-m/--multiple-decls`, `-v/--verbose`, and `-h/--help`. It integrates with manpage generation and references `secilc(8)`, `secil2tree(8)`, and `secil2conf(8)`.

State and persistence: the command is documented as a checker; no persistent output is expected besides diagnostics and exit status. Dependencies are external documentation for the CIL language. Risks: spelling and behavior must track `secilcheck.c`; the XML describes `file` arguments generically, so users need examples elsewhere to understand that these are CIL neverallow sources. Test signals should include manpage generation, option parity against `getopt_long`, and CLI examples that assert nonzero exit on violations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secilcheck.8.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secilcheck.c -->
# sources/security-integrity/selinux/secilc/secilcheck.c

Purpose: `secilcheck` verifies CIL neverallow rules against an existing binary policy. It converts declarations from the binary policy into CIL, adds user-provided neverallow CIL files, compiles the CIL DB, and invokes libcil neverallow checking against the original policydb.

Important APIs and flow: `get_binary_policy_db` opens, stats, mmaps, and reads a binary policy through `sepol_policydb_read`. `add_decls_to_cil` uses `open_memstream` and `sepol_kernel_policydb_decls_to_cil` to feed binary declarations into `cil_add_file`. `add_cil_file` reads neverallow files, skipping empty files. `main` accepts `-Q`, `-m`, `-v`, and `-h`, requires at least two positional inputs, then runs `cil_compile` and `cil_check_neverallows_against_pdb`.

State and persistence: it writes no output files; state is memory-mapped policy input, a transient `sepol_policydb_t`, and a transient `cil_db`. Risks: `fd` is not initialized before error cleanup in `get_binary_policy_db`, `sb.st_size` is used in cleanup even if `fstat` fails, `mmap` asks for `PROT_WRITE` despite `MAP_PRIVATE` read-only use, and `map` cleanup checks `if (map)` rather than excluding `MAP_FAILED`. Test signals should include invalid files, zero-length policy, declaration conversion failures, valid no-violation cases, and violation exit status.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/secilc/secilcheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/Makefile -->
# sources/security-integrity/selinux/semodule-utils/Makefile

Purpose: this top-level makefile coordinates the `semodule_package`, `semodule_link`, and `semodule_expand` utility subdirectories.

Important flow: `SUBDIRS` lists the utility directories. The `all`, `install`, `relabel`, and `clean` targets iterate over each subdir and invoke `$(MAKE) $@`, exiting on the first failure. The `test` target is empty.

State and persistence: this file does not build artifacts directly; all persistent outputs are delegated to subdirectory makefiles. Dependencies are a POSIX shell, `make`, and the subdirectory target contracts. Risks: the loop is serial, a missing subdirectory or unsupported target aborts the whole operation, and the empty `test` target can produce a false signal that tests exist or passed. Test signals are mostly build-system checks: `make all`, `make install DESTDIR=...`, `make clean`, and validating that each subdir installs the expected binaries and manpages.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_expand/Makefile -->
# sources/security-integrity/selinux/semodule-utils/semodule_expand/Makefile

Purpose: builds and installs the `semodule_expand` binary and its manpage.

Important flow: defaults set `PREFIX`, `BINDIR`, `MANDIR`, and optional `LINGUAS`; `CFLAGS` defaults to `-Werror -Wall -W`, and `LDLIBS` appends `-lsepol`. The `all` target builds `semodule_expand`; installation creates binary and manpage directories, installs the executable mode `755`, installs `semodule_expand.8`, and copies localized manpages when language directories exist. `clean` removes the binary and object files.

State and persistence: outputs are `semodule_expand`, object files, and installed files under `DESTDIR`. Dependencies are C compiler defaults, libsepol, install utilities, and localized manpage directories. Risks: `-Werror` can break builds on newer compilers, no explicit source dependency is listed beyond make's implicit rule, and `test` is absent in the subdir. Test signals should include clean rebuilds, DESTDIR install verification, and compiler warning checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_expand/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_expand/semodule_expand.c -->
# sources/security-integrity/selinux/semodule-utils/semodule_expand/semodule_expand.c

Purpose: `semodule_expand` expands a base SELinux module package into a kernel binary policy file, optionally choosing policy version and assertion checking.

Important APIs and flow: options are `-V`, `-v`, `-h`, `-c version`, and `-a` to disable assertion checking. It reads a base package with `sepol_module_package_read`, calls `sepol_link_modules` on the base policy to enable optional avrules, creates an output `sepol_policydb_t`, sets `sepol_set_expand_consume_base(handle, 1)`, expands with `sepol_expand_module`, optionally applies `sepol_policydb_set_vers`, and writes with `sepol_policydb_write`.

State and persistence: persistent output is the expanded policy file; transient state includes the sepol handle, module package, policy file wrapper, and output policydb. Dependencies are libsepol module/policydb APIs and filesystem I/O. Risks: `strtol(optarg, NULL, 10)` does not reject trailing junk, output is opened with `"we"` which is glibc-specific, and disabling assertions can hide policy errors. Test signals should cover version bounds, malformed packages, assertion failures, version output, and generated policy readability by libsepol.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_expand/semodule_expand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_link/Makefile -->
# sources/security-integrity/selinux/semodule-utils/semodule_link/Makefile

Purpose: builds and installs the `semodule_link` utility and its manpage.

Important flow: it mirrors the other semodule utility makefiles: install directories default under `/usr`, `CFLAGS` enables warnings as errors, and `LDLIBS` links `-lsepol`. `all` builds `semodule_link` through implicit compilation; `install` installs the binary and `semodule_link.8`, including localized manpages from `LINGUAS`; `clean` removes artifacts.

State and persistence: local outputs are `semodule_link` and object files, while install writes to `$(DESTDIR)$(BINDIR)` and `$(DESTDIR)$(MANDIR)/man8`. Dependencies are libsepol and make/install tooling. Risks: no explicit dependency list beyond implicit make rules, no test target, and warning-as-error sensitivity to compiler updates. Test signals are clean build, DESTDIR install, localized manpage copy behavior, and link-time verification against libsepol.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_link/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_link/semodule_link.c -->
# sources/security-integrity/selinux/semodule-utils/semodule_link/semodule_link.c

Purpose: `semodule_link` links a base module package with one or more additional module packages, optionally writing the linked package.

Important APIs and flow: `load_module` allocates a `sepol_module_package_t` and `sepol_policy_file`, opens a package, reads it with `sepol_module_package_read`, and returns the package. `main` parses `-h`, `-V`, `-v`, and `-o`; it requires a base package and at least one module package, loads all inputs, calls `sepol_link_packages(NULL, base, mods, num_mods, verbose)`, and writes the base package to `-o` via `sepol_module_package_write` if requested.

State and persistence: the base package is mutated in memory by linking; persistent output exists only when `-o` is supplied. Dependencies are libsepol module APIs and filesystem I/O. Risks: the tool prints loading messages unconditionally, so stdout is noisy even without `-v`; output is optional, so a successful link can have no artifact; and `"re"`/`"we"` modes are libc-specific. Test signals should include missing module handling, bad package reads, link conflicts, no-output dry runs, and output package re-read validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_link/semodule_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_package/Makefile -->
# sources/security-integrity/selinux/semodule-utils/semodule_package/Makefile

Purpose: builds and installs `semodule_package` and `semodule_unpackage`.

Important flow: install defaults and warning flags match sibling makefiles. `all` declares both tools, but only `semodule_package: semodule_package.o` is explicitly listed; `semodule_unpackage` relies on make's implicit rules. Installation writes both executables and both manpages, plus optional localized manpages. `clean` removes both binaries and objects.

State and persistence: outputs are local binaries/object files and installed files under `DESTDIR`. Dependencies are libsepol and implicit make rules. Risks: relying on implicit construction for `semodule_unpackage` can be fragile in constrained make environments, `-Werror` increases compiler-version sensitivity, and no tests are declared. Test signals should include both binary builds, DESTDIR installation, manpage presence, and clean idempotence.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_package/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_package/semodule_package.c -->
# sources/security-integrity/selinux/semodule-utils/semodule_package/semodule_package.c

Purpose: `semodule_package` packages a binary policy module with optional file contexts, seusers, user_extra, and netfilter contexts into a libsepol module package.

Important APIs and flow: long options require `-m/--module` and `-o/--outfile`, with optional `-f`, `-s`, `-u`, and `-n`. `file_to_data` opens optional files with `O_CLOEXEC`, stats them, and mmaps non-empty content. `main` enforces single occurrence for each input option, reads the module policy through `sepol_policydb_read(sepol_module_package_get_policy(pkg), mod)`, attaches optional payloads with `sepol_module_package_set_*`, then writes the package with `sepol_module_package_write`.

State and persistence: the persistent output is the packaged `.pp`-style file; optional payloads are mapped read-only and copied into package structures by libsepol. Dependencies are libsepol module APIs, mmap, and filesystem operations. Risks: zero-length optional payloads are silently omitted, `user_extra` setter is gated by pointer presence rather than length, and the error message for write failure prints `argv[1]` instead of the output path. Test signals should cover duplicate options, missing required options, optional payload round trips, empty payload behavior, and malformed module input.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_package/semodule_package.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_package/semodule_unpackage.c -->
# sources/security-integrity/selinux/semodule-utils/semodule_package/semodule_unpackage.c

Purpose: `semodule_unpackage` extracts the policy module and optionally file contexts from a module package.

Important APIs and flow: it expects `ppfile modfile [fcfile]`. It creates a module package and policy-file wrapper, reads the package with `sepol_module_package_read`, writes the contained policy with `sepol_policydb_write(sepol_module_package_get_policy(pkg), out)`, then, if a file-contexts output path was supplied and the package has file contexts, writes `sepol_module_package_get_file_contexts(pkg)` bytes.

State and persistence: outputs are the module file and optional file-contexts file. Dependencies are libsepol module APIs and filesystem I/O. Risks: extra arguments beyond the optional third are ignored, output files are opened with plain `"w"` rather than close-on-exec variants used elsewhere, and file contexts are skipped without warning when absent. Test signals should include valid package round trip, packages without file contexts, bad package input, output write failures, and extra-argument handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/semodule-utils/semodule_package/semodule_unpackage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.github/ISSUE_TEMPLATE/config.yml -->
# sources/storage-engines/badger/.github/ISSUE_TEMPLATE/config.yml

Purpose: configures GitHub issue creation for the Badger repository by disabling blank issues and directing support questions to organization discussions.

Important data: `blank_issues_enabled: false` prevents ad hoc issue creation through the default template, and `contact_links` defines "Badger Community Support" pointing at `https://github.com/orgs/dgraph-io/discussions`.

State and persistence: this is repository metadata consumed by GitHub; it does not affect runtime code. Dependencies are GitHub's issue-template schema. Integration points are the GitHub issue UI and the Dgraph discussions space. Risks: disabling blank issues can improve issue quality but may block reports when no suitable template exists; the support URL is external to this repository and must remain valid. Test signals are repository UI checks and YAML linting.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.github/renovate.json -->
# sources/storage-engines/badger/.github/renovate.json

Purpose: configures Renovate for dependency update automation.

Important data: the config extends `local>dgraph-io/renovate-config`, sets `rangeStrategy` to `widen`, disables Renovate handling of the Go toolchain through both `matchPackageNames` and `matchDepNames`, and lists `go` under `ignoreDeps`.

State and persistence: it is GitHub repository automation configuration; outputs are Renovate PR behavior rather than code artifacts. Dependencies are Renovate's JSON schema and the local Dgraph Renovate preset. Risks: depending on an external local preset can make behavior opaque in this repository; disabling Go updates means `go.mod` toolchain bumps rely on manual or separate processes. Test signals include Renovate config validation, Trunk renovate linting, and verifying that Go version changes are not proposed automatically.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.github/renovate.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/cd-badger.yml -->
# sources/storage-engines/badger/.github/workflows/cd-badger.yml

Purpose: manual GitHub Actions release workflow for building and uploading Badger CLI binaries.

Important flow: `workflow_dispatch` requires `releasetag`. Two build jobs check out that ref, set up Go from `go.mod`, validate that the tag starts with `v`, install build dependencies, run `make badger`, generate SHA256 files, tar the platform binary, and upload artifacts. The final `upload-to-release` job downloads artifacts and uses `gh release upload` with `GITHUB_TOKEN`.

State and persistence: persistent outputs are release assets attached to an existing GitHub release. Dependencies include `actions/checkout`, `actions/setup-go`, `actions/upload-artifact`, `actions/download-artifact`, `gh`, `sha256sum`, `tar`, `make`, and platform runners. Risks: release-tag validation only checks prefix, the arm job does not run `apt-get update`, `gh release upload` assumes the release already exists, and `contents: write` is required. Test signals are dry-run workflow dispatch on a test tag, artifact names/checksums, and actionlint.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/cd-badger.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/ci-badger-bank-tests-nightly.yml -->
# sources/storage-engines/badger/.github/workflows/ci-badger-bank-tests-nightly.yml

Purpose: scheduled and push-triggered stress CI for the Badger bank workload.

Important flow: it runs on `main` and `release/v*` pushes plus a daily cron. The job checks out code, sets up Go from `go.mod`, installs system dependencies and jemalloc, installs the Badger CLI with race detector and jemalloc tags, generates a random key file, and runs `badger bank test` for four hours with encryption. Failure handling distinguishes data-race logs from transaction invariant failures and invokes `badger bank disect` with the decryption key path for diagnosis.

State and persistence: CI writes temporary DB files, key file, and `badgerbanktest.log`; no artifacts are uploaded here. Dependencies are Badger CLI, jemalloc, race builds, and shell utilities. Risks: long duration can consume runner budget, grep filtering around `Moved $5` drives status logic, and the encryption key is stored in a file in the workspace. Test signals are nightly pass/fail, race detector output, and dissection output on invariant failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/ci-badger-bank-tests-nightly.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/ci-badger-bank-tests.yml -->
# sources/storage-engines/badger/.github/workflows/ci-badger-bank-tests.yml

Purpose: pull-request and manual CI for a shorter Badger bank invariant test.

Important flow: on PRs to `main` or `release/v*` excluding docs/images, it checks out code, sets up Go, installs dependencies and jemalloc, installs the race-enabled Badger CLI, creates a `bank` directory, and runs `badger bank test -v --dir=. -d=20m`.

State and persistence: test state is a temporary database under `bank`; no artifacts are configured. Dependencies are the Makefile dependency and jemalloc targets, Badger CLI install, race detector, and GitHub Ubuntu runner. Risks: verbose bank logging can be noisy, the test duration is significant for PR feedback, and it does not run the optional stream/subscriber bank checks. Test signals are transaction invariant failures, race detector failures, and workflow timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/ci-badger-bank-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/ci-badger-tests.yml -->
# sources/storage-engines/badger/.github/workflows/ci-badger-tests.yml

Purpose: core Badger CI for cross-compilation and test execution.

Important flow: it runs manually and on pull requests to `main` or `release/v*`, ignoring docs/images/contrib. The `cross-compile` matrix builds `./...` for Linux, Darwin, Windows, AIX, and Plan 9 combinations. The `badger-tests` job installs dependencies through `make dependency` and runs `make test`.

State and persistence: no release artifacts are produced; outputs are CI logs and test status. Dependencies include `actions/setup-go`, Go module metadata, system package installation, and repository test scripts. Risks: cross-compile catches build tags/import problems but not runtime behavior; `make dependency` uses sudo apt and can dominate runtime; `make test` delegates to `test.sh`, which is outside this item. Test signals are cross-compile success, full Badger test pass, and path-ignore correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/ci-badger-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/ci-dgraph-tests.yml -->
# sources/storage-engines/badger/.github/workflows/ci-dgraph-tests.yml

Purpose: integration CI that tests Badger main against Dgraph main.

Important flow: on pushes to Badger `main`, it checks out `dgraph-io/dgraph`, sets up Go from Dgraph's `go.mod`, installs `gotestsum`, runs `go get github.com/dgraph-io/badger/v4@main`, sets up Node, installs protobuf compiler, regenerates Dgraph protos and checks for clean diff, builds a Dgraph Docker image, builds the Dgraph test binary, cleans test cache/containers, and runs selected Dgraph packages.

State and persistence: outputs are CI logs, Docker images/containers, regenerated files checked by diff, and test binaries. Dependencies include Dgraph repository structure, Go, Node, protobuf, Docker, and Badger module resolution. Risks: `node-version: 16 || 22` is suspicious syntax for `setup-node`, external Dgraph main instability can break Badger CI, and Docker build cost is high. Test signals are Dgraph package tests, proto diff cleanliness, and module resolution to Badger main.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/ci-dgraph-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/trunk.yml -->
# sources/storage-engines/badger/.github/workflows/trunk.yml

Purpose: delegates pull-request code-quality checks to a shared Dgraph Trunk workflow.

Important flow: on PRs to `main`, with read access to contents and write access to actions/checks, the single job uses `dgraph-io/.github/.github/workflows/trunk.yml@main`.

State and persistence: results are GitHub checks created by the reusable workflow. Dependencies are the shared workflow repository, Trunk configuration in `.trunk/trunk.yaml`, and repository permissions. Risks: behavior can change when the shared workflow's `main` branch changes, and write permissions to actions/checks are broader than pure lint jobs need. Test signals include workflow invocation success, Trunk check output, and actionlint validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.github/workflows/trunk.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.trunk/configs/.checkov.yaml -->
# sources/storage-engines/badger/.trunk/configs/.checkov.yaml

Purpose: customizes Checkov security scanning under Trunk.

Important data: `skip-check` disables `CKV_GHA_7`, a GitHub Actions security rule. This likely suppresses findings around mutable action references or workflow dispatch inputs depending on Checkov's rule mapping.

State and persistence: no runtime effect; it influences lint/security check results. Dependencies are Checkov and Trunk's config discovery. Risks: skipping a GHA rule reduces security coverage and should be justified near workflows that use branch refs or dynamic inputs. Test signals are Trunk/Checkov runs confirming only the intended rule is suppressed.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.trunk/configs/.checkov.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.trunk/configs/.markdownlint.json -->
# sources/storage-engines/badger/.trunk/configs/.markdownlint.json

Purpose: configures Markdown lint behavior for Trunk.

Important data: line length is capped at 150 with table exemption; inline HTML, bare URLs, spacing in emphasis, emphasis-as-heading, and first-line-heading rules are disabled.

State and persistence: affects CI/editor lint output only. Dependencies are markdownlint and Trunk. Risks: disabled heading and inline HTML rules make docs more permissive, which can hide style drift; the 150-character cap still catches extreme lines while avoiding many table false positives. Test signals are markdownlint runs and doc formatting PR checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.trunk/configs/.markdownlint.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.trunk/configs/.yamllint.yaml -->
# sources/storage-engines/badger/.trunk/configs/.yamllint.yaml

Purpose: configures YAML linting for repository workflows and config files.

Important data: quoted strings are required only when needed, with `{|}` allowed; duplicate keys are checked; implicit octal values are forbidden.

State and persistence: affects lint results, not runtime behavior. Dependencies are yamllint and Trunk. Risks: permissive quote policy keeps files readable but can miss values that YAML coerces unexpectedly unless covered by other rules. Duplicate-key and octal checks are useful for GitHub Actions reliability. Test signals are yamllint runs over `.github` and `.trunk` files.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.trunk/configs/.yamllint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.trunk/configs/svgo.config.mjs -->
# sources/storage-engines/badger/.trunk/configs/svgo.config.mjs

Purpose: configures SVGO optimization for SVG assets under Trunk.

Important data: exports an ES module config using `preset-default`, overriding `removeViewBox: false`, `sortAttrs: true`, and `removeOffCanvasPaths: true`. Keeping `viewBox` preserves SVG scalability, while sorting attributes stabilizes diffs.

State and persistence: affects formatted/optimized SVG output, not application runtime unless SVGs are regenerated. Dependencies are SVGO v4 via Trunk. Risks: removing off-canvas paths can change intentionally hidden or clipped SVG content; retaining viewBox avoids a common rendering regression. Test signals are SVGO lint/format results and visual review of changed SVG assets.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.trunk/configs/svgo.config.mjs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/.trunk/trunk.yaml -->
# sources/storage-engines/badger/.trunk/trunk.yaml

Purpose: central Trunk configuration for Badger linting, formatting, runtime, and hooks.

Important data: pins Trunk CLI `1.25.0`, uses the official plugin source at `v1.7.4`, enables Go runtime `1.25.5`, ignores generated `pb/*.pb.go`, and enables linters/security tools including two golangci-lint variants, Trivy, Renovate, actionlint, Checkov, gofmt, markdownlint, OSV scanner, image optimizers, shell tools, trufflehog, and yamllint. Actions include announce, pre-push checks, pre-commit formatting, and upgrade notification.

State and persistence: influences local developer hooks and CI lint output. Dependencies are Trunk plugin availability and runtime downloads. Risks: overlapping golangci-lint versions can produce duplicated or inconsistent findings; pinned runtime versions can drift from `go.mod`; security scanners may be noisy without tailored ignores. Test signals are `trunk check`, reusable workflow output, and pre-commit/pre-push behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/.trunk/trunk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/Makefile -->
# sources/storage-engines/badger/Makefile

Purpose: top-level build helper for Badger CLI, tests, jemalloc installation, and system dependencies.

Important flow: `badger` depends on `jemalloc` and delegates to `make -C badger badger`; `test` depends on `jemalloc` and runs `./test.sh`; `jemalloc` downloads, configures, builds, and installs jemalloc 5.3.1 when `/usr/local/lib/libjemalloc.a` is missing; `dependency` installs apt packages needed by CI.

State and persistence: outputs include installed jemalloc in system locations, downloaded temporary sources under `/tmp/jemalloc-temp`, Badger binary artifacts in the `badger` subdir, and test logs. Dependencies are curl, tar, build tools, sudo, apt, and network access. Risks: build targets mutate system state, sudo may block noninteractive environments, network download is not checksum-verified, and test behavior depends on `test.sh`. Test signals are CI dependency install, jemalloc detection, Badger binary build, and full test run.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/backup.go -->
# sources/storage-engines/badger/backup.go

Purpose: implements Badger backup and restore over a length-prefixed protobuf stream of `pb.KVList` records.

Important APIs and flow: `DB.Backup` creates a `Stream`, sets `SinceTs`, and delegates to `Stream.Backup`. `Stream.Backup` defines `KeyToList` to collect versions for a logical key, copy values through the iterator allocator, clear transaction bits, preserve metadata/version/expiry, synthesize a delete marker for `DiscardEarlierVersions`, and stop at deleted or expired entries. `Send` decodes each buffer, tracks maximum version, removes `StreamDone` markers, and writes via `writeTo`. Restore uses `DB.Load`, which reads `uint64` little-endian record sizes, unmarshals `pb.KVList`, and feeds each `pb.KV` to `KVLoader`. `KVLoader` batches into async `batchSetAsync` writes with throttling and threshold-based flushing.

State and persistence: backup writes to any `io.Writer`; restore persists entries into the target DB and advances `orc.nextTxnTs` and `txnMark`. Dependencies include protobuf, Badger stream APIs, `y.Throttle`, and `z.Buffer`. Risks: corrupt or malicious size prefixes can force large allocations; `DB.Load` assumes no concurrent transactions; restore manipulates oracle timestamps directly. Test signals are in `backup_test.go` for full, incremental, deletion/expiry/discard, metadata-bit, and timestamp restoration behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/backup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/backup_test.go -->
# sources/storage-engines/badger/backup_test.go

Purpose: verifies backup/restore correctness across disk and memory modes, incremental streams, metadata handling, and transaction timestamp restoration.

Important tests: `TestBackupRestore1/2/3` write data, back it up, load it into new DBs, and assert keys, values, versions, user metadata, and `nextTs`. `TestBackup` checks basic backup in disk and in-memory configurations. `TestBackupLoadIncremental` applies deletes, expired entries, and discard-earlier-version entries between incremental backups, then checks restored historical/deleted metadata. `TestBackupBitClear` ensures backup/restore clears value-pointer bits when source and destination value thresholds differ.

State and persistence: tests create temp directories/files and remove them through helpers; they exercise both on-disk state and in-memory DB mode. Dependencies are `testing`, `require`, `pb.KV`, and Badger test helpers. Risks: randomized selection uses package-level `randSrc`, so exact updated indexes vary; some tests print lengths to stdout; concurrent restore assumptions are not stress-tested. Test signals are strong for functional backup semantics but weaker for corrupted backup input, huge record sizes, writer failures, and concurrent restore misuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/backup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/Makefile -->
# sources/storage-engines/badger/badger/Makefile

Purpose: builds the Badger command-line binary for the current or supplied GOOS/GOARCH.

Important flow: defaults read `GOOS` and `GOARCH` from `go env`; `all` depends on `badger`; the `badger` target runs `go build --tags=jemalloc -o badger-$(GOOS)-$(GOARCH) .`.

State and persistence: output is a platform-named binary in the `badger` CLI directory. Dependencies are Go, module dependencies, and jemalloc build tags/library availability. Risks: always building with `jemalloc` tags can fail if the environment lacks the expected native library; output naming is platform-specific and release workflows assume these names. Test signals are cross-compilation workflow, release build workflow, and local `make -C badger badger`.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/backup.go -->
# sources/storage-engines/badger/badger/cmd/backup.go

Purpose: implements the `badger backup` CLI command over the library `DB.Backup` API.

Important flow: Cobra registers flags `--backup-file/-f` and `--num-versions/-n`. `doBackup` opens Badger with `DefaultOptions(sstDir)`, `WithValueDir(vlogDir)`, and `WithNumVersionsToKeep(math.MaxInt32)` unless the flag narrows retention. It creates the backup file, wraps it in a 64 MiB buffered writer, runs `db.Backup(bw, 0)`, flushes, fsyncs the file, and closes it.

State and persistence: persistent output is the backup file; source DB is opened read-write by default through `badger.Open`. Dependencies are root command directory validation, Badger options, filesystem create/sync, and buffered I/O. Risks: source DB is not opened read-only, partial files can remain on failure, and close errors can mask earlier sync/flush context only by direct return order. Test signals should cover CLI backup/restore round trips, num-version effects, write permission failures, and backup over separate `--vlog-dir`.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/backup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/bank.go -->
# sources/storage-engines/badger/badger/cmd/bank.go

Purpose: implements the `badger bank` Jepsen-inspired stress workload and a `disect` diagnostic command for transaction invariant failures.

Important APIs and flow: bank state is `account:<id>` keys with initial balance 100. `moveMoney` updates two accounts transactionally; `seekTotal` validates the invariant that total balance equals `numAccounts * initialBal`; `runTest` initializes accounts with `WriteBatch`, starts concurrent transfer goroutines, a read-check goroutine, and optional stream/subscriber verification DBs. `runDisect` opens the DB read-only in managed mode, scans min/max versions, binary-searches for the first invalid timestamp with `findFirstInvalidTxn`, and prints account diffs via `compareTwo`.

State and persistence: test mutates a Badger DB under `--dir`, optionally encrypted; stream/subscriber checks create temp DBs. Dependencies are Cobra, Badger transactions, streaming, subscriptions, protobuf, atomics, and timers. Risks: global flags/state make tests order-sensitive, logging the encryption key is intentional but sensitive, random account selection uses global `rand`, and `disect` spelling is part of the CLI. Test signals include CI bank workflows, race-enabled runs, optional stream/subscriber modes, and dissection output after invariant failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/bank.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/bench.go -->
# sources/storage-engines/badger/badger/cmd/bench.go

Purpose: defines the `badger benchmark` parent Cobra command.

Important flow: `benchCmd` provides command metadata, and `init` registers it under `RootCmd`. Subcommands in sibling files attach read, write, and table-picking benchmarks to this parent.

State and persistence: this file has no direct persistence; it is command registration glue. Dependencies are Cobra and global `RootCmd`. Risks: the parent command has no `RunE`, so invoking it without subcommands depends on Cobra help/default behavior; subcommand initialization order relies on Go package init semantics. Test signals are CLI help output and command tree tests confirming `benchmark read`, `benchmark write`, and `benchmark picktable` are registered.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/bench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/flatten.go -->
# sources/storage-engines/badger/badger/cmd/flatten.go

Purpose: implements `badger flatten`, which forces LSM compactions to consolidate tables into one level.

Important flow: flags configure compactor worker count, number of versions, encryption key file, and compression type. `flatten` normalizes nonpositive version count to `math.MaxInt32`, reads an encryption key with `getKey`, validates compression type `0..2`, opens Badger with compactions disabled (`WithNumCompactors(0)`), explicit cache sizes, compression and encryption options, then calls `db.Flatten(fo.numWorkers)`.

State and persistence: mutates the DB's LSM table layout and may rewrite SSTables. Dependencies include Badger `Flatten`, options compression enum, and key-file reading from `rotate.go`. Risks: it opens the DB read-write and is best run without concurrent writers; high worker counts increase compaction pressure; invalid compression is rejected but empty key path means plaintext mode. Test signals should include post-restore flatten workflows, encrypted DB opening, compression combinations, and no-concurrent-write operational tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/flatten.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/info.go -->
# sources/storage-engines/badger/badger/cmd/info.go

Purpose: implements `badger info`, a health and inspection command for manifests, value logs, SSTables, keys, histograms, and discard stats.

Important APIs and flow: flags control table display, histogram, key listing, prefix filter, lookup, metadata, history, internal keys, read-only/truncate, encryption key, checksum verification mode, discard-file parsing, and external magic. `handleInfo` builds Badger options, optionally prints discard stats, calls `printInfo` to replay the manifest and compare disk files, opens the DB, and conditionally calls table, histogram, key listing, and lookup routines. `printInfo` reports manifest truncation, missing/extra/empty files, value-log size, level sizes, and abnormalities.

State and persistence: usually read-only, but `--read-only=false` and truncate options can allow recovery-style opens. Dependencies are Badger manifest/table APIs, filesystem walking, hex decoding, humanize, and options checksum enums. Risks: `checksumVerificationMode` accepts `"tableAndblock"` but flag help says `tableAndBlock`; invalid mode calls `os.Exit(1)` instead of returning an error; mean compression ratio divides by table count. Test signals should cover manifest replay, key lookup/history, prefix decoding failures, discard stats, and abnormal file reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/pick_table_bench.go -->
# sources/storage-engines/badger/badger/cmd/pick_table_bench.go

Purpose: implements `badger benchmark picktable`, a benchmark for iterator table selection logic.

Important APIs and flow: it opens Badger managed, derives table boundaries from `db.Tables`, constructs mock in-memory tables with `table.NewTableBuilder` and `OpenInMemoryTable`, initializes a local `levelHandler`, samples keys using `getSampleKeys`, and runs `testing.Benchmark(BenchmarkPickTables)`. The local `iteratorOptions`, `compareToPrefix`, and `pickTables` mirror production iterator logic with prefix and `SinceTs` filtering.

State and persistence: reads an existing DB and creates transient in-memory tables; optional CPU profile writes to a file. Dependencies are Badger table APIs, testing benchmark harness, pprof, and read-benchmark key sampling. Risks: the copied production logic can drift from real iterator code, global `keys` and `handler` make benchmark state package-global, and generated mock table ranges are synthetic. Test signals are benchmark output, CPU profile generation, and periodic diff checks against production `levelHandler.pickTables`.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/pick_table_bench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/read_bench.go -->
# sources/storage-engines/badger/badger/cmd/read_bench.go

Purpose: implements `badger benchmark read`, including random key reads and full-scan mode.

Important APIs and flow: flags configure goroutines, duration, sample size, keys-only mode, read-only open, full scan, and cache sizes. `readBench` opens Badger managed with cache settings, then either scans all entries with an iterator at `math.MaxUint64` or calls `readTest`. `getSampleKeys` uses a Badger stream to collect first-version keys into memory, stops via context cancellation when enough keys are sampled, then shuffles. Worker goroutines repeatedly call `lookupForKey`, which uses a key iterator and reads up to ten versions.

State and persistence: read-only by default, no DB mutations; global atomics track bytes and entries read. Dependencies are Badger streaming, iterators, protobuf, `z.Closer`, and random sampling. Risks: `keysOnly` flag is registered but not used by lookup logic, package-global counters are shared with write benchmarks, and empty DB handling is only in `readTest`. Test signals are benchmark throughput logs, full-scan counts, sampled-key counts, and cache-size sensitivity.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/read_bench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/restore.go -->
# sources/storage-engines/badger/badger/cmd/restore.go

Purpose: implements the `badger restore` CLI command over `DB.Load`.

Important flow: flags configure backup file path and max pending writes. `doRestore` first rejects restoring into a DB directory that already has a manifest. It opens a new Badger DB with `WithNumVersionsToKeep(math.MaxInt32)` and `WithValueDir(vlogDir)`, opens the backup file, and calls `db.Load(f, maxPendingWrites)`.

State and persistence: creates a new Badger DB under `--dir`/`--vlog-dir` and populates it from backup stream data. Dependencies are root command directory validation, filesystem stat/open, Badger open, and backup stream format. Risks: only manifest presence is checked, so non-empty directories without a manifest may still be used; partial restore can leave a DB behind on failure; restore is not designed for concurrent transactions. Test signals are backup/restore CLI round trips, existing-manifest rejection, corrupted backup input, and max-pending-writes behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/root.go -->
# sources/storage-engines/badger/badger/cmd/root.go

Purpose: defines the root `badger` Cobra command and shared directory flags.

Important flow: global `sstDir` and `vlogDir` hold persistent flag values. `RootCmd` uses `PersistentPreRunE: validateRootCmdArgs`; flags `--dir` and `--vlog-dir` are registered globally. Validation skips help commands, requires `--dir`, and defaults `vlogDir` to `sstDir` when omitted. `Execute` runs the command and exits with status 1 on error.

State and persistence: shared global state feeds all subcommands that open Badger databases. Dependencies are Cobra, OS exit behavior, and subcommand init registration. Risks: global variables make tests order-sensitive; help-command detection checks `strings.HasPrefix(cmd.Use, "help ")`, which depends on Cobra internals; commands that do not need a DB still require `--dir` unless explicitly structured as help. Test signals are CLI error behavior, help paths, default vlog-dir propagation, and subcommand flag inheritance.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/root.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/rotate.go -->
# sources/storage-engines/badger/badger/cmd/rotate.go

Purpose: implements `badger rotate`, which rewrites Badger key-registry metadata to rotate, remove, or enable encryption keys.

Important flow: flags provide old and new key paths. `doRotate` reads the old key with `getKey`, opens the key registry read-only for the DB directory with a rotation duration, reads the new key, updates options, and writes the key registry with `badger.WriteKeyRegistry`. `getKey` returns empty bytes for an empty path, enabling plaintext transitions, otherwise reads the entire file.

State and persistence: persistent mutation is the key registry in `sstDir`; DB data remains readable only with the new registry/key combination. Dependencies are Badger key-registry APIs, filesystem key reads, and root directory validation. Risks: key files are read whole without size validation, globals make tests order-sensitive, and plaintext/encrypted transitions depend on empty path semantics. Test signals in `rotate_test.go` cover wrong-key failure, encrypted-to-encrypted rotation, encrypted-to-plaintext, and plaintext-to-encrypted.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/rotate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/rotate_test.go -->
# sources/storage-engines/badger/badger/cmd/rotate_test.go

Purpose: validates the `rotate` command's encryption key transitions.

Important tests: `TestRotate` creates a 32-byte key, opens and closes an encrypted DB, verifies wrong old-key rotation fails with `ErrEncryptionKeyMismatch`, rotates to a second key, verifies DB opens with the new key, then rotates to plaintext and verifies an empty encryption key opens the DB. `TestRotatePlainTextToEncrypted` creates a plaintext DB with data, rotates it to an encrypted key, verifies opening without the key fails, then opens with the key and checks data is still present.

State and persistence: tests use temp DB directories and temp key files; global `oldKeyPath`, `newKeyPath`, and `sstDir` are mutated. Dependencies are Badger options, key registry behavior, random key generation, and testify. Risks: globals are not restored, so parallel tests could interfere; key files are not fsynced before use; random keys are non-deterministic. Test signals are strong for expected transition paths but do not cover malformed key lengths or missing key files.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/rotate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/stream.go -->
# sources/storage-engines/badger/badger/cmd/stream.go

Purpose: implements `badger stream`, which streams an input DB either into a new DB with selected options or into a backup file.

Important flow: flags configure output directory, output file, compression type, version retention, read-only input, and encryption key file. `stream` opens the input DB managed at `math.MaxUint64`, validates compression, and if `--out` is set checks that the target directory is absent or empty before calling `inDB.StreamDB(outOpt)`. If `--out` is absent and an output file is set, it calls `stream.Backup(f, 0)`.

State and persistence: may create a new output DB or a backup file; input is read-only by default. Dependencies are Badger streaming, options compression enum, file/directory checks, and `getKey`. Risks: the flag registration for `outFile` uses an empty long name with shorthand `f`, which is unusual; backup file is opened without truncating existing content; no explicit error is returned if neither output target is set. Test signals should include stream-to-empty-dir, non-empty-dir rejection, compression validation, encrypted DB streaming, and backup-file truncation expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/write_bench.go -->
# sources/storage-engines/badger/badger/cmd/write_bench.go

Purpose: implements `badger benchmark write`, a configurable write workload for Badger performance and stress testing.

Important APIs and flow: flags control key/value sizes, number of keys, sync writes, close compaction, sorted versus random writes, value thresholds, versions, caches, value-log settings, encryption, conflict detection, compression, TTL, periodic `DropAll`, `DropPrefix`, and value-log GC. `writeRandom` writes random keys through `NewManagedWriteBatch` at version 1. `writeSorted` uses `NewStreamWriter` and protobuf KV buffers split into streams. `writeBench` opens Badger managed with chosen options, starts stats/drop/GC goroutines under a `z.Closer`, runs the selected writer, then prints levels.

State and persistence: mutates the DB under `--dir`, can drop all data or prefixes, run value-log GC, and produce large SST/vlog files. Dependencies are Badger managed writes, stream writer, GC/drop APIs, atomics, filesystem walking, and humanize. Risks: `writeRandom` creates one batch for all keys and can grow large, counters/files slices are package-global, periodic destructive operations are easy to enable, and key size/drop-prefix assumptions can panic for small key sizes. Test signals are benchmark output, DB reopen/verification, GC/drop logs, and race/stress runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/cmd/write_bench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/badger/main.go -->
# sources/storage-engines/badger/badger/main.go

Purpose: entrypoint for the Badger CLI binary.

Important flow: starts an HTTP debug server loop trying ports 8080 through 9079 on `0.0.0.0`, registers zPages trace handling at `/z`, sets block profile rate and `GOMAXPROCS(128)`, checks jemalloc allocation through `z.CallocNoRef`, prints allocator stats, runs `cmd.Execute`, then prints remaining allocated bytes and leak details.

State and persistence: no database state directly; it opens a debug network listener and writes diagnostics to stdout. Dependencies include net/http/pprof, OpenTelemetry zpages, Ristretto allocator utilities, Cobra command package, and go-humanize. Risks: binding pprof on all interfaces exposes debug endpoints when the CLI is run in shared environments, the goroutine loops forever on busy ports, and hard-coded `GOMAXPROCS(128)` overrides runtime defaults. Test signals should include CLI startup in port-conflict environments, pprof exposure review, and leak-report behavior at process end.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/badger/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/batch.go -->
# sources/storage-engines/badger/batch.go

Purpose: implements `WriteBatch`, a high-throughput helper for batching many writes into Badger transactions.

Important APIs and flow: `DB.NewWriteBatch` rejects managed mode, while `newWriteBatch` initializes a transaction and throttle. `SetMaxPendingTxns` replaces the throttle. `Set`, `SetEntry`, `Delete`, `SetEntryAt`, `DeleteAt`, `Write`, and `WriteList` feed entries into the current transaction. `handleEntry` commits and retries when `ErrTxnTooBig` occurs. `commit` checks stored errors and finished state, throttles pending commits, calls `txn.CommitWith`, creates a new transaction, and propagates callback errors through an atomic `err`. `Flush` commits remaining writes, discards the transaction, waits on the throttle, and returns accumulated errors. `Cancel` finishes pending work and discards without requiring flush.

State and persistence: writes persist through Badger's normal request path; in-memory state tracks current transaction, pending commit throttle, errors, and finished flag. Dependencies include protobuf decoding, `z.Buffer`, `y.Throttle`, and transaction internals. Risks: callers must call `Flush` or `Cancel`, `SetEntryAt` requires managed mode, and post-finish calls return commit-after-finish errors. Test signals in `batch_test.go` cover high-volume writes, deletes, empty flushes, flush-after-finish, and managed error paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/batch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/batch_test.go -->
# sources/storage-engines/badger/batch_test.go

Purpose: verifies `WriteBatch` behavior under large write volume, deletes, empty batches, repeated flush/cancel, and managed-mode error paths.

Important tests: `TestWriteBatch` writes 50,000 keys and deletes 1,000, then iterates to confirm remaining keys/values. It runs disk mode and skips in-memory mode with a TODO. `TestEmptyWriteBatch` confirms empty flushes do not deadlock in normal and managed variants. `TestFlushPanic` checks flush after flush and flush after cancel return `y.ErrCommitAfterFinish`. `TestBatchErrDeadlock` checks a managed write batch with timestamp 0 returns an error rather than deadlocking.

State and persistence: tests create temp DBs and exercise on-disk write path; value threshold is lowered to avoid too many open files. Dependencies are Badger test helpers, `require`, and internal `y` errors. Risks: skipped in-memory mode leaves a known coverage gap; high-volume test can be slow or file-descriptor sensitive. Test signals are good for lifecycle and deadlock regressions, weaker for async callback error ordering and throttle resizing.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/batch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/changes.sh -->
# sources/storage-engines/badger/changes.sh

Purpose: generates a release/change description from git log entries and rewrites issue references to fully qualified GitHub links.

Important flow: Bash script with `set -e` reads `GHORG` and `GHREPO` defaults, prints a preamble containing the script source and invocation, then runs `git log --oneline --reverse "$@"` and pipes through two `sed` expressions: one removes short hashes, the other rewrites `#123`-style references to `org/repo#123`.

State and persistence: writes only to stdout. Dependencies are Bash, git, sed, and a Git history range supplied by arguments. Risks: embedding the whole script in output is verbose, issue-reference regex may rewrite patterns in unintended contexts, and unquoted `${@:1}` in the invocation display can misrepresent arguments with spaces. Test signals are sample git ranges, issue-reference rewrite checks, and shellcheck/shfmt.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/changes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/compaction.go -->
# sources/storage-engines/badger/compaction.go

Purpose: defines key-range and compaction-status bookkeeping used to prevent overlapping Badger compactions.

Important APIs and flow: `keyRange` stores left/right keys, infinity marker, and approximate size; methods detect empty ranges, stringify, compare equality, extend bounds, and test overlap using Badger key comparison. `getKeyRange` computes an inclusive range over one or more SSTables, preserving all versions by constructing left with `math.MaxUint64` timestamp and right with timestamp 0. `levelCompactStatus` tracks active ranges and deletion size per level. `compactStatus` guards per-level statuses and active table IDs; `compareAndAdd` refuses overlapping this/next-level ranges, records ranges and tables, and accumulates deletion size; `delete` removes ranges/table IDs and fatal-errors if expected state is missing.

State and persistence: state is in-memory scheduler bookkeeping; actual compaction persistence occurs elsewhere. Dependencies are `table.Table`, `y.CompareKeys`, and compaction definitions from sibling files. Risks: incorrect overlap logic can allow corrupting concurrent compactions or over-serialize work; `log.Fatal` in `delete` exits the process on bookkeeping mismatch; TODOs call out missing tests. Test signals should cover overlap boundaries, infinite/empty ranges, table ID tracking, and concurrent compaction scheduling.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/compaction.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/db.go -->
# sources/storage-engines/badger/db.go

Purpose: central Badger database lifecycle and coordination file. It defines `DB`, validates options, opens/closes persistent state, coordinates write requests, memtable flushing, value-log GC, compactions, streaming, drop operations, namespace bans, cache control, sequences, and metadata inspection.

Important APIs and flow: `Open` validates options, creates/locks directories, opens the manifest, initializes caches, key registry, memtables, level controller, value log, oracle, publisher, threshold listener, write loop, memtable flusher, compaction workers, value-log GC, and metrics goroutines. `Close` blocks writes, drains writes, stops publishers/cache monitor/GC/flushers/compactors, optionally compacts L0, closes value log, levels, manifest, registry, caches, oracle, and directory locks, then fsyncs directories. `sendToWriteCh`, `doWrites`, `writeRequests`, and `writeToLSM` form the serialized write pipeline from entries to value log, memtable, subscribers, and callbacks. `ensureRoomForWrite`, `handleMemTableFlush`, and `flushMemtable` rotate full memtables into L0 tables. `RunValueLogGC`, `Flatten`, `DropAll`, `DropPrefix`, `StreamDB`, `Subscribe`, `GetSequence`, `BanNamespace`, `Tables`, `Levels`, `Ranges`, and `CacheMaxCost` expose major public behaviors.

State and persistence: persistent state spans manifest, SSTables, value logs, WAL-backed memtables, key registry, LOCK files, banned namespace internal keys, and directory fsyncs. In-memory state includes current/immutable memtables, oracle timestamps/watermarks, caches, level controller, value-log threshold, subscriber queues, request pool, and closers. Dependencies are broad: filesystem locking, manifest/value-log/table packages, Ristretto caches, protobuf, expvar metrics, allocator pool, and internal `y`/`z` concurrency helpers.

Risks: concurrency ordering is delicate around write blocking, memtable flush channel capacity, `DropAll`/`DropPrefix` read hazards, and shutdown. Some cleanup paths assume caches are non-nil. `CacheMaxCost` dereferences caches without nil checks when `db` exists. `DropPrefix` and `Flatten` are operationally invasive. `Sync` documents partial-loss scenarios. Test signals should cover open/close recovery, directory locking, read-only/in-memory modes, write batching, memtable flush retries, value-log GC rejection, drop operations, stream DB, namespace bans, sequences, cache resizing, and race tests for close/drop/write interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/db.go -->
