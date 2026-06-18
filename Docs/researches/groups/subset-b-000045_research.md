# Group Research: subset-b-000045

This grouped report covers the subset-b-000045 source files. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tools/cfs-fuse.c -->
# sources/cloud-native/composefs/tools/cfs-fuse.c

## Purpose
`cfs-fuse.c` implements an experimental read-only FUSE low-level server for mounting composefs EROFS images from userspace. It maps a composefs image, interprets EROFS metadata directly, resolves redirected file payloads from an object `basedir`, and exposes lookup, directory, symlink, xattr, read, and seek operations through `fuse_lowlevel_ops`.

## Important APIs, Types, And Functions
The global image state includes `erofs_data`, `erofs_data_size`, `erofs_root_nid`, `erofs_super`, `cfs_header`, `erofs_metadata`, `erofs_xattrdata`, build timestamps, ACL enablement, and `basedir_fd`. `struct cfs_data` carries parsed FUSE options: `source`, `basedir`, and `noacl`.

Key helpers translate between FUSE inode numbers and EROFS nids (`cfs_nid_from_ino`, `cfs_ino_from_nid`), fetch inodes (`cfs_get_erofs_inode`), decode inode metadata (`cfs_stat`, `erofs_inode_get_mode`, `erofs_inode_get_info`), detect overlay whiteouts (`erofs_inode_is_whiteout`), compare non-null-terminated directory names (`memcmp2`), and rewrite/filter xattrs (`cfs_xattr_rewrite`, `do_getxattr`).

FUSE callbacks are assembled in `cfs_oper`: `cfs_init`, `cfs_lookup`, `cfs_getattr`, `cfs_opendir`, `cfs_readdir`, `cfs_readdir_plus`, `cfs_readlink`, `cfs_listxattr`, `cfs_getxattr`, `cfs_open`, `cfs_release`, `cfs_read`, and `cfs_lseek`.

## Control Flow
`main` parses FUSE command-line options, forces `ro,default_permissions`, opens and mmaps `source`, opens `basedir` with `O_PATH`, validates composefs and EROFS magic values, initializes global metadata pointers from the superblock, creates and mounts a FUSE session, daemonizes if requested, and enters either single-threaded or multithreaded FUSE loops.

Directory lookup and readdir operate directly on EROFS dirent blocks. `cfs_lookup` binary-searches sorted directory blocks, searches an inline tail block when present, filters whiteouts, and replies with `fuse_entry_param`. `_cfs_readdir` walks blocks from the requested offset and uses either `fuse_add_direntry` or `fuse_add_direntry_plus`.

File open checks write flags, reads trusted `overlay.redirect`, strips leading slashes, and opens the redirected object beneath `basedir_fd`. If there is no redirect, reads are served from inline/flat EROFS data via `cfs_read_inline`; otherwise `cfs_read` replies using FUSE fd-splice data.

## State And Persistence
Runtime state is global, process-local, and read-only after initialization except for FUSE request handling. The image is memory-mapped `MAP_PRIVATE`; redirected payloads are opened per file handle and closed in `release`. No persistent state is written. Cache hints (`keep_cache`, `cache_readdir`, long attr/entry timeouts) rely on immutable image semantics.

## Dependencies And Integration Points
This file depends on libfuse3 low-level APIs, Linux mount/fsverity/loop headers, EROFS composefs internal structures, and libcomposefs utility endian helpers. It integrates with composefs image files produced by `mkcomposefs`, object stores referenced by overlay redirect xattrs, and mount consumers expecting normal POSIX read-only filesystem behavior.

## Risks
`cfs_get_erofs_inode` has a TODO for bounds checking, so malformed images can point outside mapped metadata. Many dirent/xattr walks trust on-disk lengths. `cfs_read_inline` ignores the read offset when assigning `iov_base`, which is a correctness risk for inline flat reads. Fs-verity verification for redirected objects is explicitly TODO. Global state plus multithreaded FUSE is mostly read-only but assumes immutable mappings and stable `basedir_fd`.

## Test Signals
Useful tests are mount smoke tests over generated composefs images, lookup/readdir/readdirplus with tailpacked directories, xattr filtering and ACL-disabled behavior, whiteout hiding, symlink reads, inline file reads with nonzero offsets, redirected object reads, and malformed image fuzzing for bounds and length handling. The Meson target only builds this tool when `fuse3_dep` is found.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tools/cfs-fuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tools/composefs-dump.c -->
# sources/cloud-native/composefs/tools/composefs-dump.c

## Purpose
`composefs-dump.c` converts an existing composefs image into another EROFS-format composefs image. It is a small utility around libcomposefs read/write APIs, useful for dumping or normalizing image contents through the library node model.

## Important APIs, Types, And Functions
`usage` prints the `SRC DEST` contract. `write_cb` adapts `FILE *` output to `lcfs_write_options_s.file_write_cb`. `main` uses `lcfs_version_from_fd`, `lcfs_load_node_from_fd`, and `lcfs_write_to` with `LCFS_FORMAT_EROFS`.

## Control Flow
The program validates two positional arguments, opens the source read-only, reads the image version, loads the root `lcfs_node_s`, closes the input fd, opens the destination with `fopen(..., "we")`, and writes the loaded tree back out using the same version. On any open/load/write failure it exits through `err`/`errx`.

## State And Persistence
The only persistent output is the destination image. In-memory state is a loaded libcomposefs node tree that is unreferenced before exit. There is no incremental state or configuration file.

## Dependencies And Integration Points
It depends on `libcomposefs/lcfs-writer.h` and utility helpers. It integrates with images accepted by libcomposefs readers and with downstream consumers of generated EROFS composefs images.

## Risks
The utility does no option parsing beyond argument count and inherits all validation behavior from libcomposefs. Destination writes are direct to the requested path; interrupted writes may leave a partial output file. It preserves the detected version but does not expose min/max version controls.

## Test Signals
Round-trip tests should load an image, dump it, and compare structural output with `composefs-info dump` or remount behavior. Error tests should cover missing arguments, invalid source images, and unwritable destinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tools/composefs-dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tools/composefs-info.c -->
# sources/cloud-native/composefs/tools/composefs-info.c

## Purpose
`composefs-info.c` is an inspection CLI for composefs images. It can list tree paths, dump a machine-readable tree format, list referenced objects, list missing objects relative to a basedir, and measure fs-verity digests for ordinary files.

## Important APIs, Types, And Functions
The command dispatch uses `command_handler_init`, `command_handler`, and `command_handler_end` function pointers. Output helpers include `print_escaped`, `print_escaped_optional`, `print_node`, `dump_node`, and `node_build_path`. Object collection uses `PrintData`, libcomposefs hash table functions, `get_objects`, `print_objects_handler_init`, `print_objects_handler`, `print_missing_objects_handler`, and `print_objects_handler_end`. `measure_files` calls `lcfs_fd_get_fsverity` and `digest_to_string`.

Global options include `--basedir` and repeatable `--filter`, with filters passed through `lcfs_read_options_s.toplevel_entries`.

## Control Flow
`main` parses options, creates a C locale for stable escaping, selects a command, optionally opens the basedir as `O_DIRECTORY | O_PATH`, initializes handler data, then iterates over image paths. Each image is opened, loaded through `lcfs_load_node_from_fd_ext`, and passed to the selected handler. `objects` and `missing-objects` collect payloads in a hash table and print sorted unique entries at the end.

## State And Persistence
The tool is read-only except for stdout/stderr. State is process-local: filters, basedir fd, locale, hash table, and loaded node trees. The `missing-objects` command consults the filesystem through `fstatat` but does not modify it.

## Dependencies And Integration Points
It depends on libcomposefs node readers, digest helpers, internal hash table code, and locale/ctype APIs. Its `dump` output is accepted by `mkcomposefs --from-file`, making this file part of a textual interchange path for composefs trees.

## Risks
Escaping rules are central to interoperability with `mkcomposefs`; changes can break dump/import round trips. `missing-objects` treats payloads as relative by stripping leading slashes, so path expectations must match object-store conventions. The line `const char *image_path = image_path = argv[i];` is odd but benign C assignment syntax. Filters reject names containing `/`, limiting scope to top-level entries.

## Test Signals
Tests should cover `ls`, `dump`, `objects`, `missing-objects`, `measure-file`, escaping of spaces, equals signs, lone dashes, binary-ish xattr values, hardlinks, inline content, filtered top-level entries, and missing-object detection against a temporary basedir.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tools/composefs-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tools/meson.build -->
# sources/cloud-native/composefs/tools/meson.build

## Purpose
This Meson file defines the composefs command-line tool build targets: `mkcomposefs`, `mount.composefs`, `composefs-info`, `composefs-dump`, and optionally `composefs-fuse`.

## Important APIs, Types, And Functions
It declares `libcomposefs_dep` from the in-tree library and `config_inc`, resolves `thread_dep`, and creates Meson `executable` targets. `composefs-info` also compiles `../libcomposefs/hash.c` with `composefs_hash_cflags`.

## Control Flow
Target creation is declarative. `mkcomposefs` links both public and internal composefs libraries plus threads and is installed. `mount.composefs` installs into `sbindir`. `composefs-info` installs as a user tool. `composefs-dump` and `composefs-fuse` are not installed. The FUSE target is gated by `fuse3_dep.found()`.

## State And Persistence
No runtime state exists. Build state is Meson target metadata and install decisions.

## Dependencies And Integration Points
This file integrates tools with `libcomposefs`, `libcomposefs_internal`, thread support, and optional fuse3. Install paths determine packaging and system mount-helper exposure.

## Risks
Changing `install` flags affects distribution surface. `composefs-fuse` is conditional and non-installed, so tests relying on it must account for missing fuse3. Internal library linkage means ABI changes in internal headers can break tools.

## Test Signals
Build tests should verify all targets with and without fuse3, installed file placement, and link correctness for threaded `mkcomposefs` and hash-backed `composefs-info`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tools/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tools/mkcomposefs.c -->
# sources/cloud-native/composefs/tools/mkcomposefs.c

## Purpose
`mkcomposefs.c` builds composefs EROFS images from either a source directory or a textual dump file. It computes content digests, can stage payloads into a digest store, supports reproducibility and filtering flags, and can print the resulting image digest.

## Important APIs, Types, And Functions
Parsing helpers include `split_at`, `unescape_string`, `unescape_optional_string`, `parse_int_field`, `parse_mtime`, and `parse_xattr`. Dump import is represented by `dump_info`, `hardlink_fixup`, and `field_info`, with `tree_from_dump_line`, `tree_add_node`, `tree_add_hardlink_fixup`, `tree_resolve_hardlinks`, and `tree_from_dump`.

Filesystem copy and digest work includes `ensure_dir`, `mkdir_parents`, `write_to_fd`, `copy_file_data_range`, `copy_file_data_classic`, `copy_file_data`, `copy_file_with_dirs_if_needed`, `construct_copy_data`, `construct_compute_data`, `process_copy`, `process_compute`, `execute_in_threads`, `compute_digest`, and `fill_store`.

The CLI supports `--digest-store`, `--use-epoch`, `--skip-devices`, `--skip-xattrs`, `--user-xattrs`, `--print-digest`, `--print-digest-only`, `--from-file`, `--min-version`, `--max-version`, and `--threads`.

## Control Flow
`main` starts with digest-by-content build flags, parses options and version/thread constraints, validates positional source/output arguments, opens an output file unless digest-only mode is used, and then builds a node tree. In `--from-file` mode it parses a dump stream into `lcfs_node_s` objects, including deferred hardlink resolution. In directory mode it calls `lcfs_build` with digest calculation disabled/no inline, then computes digests in parallel and optionally fills the digest store in parallel.

After the tree is ready, `main` configures `lcfs_write_options_s`, writes EROFS output with `lcfs_write_to`, optionally prints the digest, closes the output, and unrefs the tree. The fuzzer build replaces the normal CLI with a `LLVMFuzzerTestOneInput` harness that parses a dump, writes an image to memory, and verifies it can be reloaded.

## State And Persistence
Persistent outputs are the image file and optional digest-store object files. Digest-store writes are staged through temporary files, fsynced, optionally fs-verity-enabled, then renamed. In-memory mutable state includes node trees, hardlink fixups, dynamic read buffers, work collections, and a shared iterator protected by `mutex_thread_access`.

## Dependencies And Integration Points
The tool depends on libcomposefs writer/build APIs, Linux fs-verity and reflink/copy syscalls, pthreads, CPU affinity/sysinfo, and standard POSIX filesystem calls. It interoperates with `composefs-info dump` through the dump grammar, with `mount.composefs` and kernel composefs through generated images, and with object stores through digest payload paths.

## Risks
Dump parsing is security-sensitive: field splitting, escaping, xattrs, hardlinks, and strict mode all affect accepted input. Some error checks after parsing `gid` and `rdev` accidentally test `uid == 0 && err`, which can obscure the field associated with an error. `copy_file_range` behavior varies across kernels/filesystems, so fallback logic is critical. Threaded digest/copy processing shares a single mutex for iteration and copy-file-range state. Output to an image file is not atomic unless the caller writes to a temporary destination.

## Test Signals
Coverage should include directory builds, `--from-file` round trips, strict and non-strict dump parsing, malformed escapes/NULs/xattrs, hardlink cycles and missing targets, inline content size limits, symlink size validation, digest-only mode, version min/max handling, multi-threaded digest/store paths, copy-file-range fallback, fs-verity best-effort enabling, and the existing fuzz harness.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tools/mkcomposefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tools/mountcomposefs.c -->
# sources/cloud-native/composefs/tools/mountcomposefs.c

## Purpose
`mountcomposefs.c` implements the `mount.composefs` helper. It parses mount-style arguments and options, translates them into `lcfs_mount_options_s`, and calls `lcfs_mount_fd` to mount a composefs image.

## Important APIs, Types, And Functions
`usage` documents helper and direct invocation forms. `parse_option` handles comma-separated mount options with backslash escaping, delegating value unescaping to `unescape_option`. `main` maps options into `lcfs_mount_options_s`, including object directories, digest, idmap fd, upper/work dirs, readonly, and verity flags.

## Control Flow
The program accepts `-t composefs`, `-o`, and `-h`, then requires `IMAGE MOUNTPOINT`. It parses mount options, splits `basedir=PATH[:PATH]` into `options.objdirs`, validates that at least one object dir exists, requires `upperdir` and `workdir` together, sets digest and verity flags, optionally opens an idmap user namespace, opens the image, calls `lcfs_mount_fd`, and reports specialized verity/signature errors before freeing allocated object-dir storage.

## State And Persistence
Runtime state is local option parsing and file descriptors. The persistent effect is a kernel mount at the requested mount point. No configuration is written.

## Dependencies And Integration Points
It depends on `libcomposefs/lcfs-mount.h`, Linux mount/fsverity headers, and POSIX open/error APIs. It integrates with `/sbin/mount.<type>` helper conventions and with composefs object directories and optional overlay upper/work dirs.

## Risks
Option parsing mutates the `-o` string in place, as mount helpers usually can but tests should cover escaping. `basedir` splitting uses colon as a separator, so object paths containing colons are not representable. A missing object dir is fatal. The code frees `options.objdirs` only on success path after `lcfs_mount_fd`; failures exit via `errx`, which is acceptable for a short-lived CLI.

## Test Signals
Tests should cover direct and mount-helper syntax, unsupported `-t`, escaped commas/equals, multi-basedir parsing, verity/tryverity/digest flag mapping, idmap fd opening, ro/rw handling, upper/work pairing validation, and error messages for libcomposefs verity failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tools/mountcomposefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.devcontainer/Dockerfile -->
# sources/cloud-native/containerd/.devcontainer/Dockerfile

## Purpose
This Dockerfile defines the base image for containerd development in VS Code/devcontainers. It layers containerd build and integration-test dependencies onto Ubuntu 22.04.

## Important APIs, Types, And Functions
It uses `mcr.microsoft.com/devcontainers/base:1-ubuntu-22.04`, installs packages such as `gperf`, `dmsetup`, `libseccomp-dev`, `xfsprogs`, `iptables`, autotools, C++ compiler, `libtool`, and `acl`, then adds the CRIU PPA and installs `criu`.

## Control Flow
The image updates apt metadata, installs dependencies without recommends, cleans apt lists, adds `ppa:criu/ppa`, installs CRIU, sets default ACLs on `/tmp`, and copies the devcontainer welcome message.

## State And Persistence
Persistent image state is installed packages, apt configuration for the CRIU PPA, `/tmp` default ACLs, and the first-run notice file.

## Dependencies And Integration Points
It integrates with `.devcontainer/devcontainer.json` as the build Dockerfile and supports scripts in `.devcontainer/setup.sh`, Makefile builds, and rootful integration tests.

## Risks
The base image and PPA are external moving dependencies. Package versions are not pinned, so rebuilds can change behavior. `/tmp` ACL changes affect permissions inside the development container and should be intentional.

## Test Signals
A devcontainer build followed by `.devcontainer/setup.sh`, `make binaries`, `make test`, and root tests is the main validation signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.devcontainer/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.devcontainer/devcontainer.json -->
# sources/cloud-native/containerd/.devcontainer/devcontainer.json

## Purpose
This file configures the VS Code/devcontainer environment for containerd development.

## Important APIs, Types, And Functions
It builds from `.devcontainer/Dockerfile`, binds the repository into `/go/src/github.com/containerd/containerd`, enables Docker-in-Docker and Go `1.26.4` features, runs `.devcontainer/setup.sh` on create, and defines post-attach tasks for `make test` and `sudo make root-test`.

## Control Flow
Devcontainer tooling builds the image, mounts the workspace, provisions features, executes `onCreateCommand`, and runs named `postAttachCommand` tasks. The container runs as `root` and passes privileged host-related run args.

## State And Persistence
State is the mounted workspace plus installed tools and binaries from setup. Privileged mounts expose `/dev` and `/run/udev`.

## Dependencies And Integration Points
It depends on devcontainers feature registry entries for Docker-in-Docker and Go, and integrates with containerd Makefile targets and setup scripts.

## Risks
The environment is privileged and rootful, appropriate for runtime tests but broad in capability. Go version drift must remain aligned with CI and `.github/actions/install-go`.

## Test Signals
Opening the devcontainer should complete setup, and the post-attach `make test` and `sudo make root-test` commands should run.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.devcontainer/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.devcontainer/setup.sh -->
# sources/cloud-native/containerd/.devcontainer/setup.sh

## Purpose
This setup script installs runtime/test helper tools and builds/installs containerd inside the devcontainer.

## Important APIs, Types, And Functions
It calls repository scripts: `script/setup/install-seccomp`, `install-runc`, `install-cni`, `install-critools`, `install-failpoint-binaries`, `install-gotestsum`, and `install-teststat`. It then runs `make binaries GO_BUILD_FLAGS="-mod=vendor"` and `sudo -E PATH=$PATH make install`.

## Control Flow
With `set -eux`, any command failure stops provisioning. The CNI plugin version is extracted from `go.mod` by grepping `containernetworking/plugins`.

## State And Persistence
The script installs host/container-level binaries and builds repository artifacts under `bin/`. It also installs containerd into the configured prefix.

## Dependencies And Integration Points
It depends on the devcontainer image packages, repository setup scripts, vendored Go modules, and Makefile install semantics.

## Risks
The `grep ... go.mod | awk '{print $2}'` version extraction assumes module file format. Running with sudo and inherited PATH can install tools globally inside the container.

## Test Signals
Successful devcontainer creation, `containerd --version`, `runc --version`, CNI binaries presence, and `make test`/`make root-test` are relevant checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.devcontainer/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/bug_report.yaml -->
# sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/bug_report.yaml

## Purpose
This GitHub issue form guides users through filing actionable containerd bug reports.

## Important APIs, Types, And Functions
The YAML defines form metadata (`name`, `description`, `labels`) and body fields: explanatory markdown, required description, reproduction steps, required expected/actual results, required version input, relevant environment information, and optional CRI configuration.

## Control Flow
GitHub renders this form when a user chooses the bug report template. Required validations block incomplete submissions for key fields.

## State And Persistence
Submitted form data becomes issue body content and applies `kind/bug`.

## Dependencies And Integration Points
It integrates with GitHub issue forms, containerd labels, and maintainers' triage workflow. The guidance points users to `ctr pprof`, `SIGUSR1`, `runc --version`, `crictl info`, and kernel/CRI configuration data.

## Risks
If labels change, automatic triage metadata can break. The template permits empty reproduction steps, so maintainers may still need follow-up for some reports.

## Test Signals
GitHub validates issue form YAML. Repository triage should monitor whether required fields reduce incomplete bug reports.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/bug_report.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/config.yml -->
# sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/config.yml

## Purpose
This issue-template config allows blank issues and directs questions/chat to GitHub Discussions and CNCF Slack.

## Important APIs, Types, And Functions
It sets `blank_issues_enabled: true` and defines `contact_links` for discussions and Slack.

## Control Flow
GitHub reads this file when rendering the new issue chooser.

## State And Persistence
No repository runtime state exists; user selections create issues or navigate to external resources.

## Dependencies And Integration Points
It integrates with GitHub Discussions and CNCF Slack community channels.

## Risks
External URLs or channel names can drift. Allowing blank issues gives flexibility but can bypass structured templates.

## Test Signals
Manual issue-creation UI validation is sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/cri_kep.yaml -->
# sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/cri_kep.yaml

## Purpose
This issue form tracks SIG-Node/Kubernetes Enhancement Proposal integration work that affects containerd CRI behavior.

## Important APIs, Types, And Functions
The template prelabels issues with `kind/feature` and `area/cri`, assigns maintainers, suggests a `[SIG-Node]` title, and captures KEP references, problem statement, desired solution, and additional context.

## Control Flow
GitHub renders the form and enforces required problem and solution fields while leaving KEP reference details optional.

## State And Persistence
Submitted data persists as an issue and informs maintainer assignment/labels.

## Dependencies And Integration Points
It integrates containerd's issue tracker with Kubernetes SIG-Node planning and CRI maintainers.

## Risks
Hard-coded assignees can become stale. The template spelling `liason` appears in the sample value and may be copied into issues.

## Test Signals
GitHub issue-form validation and maintainer triage outcomes are the relevant signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/cri_kep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/feature_request.yaml -->
# sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/feature_request.yaml

## Purpose
This GitHub issue form captures feature requests for containerd.

## Important APIs, Types, And Functions
It applies `kind/feature` and requests a required problem statement, required desired solution, and optional additional context.

## Control Flow
GitHub renders and validates the form before issue submission.

## State And Persistence
The submitted fields become an issue for roadmap or design triage.

## Dependencies And Integration Points
It integrates with repository labels and feature triage workflow.

## Risks
The form is intentionally minimal, so larger feature work may still require design documents or follow-up questions.

## Test Signals
Issue-form YAML validation and downstream triage quality are the main checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/feature_request.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/actions/install-go/action.yml -->
# sources/cloud-native/containerd/.github/actions/install-go/action.yml

## Purpose
This composite GitHub Action centralizes Go installation for containerd workflows.

## Important APIs, Types, And Functions
It defines required input `go-version` with default `1.26.4` and runs `actions/setup-go` pinned to a full commit SHA corresponding to v6.4.0.

## Control Flow
Workflows call this local action, optionally overriding `go-version`; the composite step delegates to `actions/setup-go`.

## State And Persistence
It modifies the workflow runner environment by installing/selecting Go. No repository files are modified.

## Dependencies And Integration Points
It is used by CI, release, nightly, image, CodeQL, and node e2e workflows. It should stay aligned with `go.mod`, devcontainer Go feature version, and release Dockerfile `GO_VERSION`.

## Risks
If the pinned `actions/setup-go` SHA is stale or compromised upstream policy changes, every workflow using this local action is affected. The `required: true` input still has a default, so callers usually do not pass a value.

## Test Signals
Workflow runs should confirm `go version` and cache/setup behavior after version bumps.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/actions/install-go/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/dependabot.yml -->
# sources/cloud-native/containerd/.github/dependabot.yml

## Purpose
This file configures Dependabot updates for Go modules and GitHub Actions.

## Important APIs, Types, And Functions
It uses Dependabot version 2 with weekly schedules. Go module updates are grouped for `golang.org/x/*`, `k8s.io/*`, `github.com/moby/sys/*`, and `go.opentelemetry.io/*`; action updates are checked weekly.

## Control Flow
Dependabot scans configured ecosystems and opens at most 10 PRs per ecosystem according to schedule and grouping rules.

## State And Persistence
Dependabot creates PRs; this file itself holds policy state.

## Dependencies And Integration Points
It integrates with GitHub Dependabot, Go module files at repository root, vendoring checks, and pinned GitHub Actions in workflows.

## Risks
Grouped dependency updates can combine unrelated behavior changes within a namespace. Vendor requirements mean successful PRs must update generated vendor state.

## Test Signals
Dependabot PR CI, especially `make verify-vendor` and broad CI, validates update safety.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/api-release.yml -->
# sources/cloud-native/containerd/.github/workflows/api-release.yml

## Purpose
This workflow publishes GitHub releases for API tags matching `api/v*`.

## Important APIs, Types, And Functions
It sets `GO_VERSION=1.26.4`, defaults to read-only contents permission, checks signed tags, extracts release notes from tag annotation text, uploads the notes as an artifact, and creates a release with `softprops/action-gh-release`.

## Control Flow
On tag push, job `check` checks out the tag, verifies `git tag -v`, derives `stringver`, writes `release-notes.md`, and uploads it. Job `release` needs `check`, requests `contents: write`, downloads the artifact, and creates a non-latest release named `containerd API <version>`.

## State And Persistence
Persistent outputs are a GitHub Release and transient Actions artifacts. No source files are changed.

## Dependencies And Integration Points
It depends on signed annotated tags, `GITHUB_TOKEN`, checkout/upload/download actions, and release action. It separates API releases from full containerd releases.

## Risks
The release body path is `./builds/release-notes.md`, while downloaded artifacts are usually placed under an artifact-name subdirectory; this path should be watched in workflow runs. Signature verification shell precedence is subtle and should be validated. The workflow does not configure SSH allowed signers unlike the main release workflow.

## Test Signals
Dry-run validation is hard because it triggers on tags; evidence comes from successful signed `api/v*` release runs and correct release note body rendering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/api-release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/buf-breaking.yml -->
# sources/cloud-native/containerd/.github/workflows/buf-breaking.yml

## Purpose
This workflow detects breaking changes in protobuf API files during pull requests.

## Important APIs, Types, And Functions
It triggers on PR changes to `api/**/*.proto` or `api/buf.yaml`, uses `bufbuild/buf-action@v1` with Buf `1.63.0`, and disables breaking checks when the PR has label `breaking-api-change`.

## Control Flow
For target branches `main` and `release/**`, the workflow checks out code and runs Buf against input `api` with lint/format/commenting disabled and breaking detection controlled by labels.

## State And Persistence
No repository state is persisted. The workflow reports check status on PRs.

## Dependencies And Integration Points
It integrates with Buf's breaking-change engine, GitHub PR labels, and API proto files.

## Risks
Maintainers can bypass detection with a label, which is intentional but should be controlled. Only proto and `buf.yaml` path changes trigger the workflow; generator config changes in `buf.gen.yaml` are not included.

## Test Signals
PRs changing `api/**/*.proto` should show Buf status, and labeled breaking-change PRs should bypass only the breaking gate.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/buf-breaking.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/build-test-images.yml -->
# sources/cloud-native/containerd/.github/workflows/build-test-images.yml

## Purpose
This manual workflow builds and pushes Windows-backed volume test images to a target registry namespace.

## Important APIs, Types, And Functions
It accepts workflow-dispatch inputs for target project, Azure Windows image, VM size, and Azure location. It uses Azure login/CLI, Docker installation, SSH key generation, Windows helper scripts, GHCR login, and Makefile targets under `integration/images/volume-copy-up` and `volume-ownership`.

## Control Flow
The job checks out containerd, installs Go and Docker, creates an Azure resource group and Windows helper VM, prepares Windows Docker and SSH/TLS access, fetches Docker client certificates, logs in to GHCR, builds/pushes multi-platform test images through a remote Windows Docker endpoint, and always deletes the Azure resource group.

## State And Persistence
Persistent outputs are pushed container images. Transient state includes Azure resource groups/VMs, SSH keys, Docker TLS certs, and local buildx state.

## Dependencies And Integration Points
It depends on `AZURE_SUB_ID`, `AZURE_CREDS`, GHCR package permissions, repository Windows setup scripts, Docker packages, and integration image Makefiles.

## Risks
The workflow opens SSH and Docker TLS ports on a public VM and relies on cleanup in an `always()` step. Azure quota, image availability, and remote Docker readiness can fail independently of repository code. The generated password is masked, but VM provisioning still uses password auth initially.

## Test Signals
Manual run success, image availability in GHCR, and subsequent Windows integration tests pulling those images are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/build-test-images.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/ci.yml -->
# sources/cloud-native/containerd/.github/workflows/ci.yml

## Purpose
This is the primary containerd CI workflow for pull requests and merge queue entries. It runs linting, project checks, protobuf checks, manpage generation, crossbuilds, binaries, Linux/Windows/macOS tests, Vagrant distro integration tests, CRI-in-userns tests, and Kubernetes node e2e.

## Important APIs, Types, And Functions
Major jobs are `linters`, `project`, `protos`, `man`, `crossbuild`, `binaries`, `integration-windows`, `integration-linux`, `integration-vagrant`, `tests-cri-in-userns`, `tests-mac-os`, reusable `node-e2e`, and final `results`. The workflow uses the local Go action, pinned checkout/upload/cache actions, `golangci-lint-action`, `containerd/project-checks`, Makefile targets, setup scripts, Vagrant/libvirt, Podman, cri-tools, CRIU, erofs-utils, and artifact uploads.

## Control Flow
Static gates run first (`project`, `linters`, `protos`, `man`). Build/test jobs depend on those gates. Linux integration installs runtime dependencies, builds newer erofs-utils, loads EROFS and dm-verity modules, installs containerd, runs unit/root/integration/CRI/critest/checkpoint tests, and uploads logs. Windows integration builds with `mingw32-make`, installs CNI, runs root/integration/CRI/critest, and uploads results. Vagrant tests exercise Fedora and AlmaLinux boxes with cgroupfs/systemd and runc/crun combinations. The `results` job collapses required statuses.

## State And Persistence
The workflow persists artifacts for test reports and logs. Runner state includes installed packages, kernel modules, containerd services, Vagrant boxes, test images, and temporary reports. It does not modify repository state.

## Dependencies And Integration Points
It is the central integration point for `.golangci.yml`, `Makefile`, scripts under `script/setup` and `script/test`, generated protobufs, Kubernetes cri-tools, EROFS tools, and the reusable node e2e workflow.

## Risks
The workflow is broad and sensitive to external package repositories, GitHub runner images, Azure/Windows quirks, kernel module availability, Vagrant box availability, and flaky CRI tests. Some jobs are skipped for merge queue or private ARM runners. The Linux job builds erofs-utils from a versioned tarball due to package age. Required-check masking is handled by the `results` job, so `needs` must stay aligned with intended required jobs.

## Test Signals
Passing CI itself is the signal. Important granular signals are `make verify-vendor`, `make check-protos`, lint results, crossbuilds, unit/root tests, serial and parallel integration tests, CRI integration, critest reports, checkpoint/restore, Vagrant distro coverage, macOS unit tests, and node e2e logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/codeql.yml -->
# sources/cloud-native/containerd/.github/workflows/codeql.yml

## Purpose
This workflow runs GitHub CodeQL analysis for containerd on pushes and pull requests to main and release branches.

## Important APIs, Types, And Functions
It uses checkout, the local Go install action, `github/codeql-action/init`, a build step that installs `libseccomp-dev` and runs `make`, and `github/codeql-action/analyze`. It grants `security-events: write`.

## Control Flow
The job only runs for `github.repository == 'containerd/containerd'`, checks out code, installs Go, initializes CodeQL, builds the project, and uploads analysis.

## State And Persistence
Persistent output is CodeQL SARIF/security events in GitHub code scanning.

## Dependencies And Integration Points
It integrates with GitHub Advanced Security, the Makefile default build, and libseccomp build dependency.

## Risks
Only Ubuntu is scanned despite comments mentioning other platforms. Build failures block analysis. It runs only in the upstream repository, not forks.

## Test Signals
Successful CodeQL workflow runs and uploaded code-scanning alerts are validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/codeql.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/fuzz.yml -->
# sources/cloud-native/containerd/.github/workflows/fuzz.yml

## Purpose
This workflow runs fuzzing checks on pull requests for containerd.

## Important APIs, Types, And Functions
It has `ci_fuzz` using Google OSS-Fuzz CIFuzz build/run actions for project `containerd`, and `go_test_fuzz` using the repository `script/go-test-fuzz.sh`. Crash artifacts are uploaded on failure.

## Control Flow
For upstream PRs, CIFuzz builds fuzzers, runs them for 300 seconds with `continue-on-error: true`, and uploads crash artifacts when appropriate. The Go test fuzz job checks out code, installs Go, runs Go-native fuzz targets, and uploads fuzz testdata artifacts if it fails.

## State And Persistence
Workflow artifacts may persist crash reproducers. No source state is changed.

## Dependencies And Integration Points
It depends on OSS-Fuzz project configuration, Go fuzz tests in the repository, and the local Go setup action.

## Risks
`continue-on-error` on CIFuzz run can hide runtime fuzz failures unless artifact/status handling is monitored. The workflow is upstream-only and PR-only.

## Test Signals
Fuzzer build success, Go fuzz script success, and absence of uploaded crash artifacts are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/fuzz.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/images.yml -->
# sources/cloud-native/containerd/.github/workflows/images.yml

## Purpose
This manual workflow mirrors an upstream test image into `ghcr.io/containerd` or a caller-provided target name.

## Important APIs, Types, And Functions
It accepts workflow inputs `upstream` and optional `image`, installs containerd dependencies, builds containerd with `GO_BUILDTAGS="no_btrfs"`, runs containerd, uses `ctr content fetch --all-platforms`, and pushes with `ctr images push` using `GITHUB_TOKEN`.

## Control Flow
The job checks out code, installs Go, sets GOPATH/PATH, installs `gperf` and seccomp, builds and installs containerd, starts `containerd` in the background, computes the mirror target, fetches all platforms from upstream, pushes to GHCR, and kills the daemon.

## State And Persistence
Persistent output is a GHCR package image. Runner state includes installed containerd binaries and a temporary daemon.

## Dependencies And Integration Points
It depends on GHCR package write permission, upstream registry availability, `ctr`, and containerd build/install scripts.

## Risks
The final `kill` is not guarded by `always()`, so failures before cleanup may leave a daemon running until runner teardown. Target naming is string-based and should be reviewed for unexpected upstream names.

## Test Signals
Manual run success and pullability of the mirrored GHCR image validate behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/images.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/links.yml -->
# sources/cloud-native/containerd/.github/workflows/links.yml

## Purpose
This workflow checks Markdown links in the repository.

## Important APIs, Types, And Functions
It runs on manual dispatch, daily schedule, and PR changes to the workflow itself. It uses `lycheeverse/lychee-action` with arguments excluding `vendor` and `releases`, a 30-second timeout, markdown output, and job summary.

## Control Flow
For the upstream repository, the job checks out code and runs Lychee against `./**/*.md`, failing on broken links.

## State And Persistence
No persistent repository state exists; results are workflow status and job summary.

## Dependencies And Integration Points
It integrates with Markdown documentation health and external URL availability.

## Risks
Scheduled link checks can fail due to transient external outages. PRs changing Markdown do not trigger this workflow unless the workflow file changes.

## Test Signals
Passing scheduled runs and Lychee summaries are the evidence.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/links.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/nightly.yml -->
# sources/cloud-native/containerd/.github/workflows/nightly.yml

## Purpose
This workflow performs scheduled and self-test nightly binary builds across Linux architectures and Windows amd64.

## Important APIs, Types, And Functions
Linux builds target amd64, arm64, s390x, ppc64le, and riscv64 using crossbuild packages and `make binaries`. Windows builds amd64 on `windows-latest`. Artifacts are uploaded per platform.

## Control Flow
On daily schedule or PR changes to the workflow, Linux checkout/install steps set GOPATH/PATH, install cross compilers, build each arch into separate `bin_*` directories, and upload each. Windows checks out, installs Go, sets env, builds, and uploads `bin/`.

## State And Persistence
Persistent outputs are Actions build artifacts. Runner state includes cross compiler packages and build directories.

## Dependencies And Integration Points
It uses the local Go action, Makefile `binaries`, crossbuild-essential packages, and Actions artifacts.

## Risks
Nightly does not run full tests; it detects build regressions. Cross compiler package availability and runner image changes can affect results.

## Test Signals
Successful artifact upload for each architecture is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/nightly.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/node-e2e.yml -->
# sources/cloud-native/containerd/.github/workflows/node-e2e.yml

## Purpose
This reusable workflow runs Kubernetes node e2e tests against a freshly built containerd.

## Important APIs, Types, And Functions
It is invoked with `workflow_call` and optional `k8s_version` defaulting to `master`. It checks out containerd and Kubernetes, installs Go, installs seccomp/runc/CNI, builds and installs containerd, writes a CRI config, starts systemd `containerd`, then runs `make test-e2e-node` with focused/skipped test regexes and kubelet flags.

## Control Flow
The job first frees disk space, checks out both repositories, disables swap, installs dependencies, builds/installs containerd, configures CRI runtimes for runc and `test-handler`, verifies `ctr version`, runs node e2e, and on failure collects kubelet/containerd logs and uploads them.

## State And Persistence
Runner state includes installed containerd service, Kubernetes checkout, generated `/etc/containerd/config.toml`, and failure artifacts.

## Dependencies And Integration Points
It integrates containerd with Kubernetes node conformance, systemd, runc, CNI plugins, and GitHub reusable workflow callers such as `ci.yml`.

## Risks
Testing against Kubernetes `master` is intentionally high-signal but can introduce upstream breakage unrelated to containerd. Disk pressure is managed by deleting many preinstalled toolchains. The skip/focus regex controls coverage and must be maintained as Kubernetes tests evolve.

## Test Signals
Passing node e2e and, on failure, uploaded kubelet/containerd logs are the relevant signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/node-e2e.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/release.yml -->
# sources/cloud-native/containerd/.github/workflows/release.yml

## Purpose
This workflow builds release binaries and publishes full containerd GitHub releases for tags matching `v*`; it also builds release artifacts on pushes/PRs to main and release branches.

## Important APIs, Types, And Functions
Jobs are `check`, `build`, and `release`. It verifies signed tags, extracts release notes, builds platform release tarballs through Docker Buildx using `.github/workflows/release/Dockerfile`, uploads artifacts, creates build provenance attestations, and publishes via `softprops/action-gh-release`.

## Control Flow
`check` runs only for tag pushes and validates tag signatures, including SSH allowed-signers config setup. `build` runs a platform matrix for Linux amd64/arm64/ppc64le/s390x/riscv64 and Windows amd64, setting `RELEASE_VER` for tags, invoking Docker Buildx, and uploading release tarballs. `release` runs only for tag pushes, downloads artifacts, attests `.tar.gz` files, renames the attestation bundle, and creates the latest GitHub release.

## State And Persistence
Persistent outputs are release artifacts, checksums from Makefile release targets, a GitHub Release, and provenance attestation JSONL. Intermediate Actions artifacts are also stored.

## Dependencies And Integration Points
It depends on signed tags, Docker Buildx, `tonistiigi/xx`, Go release image, the release Dockerfile, Makefile `release static-release`, GitHub artifact and attestation actions, and `GITHUB_TOKEN`.

## Risks
Release correctness depends on the build Dockerfile and Makefile staying in sync. The build job runs for PRs too but release publication is tag-only. Windows build args for CNI networking are hard-coded from previously generated packages. Tag signature shell logic is subtle and security-critical.

## Test Signals
Successful matrix artifact builds on PRs/branches, signed tag release runs, attestation creation, and uploaded release assets validate this workflow.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/release/Dockerfile -->
# sources/cloud-native/containerd/.github/workflows/release/Dockerfile

## Purpose
This Dockerfile builds cross-platform containerd release artifacts inside Docker Buildx.

## Important APIs, Types, And Functions
It defines `UBUNTU_VERSION`, `BASE_IMAGE`, `GO_VERSION=1.26.4`, and `GO_IMAGE`, imports `tonistiigi/xx:1.6.1`, installs build tools and target gcc through `xx-apt-get`, binds the Go toolchain from the Go image, wraps Go with `xx-go`, runs `make release static-release`, verifies binaries with `xx-verify`, checks the git tree, and exports `/releases` from a scratch stage.

## Control Flow
The release workflow passes target platform and release args. The Dockerfile builds a base with cross tooling, branches into `linux` or `windows` stages, copies the source, builds release artifacts for the target, verifies executable compatibility, fails if the build dirties the repository, and emits release files.

## State And Persistence
Persistent output is the release stage contents. Build cache mounts store Go build and module cache data during Buildx runs.

## Dependencies And Integration Points
It integrates with `.github/workflows/release.yml`, Makefile release targets, `tonistiigi/xx`, the Go container image, and Ubuntu package repositories.

## Risks
Base image and cross-toolchain availability affect reproducibility. The git dirty check can fail if generation during release changes tracked files. Windows CNI args are supplied externally and must match release workflow expectations.

## Test Signals
Buildx matrix success, `xx-verify` success for executables, and clean git status after `make release static-release` are key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/release/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/scorecards.yml -->
# sources/cloud-native/containerd/.github/workflows/scorecards.yml

## Purpose
This workflow runs OSSF Scorecard supply-chain security analysis.

## Important APIs, Types, And Functions
It triggers on branch protection rule changes, weekly schedule, and pushes to main. It uses read-all default permissions, grants `security-events: write` and `id-token: write` for analysis, runs `ossf/scorecard-action`, uploads `results.sarif`, and uploads SARIF to code scanning.

## Control Flow
The job checks out code without persisting credentials, runs Scorecard with SARIF output and `publish_results: false`, uploads the SARIF artifact for five days, and uploads it to GitHub code scanning.

## State And Persistence
Persistent outputs are code-scanning results and short-lived SARIF artifacts.

## Dependencies And Integration Points
It integrates with OSSF Scorecard, GitHub code scanning, and repository branch protection/security posture.

## Risks
Only default branch is supported per comment. Scorecard checks can change behavior as the action evolves, although the action is pinned by SHA.

## Test Signals
Successful scheduled runs and visible SARIF/code scanning results validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/scorecards.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/stale.yml -->
# sources/cloud-native/containerd/.github/workflows/stale.yml

## Purpose
This workflow marks and closes stale issues and pull requests that already carry labels indicating they need more information, updates, or rebasing.

## Important APIs, Types, And Functions
It runs `actions/stale` with 90 days before stale, 7 days before close, `any-of-labels` limited to `status/more-info-needed,status/needs-update,needs-rebase`, custom issue/PR messages, and dry-run behavior on PRs changing the workflow.

## Control Flow
Scheduled upstream runs request issue and pull-request write permissions and execute the stale action. PR-triggered runs operate in debug-only mode.

## State And Persistence
The workflow can add stale labels/comments and close issues/PRs.

## Dependencies And Integration Points
It integrates with GitHub issue/PR metadata and containerd triage labels.

## Risks
Label names are policy-critical. Misconfiguration could close active work, but the workflow is constrained to specific labels and dry-runs on workflow PRs.

## Test Signals
Scheduled action logs and observed stale/close comments on qualifying issues/PRs are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/stale.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/windows-hyperv-periodic-trigger.yml -->
# sources/cloud-native/containerd/.github/workflows/windows-hyperv-periodic-trigger.yml

## Purpose
This scheduled/manual trigger delegates to the upstream reusable Windows Hyper-V integration workflow.

## Important APIs, Types, And Functions
It runs daily at 01:00 UTC or manually, checks `github.repository == 'containerd/containerd'`, and uses `containerd/containerd/.github/workflows/windows-hyperv-periodic.yml@main` with Azure secrets.

## Control Flow
The single job invokes the reusable workflow and passes `AZURE_SUB_ID` and `AZURE_CREDS`.

## State And Persistence
State is created by the called workflow, not this trigger.

## Dependencies And Integration Points
It depends on GitHub reusable workflows and Azure secrets. It hard-codes the upstream repository because dynamic `uses` references are not supported.

## Risks
Forks cannot easily reuse this trigger without edits. The called workflow always comes from `main`, so scheduled coverage tracks main workflow changes.

## Test Signals
Successful delegated workflow runs validate the trigger.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/windows-hyperv-periodic-trigger.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/windows-hyperv-periodic.yml -->
# sources/cloud-native/containerd/.github/workflows/windows-hyperv-periodic.yml

## Purpose
This reusable/manual workflow provisions an Azure Windows Server VM with Containers and Hyper-V, builds containerd and hcsshim, and runs Windows Hyper-V integration, CRI integration, and critest suites.

## Important APIs, Types, And Functions
It defines Azure, SSH, image, and runtime environment variables, accepts Azure secrets through `workflow_call`, uses Azure login/CLI, SSH/SCP, PowerShell setup scripts, HNS NAT setup, hcsshim build from `master`, generated CRI config for `runhcs-wcow-hypervisor`, `go-junit-report`, `xmlstarlet`, and `actions/github-script` for final stage status.

## Control Flow
The workflow creates log directories and an SSH key, logs into Azure, creates a resource group and VM, enables SSH, installs Windows Containers and Hyper-V, reboots and waits, configures NAT, prepares the test environment, clones/builds containerd and hcsshim on the VM, runs integration tests with `USE_HYPERV=1`, prepares image/config files, runs CRI integration, builds/runs critest, converts logs to JUnit XML, checks that all logical test stages reported success, and always deletes the Azure group.

## State And Persistence
Transient state includes Azure resource groups/VMs, Windows installed features, cloned source trees, built binaries, logs, JUnit XML, and remote containerd services. Cleanup deletes the Azure resource group.

## Dependencies And Integration Points
It integrates with Azure infrastructure, Windows HNS/Hyper-V, hcsshim, containerd scripts, Kubernetes cri-tools, Testgrid-style JUnit output, and periodic trigger workflow.

## Risks
The workflow uses a static `Passw0rdAdmin` value despite a comment saying it will be generated. It clones `http://github.com/containerd/containerd` on the VM rather than the checked-out commit, so tests may not match the triggering revision. Azure resource cleanup is critical. `continue-on-error` stages rely on explicit `SUCCEEDED` outputs for final failure detection.

## Test Signals
Successful integration, CRI integration, critest stages, generated JUnit XML, and resource cleanup are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/windows-hyperv-periodic.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/windows-periodic-trigger.yml -->
# sources/cloud-native/containerd/.github/workflows/windows-periodic-trigger.yml

## Purpose
This scheduled/manual trigger delegates to the upstream reusable Windows process-isolated integration workflow.

## Important APIs, Types, And Functions
It triggers daily at 01:00 UTC or manually, gates to the upstream repository, and calls `containerd/containerd/.github/workflows/windows-periodic.yml@main` with Azure secrets.

## Control Flow
The single job invokes the reusable workflow using `workflow_call` semantics.

## State And Persistence
All runtime state is owned by the called workflow.

## Dependencies And Integration Points
It depends on GitHub reusable workflow support and configured Azure secrets.

## Risks
Hard-coded upstream workflow reference limits fork use and means the trigger always follows main's reusable workflow.

## Test Signals
Successful invocation and completion of the delegated workflow validate this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/windows-periodic-trigger.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/windows-periodic.yml -->
# sources/cloud-native/containerd/.github/workflows/windows-periodic.yml

## Purpose
This reusable/manual workflow provisions an Azure Windows Server VM and runs containerd Windows integration, CRI integration, and critest suites without Hyper-V isolation.

## Important APIs, Types, And Functions
It uses Azure secrets, Azure login/CLI, SSH/SCP, Windows setup scripts, HNS NAT setup, repository Makefile targets, cri-tools, go-junit-report, `xmlstarlet`, and `actions/github-script` for final logical stage status.

## Control Flow
The job prepares artifact directories, generates SSH keys, creates an Azure VM, enables SSH, installs the Containers feature, waits for reboot, creates NAT, prepares the VM, clones and builds containerd, runs integration tests, writes image list files, runs CRI integration, builds and runs critest against a registered Windows containerd service, pulls JUnit XML logs, checks stage success outputs, and always deletes the Azure resource group.

## State And Persistence
State is transient Azure VM/resource group state, remote source/build/log files, JUnit reports, and remote containerd service registration. Cleanup removes cloud resources.

## Dependencies And Integration Points
It integrates with periodic trigger workflow, Azure Windows images, Windows container networking, containerd scripts, cri-tools, and external test reporting.

## Risks
Like the Hyper-V workflow, it uses a static admin password and clones the repository from GitHub on the VM rather than testing the checked-out commit. SSH retry logic and NAT setup can be flaky. `continue-on-error` test steps depend on explicit output checks.

## Test Signals
Integration/CRI/critest success outputs, JUnit conversion, and resource cleanup logs are key evidence.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.github/workflows/windows-periodic.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/.golangci.yml -->
# sources/cloud-native/containerd/.golangci.yml

## Purpose
This file configures golangci-lint v2 for containerd.

## Important APIs, Types, And Functions
Enabled linters include `copyloopvar`, `depguard`, `dupword`, `gosec`, `misspell`, `modernize`, `nolintlint`, `revive`, `unconvert`, and `usetesting`; `errcheck` is disabled. Settings deny direct `github.com/opencontainers/runc` dependencies, forbid standard `regexp` in favor of `internal/lazyregexp.New`, temporarily exclude several gosec rules, tune staticcheck/revive/nolintlint, and enable `gofmt`/`goimports` formatters.

## Control Flow
`golangci-lint run` reads this config during `make check` and CI `linters`. Exclusions suppress generated or known-noisy paths and specific revive/forbidigo findings.

## State And Persistence
No runtime state exists; lint policy is persisted in YAML.

## Dependencies And Integration Points
It integrates with `Makefile` `check`, `.github/workflows/ci.yml`, generated API exclusions, and repository dependency policy.

## Risks
Excluding broad paths (`api`, `cluster`, docs, releases, test) reduces lint coverage. Many gosec exclusions defer security cleanup. Forbidigo exceptions for tests must stay targeted.

## Test Signals
Passing `golangci-lint run` on all CI OS matrix entries and useful lint findings on new code validate the config.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/Makefile -->
# sources/cloud-native/containerd/Makefile

## Purpose
The Makefile is containerd's main build, test, generation, release, install, and cleanup entry point.

## Important APIs, Types, And Functions
It defines build variables (`GO`, `ROOTDIR`, `PREFIX`, `VERSION`, `REVISION`, `PACKAGE`, `GOOS`, `GOARCH`, tags, ldflags), packages (`PACKAGES`, `API_PACKAGES`, root-test package discovery), binaries (`ctr`, `containerd`, `containerd-stress`), manpages, release names, and many phony targets.

Major targets include `all`, `check`, `ci`, `generate`, `protos`, `check-protos`, `proto-fmt`, `build`, `test`, `root-test`, `integration`, `cri-integration`, failpoint helper binaries, `benchmark`, `binaries`, `man`, `install-man`, `install-doc`, `release`, `static-release`, `install-cri-deps`, deprecated CRI release targets, `clean`, `clean-test`, `install`, `uninstall`, `coverage`, `root-coverage`, `cri-integration-coverage`, `vendor`, `verify-vendor`, `clean-vendor`, and `help`.

## Control Flow
Default `all` builds binaries. Build targets use Go package lists and ldflags embedding version metadata. Proto generation updates Buf deps, runs generation, removes undesired generated files, fixes acronyms, applies build tags, and may add a module replace if `api/next.txtpb` changed. Test targets separate normal, root, integration, and CRI integration flows. Release targets package binaries and checksums. Vendor verification copies the repo to a temporary directory, runs tidy/vendor/verify, and diffs back.

## State And Persistence
The Makefile creates `bin/`, `man/`, `releases/`, `_output/`, coverage files, generated proto files, vendor changes, installed files under `DESTDIR/PREFIX`, and may remove runtime test debris in `clean-test`.

## Dependencies And Integration Points
It integrates with Go, Buf, custom generators (`go-buildtag`, `protoc-gen-go-fieldpath`), setup/test scripts, CI workflows, release Dockerfile, devcontainer setup, systemd unit packaging, CNI/runc/cri-tools installers, and platform-specific `Makefile.$(GOOS)`.

## Risks
Targets like `clean-test` kill processes and unmount test leftovers, so they require care. Package discovery shells out to Go and git; missing tools change behavior. Generated proto and vendor targets can modify tracked files. Release/install targets differ by GOOS, especially Windows CRI deps.

## Test Signals
Important validations are `make check`, `make binaries`, `make test`, `make root-test`, `make integration`, `make cri-integration`, `make verify-vendor`, `make check-protos`, release Dockerfile builds, and CI matrix success.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/buf.gen.yaml -->
# sources/cloud-native/containerd/api/buf.gen.yaml

## Purpose
This Buf generation config defines how containerd API protobufs generate Go, gRPC, ttrpc, and fieldpath code.

## Important APIs, Types, And Functions
It uses remote plugins `buf.build/protocolbuffers/go:v1.28.1` and `buf.build/grpc/go:v1.2.0`, plus local plugins `protoc-gen-go-ttrpc` and `protoc-gen-go-fieldpath`. All outputs use `paths=source_relative`; Go generation maps `google/rpc/status.proto` to the genproto package.

## Control Flow
`make protos` runs `buf generate` in `api`, which reads this config and emits generated files alongside sources.

## State And Persistence
Generated `.pb.go`, grpc/ttrpc, and fieldpath files are persistent source artifacts.

## Dependencies And Integration Points
It integrates with Buf, generated API Go code, local generator binaries in `bin/`, and CI proto checks.

## Risks
Remote plugin version bumps can change generated output broadly. Local plugins must be installed before generation.

## Test Signals
`make protos`, clean git diff expectations, and `make check-protos` are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/buf.gen.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/buf.yaml -->
# sources/cloud-native/containerd/api/buf.yaml

## Purpose
This Buf module config declares the containerd API module and dependency set.

## Important APIs, Types, And Functions
It uses version `v2`, depends on `buf.build/googleapis/googleapis`, and defines module path `.` with name `buf.build/containerd/api-dev`.

## Control Flow
Buf commands in the Makefile and workflows read this file for dependency resolution, module identity, build, format, generate, and breaking checks.

## State And Persistence
Policy state is stored in YAML; Buf dependency updates may affect lock/dependency files elsewhere.

## Dependencies And Integration Points
It integrates with `buf.gen.yaml`, `buf-breaking.yml`, and API proto imports such as Google API protos.

## Risks
Changing module name or deps can alter breaking-check baseline and generation resolution.

## Test Signals
`buf build`, `buf format --diff --exit-code`, and PR breaking checks validate this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/buf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/doc.go -->
# sources/cloud-native/containerd/api/doc.go

## Purpose
This file declares the root `api` Go package for containerd API sources.

## Important APIs, Types, And Functions
It contains only the package declaration and license header.

## Control Flow
There is no executable control flow.

## State And Persistence
No state exists.

## Dependencies And Integration Points
It gives Go tooling a package document anchor for `github.com/containerd/containerd/api`.

## Risks
Low risk; accidental package-name changes would break imports.

## Test Signals
`go -C api test ./...` and documentation generation validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/container.pb.go -->
# sources/cloud-native/containerd/api/events/container.pb.go

## Purpose
This generated file provides Go protobuf types and descriptors for container lifecycle event messages defined in `events/container.proto`.

## Important APIs, Types, And Functions
It defines `ContainerCreate`, `ContainerUpdate`, `ContainerDelete`, nested `ContainerCreate_Runtime`, getters for each field, `ProtoReflect`, deprecated `Descriptor` methods, `File_events_container_proto`, raw descriptor data, message info arrays, dependency indexes, and `file_events_container_proto_init`.

Fields include create `ID`, `Image`, and runtime name/options (`google.protobuf.Any`); update `ID`, `Image`, `Labels`, and `SnapshotKey`; delete `ID`.

## Control Flow
Generated methods reset messages, return string/proto reflection forms, expose nil-safe getters, compress raw descriptors once, and build the file descriptor during package init.

## State And Persistence
State is in-memory protobuf descriptor metadata, guarded raw descriptor compression, and per-message protoimpl state/size/unknown fields. There is no disk persistence.

## Dependencies And Integration Points
It depends on `google.golang.org/protobuf`, `anypb`, and a blank import of `github.com/containerd/containerd/api/types` for custom options. Event publishers/consumers in containerd use these types for typed event payloads.

## Risks
Manual edits would be overwritten by `make protos`. API compatibility is controlled by field numbers and proto definitions; changing or reusing numbers can break clients. `Any` runtime options require registered typeurl handling for consumers.

## Test Signals
Generated-code freshness via `make protos`/git diff, `go -C api test ./...`, Buf breaking checks, and event serialization/deserialization tests are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/container.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/container.proto -->
# sources/cloud-native/containerd/api/events/container.proto

## Purpose
This proto defines container event payloads for create, update, and delete events.

## Important APIs, Types, And Functions
Package is `containerd.events`; Go package is `github.com/containerd/containerd/api/events;events`. It imports `google/protobuf/any.proto` and `types/fieldpath.proto`, enables `containerd.types.fieldpath_all`, and defines `ContainerCreate`, nested `Runtime`, `ContainerUpdate`, and `ContainerDelete`.

## Control Flow
There is no runtime control flow in the proto. Generation produces protobuf Go types and fieldpath helpers.

## State And Persistence
The schema is persistent API state. Field numbers and names form the compatibility contract for serialized event messages.

## Dependencies And Integration Points
It integrates with containerd's event bus, generated Go code, Buf breaking checks, and fieldpath-based event filtering.

## Risks
Removing or changing field numbers is API-breaking. Runtime options use `Any`, so consumers need type registration to inspect nested options. `fieldpath_all` exposes fields to generated filtering semantics.

## Test Signals
Buf breaking checks, generated code freshness, and event filtering/serialization tests validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/container.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/container_fieldpath.pb.go -->
# sources/cloud-native/containerd/api/events/container_fieldpath.pb.go

## Purpose
This generated file implements fieldpath lookup helpers for container event protobuf messages.

## Important APIs, Types, And Functions
It defines `Field([]string) (string, bool)` methods for `ContainerCreate`, `ContainerCreate_Runtime`, `ContainerUpdate`, and `ContainerDelete`. It imports `github.com/containerd/typeurl/v2` for `Any` decoding and `strings` for label key joining.

## Control Flow
Each `Field` method checks for an empty path, switches on the first segment, returns string fields only when non-empty, recurses into runtime fields, decodes `Any` runtime options and calls a nested `Field` adaptor when available, and special-cases labels by joining remaining path segments with `.`.

## State And Persistence
No persistent state exists. Runtime state is limited to Any decoding and map lookup.

## Dependencies And Integration Points
It integrates with containerd event filtering systems that evaluate fieldpaths against event payloads. It depends on generated proto types and typeurl registration.

## Risks
The generated comment notes runtime message recursion is probably incorrect in many cases because nested messages may not implement `Field`. Label joining means labels with dotted keys are represented through path segments. Non-string scalar handling is limited by generator behavior.

## Test Signals
Fieldpath filter tests should cover id/image/snapshot_key, labels with dotted keys, runtime name, runtime options with registered fieldpath-aware types, nil runtime, and invalid paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/container_fieldpath.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/content.pb.go -->
# sources/cloud-native/containerd/api/events/content.pb.go

## Purpose
This generated file provides Go protobuf types and descriptors for content lifecycle events.

## Important APIs, Types, And Functions
It defines `ContentCreate` with `Digest` and `Size`, `ContentDelete` with `Digest`, nil-safe getters, proto reflection methods, raw descriptor data, message info arrays, and `file_events_content_proto_init`.

## Control Flow
Generated control flow mirrors normal protoc-gen-go output: reset/store message info, string conversion, reflection, descriptor compression once, and descriptor build during init.

## State And Persistence
State is in-memory protobuf message and descriptor metadata. The file persists generated API code.

## Dependencies And Integration Points
It depends on `google.golang.org/protobuf` and a blank import of containerd API types for options. Content service event producers and consumers use these messages.

## Risks
Manual edits are overwritten. `Size` is int64 in proto but not exposed by generated fieldpath helper, so filterability is limited unless generator behavior changes.

## Test Signals
`make protos`, `go -C api test ./...`, Buf breaking checks, and content event serialization tests validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/content.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/content.proto -->
# sources/cloud-native/containerd/api/events/content.proto

## Purpose
This proto defines content store event payloads for create and delete operations.

## Important APIs, Types, And Functions
Package is `containerd.events`; Go package is `github.com/containerd/containerd/api/events;events`. It imports `types/fieldpath.proto`, enables `fieldpath_all`, and defines `ContentCreate` (`digest`, `size`) and `ContentDelete` (`digest`).

## Control Flow
There is no runtime control flow. Buf/protoc generation creates Go protobuf and fieldpath files.

## State And Persistence
The schema is persistent API state for serialized content events.

## Dependencies And Integration Points
It integrates with containerd content service events, generated code, fieldpath filtering, and Buf breaking-change checks.

## Risks
Field number changes are API-breaking. `digest` is a string rather than a strongly typed digest, so validation belongs to event producers/consumers.

## Test Signals
Buf breaking checks, generated-code freshness, content event publish/consume tests, and fieldpath filtering on digest validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/content.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/content_fieldpath.pb.go -->
# sources/cloud-native/containerd/api/events/content_fieldpath.pb.go

## Purpose
This generated file implements fieldpath lookup helpers for content event messages.

## Important APIs, Types, And Functions
It defines `Field([]string) (string, bool)` for `ContentCreate` and `ContentDelete`.

## Control Flow
Each method rejects empty paths and switches on the first field segment. Both messages expose `digest` when non-empty. `ContentCreate.size` is commented as unhandled by the generator.

## State And Persistence
No persistent state exists.

## Dependencies And Integration Points
It integrates with event filtering code that matches content events by digest.

## Risks
`size` cannot be used as a fieldpath filter through this generated helper. Empty digest returns false, which is appropriate for normal content events but should be known for tests.

## Test Signals
Fieldpath tests should cover digest matches, empty digest, invalid paths, empty path, and the known lack of `size` support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/content_fieldpath.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/doc.go -->
# sources/cloud-native/containerd/api/events/doc.go

## Purpose
This file documents and declares the `events` Go package for containerd protobuf event types.

## Important APIs, Types, And Functions
It contains the package comment and `package events` declaration.

## Control Flow
There is no executable control flow.

## State And Persistence
No runtime state exists.

## Dependencies And Integration Points
It provides Go package documentation for generated event proto files under `api/events`.

## Risks
Low risk; package name changes would break generated code and imports.

## Test Signals
`go -C api test ./...` and documentation rendering validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/doc.go -->
