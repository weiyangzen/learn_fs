# subset-b-000100 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-stress.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-stress.sh

## Purpose
Runs a broad stress suite against `fuse-overlayfs` by repeatedly creating a temporary lower/upper/work/merged overlay, mounting it, exercising high-volume and concurrent filesystem operations, and verifying postconditions. It is intended to expose races in copy-up, whiteout creation, readdir, hardlink accounting, symlink handling, xattrs, permission changes, sparse files, fsync, and multi-layer merge behavior.

## Important APIs, Types, And Functions
- `NPROC` defaults to `nproc` and controls parallel worker fan-out; `SCALE` multiplies test sizes.
- `cleanup`, registered with `trap EXIT`, unmounts `$MERGED` and removes `$TESTDIR`.
- `mount_overlay`, `remount_overlay`, and `reset_overlay` centralize mount lifecycle.
- `elapsed` returns elapsed milliseconds from a captured epoch-millis timestamp.
- `chunk_end COUNT NPROC WORKER_INDEX` gives each worker a range and makes the last worker absorb remainders.
- External test tools include `fuse-overlayfs`, `umount`, `stat`, `ln`, `chown`, `setfattr`, `getfattr`, `fallocate`, `dd`, `mknod`, and `find`.

## Control Flow
The script is linear and fail-fast under `set -xeuo pipefail`. Each numbered block resets state, prepares lower and/or merged content, mounts the overlay, runs a specific workload, validates invariants, then resets. The 40 workloads cover sequential and parallel file creation, deep and wide directories, stat storms, concurrent reads/writes, rename storms, hardlinks, copy-up storms, mixed create/stat/write/rename/unlink workloads, unlink storms, mount cycles, container-storage-like hardlink rewrites, large file throughput, concurrent mkdir/rmdir, same-file copy-up races, readdir during mutations, symlink and xattr storms, whiteout persistence, fallocate writes, cross-directory renames, copy-up/stat races, mmap-style reads, chmod/chown copy-up, truncation, multi-lower overlays, rapid open/close, tmpfile patterns, nested lower directories, concurrent appends, read-during-unlink, sparse files, lower-layer whiteout ordering, concurrent fsync, and interleaved copy-up/stat checks.

## State And Persistence
State is scoped to a `mktemp` directory under `/tmp`. The suite deliberately preserves or discards `upper` and `workdir` depending on the test: most tests remove all layers, while whiteout persistence remounts with the same upper/work layers. Multi-layer tests use separate lower directories and remove them manually. No repository files are modified.

## Dependencies And Integration Points
This is an integration test for the installed `fuse-overlayfs` binary and kernel/FUSE support. It assumes GNU-style userland flags such as `stat -c`, `dd conv=fsync`, `touch -h -d`, `getfattr --only-values`, and overlay lowerdir colon ordering. It complements narrower symlink, xattr, unlink, and unprivileged tests in the same directory.

## Risks And Edge Cases
`CHUNK=$((COUNT / NPROC))` can be zero if `NPROC` exceeds small scaled counts, causing duplicated ranges or empty worker ranges in some tests. The suite is intentionally expensive when `SCALE` or `NPROC` is high. Some xattr operations ignore failures, which keeps the stress portable but weakens assertions on filesystems without user xattr support. Tests using `mknod` whiteouts, `chown`, `fallocate`, and mount/unmount require sufficient privileges/capabilities.

## Test Signals
Success requires all shell assertions to pass and ends with `All stress tests passed!`. Failure points identify functional regressions in visibility, content preservation, link counts, whiteout semantics, final permissions, file sizes, and surviving original entries after concurrent mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-stress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-symlinks.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-symlinks.sh

## Purpose
Validates symlink behavior through `fuse-overlayfs`, including newly created symlinks, dangling links, links from lower layers, directory symlinks, symlink timestamp updates, upper symlinks overriding lower files, relative paths, chained symlink resolution, and replacing lower files with symlinks.

## Important APIs, Types, And Functions
- `cleanup` unmounts `$MERGED` and removes the temporary test directory on exit.
- Each test manually creates `lower`, `upper`, `workdir`, and `merged`, invokes `fuse-overlayfs -o lowerdir=...,upperdir=...,workdir=...`, performs shell assertions, unmounts, and removes layer directories.
- Uses `ln -s`, `readlink`, `test -L`, `test -d`, `touch -h -d`, `stat --format`, `grep`, and `rm`.

## Control Flow
The script executes ten independent cases under `set -xeuo pipefail`. It first verifies basic symlink creation and target traversal, then dangling link metadata without target access, lower-layer symlink visibility, directory symlink traversal, symlink timestamp mutation via `touch -h`, link removal without deleting the target, upper-layer symlink precedence over a lower regular file, relative link traversal in nested directories, chained link resolution, and lower-file deletion followed by upper symlink replacement.

## State And Persistence
All state lives under `/tmp/test-symlinks.*`. Each test tears down its layers after unmounting, so cases are isolated and do not rely on prior whiteouts or upperdir contents.

## Dependencies And Integration Points
Depends on `fuse-overlayfs`, mount permissions, GNU `stat`, and symlink-aware `touch -h`. It specifically exercises overlay path resolution and copy-up/whiteout interactions that regular file tests do not cover.

## Risks And Edge Cases
The timestamp test assumes the filesystem preserves symlink timestamps and formats `stat --format "%y"` with the expected second value. Absolute symlink behavior is mentioned in the header but the body only tests a relative nested symlink. Because each case is isolated, it does not test symlink persistence across remounts.

## Test Signals
Passing output ends with `All symlink tests passed!`. Failures indicate regressions in link metadata, overlay precedence, target traversal, or file-versus-symlink replacement behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-symlinks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-xattr.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-xattr.sh

## Purpose
Exercises extended attribute support in `fuse-overlayfs`: setting, reading, listing, removing, directory xattrs, lower-layer xattr visibility, internal xattr filtering, large values, copy-up preservation, xattr-triggered copy-up, multiple xattrs, and the `noxattrs=1` mount option.

## Important APIs, Types, And Functions
- `cleanup` is the only shell function and performs unmount/removal on exit.
- Test operations use `setfattr`, `getfattr`, `grep`, Python-generated 4000-byte values, `test -f upper/...`, and `fuse-overlayfs` mount options.
- The `noxattrs=1` case verifies that setting a user xattr fails.

## Control Flow
Eleven isolated cases mount a fresh overlay, run one xattr scenario, assert expected values or errors, then unmount and delete layers. Lower-layer cases prepare xattrs before mounting. Copy-up cases modify or set xattrs on lower files and then validate that metadata remains visible and, for xattr setting, that the file appears in the upperdir.

## State And Persistence
Temporary state is under `/tmp/test-xattr.*`. Each case deletes layers, so xattr state is not shared. The copy-up tests intentionally inspect the backing `upper` path before teardown, which couples the test to upperdir implementation details.

## Dependencies And Integration Points
Requires xattr-capable backing filesystems and the attr tools package. Integrates with `fuse-overlayfs` internal metadata filtering by checking that `user.fuseoverlayfs.origin` does not leak through `getfattr -d`.

## Risks And Edge Cases
Some backing filesystems may reject large xattrs or user xattrs, causing environment-specific failures. Internal xattr setup ignores failure, so that test becomes weaker if setting the lower internal xattr is unsupported. The `noxattrs` case assumes failure of `setfattr` is observable through the command exit status.

## Test Signals
Passing output ends with `All xattr tests passed!`. Strong signals include copy-up preservation of lower xattrs, upperdir materialization after setting xattrs on lower files, and filtering of internal `fuseoverlayfs` metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-xattr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/unlink.sh -->
# sources/cloud-native/fuse-overlayfs/tests/unlink.sh

## Purpose
Tests unlink and hardlink semantics through a simple `fuse-overlayfs` mount. It verifies removing a lower-layer file hides it and that hardlinked upper files preserve content and link behavior after one name is removed and recreated.

## Important APIs, Types, And Functions
- Uses POSIX shell with `set -ex`.
- Mounts `fuse-overlayfs` with `lowerdir`, `upperdir`, `workdir`, `suid`, and `dev`.
- Uses `unlink`, `rm`, `ln`, `grep`, and an umount status override via `EXPECT_UMOUNT_STATUS`.

## Control Flow
The script creates `unlink-test`, prepares a lower file `a`, mounts the overlay, unlinks `merged/a`, and asserts it is no longer visible. It then creates `merged/foo`, hardlinks `foo2`, removes `foo`, checks `foo2`, recreates `foo` as a hardlink to `foo2`, appends through `foo2`, and verifies both names expose the combined content before unmounting.

## State And Persistence
State is local to `unlink-test`, which is removed at startup but not explicitly removed at the end. Overlay upper state is inspected indirectly through merged visibility only.

## Dependencies And Integration Points
Depends on `fuse-overlayfs` and hardlink support in the backing filesystem. It complements the larger stress unlink/hardlink tests with a small deterministic regression case.

## Risks And Edge Cases
The script does not install an EXIT trap, so interrupted runs can leave a mounted test tree. It assumes the current directory is safe for creating `unlink-test`. The `suid,dev` options may be relevant to privilege-sensitive environments.

## Test Signals
Failures catch regressions where lower unlinks fail to create a hiding entry, hardlink content is lost after unlink/relink, or unmount status differs from `EXPECT_UMOUNT_STATUS`.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/unlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/unpriv.sh -->
# sources/cloud-native/fuse-overlayfs/tests/unpriv.sh

## Purpose
Validates unprivileged `fuse-overlayfs` behavior, especially lower-file deletion, mode changes, whiteout representation, security xattr isolation with `xattr_permissions=2`, and UID/GID preservation across `chgrp` and `chmod` inside user namespaces.

## Important APIs, Types, And Functions
- Starts with `test $(id -u) -gt 0`, requiring a non-root user.
- Uses `fusermount -u` for unprivileged unmounts.
- Uses `unshare -r setcap/getcap` to exercise security capabilities in a root user namespace.
- Uses `podman unshare` to check ownership after group and mode changes.
- Honors `FUSE_OVERLAYFS_DISABLE_OVL_WHITEOUT` to decide whether whiteout should be `.wh.a` or a character device at `upper/a`.

## Control Flow
The first overlay mounts read-only lower files, deletes `merged/a`, chmods `merged/b` to mode `406`, verifies merged and upper modes, and checks the expected whiteout representation. After unmount, it prepares an upper file with a capability, mounts with `xattr_permissions=2`, verifies the security xattr is hidden from the merged view until set through the merged file, then confirms ownership remains `0:1` after `podman unshare chgrp 1` and after `chmod 600`.

## State And Persistence
The script uses a local `unpriv-test` directory, resets layer directories between the two phases, and leaves cleanup to the initial `rm -rf` on subsequent runs. It intentionally inspects upperdir whiteouts and metadata as persistent side effects of merged operations.

## Dependencies And Integration Points
Requires unprivileged FUSE, user namespaces, `fusermount`, `setcap/getcap`, and Podman. It directly tests `fuse-overlayfs` behavior used by rootless container stacks.

## Risks And Edge Cases
Environment availability is the main risk: user namespaces, Podman, file capabilities, and whiteout implementation can vary. The script has no trap, so failed unmounts can leave mounted state. Assertions are numeric and Linux-specific.

## Test Signals
The strongest signals are successful non-root mount/unmount, correct hiding of deleted lower files, correct upper mode after chmod, matching configured whiteout representation, security xattr isolation, and UID/GID preservation through metadata changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/unpriv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.codecov.yml -->
# sources/cloud-native/moby/.codecov.yml

## Purpose
Configures Codecov reporting for Moby by disabling comments and annotations, relaxing project coverage status, disabling patch and changes statuses, and ignoring vendored dependencies.

## Important APIs, Types, And Functions
- `comment: false` disables Codecov PR comments.
- `github_checks.annotations: false` prevents inline annotations.
- `coverage.status.project.default.target: auto` compares against the parent/base automatically.
- `threshold: "15%"` permits a large project-level coverage delta.
- `ignore: vendor/**/*` removes vendored code from coverage calculations.

## Control Flow
Codecov consumes this file during coverage uploads from Linux and Windows CI workflows. There is no executable control flow in the file itself.

## State And Persistence
No local state. It affects persisted Codecov status checks and coverage metadata for uploaded reports.

## Dependencies And Integration Points
Integrated by `codecov/codecov-action` invocations in `.test.yml`, `.test-unit.yml`, `.windows.yml`, and related workflows. Its settings determine whether coverage status can block PRs.

## Risks And Edge Cases
The 15% project threshold is permissive and may hide meaningful coverage drops. Disabling patch status removes direct feedback on newly changed code. Ignoring `vendor` is appropriate but can mask coverage for vendored forks if the project ever treats them as first-party.

## Test Signals
Coverage upload jobs are the test signal. Expected behavior is no Codecov comments/annotations and only project-level status according to the configured auto target.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.devcontainer/devcontainer.json -->
# sources/cloud-native/moby/.devcontainer/devcontainer.json

## Purpose
Defines the VS Code devcontainer for Moby. It builds the repository Dockerfile's `devcontainer` target, bind-mounts the local workspace into the Go import path, runs as root in a privileged container, and installs the Go extension.

## Important APIs, Types, And Functions
- `build.context: ".."` and `dockerfile: "../Dockerfile"` point at the repository root.
- `target: "devcontainer"` maps to the Dockerfile stage that copies source and installs `gopls`.
- `workspaceFolder` and `workspaceMount` place the project at `/go/src/github.com/docker/docker`.
- `remoteUser: "root"` and `runArgs: ["--privileged"]` support daemon/container tests.

## Control Flow
The devcontainer CLI or VS Code builds the image, starts a privileged container, bind-mounts the repository, and opens the configured workspace folder. There is no runtime script in this JSON file.

## State And Persistence
The host workspace is persisted through the bind mount. Tooling and packages are provided by the Dockerfile image layers. Docker daemon state inside the container can persist only if volumes are configured elsewhere.

## Dependencies And Integration Points
Depends on the root `Dockerfile` `devcontainer` target, the `golang.go` VS Code extension, Docker privileged container support, and the Moby Makefile paths.

## Risks And Edge Cases
Running privileged as root is necessary for many daemon workflows but broadens local risk. The mount path uses the historical `github.com/docker/docker` import root, while some API module metadata uses `github.com/moby/moby`; path-sensitive tools must tolerate that.

## Test Signals
Successful devcontainer build and VS Code attach are the direct signals. Follow-on signals are `make shell`, Go language server startup, and daemon tests running inside the privileged environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.devcontainer/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/bug_report.yml -->
# sources/cloud-native/moby/.github/ISSUE_TEMPLATE/bug_report.yml

## Purpose
Defines the GitHub issue form for bug reports. It collects a required description, reproduction steps, Docker version output, Docker info output, and optional expected behavior/additional information, while applying the `kind/bug` label and `bug` issue type.

## Important APIs, Types, And Functions
- Top-level `name`, `description`, `type`, and `labels` configure the issue form metadata.
- Required textareas: `description`, `repro`, `version`, and `info`.
- Optional textareas: `expected` and `additional`.
- `render: bash` is used for command-output fields.
- The first markdown block directs security issues to Docker Security rather than the public tracker.

## Control Flow
GitHub renders the form when a user chooses the bug report template and validates required fields before issue creation. It does not execute repository code.

## State And Persistence
Submitted field values become the persisted issue body. Labels and issue type are applied by GitHub on creation.

## Dependencies And Integration Points
Integrates with GitHub issue forms and downstream triage automation such as label rules and PR validation conventions. The captured `docker version` and `docker info` fields support maintainers diagnosing daemon, storage driver, cgroup, runtime, kernel, and platform issues.

## Risks And Edge Cases
Long placeholders can drift from current Docker output formats. Required command output fields may discourage minimal reports or be irrelevant for non-daemon bugs, but they improve reproducibility for engine issues. Security guidance depends on users reading the markdown block.

## Test Signals
The signal is GitHub successfully rendering the form and applying `kind/bug`. Report quality can be assessed by whether new bug issues include reproductions plus environment details.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/bug_report.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/config.yml -->
# sources/cloud-native/moby/.github/ISSUE_TEMPLATE/config.yml

## Purpose
Configures repository issue template behavior: disables blank issues and routes security reports and general questions to safer or more appropriate channels.

## Important APIs, Types, And Functions
- `blank_issues_enabled: false` forces users through templates or contact links.
- Contact links point to `SECURITY.md` and GitHub Discussions.

## Control Flow
GitHub uses this file when rendering the new issue page. There is no local execution.

## State And Persistence
No repository state is changed. Users choosing a contact link leave the issue creation flow.

## Dependencies And Integration Points
Works with the bug and feature request issue forms in the same folder and with GitHub Discussions and repository security policy documentation.

## Risks And Edge Cases
Disabling blank issues can reduce noisy reports but may block valid reports that do not fit existing forms. Contact-link URLs must remain valid.

## Test Signals
Opening the new issue page should show no blank issue option and should show the two contact links.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/feature_request.yml -->
# sources/cloud-native/moby/.github/ISSUE_TEMPLATE/feature_request.yml

## Purpose
Defines a minimal GitHub issue form for feature requests. It applies the `kind/feature` label and `enhancement` issue type, and requires a single description field.

## Important APIs, Types, And Functions
- Top-level `type: "enhancement"` and `labels: kind/feature` drive triage metadata.
- The sole body control is a required textarea with id `description`.

## Control Flow
GitHub renders and validates the required field at issue creation time.

## State And Persistence
The description becomes the issue body; label and issue type are persisted by GitHub.

## Dependencies And Integration Points
Integrates with the repository's label taxonomy and `validate-pr.yml`, which expects changelog-impact PRs to carry both `kind/*` and `area/*` labels.

## Risks And Edge Cases
The form does not explicitly ask for use cases, alternatives, or compatibility impact, so maintainers may need follow-up questions. The small form is simple but low-structure.

## Test Signals
The expected signal is successful creation of a feature issue with the `kind/feature` label and a non-empty description.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/feature_request.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/actions/setup-runner/action.yml -->
# sources/cloud-native/moby/.github/actions/setup-runner/action.yml

## Purpose
Provides a composite GitHub Action that prepares Linux runners for Moby tests by loading required kernel modules, reloading overlay with `redirect_dir=off`, enabling Docker daemon experimental/live-restore/IPv6 configuration, running a best-effort kernel config check, and printing `docker info`.

## Important APIs, Types, And Functions
- Composite `runs.steps` invoke bash scripts directly.
- `modprobe ip_vs`, `ipv6`, `ip6table_filter`, and overlay reload set kernel module state.
- `jq` merges Docker daemon settings into `/etc/docker/daemon.json`.
- `sudo service docker restart` applies daemon configuration.
- `./contrib/check-config.sh || true` reports kernel support without failing.

## Control Flow
Workflows call this action before building or running tests. The action first adjusts kernel modules, then daemon JSON, restarts Docker, runs config diagnostics, and prints final Docker state.

## State And Persistence
It mutates runner-global kernel module state and `/etc/docker/daemon.json` for the remainder of the job. It does not persist beyond the ephemeral GitHub runner.

## Dependencies And Integration Points
Used by Linux unit, integration, validation, and reusable test workflows. Depends on privileged `sudo`, Docker service availability, `jq`, and repository checkout for `contrib/check-config.sh`.

## Risks And Edge Cases
Reloading overlay can fail if the module is in use. The daemon config merge assumes valid JSON and service management via `service`. Since `check-config.sh` is non-fatal, missing kernel features may only surface later as test failures.

## Test Signals
Successful action execution and `docker info` output are readiness signals. Later integration tests validate whether the runner setup was sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/actions/setup-runner/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/actions/setup-tracing/action.yml -->
# sources/cloud-native/moby/.github/actions/setup-tracing/action.yml

## Purpose
Starts an OpenTelemetry Collector container for Linux test jobs and exports OTLP endpoint/protocol variables into the GitHub Actions environment so test processes can emit traces.

## Important APIs, Types, And Functions
- Creates `/tmp/reports` with world-writable permissions for trace output.
- Runs `otel/opentelemetry-collector-contrib:0.144.0` on host networking.
- Mounts `otelcol-ci-config.yml` and `/tmp/reports`.
- Uses an inline collector config override to write `/data/otel-trace.jsonl`.
- Discovers the `docker0` IPv4 address and appends `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_PROTOCOL` to `$GITHUB_ENV`.

## Control Flow
The composite action starts the collector in detached mode, computes a container-reachable endpoint, and makes tracing environment variables available to later steps. Test workflows stop the `otelcol` container during report preparation.

## State And Persistence
Runtime state consists of the `otelcol` Docker container and trace files in `/tmp/reports`. Environment state persists within the current job through `$GITHUB_ENV`.

## Dependencies And Integration Points
Used by Linux integration and docker-py jobs. Its collector version must stay aligned with the Windows inline collector setup in `.windows.yml`.

## Risks And Edge Cases
`--net=host` and `docker0` assumptions are Linux-specific. If `docker0` has no IPv4 address or the collector image pull fails, tracing setup fails the job. World-writable reports simplify container writes but are broad permissions.

## Test Signals
Later report steps should find `otel-trace*.jsonl` under `/tmp/reports`, and test processes should be able to export OTLP over HTTP/protobuf.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/actions/setup-tracing/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/labeler.yml -->
# sources/cloud-native/moby/.github/labeler.yml

## Purpose
Maps changed file globs to repository labels for `actions/labeler`, classifying PRs by module, daemon area, builder implementation, networking, volumes, swarm, images, logging, security subareas, systemd, contrib, packaging, containerd integration, rootless, testing, docs, dependencies, CI, Windows platform, and changelog impact.

## Important APIs, Types, And Functions
- Uses `changed-files` with `any-glob-to-any-file`, `all-globs-to-all-files`, and `any-glob-to-all-files`.
- Many labels exclude `vendor/**` to avoid dependency changes triggering source-area labels.
- Labels such as `area/builder` aggregate more specific BuildKit and classic-builder paths.
- `impact/changelog` is tied to `api/docs/CHANGELOG.md`.

## Control Flow
The `labeler.yml` workflow feeds this config to `actions/labeler` on `pull_request_target`. The action evaluates changed files and applies matching labels without executing PR code.

## State And Persistence
Matching labels are persisted on the pull request. The config itself has no runtime state.

## Dependencies And Integration Points
Integrates with `validate-pr.yml`, which enforces `kind/*` and `area/*` labels when `impact/*` labels are present. It also feeds maintainer triage and release-note workflows.

## Risks And Edge Cases
Glob drift is likely as directories move. The Windows rule uses `any-glob-to-all-files`, which can behave differently from most entries. Labeling on `pull_request_target` is intentionally limited to label application; safety depends on no checkout/execution of untrusted PR code.

## Test Signals
PRs touching known paths should receive expected labels. Mislabeling or missing labels are visible through `validate-pr.yml` failures and maintainer triage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/labeler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.dco.yml -->
# sources/cloud-native/moby/.github/workflows/.dco.yml

## Purpose
Reusable workflow that validates Developer Certificate of Origin compliance against the appropriate base branch using Moby's `hack/validate/dco` script inside Alpine.

## Important APIs, Types, And Functions
- Triggered only through `workflow_call`.
- Uses `actions/checkout` with `fetch-depth: 0`.
- `actions/github-script` dumps context and computes `base-ref`.
- Runs `docker run alpine:3.22` with the repository mounted at `/workspace`.
- Passes `VALIDATE_REPO` and `VALIDATE_BRANCH` to `hack/validate/dco`.

## Control Flow
Callers invoke this workflow as a prerequisite. It checks out full history, derives the target branch from PR metadata or current ref, then runs the DCO validation script in a clean Alpine container after installing bash, git, and openssh-client.

## State And Persistence
No persistent repository state. The workflow uses GitHub checkout state and transient Docker container state.

## Dependencies And Integration Points
Used by CI, test, VM, Windows, BuildKit, and bin-image workflows. It gates downstream jobs through `needs`.

## Risks And Edge Cases
Full history is required and can be slower on large repos. Base-ref logic trusts PR payload shape. Docker availability on the runner is required even though the check is mostly git-based.

## Test Signals
The `Validate` step passing is the signal. Downstream workflows often skip or fail if DCO validation fails.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.dco.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.test-unit.yml -->
# sources/cloud-native/moby/.github/workflows/.test-unit.yml

## Purpose
Reusable Linux unit-test workflow for Moby. It builds the dev image through Buildx/Bake, runs `make -o build test-unit`, uploads coverage to Codecov, packages test reports, and creates a markdown summary with `teststat`.

## Important APIs, Types, And Functions
- Inputs: `arch` and `runnerSuffix`; optional `CODECOV_TOKEN` secret.
- Matrix `mode` runs normal and `firewalld` variants.
- Uses `.github/actions/setup-runner`, `docker/setup-buildx-action`, `docker/bake-action`, Codecov, upload/download artifact actions, and `teststat`.
- Environment versions include Go `1.26.4`, `gotestlist v0.3.1`, `teststat v0.1.25`, Buildx `edge`, and BuildKit `moby/buildkit:latest`.

## Control Flow
The `unit` job checks out, prepares runner and cache scope, builds the `dev` image from GHA cache, runs unit tests, collects report files from `bundles`, uploads coverage and artifacts. The `unit-report` job always runs after the matrix and summarizes JSON test reports.

## State And Persistence
Build cache is read through GHA cache scopes. Report artifacts are retained for one day. Codecov persists coverage metadata.

## Dependencies And Integration Points
Called by `test.yml` for amd64 and arm64. Relies on the root Makefile and Dockerfile dev target. Codecov config comes from `.codecov.yml`.

## Risks And Edge Cases
`continue-on-error` is true outside pull requests, so scheduled/push failures may not block the same way. Report collection prunes `bundles/*/root` paths to avoid large rootfs artifacts. Cache scope must match build-dev scopes or builds become slower.

## Test Signals
Unit test exit status, uploaded `test-reports-unit-*` artifacts, Codecov flags `unit,<arch>`, and `teststat` summaries provide the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.test-unit.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.test.yml -->
# sources/cloud-native/moby/.github/workflows/.test.yml

## Purpose
Reusable Linux integration workflow for Moby. It runs docker-py tests, flaky integration detection, regular integration tests across modes, integration-cli shards, Codecov uploads, OpenTelemetry trace collection, report artifact uploads, and summary generation.

## Important APIs, Types, And Functions
- Inputs: `arch`, `runnerSuffix`, `extraModes`, and required `storage` (`graphdriver` or `snapshotter`).
- Environment selects `DOCKER_GRAPHDRIVER` and `TEST_INTEGRATION_USE_GRAPHDRIVER` based on storage.
- Jobs: `docker-py`, `integration-flaky`, `integration-prepare`, `integration`, `integration-report`, `integration-cli-prepare`, `integration-cli`, and `integration-cli-report`.
- Uses `gotestlist` to shard `integration-cli` suites and `actions/github-script` to add storage-specific firewall/nftables matrix includes.

## Control Flow
The workflow builds or restores the dev image, sets up the runner and tracing, and runs test targets with environment switches. `integration-prepare` builds mode matrices, including rootless/systemd/firewalld/nftables variants. `integration-cli-prepare` computes test shards and adds extra network suites for snapshotter storage. Report jobs always download artifacts and render `teststat` summaries.

## State And Persistence
Temporary state is in Docker daemon state, `/tmp/reports`, `bundles`, and artifact storage retained for one day. Codecov persists integration and integration-cli coverage flags. `$GITHUB_ENV` carries mode-specific cache scopes and daemon options.

## Dependencies And Integration Points
Called by `test.yml` matrix. Integrates with `.github/actions/setup-runner`, `.github/actions/setup-tracing`, root Makefile targets, Docker Buildx/Bake, Codecov, and the `otelcol-ci-config.yml` file.

## Risks And Edge Cases
The matrix is large and runner-expensive. Many jobs are `continue-on-error` outside PRs. Dynamic test matrices depend on `gotestlist` output and GitHub Actions expression parsing. Rootless AppArmor setup is conditional on runner version. Trace setup assumes the collector is running when report steps call `docker stop otelcol`.

## Test Signals
Signals include job exit status, daemon logs printed from `bundles`, Codecov flags for integration modes, `test-reports-integration-*` and `test-reports-integration-cli-*` artifacts, trace JSONL files, and summary markdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.vm.yml -->
# sources/cloud-native/moby/.github/workflows/.vm.yml

## Purpose
Reusable VM-based integration workflow that runs selected Moby integration tests inside a Lima guest, primarily for distribution/kernel combinations such as Oracle Linux 8 and rootless/cgroup coverage.

## Important APIs, Types, And Functions
- Inputs: required `template` and optional `integration_dir`.
- Uses `lima-vm/lima-actions/setup`, `actions/cache` for `~/.cache/lima`, and `limactl`.
- Matrix mode runs normal and `rootless`.
- Installs Docker CE and test dependencies inside the guest.
- Runs `make test-integration` with `TEST_INTEGRATION_USE_GRAPHDRIVER=1` and optional `TEST_INTEGRATION_DIR`.

## Control Flow
The workflow starts a Lima VM from the requested template, loads kernel modules, installs Docker, copies the repository into `/tmp/docker`, selects rootless/fuse-overlayfs behavior for older Alma/Oracle-like kernels, runs integration tests inside the guest, copies `bundles` back, uploads reports, and summarizes JSON reports.

## State And Persistence
VM image cache persists through GitHub Actions cache. Guest filesystem state is temporary. Reports are copied back into host `bundles` and uploaded as one-day artifacts.

## Dependencies And Integration Points
Called by `vm.yml`. Depends on Lima, DNF-compatible guest images, Docker CE repository availability, systemd inside the guest, and Moby Makefile test targets.

## Risks And Edge Cases
Guest distro differences drive conditional behavior such as `DOCKER_IGNORE_BR_NETFILTER_ERROR` and `fuse-overlayfs` graphdriver for rootless mode. Lima startup and package repository availability are external failure points. The workflow skips PRs labeled `ci/validate-only`.

## Test Signals
Signals include Lima guest startup, `lima docker info`, integration test exit status, daemon logs, uploaded `test-reports-integration-*` artifacts, and `teststat` summaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.vm.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.windows.yml -->
# sources/cloud-native/moby/.github/workflows/.windows.yml

## Purpose
Reusable Windows workflow that builds Moby Windows binaries, runs unit tests, runs integration/integration-cli shards against built `dockerd` and `docker`, supports graphdriver and containerd-snapshotter storage modes, optionally uploads coverage, and summarizes test reports.

## Important APIs, Types, And Functions
- Inputs: `os`, `storage`, and `send_coverage`; optional Codecov token.
- Jobs: `build`, `unit-test`, `unit-test-report`, `integration-test-prepare`, `integration-test`, and `integration-test-report`.
- Uses Windows PowerShell, Docker Windows containers, `Dockerfile.windows`, `hack\make.ps1`, `gotestlist`, Codecov, artifact upload/download, and OpenTelemetry Collector MSI.
- Runtime matrix covers `builtin` and `containerd`, excluding builtin for snapshotter.

## Control Flow
The build job checks out into GOPATH, waits for the runner Docker daemon, builds the Windows base image, runs `hack\make.ps1 -Daemon -Client`, copies binaries and containerd/buildx artifacts, and uploads them. Unit tests build a test image and run `-TestUnit`. Integration preparation shards tests. Integration jobs install the collector, remove the preinstalled Docker service, register the built `dockerd` service with storage/runtime flags, wait for readiness, build busybox, run integration or integration-cli tests, collect daemon event logs, stop services, upload reports, and then summarize reports on Ubuntu.

## State And Persistence
Artifacts persist built binaries and test reports for one or two days. Windows service state, registry environment, temp daemon roots, and collector service state are mutated within the ephemeral runner.

## Dependencies And Integration Points
Called by `windows-2022.yml` and `windows-2025.yml`. Integrates with Codecov, OpenTelemetry tracing, Moby Windows Dockerfile/build scripts, containerd/runhcs binaries, `docker-buildx.exe`, and integration test environment variables.

## Risks And Edge Cases
Windows runner Docker readiness and service replacement are fragile. The workflow mutates HKLM service environment and removes the default Docker service. Snapshotter mode only runs with containerd runtime. Collector MSI URL availability and Windows base image pulls can fail. Test report names are SHA256 hashes of matrix test names.

## Test Signals
Signals include uploaded `build-<storage>-<os>` artifacts, unit and integration report artifacts, Codecov flags when enabled, daemon event logs, `docker info` before/after tests, and `teststat` summaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/.windows.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/bin-image.yml -->
# sources/cloud-native/moby/.github/workflows/bin-image.yml

## Purpose
Builds and publishes the `moby/moby-bin` binary image using the shared Docker GitHub builder workflow, with DCO validation on non-tag runs and PR-safe no-push behavior.

## Important APIs, Types, And Functions
- Triggers on manual dispatch, pushes to `master`/release branches/tags, and pull requests.
- Concurrency cancels stale PR runs only.
- `validate-dco` reuses `.dco.yml` unless the ref is a tag.
- `build` uses `docker/github-builder/.github/workflows/bake.yml` with target `bin-image-cross`.
- Grants `id-token: write` for signing attestations.
- Provides version/product metadata and semver tag rules matching `docker-*` tags.

## Control Flow
After DCO validation, the builder workflow runs unless the PR has `ci/validate-only`. It sets up QEMU, uses cache scope `bin-image`, builds cross-platform output, pushes only outside PRs, and authenticates to Docker Hub through repository secrets.

## State And Persistence
Push runs publish image tags to Docker Hub. PR runs build without push. Build cache persists through the external builder workflow.

## Dependencies And Integration Points
Depends on the root Dockerfile/Bake targets, Docker Hub credentials, GitHub OIDC, and DCO reusable workflow.

## Risks And Edge Cases
Secrets must be present for publishing. Tag strategy is tied to `docker-v*` tag names. Skipping DCO on tags is intentional but means tag workflows trust prior branch checks.

## Test Signals
Successful builder workflow completion, image metadata, and published `moby/moby-bin` tags are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/bin-image.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/buildkit.yml -->
# sources/cloud-native/moby/.github/workflows/buildkit.yml

## Purpose
Builds Moby daemon binaries and runs the upstream BuildKit integration test suite against those binaries on Linux and Windows, validating compatibility between Moby's dockerd and the BuildKit version selected by `hack/buildkit-ref`.

## Important APIs, Types, And Functions
- Jobs: `validate-dco`, `build-linux`, `test-linux`, `build-windows`, and `test-windows`.
- Linux build uses Bake target `binary` and uploads `./build`.
- Linux tests checkout Moby and BuildKit, expose GitHub runtime cache env, build BuildKit integration test image, and run `./hack/test integration`.
- Windows build produces `docker.exe`, `dockerd.exe`, registry, BuildKit `buildctl`, and containerd artifacts.
- Windows test matrix slices BuildKit packages, especially `frontend/dockerfile#1-12` through `#12-12`.

## Control Flow
DCO gates builds. Linux builds upload Moby binaries, then BuildKit tests download them into `buildkit/build/moby`, reset Docker daemon config, build the BuildKit test image, and run package/worker-specific tests. Windows builds create artifacts through `Dockerfile.windows`, check out BuildKit master for `buildctl`, then Windows tests download artifacts, compute package/test flags, and run `gotestsum` against BuildKit with `TEST_DOCKERD_BINARY` pointing to Moby `dockerd`.

## State And Persistence
Artifacts persist for one day. BuildKit cache runtime variables expose GitHub Actions cache service to tests. Windows test reports are placed under `buildkit/bin/testreports`.

## Dependencies And Integration Points
Integrates Moby, BuildKit, Docker Buildx/Bake, GitHub runtime cache, QEMU, Go setup, registry binary, and Moby's `hack/buildkit-ref` mapping.

## Risks And Edge Cases
It mixes Moby's selected BuildKit ref with BuildKit master for Windows `buildctl`, which can drift. Disabled features remove azblob/s3 and merge_diff in some workers. Windows package slicing requires correct `TESTFLAGS` construction. Tests are skipped for validate-only PRs.

## Test Signals
Build artifact checks and BuildKit integration package results are the core signals. Failures show incompatibility in BuildKit client/frontend/solver behavior against Moby dockerd.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/buildkit.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/ci.yml -->
# sources/cloud-native/moby/.github/workflows/ci.yml

## Purpose
Main build CI workflow for Moby. It validates DCO, builds static and dynamic Linux binaries on amd64 and arm64, builds cross-platform binaries, runs `govulncheck` with SARIF upload, builds the dind image, and exposes aggregate success checks including a legacy `build (binary)` check name.

## Important APIs, Types, And Functions
- Jobs: `validate-dco`, `build`, `prepare-cross`, `cross`, `govulncheck`, `build-dind`, `success`, and `build-binary`.
- Uses Docker Buildx/Bake with BuildKit `moby/buildkit:latest`.
- `prepare-cross` uses `docker/bake-action/subaction/matrix` to derive platforms from `binary-cross`.
- `govulncheck` writes SARIF and uploads it on non-PR `moby/moby` runs.

## Control Flow
DCO gates most jobs. The build matrix runs `binary` and `dynbinary` on amd64/arm64 runners and validates artifacts with `file`. Cross builds generate a platform matrix then build each target with platform override. Security scanning runs regardless of `ci/validate-only`. The `success` job fails if any dependency failed or was cancelled, and `build-binary` preserves the old required check name.

## State And Persistence
No long-lived build artifacts are uploaded in this workflow; outputs are inspected in-place. SARIF may persist in GitHub code scanning on accepted branches.

## Dependencies And Integration Points
Depends on Bake target definitions, the root Dockerfile, GitHub CodeQL SARIF upload, and DCO workflow. It is a high-level required check for build health.

## Risks And Edge Cases
The aggregate `success` job must include all required dependencies or failures may be missed. `govulncheck` has long timeout and security-events permission. Validate-only PRs skip cross and dind but not vulnerability scanning.

## Test Signals
Signals are successful binary/dynbinary file inspection, cross-build matrix completion, SARIF upload where applicable, dind cache-only build, and aggregate success jobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/codeql.yml -->
# sources/cloud-native/moby/.github/workflows/codeql.yml

## Purpose
Runs GitHub CodeQL analysis for Go on pushes, PRs, tags, weekly schedule, and manual-equivalent branch events.

## Important APIs, Types, And Functions
- Triggers include release branches, `v*`, `docker-v*`, `api/v*`, and `client/v*` tags, PRs, and Thursday 09:00 UTC schedule.
- Uses Go `1.26.4`.
- Steps use checkout, setup-go, CodeQL init, autobuild, and analyze.
- Grants `security-events: write` only to the CodeQL job.

## Control Flow
The single job checks out with shallow history depth 2, initializes CodeQL for Go, lets CodeQL autobuild the project, and uploads analysis results with category `/language:go`.

## State And Persistence
Analysis results persist in GitHub code scanning. The runner build state is temporary.

## Dependencies And Integration Points
Integrates with GitHub Advanced Security/CodeQL and Go setup. It is separate from `govulncheck` in `ci.yml`.

## Risks And Edge Cases
Autobuild may miss project-specific build tags or generated code if CodeQL cannot infer the full build. The job timeout is only 10 minutes, which can be tight for large Go projects.

## Test Signals
Successful CodeQL analysis upload and code-scanning alerts are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/codeql.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/labeler.yml -->
# sources/cloud-native/moby/.github/workflows/labeler.yml

## Purpose
Runs `actions/labeler` on pull requests to apply labels from `.github/labeler.yml`.

## Important APIs, Types, And Functions
- Trigger: `pull_request_target`, annotated for zizmor because it only labels and does not checkout or execute PR code.
- Job permission elevates `pull-requests: write` while keeping `contents: read`.
- Uses pinned `actions/labeler@v6.1.0`.
- `sync-labels: false` avoids removing labels that no longer match.

## Control Flow
For each PR target event, the workflow runs a single labeler step. Concurrency is per PR number and cancels in-progress label runs.

## State And Persistence
Applied labels persist on the pull request. No repository files or artifacts are produced.

## Dependencies And Integration Points
Consumes `.github/labeler.yml` and feeds validation/triage workflows that rely on label taxonomy.

## Risks And Edge Cases
`pull_request_target` has elevated token context; safety relies on never checking out or executing PR code. Because sync is disabled, stale labels may remain after file changes.

## Test Signals
Expected labels appearing on PRs after file changes are the observable signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/labeler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/test.yml -->
# sources/cloud-native/moby/.github/workflows/test.yml

## Purpose
Top-level Linux test workflow. It builds reusable dev images, invokes reusable integration and unit workflows for selected architectures/storage backends, runs validation scripts, validates API swagger, and runs cross-platform binary smoke tests.

## Important APIs, Types, And Functions
- Jobs: `validate-dco`, `build-dev`, `test`, `test-unit`, `validate-prepare`, `validate`, `validate-api-swagger`, `smoke-prepare`, and `smoke`.
- `build-dev` matrix covers amd64/arm64 and normal/systemd/firewalld modes.
- `test` delegates to `.test.yml` for amd64 snapshotter, amd64 graphdriver, and arm64 snapshotter.
- `test-unit` delegates to `.test-unit.yml`.
- Validation matrix derives scripts from `hack/validate`, excluding `all`, `default`, and `dco`, then adds `generate-files`.

## Control Flow
DCO runs first. Dev images are built and cached by architecture/mode. Reusable test workflows consume those caches. Validation restores the amd64 dev image, loads it into Docker, and runs `make -o build validate-<script>`. API swagger validation runs in the `api` directory. Smoke tests derive platforms from Bake `binary-smoketest` and run with QEMU/buildx.

## State And Persistence
Dev image tarballs are stored in GHA cache keyed by run id. Test reports and coverage are persisted by reusable workflows. Validation and smoke outputs are temporary.

## Dependencies And Integration Points
Coordinates the root Dockerfile, Makefile, `api/Makefile`, reusable workflows, setup-runner action, Docker Buildx/Bake, and hack validation scripts.

## Risks And Edge Cases
Large matrix cost and cache coupling are the main risks. `validate` depends on the amd64 normal dev image cache; cache miss fails intentionally. Validate-only PRs skip heavy test and smoke jobs but still run validation.

## Test Signals
Signals include successful dev image builds, delegated reusable workflow results, validation script pass/fail, swagger validation, smoke target completion, and artifact/coverage outputs from child workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/validate-milestone.yml -->
# sources/cloud-native/moby/.github/workflows/validate-milestone.yml

## Purpose
Ensures pull requests have a milestone matching the current Docker next version from `releases/versions.yaml`.

## Important APIs, Types, And Functions
- Triggered on PR open, synchronize, milestone changes, demilestone, and edit events.
- Grants `pull-requests: read`.
- Uses `actions/github-script` to list PR files and read `releases/versions.yaml`.
- If the PR modifies `releases/versions.yaml`, reads it from the PR head SHA; otherwise reads from the base branch.

## Control Flow
The script lists modified files, decides which ref to read, fetches the YAML file through GitHub REST, extracts the line containing `next:`, strips quotes, compares it with the PR milestone title, and fails if absent or mismatched.

## State And Persistence
No state is written. It reads PR metadata and repository contents and emits a check result.

## Dependencies And Integration Points
Tied to release management conventions in `releases/versions.yaml` and PR milestone usage.

## Risks And Edge Cases
The YAML parsing is line-based and looks for `next:` substring, so structural changes could break it. It trusts PR head content when the versions file is changed, which is acceptable because the check is advisory for maintainers, not a security boundary.

## Test Signals
The check passes when the PR milestone exactly equals the extracted next version and fails with explicit messages otherwise.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/validate-milestone.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/validate-pr.yml -->
# sources/cloud-native/moby/.github/workflows/validate-pr.yml

## Purpose
Validates PR metadata and changelog hygiene: impact labels must be paired with area/kind labels, changelog code blocks must match impact labels, commit messages must reference GitHub issues correctly, and release-branch PR titles must match the target branch.

## Important APIs, Types, And Functions
- Jobs: `check-labels`, `check-changelog`, `check-commit-references`, and `check-pr-branch`.
- `check-changelog` extracts a fenced `markdown changelog` block from the PR body using `awk`.
- `check-commit-references` runs `bash hack/validate/pr-gh-references` with full history.
- `check-pr-branch` parses a leading bracketed title prefix and compares it with `GITHUB_BASE_REF`.

## Control Flow
On PR open/edit/label/sync events, label checks run simple GitHub expression predicates. Changelog validation ensures impact-labeled PRs include a non-trivial changelog block and non-impact PRs do not. Commit reference validation checks out full history and runs the repository script. Branch validation allows master PRs without a prefix but requires non-master PR title prefix to equal the base branch after removing ` backport`.

## State And Persistence
The workflow writes no state; it produces PR check results.

## Dependencies And Integration Points
Integrates with labeler output, release-note conventions in PR templates, and `hack/validate/pr-gh-references`.

## Risks And Edge Cases
Changelog extraction is sensitive to exact fence text. Label checks are string containment over comma-joined label names, which is simple but can produce surprising matches if label names overlap. Branch prefix parsing requires maintainers to follow a precise title convention.

## Test Signals
Failures produce GitHub Actions error annotations explaining missing labels, changelog mismatch, bad references, or branch-title mismatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/validate-pr.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/vm.yml -->
# sources/cloud-native/moby/.github/workflows/vm.yml

## Purpose
Top-level VM workflow that runs DCO validation and delegates selected integration tests to the reusable Lima VM workflow.

## Important APIs, Types, And Functions
- Triggers on manual dispatch, pushes to master/release branches, and PRs.
- `validate-dco` reuses `.dco.yml`.
- `vm` job calls `.vm.yml` with a matrix containing `template:oraclelinux-8` and integration directories focused on container, build, and system tests.

## Control Flow
DCO runs first. The reusable VM workflow then starts Oracle Linux 8 via Lima and runs the targeted integration directories, unless PR label rules in the child workflow skip validate-only PRs.

## State And Persistence
No state is written by this wrapper beyond child workflow artifacts.

## Dependencies And Integration Points
Depends on `.vm.yml` for actual VM setup and testing. The selected template preserves cgroup v1 coverage until support is formally deprecated.

## Risks And Edge Cases
The matrix currently has one template, so coverage is focused rather than broad. Comments document known AlmaLinux 8 port-forwarding issues and the reason Oracle Linux 8 remains.

## Test Signals
Wrapper success depends on DCO plus the child VM workflow's integration report artifacts and summary.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/vm.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/windows-2022.yml -->
# sources/cloud-native/moby/.github/workflows/windows-2022.yml

## Purpose
Scheduled/manual wrapper for the reusable Windows workflow on `windows-2022`, running both graphdriver and snapshotter storage modes with coverage upload enabled.

## Important APIs, Types, And Functions
- Triggers daily at `0 10 * * *` and via `workflow_dispatch`.
- Reuses `.dco.yml` and `.windows.yml`.
- Matrix `storage` includes `graphdriver` and `snapshotter`.
- Passes `os: windows-2022` and `send_coverage: true`.

## Control Flow
DCO validation runs, then the `run` job delegates to `.windows.yml` for each storage mode with Codecov token forwarding.

## State And Persistence
Child workflow publishes build/test artifacts and coverage. This wrapper has no additional state.

## Dependencies And Integration Points
Uses Windows Server 2022 GitHub-hosted runners and the shared Windows workflow. Coverage behavior integrates with `.codecov.yml`.

## Risks And Edge Cases
It is not triggered on PRs or pushes, so Windows 2022 coverage is scheduled/manual. The inherited PR validate-only condition is effectively redundant for current triggers.

## Test Signals
Signals are child workflow results for both storage modes and Codecov uploads.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/windows-2022.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/windows-2025.yml -->
# sources/cloud-native/moby/.github/workflows/windows-2025.yml

## Purpose
Push/PR/manual wrapper for the reusable Windows workflow on `windows-2025`, running graphdriver and snapshotter modes without coverage upload.

## Important APIs, Types, And Functions
- Triggers on manual dispatch, pushes to master/release branches, and PRs.
- Reuses `.dco.yml` and `.windows.yml`.
- Matrix `storage` includes `graphdriver` and `snapshotter`.
- Passes `os: windows-2025` and `send_coverage: false`.

## Control Flow
After DCO validation, the wrapper delegates to `.windows.yml` for each storage mode unless a PR has `ci/validate-only`.

## State And Persistence
Child workflow produces build/test artifacts; no Codecov coverage is uploaded because `send_coverage` is false.

## Dependencies And Integration Points
Provides current Windows PR coverage through the shared workflow. It uses the `ltsc2025` base image selected in `.windows.yml`.

## Risks And Edge Cases
Windows 2025 runner/image behavior can differ from Windows 2022. Disabling coverage keeps PR runs lighter but means Windows coverage comes from other lanes.

## Test Signals
Signals are child workflow build, unit, integration, daemon log, and report summary results across both storage modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/windows-2025.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/zizmor.yml -->
# sources/cloud-native/moby/.github/workflows/zizmor.yml

## Purpose
Runs the zizmor GitHub Actions security scanner through a shared workflow with medium severity/confidence thresholds and the pedantic persona.

## Important APIs, Types, And Functions
- Triggers on manual dispatch, pushes, tags, and PRs.
- Uses `crazy-max/.github/.github/workflows/zizmor.yml@v1.10.0`.
- Grants `security-events: write` for SARIF/code-scanning output.
- Inputs: `min-severity: medium`, `min-confidence: medium`, and `persona: pedantic`.

## Control Flow
The workflow delegates all scanning to the external reusable workflow. Concurrency cancels stale PR runs only.

## State And Persistence
Scanner findings may persist in GitHub security/code-scanning surfaces. No local artifacts are defined in this wrapper.

## Dependencies And Integration Points
Complements inline zizmor annotations in workflows, such as the labeler `pull_request_target` justification. It depends on the external `crazy-max/.github` workflow pin.

## Risks And Edge Cases
Delegating to an external workflow centralizes scanner behavior but makes this repo dependent on that workflow's interface. Medium thresholds may intentionally ignore low-confidence findings.

## Test Signals
Successful scanner run and any generated security findings are the signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/zizmor.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.golangci.yml -->
# sources/cloud-native/moby/.golangci.yml

## Purpose
Configures `golangci-lint` v2 behavior for Moby, fixing the Go version, enabling formatters and a broad curated linter set, enforcing dependency/import policies, defining security/style exceptions, and removing issue count caps.

## Important APIs, Types, And Functions
- `run.go: "1.26.4"` avoids auto-detecting Go version from modules.
- Formatters: `gofmt` and `goimports`.
- Enabled linters include `depguard`, `forbidigo`, `gosec`, `govet`, `importas`, `staticcheck`, `revive`, `thelper`, `usestdlibvars`, and others.
- `depguard` forbids direct testify, containerd userns, unstable fsutil, and go-multierror dependencies.
- `forbidigo` bans old `sync/atomic` functions, direct `regexp.MustCompile`, and direct netlink/nlwrap methods lacking EINTR-safe wrappers.
- Exclusion rules explicitly copy default false-positive patterns and set `warn-unused: true`.

## Control Flow
`golangci-lint` reads this file during validation. Linters run with the configured settings, then exclusions filter known false positives. Issue caps are disabled so all findings are reported.

## State And Persistence
No runtime state. The file governs CI validation results and local lint output.

## Dependencies And Integration Points
Used by Moby validation targets and the Dockerfile-provided `golangci-lint` binary. It encodes project-specific API boundaries such as `gotest.tools/v3/assert`, `moby/sys/userns`, lazy regexp usage, and netlink wrapper policy.

## Risks And Edge Cases
The config is strict and can break on linter version upgrades. `warn-unused` catches stale exclusions but may require maintenance. Some disabled checks and broad gosec exclusions are technical debt and can hide issues until revisited.

## Test Signals
Validation passes when code conforms to lint, import, security, and formatting policies. Unused exclusions and forbidden API usage are high-signal failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/Dockerfile -->
# sources/cloud-native/moby/Dockerfile

## Purpose
Defines Moby's main multi-stage BuildKit Dockerfile for developer environments, CI build images, static/dynamic daemon binaries, auxiliary runtime tools, frozen test images, smoke tests, devcontainers, and dind images.

## Important APIs, Types, And Functions
- Global args define versions for Go, Debian, `xx`, Docker CLI, Buildx, Compose, registry, containerd, runc, tini, rootlesskit, crun, Delve, golangci-lint, gotestsum, shfmt, go-swagger-adjacent tooling, and Windows container utility.
- Stages include `xx`, `base`, `criu`, `registry`, `frozen-images`, `delve`, `gowinres`, `containerd`, `golangci_lint`, `gotestsum`, `shfmt`, `gopls`, Docker CLI stages, `runc`, `tini`, `rootlesskit`, `crun`, `containerutil`, `dev-*`, `build`, `binary`, `all`, `smoketest`, `devcontainer`, `dind`, and `dev`.
- Uses BuildKit features such as cache mounts, bind mounts, `COPY --link`, remote Git `ADD`, and target-platform-aware `xx-go`/`xx-apt-get`.

## Control Flow
The Dockerfile builds tool stages first, conditionally selecting dummy or real outputs for unsupported OS/arch combinations. The `dev` lineage assembles test tools, CLIs, runtimes, frozen images, daemon config, rootless tooling, optional systemd/firewalld packages, and source code. The `build` stage cross-compiles Moby binaries through `hack/make.sh`, verifies them with `xx-verify`, and publishes scratch `binary`/`all` outputs. Smoke and dind stages consume built binaries for validation and nested Docker use.

## State And Persistence
Build cache mounts persist apt and Go build/module caches across BuildKit runs. Final output stages are immutable images or scratch artifacts. Dev images declare Docker data volumes for `/var/lib/docker` and rootless storage.

## Dependencies And Integration Points
Integrated by the root Makefile, GitHub Bake workflows, devcontainer config, dind image builds, test workflows, and packaging flows. It pulls from Docker Hub, GitHub repositories, Debian/openSUSE apt repos, and upstream container runtime projects.

## Risks And Edge Cases
The file is a central supply-chain surface: many version args and remote `ADD` sources must be audited. External apt/GitHub/image availability can break builds. Platform conditionals must keep dummy stages aligned with unsupported outputs. `DOCKER_STATIC`, `SYSTEMD`, and `FIREWALLD` args materially change build/test behavior.

## Test Signals
Signals include successful Bake targets (`binary`, `dynbinary`, `binary-cross`, `dev`, `dind`, `binary-smoketest`), `xx-verify` checks, tool version commands, smoke `dockerd --version` and `docker-proxy --version`, and downstream unit/integration CI using the dev image.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/Makefile -->
# sources/cloud-native/moby/Makefile

## Purpose
Provides the primary developer and CI command surface for building Moby binaries/images, entering the dev environment, running unit/integration/docker-py tests, validating code, generating files, and delegating Swagger tasks to the API module.

## Important APIs, Types, And Functions
- Variables: `DOCKER`, `BUILDX`, `DOCKER_GITCOMMIT`, validation refs, `DOCKER_ENVS`, `BIND_DIR`, `DOCKER_MOUNT`, cache volumes, `DOCKER_FLAGS`, `DOCKER_IMAGE`, and build/bake commands.
- Targets include `all`, `binary`, `dynbinary`, `cross`, `clean-cache`, `install`, `run`, `build`, `shell`, `dev`, `test`, `test-docker-py`, `test-integration`, `test-integration-flaky`, `test-unit`, `validate`, `validate-generate-files`, `validate-%`, `win`, `swagger-gen`, `swagger-docs`, `generate-files`, and `validate-bind-dir`.
- The `build` target chooses `--target=dev-base` when bind-mounting `.` and `--target=dev` otherwise.

## Control Flow
Most developer commands first build or reuse the Docker dev image, then run repository scripts inside a privileged container with curated env passthrough, bind mounts, cache volumes, and optional TTY/stdin behavior. Build targets call `docker buildx bake`; test/validation targets call `hack/make.sh`, `hack/test/unit`, or `hack/validate/*` inside the dev container. `generate-files` writes BuildKit local output into a temp dir and copies it back.

## State And Persistence
Persistent state includes Docker build cache, named volumes `docker-dev-cache` and `docker-mod-cache`, `bundles`, optional bind-mounted source, and `.git` mount. `generate-files` mutates the working tree. `clean-cache` removes the named volumes.

## Dependencies And Integration Points
Integrates the root Dockerfile, Bake definitions, hack scripts, API Makefile, Docker daemon privileges, CI environment variables, and optional externally supplied Docker CLI path.

## Risks And Edge Cases
The env allowlist intentionally excludes `DOCKER_BUILDTAGS` to avoid shadowing Dockerfile defaults. Privileged container execution is powerful. `BIND_DIR` validation prevents unsafe absolute/parent paths. Interactive/CI TTY handling affects command behavior in automation.

## Test Signals
Successful Make targets and generated `bundles` are the direct signals. CI workflows rely on `make -o build ...` to skip rebuilding when images are already prepared.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/Dockerfile -->
# sources/cloud-native/moby/api/Dockerfile

## Purpose
Defines a small API-module development image for swagger generation and validation.

## Important APIs, Types, And Functions
- Uses `golang:${GO_VERSION}-alpine` as `base`.
- Installs `bash`, `make`, and `yamllint`.
- `swagger` stage installs `github.com/go-swagger/go-swagger/cmd/swagger@v0.33.1` with BuildKit caches.
- `dev` stage copies the swagger binary and sets workdir `/go/src/github.com/moby/moby/api`.

## Control Flow
The API Makefile builds the `dev` target. During image build, the swagger stage compiles the pinned swagger CLI and verifies it with `swagger version`; the final dev stage makes that binary available to scripts.

## State And Persistence
Go build and module caches can persist through BuildKit cache mounts. Final image state contains the swagger binary and Alpine tooling.

## Dependencies And Integration Points
Used by `api/Makefile` targets `swagger-gen`, `validate-swagger`, and `validate-swagger-gen`, and indirectly by top-level `test.yml` API swagger validation.

## Risks And Edge Cases
The Makefile passes `SWAGGER_VERSION`, while this Dockerfile declares `GO_SWAGGER_VERSION`; the default still works, but override naming must be handled carefully. Alpine tooling can differ from Debian dev image behavior.

## Test Signals
Image build success and `swagger version` output are build-time signals; script success in API Makefile targets validates runtime behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/Makefile -->
# sources/cloud-native/moby/api/Makefile

## Purpose
Provides API-module commands for building the swagger dev image, generating swagger-derived API types, serving rendered API docs, validating `swagger.yaml`, and checking generated output freshness.

## Important APIs, Types, And Functions
- Variables: `DOCKER`, `BUILDX`, `API_DIR`, `PROJECT_PATH`, `DOCKER_MOUNT`, `DOCKER_IMAGE`, `DOCKER_WORKDIR`, `DOCKER_RUN`, `DOCKER_BUILD_ARGS`, and `SWAGGER_DOCS_PORT`.
- Targets: `build`, `swagger-gen`, `swagger-docs`, `validate-swagger`, `validate-swagger-gen`, and `help`.
- `swagger-docs` runs `redocly/redoc:v2.5.1` with `SPEC_URL=swagger/swagger.yaml`.

## Control Flow
`swagger-gen` and validation targets build the dev image first, then run scripts from `api/scripts` inside a container with the API directory mounted into the project path. `swagger-docs` starts a Redoc container serving the current directory on the configured port.

## State And Persistence
Swagger generation mutates files under the mounted API directory. Validation targets should leave the tree unchanged. The docs preview container is ephemeral.

## Dependencies And Integration Points
Called by the root Makefile and GitHub `validate-api-swagger` job. Depends on `api/Dockerfile`, API scripts, Docker Buildx, and Redoc.

## Risks And Edge Cases
Only the API directory is mounted, so scripts needing repository-wide context must work within that constraint. The build arg `SWAGGER_VERSION` does not match the Dockerfile's `GO_SWAGGER_VERSION` arg. Docs preview binds a local port that can conflict with other services.

## Test Signals
Successful `make validate-swagger` and `make validate-swagger-gen` are CI signals. `swagger-gen` should leave generated files matching the swagger spec.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/doc.go -->
# sources/cloud-native/moby/api/doc.go

## Purpose
Declares the Go package for the Moby API module.

## Important APIs, Types, And Functions
- `package api` is the only declaration.

## Control Flow
There is no executable control flow. The file gives the directory a Go package declaration for documentation/build tooling.

## State And Persistence
No state.

## Dependencies And Integration Points
Integrates with Go tooling that expects a package in the `api` directory and with generated API code/tests elsewhere in the module.

## Risks And Edge Cases
Because there is no package comment or exported API here, documentation quality depends on generated or adjacent files. Lint settings currently disable package-comment enforcement.

## Test Signals
Go tooling should parse the package successfully.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/doc.go -->
