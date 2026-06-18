# subset-b-009259 research

Grouped code research for kdevops script files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/contrib_graph.py -->
# sources/test-tools/kdevops/scripts/contrib_graph.py

Purpose: generates contribution visualizations from the current git repository, writing PNG and PDF reports under `docs/contrib/`. It accepts optional `--year`, optional `--month`, and `--show`, then analyzes git history for contributor totals, month-level commit counts, and `Generated-by:` tag adoption.

Important APIs and functions: `run_git_command()` shells out to git with `shell=True`; `get_date_range()` computes bounded date filters; `get_contribution_data()` runs several `git log` pipelines and returns contributor totals, monthly data, total commits, period text, an AI-boom marker, and generated-by monthly counts; `create_contribution_graphs()` builds a multi-panel matplotlib/seaborn figure; `main()` validates CLI dates and repository context.

Control flow: CLI validation happens first, then git repository detection, contribution data extraction, plotting, optional display, and completion logging. The plotting function builds seven views: contributor bar chart, pie chart, activity heatmap, monthly timeline, top-contributor timeline, text statistics, and generated-by adoption trend.

State and persistence: reads only git history but writes `docs/contrib/kdevops_contributions_*.png` and `.pdf`, creating the directory if needed. It depends on current system time when bounding current-year plots and embedding generation timestamps.

Dependencies and integration: depends on git, matplotlib, numpy, pandas, and seaborn. It is a standalone reporting tool, likely run from the kdevops repo root.

Risks: `run_git_command()` uses shell strings, so internal command construction must remain trusted. Monthly aggregation keys only by month number, so all-time mode collapses the same month across different years in some charts. Git author names are used directly in labels. Large histories may be slow. Test signals include running in a small temporary git repo with known commits, checking output file creation, and unit testing date range and parser behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/contrib_graph.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/cwd-append.sh -->
# sources/test-tools/kdevops/scripts/cwd-append.sh

Purpose: prints the current working directory joined with its first argument. It is used as a tiny Kconfig helper for defaults such as appending `kdevops` to the current path.

Important APIs and functions: no functions; it executes `echo $(pwd)/$1`.

Control flow: linear startup, calls `pwd`, interpolates `$1`, prints one line, exits with the shell status from `echo`.

State and persistence: no persistent state; reads the process working directory and the first positional argument only.

Dependencies and integration: uses `/bin/bash` and `pwd`. The observed integration point is `kconfigs/Kconfig.libvirt`, where it provides a default custom libvirt storage pool path.

Risks: the argument is unquoted, so whitespace, glob characters, or empty values can produce surprising output. The command substitution is unnecessary and also unquoted. Test signals are simple shell tests from directories with spaces and without an argument to confirm expected Kconfig-safe behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/cwd-append.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_api.py -->
# sources/test-tools/kdevops/scripts/datacrunch_api.py

Purpose: provides the shared low-level DataCrunch API client for kdevops scripts. It handles OAuth2 client-credentials token retrieval, authenticated GET and POST requests, and high-level list helpers for instance types, images, locations, instances, SSH keys, and instance availability.

Important APIs and functions: `get_api_key()` delegates to `datacrunch_credentials`; `get_access_token()` reads credentials, posts form data to `/oauth2/token`, caches `_access_token_cache`, and supports `force_refresh`; `make_api_request()` performs authenticated GET with one 401 retry; `make_api_post()` sends JSON POSTs; `list_instance_types()`, `list_images()`, `list_locations()`, `list_instances()`, `list_ssh_keys()`, and `get_instance_availability()` normalize common response shapes. `main()` is a manual connectivity smoke test.

Control flow: callers either request a token directly or call a high-level function, which obtains a token if needed, makes an HTTP request, decodes JSON, normalizes list-bearing objects, and returns `None` on errors. The manual CLI checks credentials, token acquisition, then several endpoints.

State and persistence: no files are written. The only state is the in-process access token cache; credentials are read from the credentials module.

Dependencies and integration: uses standard-library `urllib`, `json`, `socket`, and local `datacrunch_credentials.py`. It is imported by `generate_datacrunch_kconfig.py` and `datacrunch_ssh_keys.py`.

Risks: cached tokens are not expiration-aware, so failed requests rely on 401 refresh. Error handling prints to stderr and suppresses bodies for GET retry failures. API schema drift can yield empty defaults. Test signals include mocking `urllib.request.urlopen`, testing list response normalization, 401 refresh behavior, missing credentials, and malformed JSON handling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_api.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_check_capacity.py -->
# sources/test-tools/kdevops/scripts/datacrunch_check_capacity.py

Purpose: CLI capacity checker for DataCrunch GPU instance availability. It supports spot availability via `/instance-availability`, on-demand deployability via `/instance-types` plus `/locations`, JSON output for automation, and `--pick-first` for Ansible/Terraform selection flows.

Important APIs and functions: `load_credentials()` reads an INI credentials file, accepting `client_secret`, `datacrunch_api_key`, or `api_key`; `get_oauth_token()` posts to `/oauth2/token` with `requests`; `check_availability()` returns a list of location records for a specific instance or capacity maps; `main()` parses `--instance-type`, `--location`, `--json`, `--pick-first`, `--credentials`, and `--on-demand`.

Control flow: credentials are loaded, an OAuth token is acquired, capacity is queried, then output mode decides whether to print first location, JSON, or human-readable availability. The spot path filters `availabilities`; the on-demand path treats listed instance types as deployable in every returned location.

State and persistence: reads credentials only; no writes. Exit codes carry availability: no results for a requested instance exits nonzero, and API/credential failures exit immediately.

Dependencies and integration: depends on third-party `requests`. `datacrunch_select_tier.py` invokes it, and Terraform bringup playbooks call it for location and capacity checks.

Risks: on-demand location mapping is approximate and may overstate deployability. The help text still mentions setting only a client secret in one error path, while code requires both client ID and secret. It exits within helper functions, which makes library-style reuse hard. Test signals include mocking `requests`, verifying JSON shapes, `--pick-first` behavior, credentials variants, and nonzero exit when capacity is absent.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_check_capacity.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_credentials.py -->
# sources/test-tools/kdevops/scripts/datacrunch_credentials.py

Purpose: manages DataCrunch OAuth2 credentials in `~/.datacrunch/credentials`, with profile support and a command-line utility for setting, checking, retrieving, and testing credentials.

Important APIs and functions: `get_credentials_file_path()` returns the default credentials path; `read_credentials_file()` parses an INI profile and DEFAULT fallbacks; `get_credentials()` checks the default path first, then `DATACRUNCH_CREDENTIALS_FILE`; `get_api_key()` returns the client secret for backward compatibility; `create_credentials_file()` creates or updates a profile and chmods the file to `0600`; `main()` implements `get`, `set`, `check`, `test`, and `path`.

Control flow: library callers read credentials without side effects. The `set` command prompts for client ID and hidden client secret, writes the INI file, and reports test instructions. The `test` command obtains an OAuth token and queries `/instances`.

State and persistence: writes `~/.datacrunch/credentials` or reads an environment-specified file. Secrets are stored in plaintext INI form but with restricted permissions when this script writes them.

Dependencies and integration: standard library only. It is imported by `datacrunch_api.py` and indirectly by DataCrunch Kconfig and SSH-key helpers.

Risks: parse errors are silently ignored in `read_credentials_file()`, which can obscure configuration problems. The `check` command masks all but the final four characters but assumes secret length is at least four. Usage strings still show older single-argument API key examples in a few places. Test signals include temp HOME tests for profile writes, env-file fallback, chmod checks, missing/malformed INI behavior, and mocked OAuth tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_credentials.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_select_tier.py -->
# sources/test-tools/kdevops/scripts/datacrunch_select_tier.py

Purpose: selects the best available DataCrunch GPU instance from named fallback tier groups such as `h100-or-less` or `b300-or-less`. It is designed for automation that can accept progressively lower GPU tiers when higher tiers have no capacity.

Important APIs and data: `GPU_TIERS` maps tier names to DataCrunch instance type strings; `TIER_ORDER` orders tiers from highest to lowest; `TIER_GROUPS` defines common maximum-tier groups. `get_all_available_capacity()` shells out to `datacrunch_check_capacity.py --json`; `check_instance_availability()` scans a capacity map; `check_instance_on_demand()` invokes the capacity checker for a specific on-demand instance; `select_instance_from_tiers()` implements fallback; `list_tier_groups()` prints available groups; `main()` returns `instance_type location`.

Control flow: the CLI lists tiers or validates a requested group, fetches capacity once, iterates tiers in priority order, skips excluded instance types, checks spot first, optionally probes on-demand, and exits 0 on a selection.

State and persistence: no persistent writes; it reads credentials indirectly through the capacity checker and emits the selected pair on stdout.

Dependencies and integration: depends on Python subprocess and JSON plus sibling `datacrunch_check_capacity.py`. Terraform bringup playbooks invoke it for wildcard tier selections and retry exclusions.

Risks: all capacity failures collapse to an empty map, making auth/network/schema errors indistinguishable from no capacity unless verbose output catches context. Tier definitions are hardcoded and can drift from provider inventory. Test signals include monkeypatching `subprocess.run`, tier ordering tests, exclusion handling, on-demand fallback behavior, and CLI exit codes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_select_tier.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_ssh_key_name.py -->
# sources/test-tools/kdevops/scripts/datacrunch_ssh_key_name.py

Purpose: emits a deterministic DataCrunch SSH key name for the current kdevops checkout. The name format is `kdevops-datacrunch-<8-char-md5>`.

Important APIs and functions: `get_unique_key_name()` resolves the git repository root with `git rev-parse --show-toplevel`, falls back to `os.getcwd()`, hashes that path with MD5, and returns the formatted name. `main()` prints it.

Control flow: one lookup/hash/print path; failures to run git are expected and handled by cwd fallback.

State and persistence: no writes. The output depends on absolute checkout path, so moving a repository changes the generated key name.

Dependencies and integration: uses standard library plus external git. It is referenced by `terraform/datacrunch/kconfigs/Kconfig.identity` to provide a default unique SSH key name for DataCrunch provisioning.

Risks: MD5 is used only for stable naming, not cryptographic security, but path disclosure through predictable names may still be a consideration. Different symlink/canonical path contexts can produce different names. Test signals include running inside and outside a git repo and checking stability from subdirectories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_ssh_key_name.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_ssh_keys.py -->
# sources/test-tools/kdevops/scripts/datacrunch_ssh_keys.py

Purpose: manages DataCrunch SSH keys through the DataCrunch API, including listing keys, uploading a public key, deleting a remote key, generating a local key pair, and setting up the expected kdevops Terraform key.

Important APIs and functions: `list_ssh_keys()`, `add_ssh_key()`, and `delete_ssh_key()` wrap API endpoints; `generate_unique_key_name()` creates a cwd-based MD5 name; `generate_ssh_key_pair()` invokes `ssh-keygen -t ed25519`; `get_default_key_file()` hashes the git root with SHA256 and returns `~/.ssh/kdevops_terraform_<hash>`; `setup_ssh_key()` generates and uploads if needed; `cleanup_ssh_key()` removes remote keys; `main()` exposes `list`, `add`, `delete`, `setup`, and `cleanup`.

Control flow: the CLI first verifies credentials, then dispatches. Setup checks for an existing remote key by name, creates the local key if absent, reads `.pub`, and posts it. Delete resolves name or ID to an API ID, then attempts a direct HTTP DELETE.

State and persistence: writes local private/public keys under `~/.ssh` when setup generates them; remote state changes in the DataCrunch account; no local deletion during cleanup.

Dependencies and integration: imports `datacrunch_api`, uses external `ssh-keygen` and git. It supports DataCrunch Terraform identity workflows.

Risks: key-name hashing differs from `datacrunch_ssh_key_name.py` because one uses cwd MD5 while the other uses git-root MD5, which can cause mismatched default names. DELETE endpoint behavior is noted as uncertain. Test signals include mocked API calls, temp HOME key generation, idempotent setup with existing remote key, and delete-by-name resolution.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_ssh_keys.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_indentation_issues.py -->
# sources/test-tools/kdevops/scripts/detect_indentation_issues.py

Purpose: scans files for indentation problems, with file-type-specific rules for YAML, Python, Makefiles, and Kconfig. It is part of kdevops style tooling.

Important APIs and functions: `check_file_indentation(file_path)` reads a file as bytes, skips null-containing binary files, decodes UTF-8 with ignored errors, infers early indentation style, and returns issue strings. `main()` accepts explicit paths or defaults to `git diff --name-only`, skips common binary extensions, prints findings, and exits 1 when issues exist.

Control flow: path discovery, per-file filtering, issue collection, summary, and exit code. YAML and Python reject tabs in leading whitespace; Makefile recipes immediately after target lines should start with a tab; Kconfig is intentionally exempt from mixed-indent checks.

State and persistence: read-only; no files are modified.

Dependencies and integration: standard library plus git when no paths are provided. `scripts/style.Makefile` invokes it in style-check flows.

Risks: Makefile recipe detection is simplistic and misses multiline targets, conditionals, and recipes not immediately after a colon. The inferred mixed-indent branch has ineffective comparisons because `uses_tabs`/`uses_spaces` are file-level booleans. Test signals include fixture files for YAML tabs, Python tabs, Makefile recipes, Kconfig help text, binary skip behavior, and git-diff default path discovery.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_indentation_issues.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_libvirt_session.sh -->
# sources/test-tools/kdevops/scripts/detect_libvirt_session.sh

Purpose: determines the libvirt URI that kdevops should use, defaulting to `qemu:///system`, switching to `qemu:///session` for distributions detected by libvirt pool helpers, and honoring explicit configuration.

Important APIs and functions: sources sibling `libvirt_pool.sh` and calls `get_pool_vars`, then inspects `USES_QEMU_USER_SESSION` and `CONFIG_LIBVIRT_URI_PATH`.

Control flow: initialize default URI, load helper state, call distribution/pool detection, switch to session when requested, override with configured URI path if non-empty, print final URI.

State and persistence: read-only process state; depends on sourced shell variables from helper scripts and possibly `.config` through those helpers.

Dependencies and integration: `/bin/bash`, `dirname`, and `libvirt_pool.sh`. It is designed for Kconfig or provisioning logic that needs the right libvirt connection string.

Risks: unquoted `dirname $0` and source paths may fail with spaces. `OS_FILE` is assigned but not used directly. Behavior is opaque without `libvirt_pool.sh` side effects. Test signals include stubbing `libvirt_pool.sh` to set `USES_QEMU_USER_SESSION`, testing override behavior, and running under paths with spaces.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_libvirt_session.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_whitespace_issues.py -->
# sources/test-tools/kdevops/scripts/detect_whitespace_issues.py

Purpose: detects trailing whitespace, missing final newlines, and more than two consecutive blank lines in text files.

Important APIs and functions: `check_file_whitespace(file_path)` reads bytes, skips null-containing binaries, decodes lines preserving endings, reports per-line trailing whitespace, missing final newline, and excessive blank blocks. `main()` accepts explicit paths or defaults to modified git files, skips common binary suffixes, prints a summary, and returns 1 when issues are found.

Control flow: discover paths, skip missing/binary-like files, aggregate issue counts, print fix guidance, return status.

State and persistence: read-only; no file modifications.

Dependencies and integration: standard library plus git for default mode. `scripts/style.Makefile` invokes it as a style checker.

Risks: decoding with `errors="ignore"` can hide invalid UTF-8 and still scan partially. The default `git diff --name-only` only covers unstaged changes relative to the index, not all tracked files. Emoji output may not be desirable in strict logs. Test signals include fixtures for each whitespace issue, binary skip, missing path warning, and exit status with explicit path lists.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_whitespace_issues.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/docker-mirror-setup.sh -->
# sources/test-tools/kdevops/scripts/docker-mirror-setup.sh

Purpose: sets up a local Docker registry mirror for kdevops workflows. It creates mirror directories, writes a registry proxy configuration for Docker Hub, runs a `registry:2` container, and can emit daemon mirror configuration.

Important APIs and functions: `check_docker()` validates docker CLI and daemon access; `setup_directories()` creates `$MIRROR_DIR/{registry,images,config}` with sudo; `create_registry_config()` writes registry YAML through `/tmp`; `start_registry()` replaces any existing named container and runs the mirror; `configure_docker_daemon()` writes or stages `/etc/docker/daemon.json`; `main()` orchestrates setup.

Control flow: if the first arg is `--configure-daemon`, only daemon configuration runs. Otherwise the script checks Docker, creates directories/config, starts the registry, verifies `http://localhost:$REGISTRY_PORT/v2/`, and prints next steps.

State and persistence: writes under the mirror directory, creates/removes Docker containers, writes temp config files, may modify `/etc/docker/daemon.json`, and restarts Docker when no existing daemon config exists.

Dependencies and integration: Docker, sudo, curl, systemctl. Related Makefile and Ansible role targets provide a richer docker-mirror workflow.

Risks: existing daemon config is not merged automatically, only backed up/staged. Container replacement is destructive for the named container but preserves mounted registry data. Registry uses insecure localhost HTTP. Test signals include shellcheck, dry-run/container integration tests in a disposable Docker host, and daemon-config tests with existing and absent config.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/docker-mirror-setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/ensure_newlines.py -->
# sources/test-tools/kdevops/scripts/ensure_newlines.py

Purpose: recursively ensures selected text-like files under the current directory end with a newline.

Important APIs and functions: `needs_newline(file_path)` reads bytes, ignores empty and null-containing files, and checks final byte; `add_newline(file_path)` opens append mode and writes `\n`; `main()` walks `.`, skips hidden directories plus `__pycache__` and `node_modules`, and processes known extensions and special filenames.

Control flow: directory walk, file type filter, need check, append newline, count and report.

State and persistence: modifies files in place by appending a newline. It does not preserve binary mode line-ending style if a text file uses CRLF and lacks a final newline.

Dependencies and integration: standard library only. `scripts/style.Makefile` invokes it during style checks, currently with `|| true`, so failures do not stop the style target.

Risks: broad recursive walk can touch many files outside intended changed-file scope. It does not skip all generated/build/cache directories. Bare `except` blocks suppress useful errors. Test signals include temp directory fixtures for targeted suffixes, hidden directory skips, binary skips, CRLF edge cases, and permission-denied behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/ensure_newlines.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/fix_indentation_issues.py -->
# sources/test-tools/kdevops/scripts/fix_indentation_issues.py

Purpose: modifies files to correct simple indentation issues for YAML, Python, and Makefile recipe lines.

Important APIs and functions: `fix_file_indentation(file_path, dry_run=False)` skips null-containing binaries, determines file type, converts leading tabs to four spaces for YAML/Python, and converts leading spaces to tabs for recipe lines immediately following Makefile targets. `main()` accepts paths or defaults to all `git ls-files`, supports `--dry-run`, and prints totals.

Control flow: parse CLI, discover paths, filter missing/non-file/common binary suffixes, call fixer per file, write modified content when not dry-run, return 0.

State and persistence: rewrites modified files in binary mode using UTF-8 encoded content; dry-run only reports counts.

Dependencies and integration: standard library plus git for default all-tracked-file mode. `scripts/style.Makefile` calls the whitespace fixer directly; this indentation fixer is available for manual remediation.

Risks: all tracked-file default is broad and could rewrite many files. Makefile recipe detection is oversimplified. UTF-8 decode with ignored errors can drop undecodable bytes in rewritten files. The print order reports line changes before file headers, which is awkward for logs. Test signals include dry-run invariance, YAML/Python tab conversion, Makefile recipe fixtures, binary skip, and non-UTF-8 file protection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/fix_indentation_issues.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/fix_whitespace_issues.py -->
# sources/test-tools/kdevops/scripts/fix_whitespace_issues.py

Purpose: fixes trailing whitespace, missing final newline, and excessive blank lines in selected files.

Important APIs and functions: `fix_file_whitespace(file_path)` skips null-containing binaries, decodes text, removes trailing spaces/tabs while preserving `\n` or `\r\n`, limits blank runs to two lines, appends a final newline, writes back on modification, and returns fix messages. `main()` uses explicit paths or `git diff --name-only`, skips common binary suffixes, prints per-file fixes, and exits 0.

Control flow: path discovery, filtering, per-file transformation, write if changed, summary.

State and persistence: rewrites files in text mode with UTF-8 encoding when modified. It can normalize encoding for files decoded with ignored errors.

Dependencies and integration: standard library plus git. `scripts/style.Makefile` uses this script to fix modified files.

Risks: invalid UTF-8 bytes can be dropped on write. Default mode only touches modified files, while explicit paths can be broad. The blank-line reducer may alter intentional spacing in generated text or markdown. Test signals include fixtures for CRLF, final newline, trailing tabs, blank runs, binary skip, and no-op idempotence after a second run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/fix_whitespace_issues.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/gen_pcie_passthrough_vars.sh -->
# sources/test-tools/kdevops/scripts/gen_pcie_passthrough_vars.sh

Purpose: emits YAML-style `pcie_passthrough_devices` entries from dynamic Kconfig variables for libvirt PCIe passthrough.

Important APIs and functions: sources `${TOPDIR}/.config` and `${TOPDIR}/scripts/lib.sh`; uses `CONFIG_KDEVOPS_DYNAMIC_PCIE_PASSTHROUGH_NUM_DEVICES`, per-device `CONFIG_KDEVOPS_DYNAMIC_PCIE_PASSTHROUGH_####_*` variables, and passthrough target mode config.

Control flow: fail if device count is empty, print the list header, load `vfio-pci`, adjust group and permissions on `/sys/bus/pci/drivers_probe`, iterate configured device slots, evaluate enabled entries, collect fields with `eval`, decide target guest, and echo inline YAML objects.

State and persistence: changes kernel module state by loading `vfio-pci` and changes ownership/mode of `/sys/bus/pci/drivers_probe`. It writes only to stdout for vars generation.

Dependencies and integration: bash, sudo, modprobe, seq, kdevops `.config`, and dynamic PCI Kconfig Makefile integration where output is appended to extra vars.

Risks: heavy use of `eval` on config-derived variable names requires trusted config. Unquoted variables can break on spaces. Sudo operations may prompt or fail in noninteractive runs. Test signals include a stub `.config` in a disposable environment, shellcheck, validation of generated YAML with enabled/disabled devices, and failure when device count is missing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/gen_pcie_passthrough_vars.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/gen_ssh_key.sh -->
# sources/test-tools/kdevops/scripts/gen_ssh_key.sh

Purpose: generates the kdevops SSH private key configured by `KDEVOPS_SSH_PRIVKEY`.

Important APIs and functions: sources `${TOPDIR}/.config` and `${TOPDIR}/scripts/lib.sh`, prints the key path, then runs `ssh-keygen -t rsa -C generated-by-kdevops -f $KDEVOPS_SSH_PRIVKEY -q -N ""`.

Control flow: linear source/configure/generate sequence.

State and persistence: writes a new RSA private/public key pair at the configured path. Existing-file behavior is delegated to `ssh-keygen`, which may prompt or fail depending on environment and options.

Dependencies and integration: bash, kdevops config, and `ssh-keygen`. It participates in provisioning identity setup.

Risks: unquoted key path fails for spaces and can be unsafe. It uses RSA without specifying bit length instead of newer ed25519 defaults used by DataCrunch helpers. No explicit parent directory creation. Test signals include running with a temp `TOPDIR` and key path, checking file permissions, existing-key behavior, and noninteractive failure modes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/gen_ssh_key.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_ci_commit_message.sh -->
# sources/test-tools/kdevops/scripts/generate_ci_commit_message.sh

Purpose: builds a structured commit message for kdevops CI results archives. It formats either kdevops validation or Linux test-suite results with build metadata, execution results, and machine-readable metadata.

Important APIs and functions: `wrap_commit_subject()` folds long subjects; `calculate_duration()` uses `ci.start_time`; `determine_scope()` chooses `kdevops` or `tests` from `TEST_MODE`; `get_kernel_info()` reads the `linux` repo; `get_kdevops_info()` reads current repo; `get_test_results()` reads result files; `get_workflow_type()` classifies workflow names; `generate_commit_message()` assembles heredoc output; `main()` validates `CI_WORKFLOW`.

Control flow: environment defaults are initialized, metadata files are read when present, git state is queried, result content is loaded, a header is selected based on scope/status, and the formatted message is printed to stdout.

State and persistence: read-only; consumes CI metadata files such as `ci.commit_extra`, `ci.result`, `ci.ref`, and `ci.trigger`.

Dependencies and integration: bash with `set -euo pipefail`, git, date, fold, sed, cut. It is intended for GitHub Actions or archive automation.

Risks: pipe-delimited parsing of git subjects can break if subjects contain `|`. The required `CI_WORKFLOW` check is ineffective because a default is assigned. A Unicode arrow appears in one line, which may matter in strict ASCII logs. Test signals include fixture repos, all workflow-type branches, missing metadata files, pass/fail result values, long subject wrapping, and `TEST_MODE=kdevops-ci` formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_ci_commit_message.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_cloud_configs.py -->
# sources/test-tools/kdevops/scripts/generate_cloud_configs.py

Purpose: orchestrates dynamic Kconfig generation for cloud providers: Lambda Labs, DataCrunch, AWS, Azure, GCE, and OCI. It also prints a concise provider summary.

Important APIs and functions: provider-specific `generate_*_kconfig()` functions run sibling/provider scripts and write generated Kconfig files; `get_lambdalabs_summary()` queries `lambda-cli` JSON endpoints; `process_*()` functions print provider status; `generate_datacrunch_kconfig()` invokes `generate_datacrunch_kconfig.py`; `main()` parses `--provider` and dispatches.

Control flow: print a heading, run one selected provider or all providers, then print menuconfig guidance. AWS/Azure/GCE/OCI each run three provider scripts and write stdout to matching generated files. Lambda and DataCrunch delegate to their own generators.

State and persistence: writes generated Kconfig files under provider `terraform/*/kconfigs` directories. No atomic writes are used, so interrupted runs can leave partial files.

Dependencies and integration: subprocesses, JSON parsing, provider-specific scripts, and Lambda CLI. It is called from `scripts/dynamic-cloud-kconfig.Makefile` for default and provider-specific cloud config targets.

Risks: executable path assumptions require running from the kdevops layout. Errors often degrade to printed warnings while leaving existing generated files untouched or partially updated. Provider script stdout is trusted as valid Kconfig. Test signals include mocking subprocesses, temp provider directories, selected-provider dispatch, write-failure paths, and invalid JSON from Lambda CLI.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_cloud_configs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_datacrunch_kconfig.py -->
# sources/test-tools/kdevops/scripts/generate_datacrunch_kconfig.py

Purpose: generates DataCrunch dynamic Kconfig files for instance types, OS images, and locations, using live DataCrunch API data when credentials and connectivity are available and static fallback defaults otherwise.

Important APIs and functions: `sanitize_kconfig_name()` uppercases and replaces Kconfig-unsafe characters; `generate_instance_types_kconfig()` filters H100/GPU instance types and emits choice plus string value config; `generate_images_kconfig()` prefers PyTorch then Ubuntu images; `generate_locations_kconfig()` emits datacenter choices; `main()` writes selected generated files under `terraform/datacrunch/kconfigs` by default.

Control flow: parse `--output-dir` and `--type`, warn if no API key/client secret is available, ensure output directory, generate each requested Kconfig string, and write `Kconfig.compute.generated`, `Kconfig.images.generated`, and/or `Kconfig.location.generated`.

State and persistence: writes generated Kconfig files directly. It reads credentials indirectly through `datacrunch_api.py`.

Dependencies and integration: imports DataCrunch API helpers. `generate_cloud_configs.py` and `scripts/dynamic-cloud-kconfig.Makefile` invoke it; generated files are sourced by DataCrunch Kconfig fragments.

Risks: price conversion uses `float()` on provider data and can fail for unexpected values. Fallback instance symbol `1X_H100_PCIE` may not match live naming. It warns about missing API key but still calls list functions, which will print credential errors. Test signals include mocked API response fixtures, fallback mode, Kconfig syntax checks, and sanitization edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_datacrunch_kconfig.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_mmtests_graphs.py -->
# sources/test-tools/kdevops/scripts/generate_mmtests_graphs.py

Purpose: parses mmtests comparison output for `thpcompact`-style fault metrics and generates two PNG graphs plus an explanatory `graphs.html` report comparing baseline and development kernels.

Important APIs and functions: `parse_comparison_file()` extracts Amean rows for `fault-base`, `fault-huge`, and `fault-both`; `create_performance_comparison_graph()` writes `performance_comparison.png`; `create_detailed_thread_analysis()` writes `thread_analysis.png`; `generate_graphs_html()` writes an HTML report embedding both images; `main()` validates three CLI args and orchestrates parsing/rendering.

Control flow: check `comparison.txt`, output dir, and `baseline-dev` kernel name argument, create output dir, parse data, render summary graph, render thread analysis, render HTML, and print completion.

State and persistence: writes files under the supplied output directory. It uses matplotlib's `Agg` backend for headless operation.

Dependencies and integration: matplotlib, numpy, regex parsing, pathlib. It is referenced by mmtests CI/reporting flows.

Risks: the regex only matches decimal numeric values and specific `fault-*` names, so format changes or integer values are ignored. HTML includes a large static explanation with emoji/non-ASCII symbols. If parsed data is empty, graphs are still attempted and may produce low-value reports. Test signals include parser fixtures from real mmtests output, empty-data behavior, output file existence, and image smoke tests under headless CI.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_mmtests_graphs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_refs.py -->
# sources/test-tools/kdevops/scripts/generate_refs.py

Purpose: generates Kconfig choices for git references or kernel.org release references. It supports remote `git ls-remote` refs and `kernel.org/releases.json`, optional static extra configs from YAML, and daily regeneration throttling.

Important APIs and functions: `popen()` runs subprocesses and returns stdout; `parser()` defines shared options and `gitref`/`kreleases` subcommands; `check_file_date()` skips fresh outputs unless `--force`; `_ref_generator_choices_static()` and `_ref_generator_choices()` emit Kconfig symbols; `ref_generator()` writes the final Kconfig file; `remote()` runs `git ls-remote`; `gitref_getreflist()` extracts ref names; `_get_extraconfs()` loads YAML; `_check_connection()` probes network; `gitref()` and `kreleases()` gather refs; `main()` dispatches.

Control flow: parse known args, skip fresh output unless forced, dispatch to the selected subcommand, gather dynamic and static refs, then rewrite the output Kconfig file from scratch.

State and persistence: creates parent directories, removes existing output, and writes generated Kconfig. Network availability gates dynamic generation for both git and kernel.org paths.

Dependencies and integration: git, PyYAML, urllib, socket, and Kconfig generator Makefiles (`gen-refs-*`). It feeds boot/kernel reference menu choices.

Risks: `popen()` references `stdout` even when `comm=False`, which would be undefined if used that way. Network probe host is hardcoded to kernel.org for all gitref repos. If connection fails, `gitref()` emits no file. YAML schema is assumed. Test signals include fixture YAML, mocked subprocess output, forced/fresh-date behavior, kernel release JSON fixtures, and no-network behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_refs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-default-bridge.sh -->
# sources/test-tools/kdevops/scripts/get-distro-default-bridge.sh

Purpose: returns the default bridge IP address for a distro and virtualization type. Today it always returns `192.168.122.1`.

Important APIs and functions: no functions. It reads `$1` as `DISTRO`, `$2` as `VIRT_TYPE`, calls `scripts/os-release-check.sh fedora`, and echoes the default bridge.

Control flow: assigns arguments, runs a Fedora detection command, echoes `192.168.122.1` and exits whether Fedora is detected or not.

State and persistence: no persistent state; reads host os-release indirectly through `os-release-check.sh`.

Dependencies and integration: bash and `scripts/os-release-check.sh`. `scripts/provision.Makefile` exports `KDEVOPS_DEFAULT_BRIDGE_IP_GUESTFS` from this script.

Risks: parameters are currently unused, so the interface promises distro/virt-specific behavior that is not implemented. Running from outside the repo root can break the relative `scripts/os-release-check.sh` call. Test signals are straightforward: run for supported distro names and assert the default IP, plus test from non-root cwd if callers rely on it.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-default-bridge.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-has-hop-count-sources.sh -->
# sources/test-tools/kdevops/scripts/get-distro-has-hop-count-sources.sh

Purpose: checks whether the first configured Debian package source is within an acceptable traceroute hop count, returning `y` or `n`. It supports legacy `sources.list` and DEB822 `debian.sources`.

Important APIs and functions: no shell functions. It reads optional acceptable hop count argument, checks `/etc/debian_version`, selects a sources file, extracts the first repository host, runs `traceroute -n -w 1,1,1`, computes line count minus one, and compares with the threshold.

Control flow: non-Debian, missing sources, missing traceroute, empty host, or excessive hops all return `n`; acceptable hop count returns `y`.

State and persistence: read-only against `/etc` and network path; no writes.

Dependencies and integration: bash, grep, awk, sed, cut, traceroute. Used by `Kconfig.guestfs`, `Kconfig.distro`, and devconfig mirror checks to infer local mirror suitability.

Risks: host extraction only considers the first source and may mis-handle complex DEB822 files with multiple `URIs:`. `traceroute` line count can include failures or DNS behavior despite `-n`. Unquoted variables risk path/URL whitespace issues. Test signals include containerized fixture parsing for both source formats, missing traceroute behavior, and stubbed traceroute output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-has-hop-count-sources.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-prefix.sh -->
# sources/test-tools/kdevops/scripts/get-distro-prefix.sh

Purpose: should detect a distro prefix from a fixed list and fall back to `debian`.

Important APIs and functions: no functions. It defines `DEFAULT_DISTRO=debian`, iterates distro names, and is intended to call `./scripts/os-release-check.sh`.

Control flow: as written, the `if` compares the literal string `"./scripts/os-release-check.sh $i"` to `"y"` rather than executing the command. That condition is always false, so the script always echoes `debian`.

State and persistence: read-only; no writes.

Dependencies and integration: bash. `scripts/provision.Makefile` exports `KDEVOPS_DEFAULT_DISTRO` from this script.

Risks: the current command-substitution bug means non-Debian hosts are misdetected, which can cascade into default provisioning and Kconfig choices. The script also assumes repo-root execution if fixed to use the relative helper. Test signals should include distro-detection fixtures or a stub `os-release-check.sh`; current behavior can be captured by asserting it returns `debian` even when the stub would return `y` for Fedora.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-prefix.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_distro_regcode.sh -->
# sources/test-tools/kdevops/scripts/get_distro_regcode.sh

Purpose: dispatches to a distro-specific regulatory-code helper and prints `Unset` when no helper exists.

Important APIs and functions: no functions. It builds `DISTRO_REGCODE_SCRIPT="${TOPDIR}/scripts/get_distro_regcode_$1.sh"`, tests it with `-s`, executes it, or echoes `Unset`.

Control flow: one conditional dispatch based on whether the helper file exists and is non-empty.

State and persistence: read-only; output depends on `${TOPDIR}` and the first positional argument.

Dependencies and integration: bash and distro-specific sibling scripts. It likely feeds wireless/regulatory Kconfig defaults.

Risks: `$1` and `$TOPDIR` are not validated. The target helper is executed without quoting, so spaces in `TOPDIR` fail. Since `$1` is embedded in a path, callers must keep it to trusted distro identifiers. Test signals include helper-present/helper-missing cases, empty helper file, missing TOPDIR, and arguments with unexpected characters.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_distro_regcode.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_gdb_base_port.sh -->
# sources/test-tools/kdevops/scripts/get_gdb_base_port.sh

Purpose: deterministically derives a base gdbserver port from the script file's MD5 checksum.

Important APIs and functions: no functions. It runs `md5sum "$0"`, strips non-digits from the checksum, takes the last four digits, and echoes them.

Control flow: linear checksum, digit filtering, substring extraction, print.

State and persistence: no writes. The output changes when this script's content/path target changes enough to alter the checksum.

Dependencies and integration: bash, md5sum, awk, tr. `kconfigs/Kconfig.libvirt` uses it as the default for `LIBVIRT` gdb base port.

Risks: last four digits can produce low, reserved, or already-used ports, and may be fewer than four digits if the checksum digit string is unexpectedly short. It does not ensure numeric range suitability. Test signals include asserting stable output for a known file copy and validating the result is numeric and acceptable for the consuming Kconfig.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_gdb_base_port.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_can_sudo.sh -->
# sources/test-tools/kdevops/scripts/get_libvirsh_can_sudo.sh

Purpose: intended to report whether kdevops can use sudo-enabled libvirt storage pool heuristics, but currently always returns `n`.

Important APIs and functions: sources `libvirt_pool.sh` but does not call its helper functions. It initializes `CAN_SUDO="n"` and exits with `n` if unchanged.

Control flow: source helper, initialize variables, check `CAN_SUDO`, echo `n`, exit. The final `echo y` is unreachable without code that changes `CAN_SUDO`.

State and persistence: read-only; depends only on cwd for `BASE_DIR` and helper sourcing, but helper side effects are unused in current flow.

Dependencies and integration: bash and `libvirt_pool.sh`. `kconfigs/Kconfig.libvirt` uses it for a default capability setting.

Risks: comments describe advanced heuristics that are disabled by implementation, so users may expect auto-detection that never occurs. Source path is unquoted. Test signals include current assertion that it prints `n`, plus future tests around helper-driven sudo detection if re-enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_can_sudo.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_enabled.sh -->
# sources/test-tools/kdevops/scripts/get_libvirsh_pool_enabled.sh

Purpose: determines whether libvirt storage pool path inference should be enabled for the current working directory.

Important APIs and functions: sources `libvirt_pool.sh`, initializes libvirt-related globals, calls `get_pool_vars`, `virsh_works`, `virsh_get_pool_list`, and `virsh_path_in_pool_list_exists`.

Control flow: derive `BASE_DIR` from `$PWD`, load pool variables, bail out with `n` if `virsh_works` reports no, otherwise gather pool list and print the result of path-in-pool detection.

State and persistence: read-only; uses libvirt/virsh state and current working directory.

Dependencies and integration: bash, `libvirt_pool.sh`, virsh through helper functions. `kconfigs/Kconfig.libvirt` consumes it for `LIBVIRT_STORAGE_POOL_PATH_INFER_ADVANCED`.

Risks: helper function output is the script's output contract; any stderr/stdout noise from helpers can corrupt Kconfig defaults. Path parsing uses `awk -F"/" '{print $2}'`, which only captures the top-level directory. Test signals include stubbing helper functions for virsh success/failure and matching/nonmatching pools.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_enabled.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_name.sh -->
# sources/test-tools/kdevops/scripts/get_libvirsh_pool_name.sh

Purpose: returns the libvirt storage pool name whose path matches the current working directory's top-level base path, or `default` when inference is unavailable.

Important APIs and functions: sources `libvirt_pool.sh`; calls `get_pool_vars`, `virsh_works`, `virsh_get_pool_list`, `virsh_path_in_pool_list_exists`, and `virsh_path_pool_list_name`.

Control flow: initialize helper globals, load pool vars, return `default` if virsh is unavailable, collect pool list, return `default` if no pool path matches, otherwise print the matched pool name.

State and persistence: read-only against libvirt state and cwd.

Dependencies and integration: bash, libvirt helper functions, virsh. `kconfigs/Kconfig.libvirt` uses it as an inferred storage pool name default.

Risks: relies on sourced functions emitting exactly one clean value. Current-directory matching by top-level path may be too coarse on systems with multiple pools under the same prefix. Source path and variable expansions are mostly unquoted. Test signals include stubs for no virsh, no match, and match cases, plus cwd path variations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_name.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_path.sh -->
# sources/test-tools/kdevops/scripts/get_libvirsh_pool_path.sh

Purpose: returns an inferred libvirt storage pool path for the current kdevops checkout, falling back to local/default paths when virsh or matching pools are unavailable.

Important APIs and functions: sources `libvirt_pool.sh`; calls `get_pool_vars`, `virsh_works`, `virsh_get_pool_list`, `virsh_path_in_pool_list_exists`, and `virsh_path_pool_list_path`.

Control flow: if virsh does not work, print `$(pwd)/default`; if virsh works but the current base path is not in any pool list, print `/var/lib/libvirt/images`; otherwise print the matched pool path.

State and persistence: read-only; output depends on cwd and libvirt pool state.

Dependencies and integration: bash, libvirt helpers, virsh. `kconfigs/Kconfig.libvirt` uses it for `LIBVIRT_STORAGE_POOL_PATH_INFER_ADVANCED`.

Risks: fallback behavior differs between virsh-unavailable and no-match cases, which may surprise users. Unquoted source path and `pwd` output can fail with spaces. Helper stdout purity matters. Test signals include helper stubs for each branch and Kconfig default validation with paths containing spaces.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirsh_pool_path.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirt_qemu_bin_path.sh -->
# sources/test-tools/kdevops/scripts/get_libvirt_qemu_bin_path.sh

Purpose: prints the expected QEMU system emulator binary path for the host architecture.

Important APIs and functions: no functions. It echoes `/usr/bin/qemu-system-` followed by `uname -m`.

Control flow: single echo command.

State and persistence: no state or writes; output depends on the runtime kernel architecture string.

Dependencies and integration: bash and `uname`. It likely feeds libvirt/Kconfig defaults for QEMU binary location.

Risks: not all distributions place QEMU binaries under `/usr/bin`, and some architecture names differ from QEMU binary suffixes. It does not verify the path exists or is executable. Test signals include asserting output for common architectures and adding an existence check in consumers or tests where a real host has QEMU installed.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirt_qemu_bin_path.sh -->
