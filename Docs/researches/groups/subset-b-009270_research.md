# subset-b-009270 research

Grouped research report for vLLM kdevops workflow configuration and lcov packaging, CI, and helper scripts. Each section preserves the exact source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/vllm/Kconfig -->
# sources/test-tools/kdevops/workflows/vllm/Kconfig

Purpose: Kconfig menu for the kdevops vLLM workflow. It exposes deployment choices for latest Docker, official Production Stack Helm chart, and bare-metal/systemd deployments, then emits selected values to YAML for Ansible and Helm automation.

Important APIs/types/functions: Kconfig `choice`, `config`, `if`, `depends on`, `default`, `range`, `help`, and kdevops-specific `output yaml`. Key symbols include `VLLM_DEPLOYMENT_TYPE`, `VLLM_K8S_MINIKUBE`, `VLLM_K8S_EXISTING`, model identity fields, `VLLM_CLI_VERSION_OVERRIDE`, `VLLM_ENGINE_IMAGE_TAG`, CPU/GPU resource settings, router/observability toggles, benchmark settings, Production Stack chart settings, and bare-metal runtime/systemd settings.

Control flow: the whole file is gated by `KDEVOPS_WORKFLOW_ENABLE_VLLM`. The first choice selects one deployment mode. Kubernetes-specific options appear only for Docker or Production Stack. Version defaults are chosen from CLI environment override state, Production Stack CPU mode, and stable defaults. Production Stack and bare-metal subsections are conditionally enabled by their deployment choice, and nested options such as LMCache, router routing algorithm, monitoring ports, autoscaling bounds, custom values file, and declared-host GPU shape appear only when their parent booleans are enabled.

State/persistence behavior: the file does not execute deployment itself; it persists user-selected and computed configuration into generated YAML. Defaults encode operational state assumptions, especially CPU inference for libvirt, GPU count zero under CPU mode, memory guidance for Production Stack, Helm namespace/release names, model defaults, and benchmark result directory `/data/vllm-benchmark`.

Dependencies/integration: depends on surrounding kdevops symbols such as `LIBVIRT`, `TERRAFORM`, `USE_LIBVIRT`, `KDEVOPS_USE_DECLARED_HOSTS`, and `LIBVIRT_MEM_*`. Generated YAML feeds the vLLM Ansible playbook and templates that deploy Kubernetes, Helm, Docker, Minikube, LMCache, observability, and bare-metal services.

Risks/test signals: several version help strings are time-sensitive and may drift from actual vLLM releases. `VLLM_VERSION_CUSTOM` defaults the image tag to `v0.10.2` instead of accepting a custom prompt value, so custom-version semantics likely depend on external override paths. CPU inference defaults use `latest`, which can reduce reproducibility. Test signals are kconfig parsing, generated YAML shape, menu visibility under each backend, and successful downstream Ansible/Helm deployment with CPU and GPU configurations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/vllm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/vllm/Makefile -->
# sources/test-tools/kdevops/workflows/vllm/Makefile

Purpose: Makefile entry points for the kdevops vLLM workflow. It wraps `playbooks/vllm.yml` with focused tag sets for deploy, benchmark, monitor, teardown, cleanup, results collection, status inspection, quick testing, and help output.

Important APIs/types/functions: GNU make targets, `HELP_TARGETS += vllm-help-menu`, `$(Q)` quiet prefix, recursive `$(MAKE)`, `ansible-playbook`, `ansible`, `kubectl`, `helm`, `docker`, `grep`, `ps`, and helper scripts `scripts/vllm-status-summary.py` and `scripts/vllm-quick-test.sh`.

Control flow: `vllm` and `vllm-deploy` run the same Ansible playbook with data partition, vars, dependency, Docker config, and deploy tags. Benchmark, monitor, teardown, cleanup, and result targets use narrower tag lists. Cleanup variants pass extra JSON variables to remove binaries or purge data. `vllm-status` emits diagnostic sections and runs remote shell checks against all hosts. `vllm-status-simplified` pipes detailed status through a Python summarizer. `vllm-help-menu` prints the workflow command list.

State/persistence behavior: most targets mutate remote or guest state through Ansible. They depend on `extra_vars.yaml`, inventory `hosts`, and deployment artifacts such as `/data/vllm/prod-stack-values.yaml`, Kubernetes namespaces, Helm releases, Docker images, and benchmark result directories. The Makefile itself stores no durable state.

Dependencies/integration: integrates the vLLM Kconfig/YAML output with `playbooks/vllm.yml`. It assumes baseline/dev inventory groups, Ansible access to nodes, Kubernetes and Helm commands on target nodes, optional Minikube, Docker, and the support scripts named above.

Risks/test signals: status commands suppress many errors with `2>/dev/null || echo`, making them useful for humans but weak for CI gating. Namespace checks are hard-coded to `vllm-system`, which can diverge from `VLLM_HELM_NAMESPACE`. Test signals include `make vllm-help-menu`, dry or targeted Ansible tag runs, `make vllm-status-simplified`, quick API test success, and cleanup idempotence.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/vllm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/.github/dependabot.yml -->
# sources/test-tools/lcov/.github/dependabot.yml

Purpose: Dependabot configuration for lcov GitHub Actions dependencies. It asks Dependabot to scan workflow actions in the repository root and open weekly update pull requests.

Important APIs/types/functions: Dependabot schema `version: 2`, `updates`, `package-ecosystem: github-actions`, `directory: /`, `schedule.interval: weekly`, labels, and commit-message customization.

Control flow: GitHub Dependabot reads this file, checks action references under `.github/workflows`, and creates PRs when newer versions are available. The configured commit message prefix is `Actions` with scope included, and PRs are labeled `enhancement`.

State/persistence behavior: no runtime state in the repository beyond Dependabot-authored branches and pull requests. The schedule is weekly and not pinned to a day/time here, so GitHub chooses the exact run timing.

Dependencies/integration: integrates with GitHub's hosted Dependabot service and the workflow files that use actions such as checkout, upload-artifact, codespell, and release creation.

Risks/test signals: only GitHub Actions dependencies are covered; system packages, Perl CPAN modules, and project scripts are outside this update lane. Test signals are Dependabot successfully parsing the config and opening scoped action update PRs.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/.github/workflows/codespell.yml -->
# sources/test-tools/lcov/.github/workflows/codespell.yml

Purpose: GitHub Actions workflow that enforces spelling cleanliness with codespell on pull requests, pushes, weekly scheduled runs, and manual dispatch.

Important APIs/types/functions: workflow triggers, restricted `permissions: contents: read`, `actions/checkout@v6`, and `codespell-project/actions-codespell@v2` with `ignore_words_list`.

Control flow: a single `codespell` job runs on `ubuntu-24.04`, checks out the repository, and invokes the codespell action. Ignored tokens are documented inline as man-page markup, abbreviations, or variable names that should not fail the run.

State/persistence behavior: no repository state is modified. The only persisted outputs are GitHub Actions logs and check results associated with the commit or PR.

Dependencies/integration: integrates with GitHub Actions and the external codespell action. It complements the local `make checkstyle` Perl formatting lane by catching spelling issues across the tree.

Risks/test signals: ignore words must remain lowercase and comma-separated, as noted in the file. New project-specific terms may need additions or the job can produce false positives. The primary signal is the job status on PRs and scheduled weekly runs.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/.github/workflows/rpm_action.yml -->
# sources/test-tools/lcov/.github/workflows/rpm_action.yml

Purpose: GitHub Actions workflow that builds lcov RPM artifacts and publishes them on version-tagged releases.

Important APIs/types/functions: GitHub triggers for pushes to `main`/`master`, tags matching `v*`, pull requests, and manual dispatch; `permissions: contents: write`; `actions/checkout@v6`; apt packages `rpm`, `devscripts`, `equivs`, Sphinx packages, Perl, and git; `make rpms`; `$GITHUB_OUTPUT`; and `softprops/action-gh-release@v3`.

Control flow: the job checks out full history, installs build dependencies, runs `make rpms`, derives a version from the tag name or `git describe --tags --always`, and only on `refs/tags/v*` creates a GitHub release containing `*.noarch.rpm` and `*.src.rpm`.

State/persistence behavior: PR and branch runs only build artifacts in the runner workspace. Tag runs persist release assets through GitHub Releases. The source tree is not modified in CI.

Dependencies/integration: delegates package logic to the top-level lcov `Makefile`, which builds docs, tarball, and RPMs through `rpmbuild` and `rpm/lcov.spec`. Requires enough git history for version derivation.

Risks/test signals: `contents: write` is needed only for release creation, so non-tag runs still carry broader permissions than required. The `ubuntu-latest` runner may shift over time and affect package availability. Signals are successful `make rpms`, expected RPM filenames in the workspace, and release upload success for `v*` tags.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/.github/workflows/rpm_action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/.github/workflows/run_test_suite.yml -->
# sources/test-tools/lcov/.github/workflows/run_test_suite.yml

Purpose: GitHub Actions workflow for lcov regression testing across selected GCC versions and Ubuntu runners, including install/uninstall verification and artifact capture.

Important APIs/types/functions: workflow triggers, read-only permissions, matrix strategy, `actions/checkout@v6`, apt package installation, CPAN install of `Memory::Process`, optional Ubuntu `resolute` repository for GCC 16, systemwide compiler symlink replacement, `make install`, `make uninstall`, `make check`, and `actions/upload-artifact@v7`.

Control flow: the matrix covers GCC 9, 10, 14, and 16 on Ubuntu 24.04, skipping 11-13 as equivalent coverage. Each job installs Perl, LLVM, Python, Sphinx, and GD dependencies; adds a future Ubuntu repo for GCC 16; rewires `/usr/bin` compiler and gcov command symlinks to the selected version; stages installation under `ROOT` with `PREFIX=/usr CFG_DIR=/etc`; uninstalls and diffs the staging root for leftovers; runs the test suite; then uploads `tests/test.log` and the whole `tests` directory.

State/persistence behavior: runner-local package installs and `/usr/bin` symlink changes are ephemeral. The staged install tree `ROOT` is created and expected to be empty after uninstall. Test logs and shrapnel are persisted as artifacts.

Dependencies/integration: exercises the project Makefile install/uninstall/check targets, docs build dependencies, gcov behavior across compiler versions, Perl modules documented in README, and tests under `tests`.

Risks/test signals: modifying system compiler symlinks is broad but isolated to the runner. GCC 16 depends on a future Ubuntu repository and may be fragile. The uninstall check is a strong signal for packaging hygiene; `make check` plus uploaded logs are the main behavioral test signals.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/.github/workflows/run_test_suite.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/Makefile -->
# sources/test-tools/lcov/Makefile

Purpose: primary build, install, package, style, test, and release driver for lcov. It builds documentation, installs executable tools, support scripts, libraries, man/html docs, examples, tests, configuration, creates tarballs/RPMs, runs regression tests, and finalizes releases.

Important APIs/types/functions: GNU make variables and targets; `bin/get_version.sh`; `bin/fix.pl`; `bin/copy_dates.sh`; `install`, `rm`, `rmdir`, `mktemp`; recursive `make` in `docs`, `tests`, and `example`; `rpmbuild`; `git`; and `bin/checkstyle.sh`. Key variables include `VERSION`, `RELEASE`, `FULL`, `TOOL_NAME`, interpreter paths, `PREFIX`, `DESTDIR`, `CFG_DIR`, `BIN_DIR`, `LIB_DIR`, `SHARE_DIR`, `EXES`, `SCRIPTS`, `LIBS`, `MANPAGES`, and coverage database paths.

Control flow: `all` prints target information. `doc` builds man and HTML docs. `install` depends on docs, installs tools and scripts, rewrites version/path metadata through `fix.pl`, installs libraries and docs, copies cleaned examples/tests, fixes executable bits, and installs `lcovrc`. `uninstall` removes installed files and attempts to prune empty directories. `dist` builds a tarball plus binary/source RPMs; the tarball copies distribution content, preserves dates, cleans generated files, rewrites version/date metadata, generates `CHANGES`, and archives with root ownership. `rpms` builds from the tarball through `rpmbuild`. `check` runs tests, optionally twice with coverage and forced parallel mode. `checkstyle` discovers Perl files/modules, runs `checkstyle.sh`, and optionally updates files from `.tdy` output. `release` validates command-line `VERSION`, clean git state, absent tag, then updates dates/version, commits, and tags.

State/persistence behavior: generates docs under `docs/_build`, packages in the repository root, temporary RPM/tar trees under `TMP_DIR`, test logs under `tests`, optional coverage databases and HTML report, `.tdy`/`.orig` style files, installed trees under `DESTDIR`, and release commits/tags. It enforces absolute `DESTDIR + PREFIX` at parse time.

Dependencies/integration: central integration point for lcov runtime scripts, Perl library, docs, RPM spec, examples, tests, CI workflows, and release tooling. CI workflows call `make install`, `make uninstall`, `make check`, and `make rpms`.

Risks/test signals: `TMP_DIR := $(shell mktemp -d)` runs at make parse time and may create unused temporary directories for simple targets. `uninstall` loops over `man/*.$section` while install uses built docs, which may miss installed manpage removal unless a matching `man` directory exists. `SCRIPTS` uses `ls scripts`, so an absent scripts directory or unusual filenames can affect parsing. Strong signals are successful staged install/uninstall with empty `ROOT`, `make check`, RPM creation, and release dry review before pushing.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/checkstyle.sh -->
# sources/test-tools/lcov/bin/checkstyle.sh

Purpose: Bash helper that checks Perl source formatting with `perltidy`, either for the full file or only for style regressions introduced since a git baseline.

Important APIs/types/functions: shell functions `realpath`, `relpath`, `die`, and `report`; environment variables `PERLTIDY`, `PERLTIDYRC`, `GITBASE`, and `MODE`; commands `mktemp`, `trap`, `diff`, `sed`, `grep`, `git show`, and `perltidy`.

Control flow: the script resolves the repository/tool root, validates `MODE` as `diff` or `full`, creates a temporary directory, and iterates over all file arguments. In diff mode it obtains the baseline version from `git show "$GITBASE:$RELFILE"`, tidies both baseline and working copies, and reports only newly introduced offending lines. In full mode it tidies the working file and reports all differences. Clean files have their `.tdy` output removed; files with issues retain `.tdy` for review or Makefile-driven update.

State/persistence behavior: temporary comparison files are removed by the exit trap. Per-file tidy output is written beside the checked file as `FILE.tdy`; it remains on failures and is deleted on success. The script reads git history but does not change git state.

Dependencies/integration: used by the lcov Makefile `checkstyle` target after it discovers Perl scripts and modules. Requires `.perltidyrc` at the tool root, git history for diff mode, and a working `perltidy` binary.

Risks/test signals: the custom `realpath` shadows system `realpath` and assumes paths exist. Diff mode fails for files absent from the baseline, which can make newly added files require full-mode handling. The report algorithm is line-diff based, so complex rewrites can produce noisy findings. Signals are exit status, printed offending line groups, and presence or absence of `.tdy` files.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/checkstyle.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/copy_dates.sh -->
# sources/test-tools/lcov/bin/copy_dates.sh

Purpose: copies modification timestamps from a source tree to a target tree, preferring the latest git commit time for clean tracked files. It is used to make distribution trees carry stable source-history dates.

Important APIs/types/functions: shell argument validation, `.git` detection, optional verbose mode through `V`, `find`, `touch -r`, `git diff --quiet`, `git diff --cached --quiet`, `git log --pretty=format:%cd --date=iso`, and `touch --date`.

Control flow: the script requires `SOURCE` and `TARGET`, records whether `SOURCE/.git` exists, changes into `SOURCE`, and walks every file under `find * -type f`. Missing target counterparts are skipped. For every matching file it first copies the source file mtime. If the source is a git repository and the file has no unstaged or staged modifications, it replaces that mtime with the most recent commit date for that file.

State/persistence behavior: only target file mtimes are mutated. Source files and git state are read-only. Files without a target counterpart or without a commit timestamp are left at their copied source mtime.

Dependencies/integration: called by the lcov Makefile during tarball creation and release preparation. It supports reproducible or history-aligned release artifacts before `fix.pl` adjusts embedded dates.

Risks/test signals: `find *` skips dotfiles at the source root and can behave poorly with newlines in filenames. Git errors are not fatal inside the loop except through command exit behavior, and untracked files get source mtimes rather than commit dates. Signals are target mtimes matching clean git commit dates for tracked files and source mtimes for dirty or non-git files.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/copy_dates.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/fix.pl -->
# sources/test-tools/lcov/bin/fix.pl

Purpose: Perl release/install fixup utility that rewrites version strings, release numbers, dates, interpreter paths, library paths, binary paths, script paths, RPM spec metadata, and optional version files across lcov artifacts.

Important APIs/types/functions: `Getopt::Long`; environment variables `V`, `SOURCE_DATE_EPOCH`, `LCOV_PERL_PATH`, and `LCOV_PYTHON_PATH`; functions `get_file_info`, `update_man_page`, `update_perl`, `update_python`, `update_txt_file`, `update_spec_file`, `write_version_file`, `guess_filetype`, `usage`, and `main`.

Control flow: options select file type explicitly or allow `guess_filetype` from shebang, extension, man macros, spec markers, or text heading patterns. `main` optionally writes a version file, then for each file reads the full source, computes date/mode info, applies requested transforms for matching type, writes changed content through `filename.new`, preserves mode, renames atomically enough for local filesystems, and restores mtime using the selected epoch. Manpages get `LCOV <version>`, escaped dates, and `.ds scriptdir`. Perl tools get `$VERSION`, optional shebang replacement, and `FindBin` path rewrites. Python gets optional shebang replacement. Text files get `Last changes:` dates. Spec files get `Version:` and `Release:`.

State/persistence behavior: mutates input files in place when content changes, writes optional `--verfile`, preserves permissions, and sets atime/mtime to the chosen timestamp. It may remove `use FindBin;` lines when path rewrites are requested.

Dependencies/integration: heavily used by the Makefile during install, dist, RPM, and release flows. It encodes install-time paths such as libdir/bindir/scriptdir and release metadata into scripts, libraries, docs, README, and RPM spec files.

Risks/test signals: regex rewrites assume stable formatting and may miss changed declarations or replace unintended matching lines. `update_perl` skips shebang replacement for exactly `/usr/bin/env perl`, which may be intentional but surprising with `--fixinterp`. `SOURCE_DATE_EPOCH` is capped by file mtime, so future or externally supplied epochs newer than the file are not used. Signals include diffing rewritten artifacts, preserving executable modes, correct `.version` contents, and staged install scripts resolving installed paths instead of source-tree `FindBin` paths.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/fix.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/gendesc -->
# sources/test-tools/lcov/bin/gendesc

Purpose: lcov command-line tool that converts a human-readable test description file into the `TN:` and `TD:` description format consumed by `genhtml`.

Important APIs/types/functions: Perl modules `File::Basename`, `Getopt::Long`, `Cwd::abs_path`, `FindBin`, and `lcovutil`; imported globals `$tool_name`, `$tool_dir`, `$lcov_version`, `$lcov_url`, `die_handler`, and `warn_handler`; options `--output-filename`, `--version`, and `--help`; functions `print_usage` and `gen_desc`.

Control flow: the script installs lcovutil warning/die handlers, parses options, handles help/version exits, requires one input filename, and calls `gen_desc`. `gen_desc` opens the input and optional output file, then scans line by line. A line matching `^(\w[\w-]*)(\s*)$` starts a test name and emits `TN: name`. An indented nonblank line emits `TD: text`. Empty lines inside observed description blocks are preserved as a single `TD: ` paragraph separator when followed by another description line.

State/persistence behavior: output is written to stdout unless `--output-filename` is provided, in which case the target file is overwritten. No other persistent state is maintained.

Dependencies/integration: installed as one of the public lcov executables. It depends on `lib/lcovutil.pm` for tool metadata and shared diagnostics, and its output is consumed by `genhtml` as test-case description metadata.

Risks/test signals: malformed lines are silently ignored rather than rejected, so input mistakes can drop descriptions without a nonzero exit. Test names are limited to word characters plus hyphen after a word-character start. The script imports some modules/globals that are not directly used after initialization. Signals are help/version output, conversion of multi-line descriptions, preservation of paragraph breaks, and correct file overwrite behavior with `-o`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/gendesc -->
