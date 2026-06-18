# Research Group subset-b-009559

This grouped report covers Blobfuse2 GitHub Actions, Azure DevOps templates, lint configuration, and top-level pipeline definitions under `sources/user-network-fs/blobfuse2`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/actions/perftesting/action.yml -->
# sources/user-network-fs/blobfuse2/.github/actions/perftesting/action.yml

## Purpose
This composite GitHub Action builds Blobfuse2 on a benchmark runner, creates a storage-backed mount configuration, runs FIO read/write benchmark scripts, and publishes bandwidth and latency JSON results to the `benchmarks` branch when running on `main`.

## Important APIs, Types, and Functions
The action input contract is `ARCH`, four Azure account/key pairs for standard, premium, standard HNS, and premium HNS accounts, `BENCH_CONTAINER`, `GITHUB_TOKEN`, and `CACHE_MODE`. It calls repository scripts `go_installer.sh`, `build.sh`, `tools/install_fio.sh`, `perf_testing/scripts/fio_bench.sh`, and `blobfuse2 gen-test-config`. It integrates with `benchmark-action/github-action-benchmark@v1` and the local `.github/actions/disk-benchmark` action.

## Control Flow
Steps install FUSE3 and tools, install Go, build Blobfuse2, copy the binary to `/usr/bin`, select `AZURE_STORAGE_ACCOUNT` and `AZURE_STORAGE_ACCESS_KEY` from `matrix.TestType`, generate either block-cache or file-cache config, optionally creates an ARM64 RAID0 local SSD mount, optionally runs disk benchmarks once, prepares mount/cache paths, then runs read and write FIO benchmark scripts. Result publishing is gated to `github.ref == refs/heads/main`.

## State and Persistence Behavior
The action mutates runner state by installing apt packages, killing apt locks, creating `/mnt/blob_mnt` and `/mnt/localssd/tempcache`, creating `/dev/md0` on ARM64, and exporting Azure credentials through `GITHUB_ENV`. Benchmark JSON is persisted to the `benchmarks` branch by the benchmark action.

## Dependencies and Integration Points
It is invoked by `.github/workflows/benchmark.yml` and assumes matrix keys `TestType` and `CacheMode` exist. It depends on self-hosted benchmark runners, Azure storage secrets, FUSE3, Go, FIO, jq, mdadm, and repository config templates `azure_block_bench.yaml` and `azure_key_perf.yaml`.

## Risks and Edge Cases
The YAML uses `if :` with a space before the colon in several steps, which is suspicious for GitHub Actions syntax. ARM64 disk setup assumes exactly six NVMe partition devices. Config files and logs print generated config contents, so secret redaction depends on GitHub masking. Apt lock killing is aggressive. Benchmark publication auto-pushes to a branch and can conflict with concurrent benchmark jobs.

## Test Signals
Useful signals are a manual `benchmark.yml` run, successful config generation for both cache modes, FIO script exit status, created `read/*_results.json` and `write/*_results.json`, benchmark branch updates, and ARM64 runner validation that `/mnt/localssd` exists before file-cache tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/actions/perftesting/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/dependabot.yml -->
# sources/user-network-fs/blobfuse2/.github/dependabot.yml

## Purpose
This file configures Dependabot to keep GitHub Actions and Go module dependencies current.

## Important APIs, Types, and Functions
The two `updates` entries use Dependabot package ecosystems `github-actions` and `gomod`, both rooted at `/` and scheduled daily.

## Control Flow
Dependabot scans the repository root each day for workflow action references and `go.mod` dependency changes, then opens pull requests when updates are available.

## State and Persistence Behavior
There is no runtime state in the repo. Dependabot state and PR metadata live in GitHub. Generated PRs can mutate workflow versions and Go dependency files once merged.

## Dependencies and Integration Points
This integrates with GitHub Dependabot and indirectly affects every workflow that references external actions plus the Go module graph used by CI.

## Risks and Edge Cases
Daily updates can create high PR volume, and major action upgrades may break pinned workflow assumptions. No grouping, ignore rules, or labels are configured, so triage policy is entirely external.

## Test Signals
Signals are Dependabot PR creation, GitHub Actions CI on dependency update PRs, and successful `go mod` resolution after Dependabot updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/arm-ci.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/arm-ci.yml

## Purpose
This workflow cross-compiles Blobfuse2 for ARM32/armhf with libfuse3 and verifies the resulting binary under qemu.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, apt packages for qemu and ARM cross compilation, `wget` plus `dpkg-deb` to extract armhf `libfuse3-dev` and runtime packages, `actions/setup-go@v6`, and `go build`.

## Control Flow
The workflow runs on manual dispatch, pushes to `main`, and pull requests to `main`. It installs qemu and `arm-linux-gnueabihf` tools, downloads Ubuntu armhf libfuse packages, sets `GOOS=linux`, `GOARCH=arm`, `GOARM=7`, `CGO_ENABLED=1`, `CC`, `CGO_CFLAGS`, and `CGO_LDFLAGS`, builds `blobfuse2-arm`, then runs `blobfuse2-arm --version` through `qemu-arm`.

## State and Persistence Behavior
All state is workspace-local under `deps/` and the built `blobfuse2-arm` artifact. No artifacts are uploaded and no branches are mutated.

## Dependencies and Integration Points
It integrates Go CGO compilation with libfuse headers and ARM qemu runtime. The job validates a platform not covered by normal amd64 Linux CI.

## Risks and Edge Cases
The libfuse URLs point to old Ubuntu release package paths and can break if unavailable. It verifies only `--version`, not mounting. Cross-linking depends on extracted library paths and qemu sysroot compatibility. Unit tests are explicitly omitted.

## Test Signals
Signals are successful armhf package extraction, `file blobfuse2-arm` showing ARM output, and qemu returning version output without missing loader or libfuse errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/arm-ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/benchmark.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/benchmark.yml

## Purpose
This workflow runs weekly and manually triggered benchmark jobs across x86 and ARM64 self-hosted runners, storage account types, and cache modes.

## Important APIs, Types, and Functions
The workflow defines a `PerfTesting` job with a matrix over runner config, `TestType`, and `CacheMode`. It calls the local composite action `.github/actions/perftesting` and passes GitHub token plus Azure storage account secrets.

## Control Flow
On Sunday schedule or `workflow_dispatch`, the job runs with `max-parallel: 1` to reduce performance interference. Each matrix row checks out the selected ref and delegates all setup, build, mount, FIO execution, and benchmark publication to the composite action.

## State and Persistence Behavior
The workflow itself persists benchmark pages/data through the composite action on `main`. Runner state includes installed packages, local mount/cache paths, and possible ARM RAID setup.

## Dependencies and Integration Points
It depends on self-hosted labels `1ES.Pool=blobfuse2-benchmark` and `1ES.Pool=blobfuse2-benchmark-arm`, Azure storage secrets, and the benchmark action's `benchmarks` branch convention.

## Risks and Edge Cases
The action relies on `matrix.TestType` and `matrix.CacheMode`, so renaming those matrix keys breaks the composite action. `TestType` only lists standard and premium even though the composite action has HNS inputs. Long timeout and self-hosted state make stale mounts or disk layout drift likely.

## Test Signals
Signals include all matrix rows completing, FIO result JSON files existing, benchmark branch updates, and no cross-run contamination in `/mnt/blob_mnt` or `/mnt/localssd/tempcache`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/benchmark.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/blobfuse-buddy.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/blobfuse-buddy.yml

## Purpose
This workflow posts AI-generated replies to newly opened issues or discussions, with a manual-dispatch mock mode for testing the reply path.

## Important APIs, Types, and Functions
It uses `azure/login@v3` with OIDC, `actions/setup-python@v6`, Python packages `openai`, `azure-identity`, `requests`, `mcp`, `httpx`, and `python-dotenv`, and repository script `scripts/call_agent.py`. It writes a `mock_event.json` payload for manual tests.

## Control Flow
The workflow triggers on `issues.opened`, `discussion.created`, or manual dispatch. It checks out code, authenticates to Azure, sets Python 3.11, installs dependencies, optionally synthesizes a GitHub event payload from workflow inputs, then runs `scripts/call_agent.py` with event path, GitHub token, Azure AI Foundry endpoint, API version, repository name, and a dry-run flag for manual dispatch.

## State and Persistence Behavior
Manual dispatch creates `mock_event.json` in the workspace. Production runs can write issue or discussion comments through the GitHub token. Azure login state is ephemeral in the runner.

## Dependencies and Integration Points
It integrates GitHub issue/discussion events with Azure AI Foundry through OIDC secrets `AZURE_MCP_CLIENT_ID`, `AZURE_MCP_TENANT_ID`, and `AZURE_MCP_SUBSCRIPTION_ID`. The real behavior is concentrated in `scripts/call_agent.py`.

## Risks and Edge Cases
The workflow grants write permission to issues and discussions, so prompt-injection handling and script safeguards matter. The manual mock hardcodes default title/body values before reading inputs. The API version is a future preview string, so availability and SDK compatibility are sensitive.

## Test Signals
Signals include manual dispatch dry-run output, successful Azure login, `scripts/call_agent.py` completing, and a real issue/discussion run producing an appropriate comment without exposing secrets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/blobfuse-buddy.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/codeql-analysis.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/codeql-analysis.yml

## Purpose
This workflow runs GitHub CodeQL analysis for Go code on pushes and pull requests targeting `main`.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, `github/codeql-action/init@v4`, `github/codeql-action/autobuild@v4`, and `github/codeql-action/analyze@v4` with matrix language `go`.

## Control Flow
For each trigger, the job checks out the repository, initializes CodeQL for Go, lets CodeQL autobuild the project, and uploads analysis results to GitHub security events.

## State and Persistence Behavior
The workflow creates CodeQL databases and build artifacts on the runner and persists SARIF/security findings into GitHub's code scanning backend.

## Dependencies and Integration Points
It integrates with GitHub code scanning and depends on the Go project being autobuildable on `ubuntu-latest`. The job has `security-events: write` permission.

## Risks and Edge Cases
Autobuild may miss CGO/FUSE-specific build requirements or build tags used by Azure DevOps. There is no custom query config or manual build fallback enabled.

## Test Signals
Signals include CodeQL database creation, successful autobuild, and code scanning alerts appearing or updating in GitHub Security.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/codeql-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/codespell.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/codespell.yml

## Purpose
This workflow checks repository text and filenames for common spelling mistakes.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6` and `codespell-project/actions-codespell@master`. Options enable filename checks, skip binary/vendor/noisy paths, and define an ignore word list for project-specific tokens.

## Control Flow
The job runs on pushes to `main` and pull requests to `main` or `blobfuse/2.*`, checks out the repository, then invokes codespell with the configured skip and ignore settings.

## State and Persistence Behavior
There is no persistent state. Failures are reported as workflow errors.

## Dependencies and Integration Points
It integrates with GitHub PR checks and protects code, comments, docs, workflow names, and filenames from spelling regressions.

## Risks and Edge Cases
The action is referenced from `master`, not a version tag or commit. The skip list and ignore list are broad enough to hide some real mistakes. Codespell can produce false positives on domain-specific storage terms.

## Test Signals
Signals are a clean codespell job on PRs and intentional typo test PRs failing unless covered by explicit ignore rules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/issueMetrics.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/issueMetrics.yml

## Purpose
This monthly workflow generates issue and pull-request metrics for the previous 90 days and publishes the report to the `benchmarks` branch.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, `actions/setup-python@v6`, `PyGithub`, and repository script `scripts/issueMetrics.py --days 90`. It writes `issueMetric.txt` and date-stamped files under `issueMetrics/`.

## Control Flow
On manual dispatch or the first day of each month, it checks out main, installs Python dependencies, runs the metrics script with `GH_TOKEN` and `REPO_NAME`, checks out the `benchmarks` branch into `benchmarks-branch`, copies the generated report into current and archival paths, commits if there are changes, and pushes to `benchmarks`.

## State and Persistence Behavior
Persistent state is the `benchmarks` branch report file and dated history files. The workflow mutates git config and branch contents in the secondary checkout.

## Dependencies and Integration Points
It integrates GitHub repository issue/PR data with the project's benchmark/reporting branch. It depends on `scripts/issueMetrics.py` and GitHub token access.

## Risks and Edge Cases
The `contents: write` permission allows branch mutation. If the `benchmarks` branch is missing or diverged, the checkout/push path fails. Metrics quality depends on API pagination and rate limits inside the script.

## Test Signals
Signals include successful report generation, a no-op commit path when unchanged, and a dated `issueMetrics/issueMetric-YYYY-MM-DD.txt` file on `benchmarks`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/issueMetrics.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/mirror-to-blob.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/mirror-to-blob.yml

## Purpose
This workflow mirrors repository code, wiki content, public documentation, and exported GitHub history into Azure Blob Storage for downstream retrieval or AI/search workflows.

## Important APIs, Types, and Functions
It uses `azure/login@v3`, Azure CLI `az storage copy`, `az storage blob upload-batch`, and `az storage blob download-batch`, plus repository scripts `scripts/fetch_public_docs.py` and `scripts/export_github_history.py`.

## Control Flow
On weekly schedule or manual dispatch, the job authenticates to Azure by OIDC, uploads the repository tree excluding `.git` to `repo-code`, clones and uploads the wiki to `repo-docs/wiki`, fetches public docs and uploads `public/`, restores previous GitHub export state from `repo-gh`, runs the export script with `GITHUB_TOKEN`, and uploads the refreshed JSONL/state output back to `repo-gh`.

## State and Persistence Behavior
Persistent state lives in Azure Blob containers/prefixes `repo-code`, `repo-docs`, and `repo-gh`. The `out_github_export` directory is restored from blob so the exporter can append/update incrementally instead of starting from scratch.

## Dependencies and Integration Points
It depends on Azure OIDC secrets, storage account `blobfusemcpserver`, Azure CLI availability on GitHub-hosted runners, Python `html2text` and `requests`, and public access to the Azure Storage Fuse wiki.

## Risks and Edge Cases
Repository code upload may include files not intended for public AI ingestion unless excluded. The workflow has read permissions for issues and PRs and uploads historical data to blob. Incremental state corruption can affect future exports. `az storage copy` and upload options differ between commands, so destination-path mistakes are easy.

## Test Signals
Signals include blob prefixes updated after a run, restored `state.json` on repeat runs, successful wiki clone, successful script exits, and no unauthorized secret material in uploaded content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/mirror-to-blob.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/pr-mirror-cleanup.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/pr-mirror-cleanup.yml

## Purpose
This workflow deletes stale `pr-mirror/<PR#>` branches created for Azure DevOps CI runs on external pull requests.

## Important APIs, Types, and Functions
It uses `actions/github-script@v9` and GitHub REST APIs `repos.listBranches`, `pulls.get`, and `git.deleteRef`.

## Control Flow
On daily schedule or manual dispatch, the script lists all branches, filters names with the `pr-mirror/` prefix, parses the PR number, fetches the PR, and deletes the mirror branch if the PR is closed, missing, or its current head SHA differs from the branch tip.

## State and Persistence Behavior
The persistent state is Git references under `refs/heads/pr-mirror/*`. The workflow mutates only those refs.

## Dependencies and Integration Points
It complements `.github/workflows/pr-mirror.yml` and supports the Azure DevOps `blobfuse2-1es_ci` workflow for fork PR validation.

## Risks and Edge Cases
It assumes branch names after the prefix are positive integers. API failures other than 404 are skipped, which can leave stale branches. It uses no checkout and no secrets, limiting blast radius.

## Test Signals
Signals are deleted mirror branches for closed or force-pushed PRs, preserved mirror branches for open PRs with matching head SHA, and workflow logs showing deletion reasons.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/pr-mirror-cleanup.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/pr-mirror.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/pr-mirror.yml

## Purpose
This workflow lets a maintainer mirror a pull request head commit into an upstream `pr-mirror/<PR#>` branch so Azure DevOps CI can be manually queued for fork PR code without running fork-authored workflow code in GitHub Actions.

## Important APIs, Types, and Functions
It uses `actions/github-script@v9` for reaction/comment/status APIs, `actions/checkout@v6`, `git fetch` from `refs/pull/<n>/head`, and `git push --force-with-lease` to the mirror ref.

## Control Flow
The job only runs when an issue comment is exactly `/mirror`, the issue is a pull request, and the commenter is OWNER or MEMBER. It reacts to the comment, resolves PR head SHA/number/state, refuses closed PRs, checks out the upstream repo without fork code, fetches `pull/<number>/head`, verifies fetched SHA equals the PR head SHA, refreshes existing mirror tracking ref if present, force-pushes the SHA to `pr-mirror/<number>`, comments with maintainer instructions, and sets a pending commit status named `pr-mirror`.

## State and Persistence Behavior
Persistent state includes mirror branches, PR comments, comment reactions, and commit status records. The workflow does not persist artifacts.

## Dependencies and Integration Points
It integrates GitHub PR review workflow with Azure DevOps `blobfuse2-1es_ci`. Comments explicitly instruct maintainers to run the ADO pipeline against the mirror branch.

## Risks and Edge Cases
Security depends on ADO loading trusted pipeline YAML from a fixed ref, as documented in comments. The exact-body trigger ignores whitespace or additional text. `--force-with-lease` reduces accidental overwrite risk but still updates branch state.

## Test Signals
Signals include a maintainer `/mirror` comment creating or updating the expected branch, SHA verification logs, a PR comment containing the branch link, and pending commit status on the mirrored SHA.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/pr-mirror.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/publish-container.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/publish-container.yml

## Purpose
This workflow builds a Blobfuse2 container image and publishes it to GitHub Container Registry when release-like tags are pushed.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, `actions/setup-go@v6`, `docker/setup-buildx-action@v4`, `docker/login-action@v4`, `docker/metadata-action@v6`, and `docker/build-push-action@v7`. It calls `./build.sh` and copies the built binary plus setup files into `docker/`.

## Control Flow
On tag pushes matching `v*` or `blobfuse2-*`, the job installs FUSE dependencies, builds Blobfuse2, prepares Docker context, logs into `ghcr.io` with `GITHUB_TOKEN`, computes semver/ref tags for both `v` and `blobfuse-` tag formats, builds and pushes the Docker image from `docker/Dockerfile`, then deletes temporary copied files from `docker/`.

## State and Persistence Behavior
Persistent output is the pushed GHCR package `ghcr.io/azure/blobfuse2` with generated tags and labels. Workspace mutations under `docker/` are cleaned at the end.

## Dependencies and Integration Points
It depends on Go module settings, the repository Dockerfile, setup files, FUSE apt packages, and package write permission to GHCR.

## Risks and Edge Cases
Metadata semver patterns assume tags parse correctly with `v` or `blobfuse-` prefixes. Cleanup runs only after a successful push step; failed jobs may leave copied files in the ephemeral workspace. It does not build multi-arch images.

## Test Signals
Signals include successful binary build, generated Docker metadata, pushed GHCR tags for release tags, and ability to pull `ghcr.io/azure/blobfuse2:<tag>`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/publish-container.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/trivy.yaml -->
# sources/user-network-fs/blobfuse2/.github/workflows/trivy.yaml

## Purpose
This workflow builds the Blobfuse2 binary and scans it with Trivy, uploading SARIF results to GitHub code scanning.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, shell `go build -o blobfuse2`, `aquasecurity/trivy-action` pinned by commit, and `github/codeql-action/upload-sarif@v4`.

## Control Flow
The workflow runs on manual dispatch, pushes to `main`, `master`, or `blobfuse/2*`, pull requests to the same branch set, and a weekly schedule. It installs FUSE libraries, builds the binary, scans `./blobfuse2` as a filesystem target with unfixed issues ignored and all severities included, prints the SARIF file, and uploads it.

## State and Persistence Behavior
Runner state includes the built `blobfuse2` and `trivy-results-binary.sarif`. Persistent state is code scanning SARIF results in GitHub.

## Dependencies and Integration Points
It integrates binary vulnerability scanning with GitHub Security. It overlaps with CodeQL but targets dependency/binary findings rather than source queries.

## Risks and Edge Cases
The workflow scans the built binary path, not the whole repository or container image. Printing full SARIF can make logs noisy. It installs FUSE packages before build but does not use the repository's `build.sh`, so build flags may diverge.

## Test Signals
Signals are successful Go build, SARIF generation, SARIF upload, and GitHub Security tab entries matching Trivy output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/update-latest-version.yml -->
# sources/user-network-fs/blobfuse2/.github/workflows/update-latest-version.yml

## Purpose
This workflow updates the `benchmarks` branch release sentinel used by Blobfuse2 version checks whenever a non-preview `blobfuse2-*` release tag is pushed.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, shell tag parsing via `${GITHUB_REF_NAME#blobfuse2-}`, `rm -f *`, `touch`, git add/commit/push, and a job-level `if` excluding tag names containing `preview`.

## Control Flow
On `blobfuse2-*` tag push, non-preview tags check out the `benchmarks` branch, derive the version, enter `release/latest/`, remove all existing sentinel files, create an empty file named after the new version, and commit/push only if changes are staged.

## State and Persistence Behavior
Persistent state is `release/latest/<version>` on the `benchmarks` branch. The workflow intentionally represents the latest version as an empty filename.

## Dependencies and Integration Points
It integrates release tags with Blobfuse2's runtime latest-version check against raw GitHub content on the `benchmarks` branch.

## Risks and Edge Cases
`rm -f *` is destructive within `release/latest/` and assumes that directory exists and contains only sentinel files. Preview exclusion is a substring check. Concurrent tag pushes can race on the branch.

## Test Signals
Signals are a new sentinel file in `benchmarks:release/latest/`, no commit when already current, and runtime version check resolving the expected latest release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/workflows/update-latest-version.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.golangci.yml -->
# sources/user-network-fs/blobfuse2/.golangci.yml

## Purpose
This config defines the Go lint and formatting policy enforced by golangci-lint for Blobfuse2.

## Important APIs, Types, and Functions
Enabled linters include `errcheck`, `gocheckcompilerdirectives`, `govet`, `ineffassign`, `misspell`, `predeclared`, `staticcheck`, `testifylint`, and `unused`. Formatter checks include `gofmt` and `goimports`. `testifylint` enables all checks except `require-error` and `suite-thelper`; `staticcheck` runs all checks except `ST1003` and `ST1005`.

## Control Flow
When golangci-lint runs, it applies enabled linters and formatters, excludes generated code loosely, applies false-positive presets, and excludes paths ending in `third_party`, `builtin`, and `examples`.

## State and Persistence Behavior
There is no runtime state. It affects CI pass/fail and local lint output.

## Dependencies and Integration Points
The Azure DevOps 1ES CI workflow installs `golangci-lint v2.11.0` and runs it with build tags from the distro matrix. This config supplies the rule set.

## Risks and Edge Cases
Lint semantics depend on the installed golangci-lint version. Broad generated and path exclusions can hide issues. Max issue counts are unlimited, so a bad run can produce large logs.

## Test Signals
Signals are clean `golangci-lint run --build-tags $(tags)` output and no drift between local lint version and CI-installed version.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/bfusemon.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/bfusemon.yml

## Purpose
This Azure DevOps template validates Blobfuse2 health monitor integration by mounting with monitoring enabled, exercising file operations, and printing monitor JSON output.

## Important APIs, Types, and Functions
It calls `blobfuse2 gen-test-config` with `azure_key_hmon.yaml`, symlinks `bfusemon` into `/usr/local/bin`, mounts through the shared `mount.yml` template, and cleans up through `cleanup.yml`.

## Control Flow
The template creates a key-based block config with `HMON_OUTPUT`, creates mount and cache directories, mounts Blobfuse2 after installing the `bfusemon` symlink, prints process information, performs create/copy/mkdir/move/delete operations on the mount, waits, prints `monitor_*.json`, then unmounts without deleting containers.

## State and Persistence Behavior
It mutates `/usr/local/bin/bfusemon`, writes config and monitor JSON in `$(WORK_DIR)`, and uses `$(MOUNT_DIR)` and `$(TEMP_DIR)`. No long-term storage state is intended beyond operations against the test container.

## Dependencies and Integration Points
It depends on `build.yml` having built both `blobfuse2` and `bfusemon`, on block account variables, and on the common mount/cleanup templates.

## Risks and Edge Cases
The symlink requires sudo and may collide with an existing `bfusemon`. The test prints generated config and monitor output. It validates monitor presence but not structured JSON fields beyond manual log inspection.

## Test Signals
Signals include a running `bfusemon` process, successful file operations, `monitor_*.json` containing health output, and clean unmount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/bfusemon.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/build-release.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/build-release.yml

## Purpose
This template installs Go, builds release binaries for Blobfuse2 and `bfusemon`, and optionally runs unit tests for release packaging contexts.

## Important APIs, Types, and Functions
Parameters include `work_dir`, `root_dir`, `unit_test`, `tags`, and `container`. It invokes `go_installer.sh`, Azure DevOps `Go@0 get`, `./build.sh <tags>`, `./build.sh health`, `blobfuse2 --version`, `bfusemon --version`, and optional `go test`.

## Control Flow
The template installs Go into the supplied root directory, downloads Go dependencies, builds Blobfuse2 with optional build tags, verifies the binary, builds and verifies the health monitor, and when `unit_test` is true writes `$HOME/azuretest.json` from pipeline storage variables before running unit tests with `--tags=unittest,<tags>`.

## State and Persistence Behavior
It creates binaries in `work_dir`, writes `$HOME/azuretest.json`, and may generate `utcover.cov`. It does not create or delete Azure containers itself.

## Dependencies and Integration Points
It integrates release build stages with shared storage account secrets and the repository build script. It is similar to `build.yml` but parameterized for release template callers.

## Risks and Edge Cases
The JSON config is assembled with shell `echo` and includes storage secrets in logs via `cat`. Unit tests depend on external Azure test accounts. Build behavior must stay aligned with `build.sh` and Microsoft Go/FIPS expectations.

## Test Signals
Signals are `blobfuse2 --version`, `bfusemon --version`, successful dependency restore, and optional unit test pass under requested build tags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/build-release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/build.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/build.yml

## Purpose
This is the central Azure DevOps setup template: it installs distro dependencies, checks out/builds Blobfuse2, creates mount/cache/GOPATH directories, creates temporary Azure containers, generates ADLS SAS, writes Azure test configuration, and optionally runs unit tests.

## Important APIs, Types, and Functions
Parameters control MSI/AzCLI skipping, health monitor build, proxy setup, and unit test execution. It composes `package-install.yml` and `container.yml`, calls `go_installer.sh`, `Go@0 get/test/tool`, `./build.sh $(tags)`, `./build.sh health`, `blobfuse2 --version`, and writes `$HOME/azuretest.json`.

## Control Flow
The template installs packages for the current `distro`, checks out self, prints environment and disk info, optionally installs and configures mitmproxy, installs Go, downloads dependencies, builds Blobfuse2 and optionally `bfusemon`, verifies the binary, prepares mount/cache/GOPATH directories, generates a random container name, creates block and ADLS containers, generates ADLS container SAS, writes test credentials/config flags to `$HOME/azuretest.json`, optionally runs unit tests and coverage report, and saves `utcover.cov`.

## State and Persistence Behavior
State includes generated containers in Azure storage, SAS variables set through `##vso[task.setvariable]`, local mount/cache directories, Go workspace, built binaries, optional coverage artifacts, and `$HOME/azuretest.json`. Container cleanup is left to calling pipelines via `cleanup.yml`.

## Dependencies and Integration Points
Nearly every Azure pipeline stage invokes this template. It depends on variable group `NightlyBlobFuse`, distro matrix variables, package install support, Azure CLI, storage account secrets, and repository test code.

## Risks and Edge Cases
Secrets are written into a JSON file and printed. Unit test step is `continueOnError: true` in this template, so callers must check coverage/report implications. Proxy setup exports environment variables in one shell step only, which may not affect later steps. Container creation is conditional on Ubuntu inside `container.yml`, which matters for non-Ubuntu stages.

## Test Signals
Signals include package install success, `blobfuse2 --version`, created storage containers, generated ADLS SAS, valid `$HOME/azuretest.json`, unit test and coverage output when enabled, and later cleanup deleting containers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/cleanup.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/cleanup.yml

## Purpose
This template unmounts Blobfuse2 mounts and optionally deletes temporary block and ADLS containers.

## Important APIs, Types, and Functions
Parameters are `unmount` and `delete_containers`. It uses `ps`, `df`, `sudo umount -f`, `pidof blobfuse2`, `rm -rf` on mount/cache contents, `/etc/mtab`, and composes `container.yml` for deletion.

## Control Flow
If unmounting is enabled, it prints process/disk state, force unmounts `$(MOUNT_DIR)`, waits, kills Blobfuse2, clears mount and temp directories, and prints mount table under `condition: always()`. If deletion is enabled, it calls `container.yml` twice to delete the generated container from block and ADLS accounts.

## State and Persistence Behavior
It mutates runner mount/cache directories and can delete Azure storage containers named `$(containerName)`.

## Dependencies and Integration Points
It is called before mounts in `mount.yml`, at the end of most test templates, and at the end of top-level pipeline jobs.

## Risks and Edge Cases
`sudo kill -9 \`pidof blobfuse2\`` can kill all Blobfuse2 processes on the agent, which is risky on shared self-hosted runners. `rm -rf $(MOUNT_DIR)/*` can remove mounted contents if unmount failed. Container deletion depends on variables and is Ubuntu-conditioned in `container.yml`.

## Test Signals
Signals include no remaining Blobfuse2 process, no mounted FUSE entry in `df`/`mtab`, empty mount/cache directories, and deleted test containers when requested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/cleanup.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/container.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/container.yml

## Purpose
This template manages temporary Azure Storage containers and ADLS container SAS values for pipeline tests.

## Important APIs, Types, and Functions
Parameters switch among `generate_container`, `create_container`, `delete_container`, and `generate_adls_sas`, with account metadata and optional container name. It uses Azure CLI `az storage container create/delete` and `az storage fs generate-sas`.

## Control Flow
When generating a container, it creates a random 40-character lowercase/number name and sets Azure DevOps variable `containerName`. When creating, it uses account key auth and `--fail-on-exist`. When generating ADLS SAS, it creates a 70-minute filesystem SAS with broad ACL/data permissions and stores it as `BF2_ADLS_ACC_SAS`. When deleting, it deletes `$(containerName)` from the specified account.

## State and Persistence Behavior
Persistent state is storage containers in Azure accounts and pipeline variables set through `##vso[task.setvariable]`. Steps run only when `variables['distro'] == 'ubuntu'`.

## Dependencies and Integration Points
It is used by `build.yml`, `cleanup.yml`, and release/unit-test setup. It depends on Azure CLI, account names/keys, and a valid distro variable.

## Risks and Edge Cases
Non-Ubuntu jobs skip creation/deletion because of conditions, so callers must provide existing containers or handle cleanup differently. The random-name generation can block or be slow on entropy-starved hosts. SAS expiry is short and can expire in long jobs.

## Test Signals
Signals include visible `containerName` variable, successful container creation in both accounts, generated ADLS SAS, and cleanup deleting the same container.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/container.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/data-integrity.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/data-integrity.yml

## Purpose
This template validates data consistency for file cache, block cache, read-only, direct-IO, disk block-cache path, and legacy stream configuration paths.

## Important APIs, Types, and Functions
It composes `data.yml` for data generation/copy/checks and `mount.yml` for mount lifecycle. It calls `blobfuse2 gen-test-config` with `azure_key.yaml`, `azure_key_bc.yaml`, and `azure_stream.yaml`, then mounts with options such as `--file-cache-timeout=3200`, `-o direct_io`, `-o ro`, and block-cache path/block-size flags.

## Control Flow
It first generates random local test files. For `file_cache`, it creates a file-cache config, mounts normally and with direct IO, copying and verifying data each time. For `block_cache`, it creates a block-cache config, tests normal, direct IO, read-only verify, direct IO with explicit disk block-cache path and block size, repeats verification against cached disk blocks, and finally tests backward-compatible stream config redirecting to block cache.

## State and Persistence Behavior
It creates local data under `$(ROOT_DIR)/data_files`, writes config files, uses `$(MOUNT_DIR)` and `$(TEMP_DIR)`, writes/reads data in Azure containers, and publishes/tails `blobfuse2-logs.txt` on failure.

## Dependencies and Integration Points
It depends on `data.yml`, `mount.yml`, generated containers, account credentials, and repository config templates. It is used by nightly FileCacheValidation and BlockCacheValidation stages.

## Risks and Edge Cases
The template prints configs. A failed cleanup can cause later verification to read stale data. The read-only block-cache case assumes data from previous writes remains available. Stream compatibility is tested under the block-cache branch only.

## Test Signals
Signals are successful MD5 comparisons from `data.yml`, clean mounts across all options, and failure artifacts/log tails when a mode corrupts or hides data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/data-integrity.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/data.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/data.yml

## Purpose
This helper template generates random local files, copies them into a Blobfuse2 mount through several copy methods, and validates mount content hashes against the local originals.

## Important APIs, Types, and Functions
Parameters are `generate_data`, `copy_data`, and `check_consistency`. It uses `dd`, `md5sum`, `cp`, `tar`, GNU `parallel`-style behavior in scripts, kernel cache dropping, and Azure DevOps variable `DATA_DIR`.

## Control Flow
When generating, it recreates `$(ROOT_DIR)/data_files`, emits `DATA_DIR`, and creates files across byte, KB, and MB block sizes and multiple counts. Copy mode writes those files to `$(MOUNT_DIR)` with regular copies and suffix variants for sequential, tar-parallel, and async/parallel paths. Check mode drops kernel page cache, computes hashes for original and copied variants, extracts hash columns, and diffs each mount hash list against the local checklist.

## State and Persistence Behavior
It persists generated files under `DATA_DIR`, temporary checksum files under the home directory, and copied data in the mounted Azure container. It clears old `~/mc*` files before verification.

## Dependencies and Integration Points
It is consumed by `data-integrity.yml` and depends on a mounted Blobfuse2 filesystem plus local data generation having run before copy/check phases.

## Risks and Edge Cases
Large random data generation is IO-heavy. Hash comparison assumes exact filename suffix conventions from copy steps. Dropping kernel cache requires sudo and affects the whole runner.

## Test Signals
Signals are successful creation of all file sizes, no copy errors, and zero diff between local checksum list and every mount checksum variant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/data.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests-spcl.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests-spcl.yml

## Purpose
This template generates a specific Blobfuse2 configuration and runs the shared end-to-end test template against it.

## Important APIs, Types, and Functions
Parameters include config template paths, output config, account metadata, `idstring`, `adls`, distro name, quick-test flag, verbose logging, clone flag, and ADLS symlink behavior. It calls `blobfuse2 gen-test-config`, then delegates to `e2e-tests.yml`.

## Control Flow
The template creates a config from `conf_template`, prints it, calls `e2e-tests.yml` with a mount command using that config and `--default-working-dir=$(System.DefaultWorkingDirectory)`, then unmounts via `cleanup.yml`.

## State and Persistence Behavior
It writes the generated config file and uses the normal mount/cache/container state owned by caller variables.

## Dependencies and Integration Points
It is heavily used by `verbose-tests.yml` to test block cache, file cache, LRU, empty-file, direct-IO, and symlink configurations.

## Risks and Edge Cases
It prints generated config. It assumes `WORK_DIR`, `MOUNT_DIR`, `TEMP_DIR`, and `containerName` exist. The default working directory differs from some other templates that use `$(WORK_DIR)`.

## Test Signals
Signals are config generation success, successful E2E Go tests, log artifact publication when requested, and cleanup unmounting after the run.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests-spcl.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests-xload.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests-xload.yml

## Purpose
This template validates xload/preload behavior by comparing MD5 checksums from a normal file-cache mount and a read-only preload mount.

## Important APIs, Types, and Functions
It installs Python/JQ dependencies, generates configs with `azure_key.yaml` and `azure_key_xload.yaml`, uses `mount.yml`, `head`, `python3 testdata/scripts/generate-parquet-files.py`, `jq`, `md5sum`, and `diff`.

## Control Flow
The template installs dependencies, creates and mounts a normal read-write file-cache config, generates random files and parquet files on the mount, records MD5 sums, generates a preload config, mounts read-only, polls an `xload_stats_*.json` file until `PercentCompleted` is `100`, records MD5 sums again, unmounts, and diffs the two checksum files.

## State and Persistence Behavior
It writes generated data into the Azure container, checksum files in `$(WORK_DIR)`, xload stats JSON in `$(WORK_DIR)`, and logs/traces on failure.

## Dependencies and Integration Points
It is used by the nightly `XloadValidation` stage and depends on `jq`, Python data libraries, parquet generation script, and the stats manager output format.

## Risks and Edge Cases
The polling loop has no explicit timeout inside the shell step beyond job timeout. `ls $(WORK_DIR)/xload_stats_*.json` assumes one stats file exists. Diffing raw `md5sum` output can be sensitive to path/name differences.

## Test Signals
Signals include `PercentCompleted = 100`, matching MD5 output, successful read-only mount, and absence of failure logs/traces.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests-xload.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests.yml

## Purpose
This shared template mounts Blobfuse2 and runs the Go end-to-end test suite against the mounted filesystem.

## Important APIs, Types, and Functions
Parameters include `idstring`, `distro_name`, a step-valued `mountStep`, `adls`, `clone`, `quick_test`, `enable_symlink_adls`, `artifact_name`, and `verbose_log`. It composes `mount.yml`, runs `df`, `pidstat`, and `Go@0 test` under `test/e2e_tests`.

## Control Flow
It mounts using the provided mount step, verifies `df` contains `blobfuse2`, samples CPU usage through `pidstat` and fails if high, then runs `go test -v -timeout=2h ./...` with mount path, ADLS flag, clone flag, temp path, quick-test flag, symlink flag, and distro name. It optionally publishes `blobfuse2-logs.txt`, tails logs on failure, and clears logs always.

## State and Persistence Behavior
It uses the mount/cache paths owned by the caller and clears `blobfuse2-logs.txt` after execution. Optional artifacts persist logs in Azure Pipelines.

## Dependencies and Integration Points
This is the main E2E harness used by `verbose-tests.yml`, proxy tests, release distro tests, and special config templates. It depends on `mount.yml` for cleanup and mount orchestration.

## Risks and Edge Cases
The CPU comparison uses shell string comparison semantics for `[[ $cpu > 5 ]]`, which may misclassify decimal values. Clearing logs can remove debugging context after artifact publication conditions. Test runtime can be long.

## Test Signals
Signals are mount visibility in `df`, low idle CPU after mount, successful Go E2E tests, and log artifacts when verbose logging is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/fio-data-integrity.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/fio-data-integrity.yml

## Purpose
This template runs FIO workloads on a Blobfuse2 mount to validate data integrity across large sequential, random, multithreaded, and sparse-file cases.

## Important APIs, Types, and Functions
It generates file-cache or block-cache configs, mounts through `mount.yml`, installs `fio`, and executes job files under `test/fio/` including `rw.fio`, `seq-write-1f-10th.fio`, `hole_inside_blocks.fio`, and `hole_over_blocks.fio`.

## Control Flow
After config generation and mount, it clears the mount directory before each workload, then runs read/write 10G single-file, 1G x 10 files, random write variants, multithreaded offset writes, and sparse-hole workloads. Failure paths publish logs and traces.

## State and Persistence Behavior
It writes large FIO test data into the mounted Azure container, uses local cache paths, and emits `blobfuse2-logs.txt`/trace diagnostics on failure.

## Dependencies and Integration Points
It is optionally invoked by the nightly `FioTests` stage for file cache and block cache. It depends on FIO job files and adequate storage capacity/time.

## Risks and Edge Cases
The workloads are heavy and can be expensive or timeout-prone. Repeated `rm -rf ./*` depends on working directory being the mount. Validation relies on FIO job integrity settings in the job files, as noted by the file comments.

## Test Signals
Signals are successful FIO exits for all job files, no integrity mismatch, and useful log/trace output on failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/fio-data-integrity.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/huge-list-test.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/huge-list-test.yml

## Purpose
This template validates listing behavior and request count on a pre-populated huge container, such as the `million-files` benchmark container.

## Important APIs, Types, and Functions
Parameters include `idstring`, a step-valued `mountStep`, and `distro_name`. It uses `fusermount`, `pidof`, `df`, `ls -1 | wc -l`, log grep for `OUTGOING REQUEST`, and log clearing.

## Control Flow
It pre-cleans stale mounts/processes, runs the supplied mount step, waits and verifies the mount, lists the mount root and counts entries, counts outgoing requests in `blobfuse2-logs.txt`, prints logs, clears logs, then unmounts without deleting container data.

## State and Persistence Behavior
It intentionally does not delete container data because the huge dataset is reused. It mutates only mount state and local logs.

## Dependencies and Integration Points
It is used by `verbose-tests.yml` after generating a config against `huge_container`. It depends on a pre-existing container with many entries.

## Risks and Edge Cases
If cleanup deletes mount contents accidentally, the shared huge dataset could be damaged, so this template avoids container cleanup. Listing can exceed timeout if the container size or service latency changes.

## Test Signals
Signals include successful root listing count, acceptable outgoing request count from logs, and clean unmount after the listing test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/huge-list-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/invalid-command-tests.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/invalid-command-tests.yml

## Purpose
This template checks that Blobfuse2 commands return the expected invalid-flag exit code when passed unsupported options.

## Important APIs, Types, and Functions
It invokes root `blobfuse2`, `mount`, `unmount`, `mountv1`, `secure`, and `version` commands with `--invalid-param` and expects exit code `2`.

## Control Flow
Each script starts the command in the background and immediately checks `$?`, exiting success only when the command launch returned `2`.

## State and Persistence Behavior
No persistent state is intended. Some commands reference `$(MOUNT_DIR)` but should fail before mutating mount state.

## Dependencies and Integration Points
It is used early in nightly base tests after build. It validates CLI argument parsing across command groups.

## Risks and Edge Cases
Using `&` backgrounds the command, so `$?` usually reports background launch success rather than the process exit code. This may make the test ineffective unless the shell fails before backgrounding. It does not use `wait`.

## Test Signals
Correct signals should be exit code `2` for each invalid command. A stronger test would remove backgrounding and assert directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/invalid-command-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/linux-git.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/linux-git.yml

## Purpose
This template stress-tests Blobfuse2 by downloading, extracting, building Linux source, and cloning large Git repositories on the mount.

## Important APIs, Types, and Functions
It installs Linux build dependencies, generates file-cache or block-cache configs, mounts with `--file-cache-timeout=3200 --block-cache-pool-size=2048`, downloads Linux 6.13 tarball, runs `unxz`, `tar`, `make defconfig`, `make -j$(nproc)`, `make clean`, and clones VS Code, libfuse, and Azure Storage Fuse repositories.

## Control Flow
After installing tools and generating the selected cache config, it mounts Blobfuse2, prints mount contents, downloads and expands Linux source directly on the mount, builds and rebuilds it, then performs several Git clone operations under the mount.

## State and Persistence Behavior
It writes very large source trees and Git repositories into the mounted container and uses local cache storage. Cleanup is done by the calling nightly stage.

## Dependencies and Integration Points
It is optionally invoked by nightly `CompileLinux_GitClone` when `linux_git_test` is not `none`. It depends on internet access to kernel.org and GitHub plus build tool availability.

## Risks and Edge Cases
The test is bandwidth, CPU, and storage intensive. It downloads a fixed Linux version but labels it "latest". External network availability can fail the pipeline independent of Blobfuse2. Large builds can expose cache pressure and timeout issues.

## Test Signals
Signals include successful tar extraction, two successful kernel builds, successful `make clean`, and completed Git clones without filesystem errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/linux-git.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/mount-test.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/mount-test.yml

## Purpose
This template runs the Go mount test suite against a generated config.

## Important APIs, Types, and Functions
Parameters are `config` and `idstring`. It composes `cleanup.yml`, then runs `Go@0 test` for `test/mount_test/mount_test.go` with working dir, mount path, config file, and build tags.

## Control Flow
It unmounts first, runs the mount test suite with a two-hour timeout and `continueOnError: true`, prints `blobfuse2-logs.txt`, clears logs, then unmounts again.

## State and Persistence Behavior
It uses and clears mount state and logs. It does not delete containers.

## Dependencies and Integration Points
It is used by `verbose-tests.yml` for mount behavior validation after config generation.

## Risks and Edge Cases
`continueOnError: true` can allow later steps to proceed after mount test failures unless the containing pipeline checks task result semantics. Logs are always cleared after printing.

## Test Signals
Signals are Go test results from `test/mount_test`, Blobfuse2 logs, and clean unmount before and after the suite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/mount-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/mount.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/mount.yml

## Purpose
This shared template standardizes pre-mount cleanup, mount execution, wait, process visibility, and optional mount directory cleanup.

## Important APIs, Types, and Functions
Parameters include a step-valued `mountStep`, display `prefix`, and `ro_mount`. It composes `cleanup.yml`, runs the supplied mount step, sleeps, prints `ps` output, and conditionally clears `$(MOUNT_DIR)/*`.

## Control Flow
Each use first unmounts and avoids container deletion, executes the caller-provided mount command, waits ten seconds, prints Blobfuse2 processes, and if not a read-only mount, removes existing files under the mount as pre-start cleanup.

## State and Persistence Behavior
It mutates the active mount and may delete all files under `$(MOUNT_DIR)` after mounting. It relies on caller-owned Azure container state.

## Dependencies and Integration Points
Most test templates call this before running filesystem operations. It centralizes the mount lifecycle for E2E, data, FIO, stress, scenario, and health monitor tests.

## Risks and Edge Cases
Because cleanup of mount contents happens after mounting, an accidental wrong mount path or failed unmount can delete local or remote data. The `ro_mount` flag must be set correctly for read-only validation.

## Test Signals
Signals are successful mount command completion, visible Blobfuse2 process, and clean pre-start directory state for write tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/mount.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/package-install.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/package-install.yml

## Purpose
This template installs distro-specific build and runtime dependencies required for Blobfuse2 Azure pipeline jobs.

## Important APIs, Types, and Functions
It uses apt, yum/dnf, zypper, and tdnf branches conditioned on `variables['distro']`. It installs compilers, git, make/cmake, Python, FUSE/FUSE3 development packages, GNU parallel, and Azure CLI for Ubuntu.

## Control Flow
For Ubuntu it handles apt locks, installs build tools, conditionally installs FUSE2 or FUSE3 based on `$(tags)`, verifies fusermount versions, and installs Azure CLI. RHEL, CentOS, Oracle, Rocky, SUSE, and Mariner branches install equivalent packages with distro-specific repository fixes.

## State and Persistence Behavior
It mutates the agent OS package state and can update system packages. No repository files are persisted.

## Dependencies and Integration Points
It is the first step of `build.yml` and underpins all Azure DevOps jobs across distro matrices.

## Risks and Edge Cases
The Ubuntu branch aggressively kills apt processes and lock holders. Distro package names and repository availability can drift. Azure CLI is installed only in Ubuntu branch, while later templates may assume `az` exists.

## Test Signals
Signals include successful package manager commands, available compiler/FUSE tools, `az --version` on Ubuntu, and later build/mount steps succeeding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/package-install.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/release-distro-tests.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/release-distro-tests.yml

## Purpose
This template validates an installed Blobfuse2 release package on block blob and ADLS accounts by generating configs, mounting, and running quick E2E tests.

## Important APIs, Types, and Functions
Parameters include root/work/mount/temp directories, container, and extra mount flags. It calls installed `blobfuse2 version`, `blobfuse2 --help`, `blobfuse2 gen-test-config`, `blobfuse2 mount/unmount`, and `Go@0 test` under `test/e2e_tests`.

## Control Flow
It checks version/help, prepares mount and temp directories, generates a block config using block account variables, mounts block blob, verifies mount with `df`, runs quick E2E tests, unmounts and clears logs, then repeats config generation, mount, verify, E2E, and unmount for ADLS.

## State and Persistence Behavior
It writes block and ADLS config files under the root directory, uses the installed system `blobfuse2`, and writes test data into the provided container. Logs are printed and cleared.

## Dependencies and Integration Points
It is intended for release distro validation where Blobfuse2 has already been installed from a package. It depends on repository test code and Azure account variables.

## Risks and Edge Cases
It prints configs containing credentials unless masking catches them. It kills Blobfuse2 before mounting. The Go tests rely on source checkout even though the binary is system-installed.

## Test Signals
Signals include installed binary version/help output, successful block and ADLS mounts, and quick E2E pass for both account types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/release-distro-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/rman-backup-simulation.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/rman-backup-simulation.yml

## Purpose
This template simulates Oracle RMAN backup workloads on a Blobfuse2 mount to validate database-like file integrity without requiring Oracle XE.

## Important APIs, Types, and Functions
It generates file-cache or block-cache configs, mounts through `mount.yml`, and runs `test/scripts/rman_backup_simulation.sh $(MOUNT_DIR) $(ROOT_DIR) 10M,100M,1G,10G`.

## Control Flow
The template creates a cache-mode-specific config from Azure key templates, mounts Blobfuse2 with `--file-cache-timeout=3200`, runs the simulation script for several database file sizes, and prints logs/traces on failure.

## State and Persistence Behavior
It writes simulated RMAN backup data into the mounted container and uses local root/cache directories. It does not clean up itself beyond caller cleanup.

## Dependencies and Integration Points
It is used by nightly `RmanBackupTests` on Oracle Linux before the real RMAN test.

## Risks and Edge Cases
Large 10G simulations can stress storage capacity and timeouts. The script is external to the template, so integrity guarantees depend on its validation behavior.

## Test Signals
Signals are successful simulation script exit across all sizes and no Blobfuse2 logs/traces indicating write/read failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/rman-backup-simulation.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/rman-backup.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/rman-backup.yml

## Purpose
This template runs actual Oracle RMAN backup workloads against a Blobfuse2 mount to validate database backup behavior and integrity.

## Important APIs, Types, and Functions
It generates cache-mode-specific configs, mounts through `mount.yml` with `-o allow_other`, edits `/etc/fuse.conf` to enable `user_allow_other`, and runs `test/scripts/rman_backup.sh $(MOUNT_DIR) $(ROOT_DIR) 10M,100M,1G,10G`.

## Control Flow
The template creates the config, mounts Blobfuse2 after enabling FUSE `allow_other` so the `oracle` user can access the mount, runs the RMAN script for multiple database file sizes, and prints logs/traces on failure.

## State and Persistence Behavior
It mutates `/etc/fuse.conf`, writes real RMAN backup data to the mounted container, and depends on Oracle XE state on the agent.

## Dependencies and Integration Points
It is used by nightly `RmanBackupTests` on Oracle Linux and requires Oracle XE availability or installation by the script.

## Risks and Edge Cases
System-level FUSE config is modified. The test is long and environment-specific. Block-cache RMAN paths are disabled in the nightly pipeline due to known issues, indicating risk around that mode.

## Test Signals
Signals include successful Oracle RMAN script completion for all sizes, no permission errors from `allow_other`, and no integrity failures in logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/rman-backup.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/scenario.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/scenario.yml

## Purpose
This template runs targeted Go filesystem scenario tests against normal and direct-IO Blobfuse2 mounts.

## Important APIs, Types, and Functions
It generates file-cache or block-cache configs, creates a second local temp mountpoint `$(WORK_DIR)/t1`, mounts with `mount.yml`, and runs `go test -v ./test/scenarios -mountpoints="$(MOUNT_DIR),$(WORK_DIR)/t1"` with optional `-mount-point-direct-io=true`.

## Control Flow
After config generation and temp directory creation, it mounts normally and runs the scenario suite comparing/using the Blobfuse2 mount and local path. It then remounts with `-o direct_io` and reruns the scenario suite with the direct-IO flag.

## State and Persistence Behavior
It writes scenario data into both the Blobfuse2 mount and `$(WORK_DIR)/t1`, and prints logs/traces on failure.

## Dependencies and Integration Points
It is optionally used by nightly `ScenarioTests`, currently for file cache while block-cache scenario invocation is commented out due to known issues.

## Risks and Edge Cases
The local comparison directory is under `WORK_DIR` and may retain state if not cleaned. Known block-cache issues mean coverage is incomplete by design.

## Test Signals
Signals are successful Go scenario tests in normal and direct-IO modes plus failure log artifacts when scenario operations diverge.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/scenario.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/stress-test.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/stress-test.yml

## Purpose
This template mounts Blobfuse2 and runs the repository stress test suite.

## Important APIs, Types, and Functions
Parameters include `stress_dir`, `idstring`, `parallel`, a step-valued `mountStep`, `quick`, and `distro_name`. It composes `mount.yml`, runs `Go@0 test test/stress_test/stress_test.go`, and cleans up through `cleanup.yml`.

## Control Flow
It mounts using the provided step, runs stress tests with mount path and quick flag under a 120-minute timeout, deletes all files under the mount, prints and clears logs, then unmounts without deleting containers.

## State and Persistence Behavior
It creates stress-test data in the mounted container, clears it with `rm -rf`, and clears `blobfuse2-logs.txt`.

## Dependencies and Integration Points
It is invoked by `verbose-tests.yml` as part of comprehensive storage account testing.

## Risks and Edge Cases
The Go stress test has `continueOnError: true`, so downstream steps can continue after failures. The `stress_dir` and `parallel` parameters are not used by the current commands. Deleting mount contents is broad.

## Test Signals
Signals are Go stress test output, clean file deletion after the run, and logs showing no Blobfuse2 errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/stress-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/verbose-tests.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/verbose-tests.yml

## Purpose
This orchestration template runs the broadest set of E2E, auth, cache, mount, stress, and huge-list tests for one storage service/account combination.

## Important APIs, Types, and Functions
Parameters cover account endpoint/type/name/key/SAS, credential booleans, Azurite config, stress and huge-list inputs, distro name, quick flags, and verbose logging. It composes `e2e-tests.yml`, `e2e-tests-spcl.yml`, `mount-test.yml`, `stress-test.yml`, and `huge-list-test.yml`, and generates configs for key, SAS, Azure CLI, Azurite, block-cache, file-cache, LRU, empty-file, direct-IO, symlink, stress, and huge-list variants.

## Control Flow
It conditionally creates key, SAS, Azure CLI, and Azurite configs and runs E2E tests for enabled credential types. It always runs block-cache special E2E, then several file-cache/symlink/direct-IO special configs. If Azurite is enabled, it installs and starts Azurite with documented fake credentials. It generates a huge config, runs mount tests, stress tests, then regenerates config against the huge container and runs listing tests.

## State and Persistence Behavior
It writes many generated config files, may start an Azurite service and create a local emulator container, writes remote test data into Azure containers, uses shared mount/cache paths, and emits logs/artifacts through child templates.

## Dependencies and Integration Points
It is called by nightly base tests for block blob and ADLS. It depends on generated containers from `build.yml`, storage credentials, child templates, and repository config templates.

## Risks and Edge Cases
The parameter surface is large, and unused service principal parameters suggest drift. Config files are printed. Azurite uses public fake credentials intentionally. Failures in child templates with `continueOnError` can reduce strictness. Huge-list tests rely on a persistent preloaded container.

## Test Signals
Signals include successful E2E passes for enabled credentials, block/file cache special config passes, mount-test and stress-test completion, and huge-list output/counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/verbose-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/verify-auth.yml -->
# sources/user-network-fs/blobfuse2/azure-pipeline-templates/verify-auth.yml

## Purpose
This template performs a lightweight mount-and-file-operations check for an authentication configuration.

## Important APIs, Types, and Functions
It accepts `idstring`, `distro_name`, and a step-valued `mountStep`. It uses `mount.yml` and then basic shell file operations on `$(MOUNT_DIR)`.

## Control Flow
The template mounts via the supplied mount step, prints `df`, Blobfuse2 processes, and a mount listing, then removes existing mount contents, creates directory `A`, creates/copies small files, lists the resulting tree, removes `A`, prints `blobfuse2-logs.txt`, and clears the log file.

## State and Persistence Behavior
It writes small files into the mounted test container, deletes the test directory, and clears local Blobfuse2 logs. It does not unmount or delete containers itself.

## Dependencies and Integration Points
It is used by proxy and MSI portions of the nightly pipeline to validate SAS/MSI auth configs without running the full E2E suite.

## Risks and Edge Cases
The check is intentionally shallow and may not catch auth edge cases beyond mount and simple IO. The listing, fileops, and remove steps all use `continueOnError: true`, so caller-level result handling is important. It depends on the supplied mount step already using the intended credential config.

## Test Signals
Signals are successful mount, file create/write/copy/list/remove operations, and no authentication errors in Blobfuse2 logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/azure-pipeline-templates/verify-auth.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-1es_ci.yaml -->
# sources/user-network-fs/blobfuse2/blobfuse2-1es_ci.yaml

## Purpose
This Azure DevOps 1ES CI pipeline runs official compliance-backed CI for PRs, including mirrored fork PR branches, with build, unit tests, lint, formatting, notices, copyright, cleanup, and component governance.

## Important APIs, Types, and Functions
It triggers on `pr-mirror/*` branches and PRs to `main` excluding documentation-only paths. It extends `v1/1ES.Official.PipelineTemplate.yml@1esPipelines`, uses Windows source analysis pool settings, and composes `azure-pipeline-templates/build.yml` and `cleanup.yml`. It runs `golangci-lint v2.11.0`, `gofmt`, `notices_fix.sh`, grep copyright checks, and `ComponentGovernanceComponentDetection@0`.

## Control Flow
The CI stage runs a distro/architecture matrix for Ubuntu 20, Ubuntu 22, and Ubuntu 22 ARM64 on 1ES pools. Each job builds and runs unit tests, executes lint with build tags, checks current-year Microsoft copyright headers, checks Go formatting, regenerates NOTICE and verifies diff size, deletes containers, then runs component governance.

## State and Persistence Behavior
It creates temporary Azure containers through `build.yml`, writes coverage/log files locally, mutates NOTICE in the workspace for diff checking, and relies on `cleanup.yml` to delete containers. Compliance results persist in Azure DevOps/1ES systems.

## Dependencies and Integration Points
It connects GitHub PR mirroring (`pr-mirror.yml`) to Azure DevOps. It depends on variable group `NightlyBlobFuse`, 1ES templates, custom agent pools, build templates, and the repository lint config.

## Risks and Edge Cases
The mirror-branch trigger must be paired with trusted YAML loading to avoid fork-authored pipeline changes. Lint logic expects one line of output for no issues, which is fragile. `cleanup.yml` with `unmount: false` deletes containers but does not clean mount state.

## Test Signals
Signals include passing matrix jobs, clean lint/format/notice/copyright checks, deleted temporary containers, and component governance registration without high alerts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-1es_ci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-code-coverage.yaml -->
# sources/user-network-fs/blobfuse2/blobfuse2-code-coverage.yaml

## Purpose
This Azure DevOps pipeline collects broad Blobfuse2 Go coverage across unit tests, mounted E2E paths, CLI commands, secure config paths, health monitor commands, proxy paths, and account cleanup.

## Important APIs, Types, and Functions
Parameters are `coverage_test` and `cleanup_test`. It composes `build.yml` and `cleanup.yml`, builds a coverage binary with `go test -coverpkg="./..." -c`, runs many `blobfuse2.test -test.coverprofile=...` commands, runs E2E tests, generates coverage reports with `go tool cover`, publishes build artifacts, and runs `test/scripts/coveragecheck.sh`.

## Control Flow
The `BuildAndTest` stage runs Ubuntu 20 and Ubuntu 22 matrix jobs. It builds containers and binaries, runs unit coverage, builds `blobfuse2.test`, generates block and ADLS configs, mounts with coverage collection including profiler/health-monitor configs, exercises CLI commands for generate, mount/list/unmount, secure encrypt/set, doc, version, config-change simulation, health-monitor stop, and proxy variants, merges `.cov` files while excluding selected packages, publishes reports, checks overall and file-level thresholds, and deletes containers. The `AccountCleanUp` stage optionally installs Go and runs storage account cleanup tests against block and ADLS accounts.

## State and Persistence Behavior
It writes many `.cov`, `.rpt`, and `.html` files, profiler temp configs, secure encrypted configs, proxy logs, mounted data, and Azure test containers. Persistent outputs are published coverage artifacts and cleaned storage accounts.

## Dependencies and Integration Points
It depends on `NightlyBlobFuse`, custom Ubuntu pools, storage accounts, E2E tests, coverage scripts, mitmproxy, and health monitor binary support.

## Risks and Edge Cases
The pipeline is long and stateful, with many background mounts and forced unmounts. Coverage filtering is hard-coded and can hide changed packages. There is a duplicate `workingDirectory` key in the remount test snippet. Proxy environment setup may not apply globally. Secrets are used in generated configs.

## Test Signals
Signals include coverage artifact publication, `coveragecheck.sh` pass, successful block/ADLS/proxy E2E coverage runs, valid health monitor stop coverage, and account cleanup test completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-code-coverage.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-nightly.yaml -->
# sources/user-network-fs/blobfuse2/blobfuse2-nightly.yaml

## Purpose
This is the main daily Blobfuse2 validation pipeline. It builds and tests across distros, account types, auth modes, cache modes, proxy/MSI paths, data integrity, xload, health monitor, FIO, scenarios, RMAN, and optional Linux/Git workloads.

## Important APIs, Types, and Functions
Parameters toggle `base_test`, `exhaustive_test`, non-Ubuntu distros, `fio_test`, `scenario_tests`, `rman_backup_test`, `linux_git_test`, `proxy_test`, `msi_test`, `quick_stress`, `verbose_log`, and `healthmon`. It composes most templates in `azure-pipeline-templates`, especially `build.yml`, `verbose-tests.yml`, `invalid-command-tests.yml`, `verify-auth.yml`, `data-integrity.yml`, `e2e-tests-xload.yml`, `bfusemon.yml`, `fio-data-integrity.yml`, `scenario.yml`, `rman-backup*.yml`, `linux-git.yml`, and `cleanup.yml`.

## Control Flow
The daily schedule starts with `BuildAndTest` when enabled. Block Blob and ADLS jobs build and optionally run exhaustive verbose tests over Ubuntu 20, Ubuntu 22, and ARM64. Optional proxy tests generate proxy configs and validate key/SAS auth through E2E/auth templates. Optional MSI tests build with MSI enabled and verify block/ADLS MSI mounts. Later stages validate file cache and block cache data integrity for block and ADLS, xload preload behavior, health monitor output, optional FIO integrity workloads, scenario tests, RMAN simulation and Oracle XE backup tests, and optional Linux compile/Git clone workloads.

## State and Persistence Behavior
Each job creates Azure containers, mount/cache directories, generated configs, logs, data files, and sometimes persistent huge-list container reads. Cleanup stages usually delete containers except RMAN cleanup leaves containers undeleted in its shown configuration. Variable group `NightlyBlobFuse` supplies credentials and account names.

## Dependencies and Integration Points
This pipeline is the integration hub for the Azure DevOps template library. It depends on many custom self-hosted pools, distro-specific images, Azure storage accounts, Oracle agents, optional huge containers, proxy tooling, Azurite in child templates, and Go test suites.

## Risks and Edge Cases
The YAML contains a duplicated `matrix:` key in the Healthmon stage, which may be invalid or confusing. Many stages are conditionally enabled, so default coverage omits FIO and Linux/Git workloads. Some child templates use `continueOnError`, broad process kills, and config printing. The pipeline is sensitive to stale self-hosted agent state.

## Test Signals
Signals are stage-level pass/fail across all enabled parameter combinations, created/deleted container balance, no stale mounts, successful data checksum comparisons, E2E and stress Go test passes, RMAN integrity success, and clean logs/traces.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-nightly.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-perf.yaml -->
# sources/user-network-fs/blobfuse2/blobfuse2-perf.yaml

## Purpose
This weekly Azure DevOps performance pipeline compares Blobfuse2 cache modes, Blobfuse v1 behavior, FIO workloads, upload/download, Git clone performance, and optionally ResNet50 image classification throughput.

## Important APIs, Types, and Functions
It schedules weekly Saturday runs, has parameter `resnet_test`, uses `build.yml` and `cleanup.yml`, generates Blobfuse2 and Blobfuse v1 configs, and invokes scripts `test/scripts/file_block_compare.sh`, `fio.sh`, `run.sh`, `git_clone.sh`, `test/perf_test/resnet50_classify.py`, and `test/perf_test/generate_perf_report.py`.

## Control Flow
The `ShortRunning` stage runs on the perf pool, installs libraries and Blobfuse v1, cleans the workspace, clones the repo manually, checks out the pipeline branch, builds Blobfuse2, generates v2 file/block configs and v1 config, runs block-vs-file compare, sequential/random/CSI FIO tests, upload/download tests, and Git clone tests, printing result files after each. If enabled, `LongRunning` installs Python ML dependencies, compares an older Blobfuse2 release package with the current main build on ResNet50, generates a performance report, publishes the JSON artifact, unmounts, and cleans up.

## State and Persistence Behavior
It uses fixed paths under `/home/vsts/workv2` and `/mnt/blobfuse2tmp`, writes performance result files in the repo workspace, writes `blobfuse2-perf.json`, mounts/unmounts storage, and publishes the performance JSON artifact.

## Dependencies and Integration Points
It depends on a dedicated `blobfuse-perf-pool`, performance storage account variables, internet access for repo clone and old release download, Blobfuse v1 apt package, FIO, Python/TensorFlow/Pillow for ResNet, and repository perf scripts.

## Risks and Edge Cases
Performance jobs are highly sensitive to self-hosted runner drift, network conditions, and fixed workspace paths. The template passes parameter names to `build.yml` that do not match its current parameter contract, suggesting legacy drift. It clones from GitHub rather than using checkout, so branch resolution must work from `Build.SourceBranch`.

## Test Signals
Signals include populated result text files, successful FIO/upload/download/git clone scripts, published `Blobfuse2_performance_report`, and regression script pass for ResNet metrics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-perf.yaml -->
