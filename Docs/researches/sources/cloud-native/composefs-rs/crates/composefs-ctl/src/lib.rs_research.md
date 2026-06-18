# sources/cloud-native/composefs-rs/crates/composefs-ctl/src/lib.rs

## Purpose
This is the main library for `cfsctl`. It re-exports composefs crates for downstream convenience, defines the primary CLI, resolves repository configuration, dispatches commands, integrates OCI/HTTP/varlink features, and provides helpers for reading filesystems, computing image IDs, committing images, mounting, garbage collection, boot preparation, and integrity checks.

## Important APIs, types, and functions
Public surface includes re-exports of `composefs`, `composefs_boot`, and optional `composefs_http`/`composefs_oci`; modules `composefs_info`, `mkcomposefs`, and `varlink`; `App`; `HashType`; `ErofsVersion`; `run_from_iter`; `run_if_socket_activated`; `run_app`; `open_repo`; and `default_repo_path`.

`App` defines global repository flags (`--repo`, `--user`, `--system`), hash and EROFS format overrides, verity behavior, upgrade controls, `--no-repo`, and all subcommands. `Command` includes repository lifecycle, image creation, compute/dump, mount, GC, fsck, varlink, compatibility tool forwarding, and optional HTTP/OCI commands. `OciCommand` covers layer import, image pull/list/inspect/tag/untag, mount, compute-id, prepare-boot, fsck, and varlink.

Core helpers include `resolve_repo_path`, `resolve_hash_type`, `run_init`, `open_repo_at`, `load_filesystem_from_ondisk_fs`, `dump_file_impl`, `run_cmd_without_repo`, and `run_cmd_with_repo`. Feature-gated helpers include `IndicatifReporter`, `OciReference`, `resolve_oci_image`, `resolve_oci_config`, and `load_filesystem_from_oci_image`.

## Control flow
`run_app` first handles hidden compatibility tool dispatch, then `init`, then varlink service modes, then no-repository compute/dump paths. For repository-backed commands it resolves the repo path, determines the effective hash algorithm from `meta.json` or old-format inference, opens the correctly typed repository, and dispatches into `run_cmd_with_repo`.

`run_cmd_without_repo` supports compute-id and create-dumpfile by reading an on-disk root and optionally applying boot transforms from a directory fd. `run_cmd_with_repo` wraps the repository in `Arc` and handles each command. OCI commands resolve refs or digests, call composefs-oci APIs, optionally generate boot images, and for `PrepareBoot` transform the rootfs, commit it, write boot resources, and create deployment state directories.

## State and persistence behavior
This file orchestrates persistent repository state. `run_init` creates or updates repo metadata, optionally resetting old metadata and recording default EROFS format. Image creation reads source files into repository objects and commits image refs. GC deletes unreachable objects unless dry-run. Mount commands affect the system mount namespace. Fsck reads and validates repository state. OCI commands create streams, images, refs, tags, and boot image links. `PrepareBoot` also writes boot partition files and creates `state/deploy/<image-id>/var`, `etc/upper`, and `etc/work`.

## Dependencies and integration points
It integrates almost every crate in the workspace: composefs repository, EROFS, filesystem reading, mount, fs-verity, boot transforms, OCI, HTTP, varlink, and progress reporting. It uses `clap` for CLI shape, `tokio` for async operations, `rustix` for fd and mount-related operations, `serde_json` for JSON output, `comfy-table` for image listing, and `indicatif` for progress bars.

## Risks
Dispatch complexity is high and feature-gated paths can diverge. Hash selection must happen before generic repository opening; mistakes can read a repo with the wrong `ObjectID`. No-repo compute-id defaults to SHA-512 when repo metadata cannot be resolved, which may surprise users. `Transaction` parks forever and relies on process lifetime. `PrepareBoot` writes boot state after choosing only the first boot entry. CLI behavior differs by enabled features, effective uid, systemd socket activation environment, and repository metadata age.

## Test signals
Local tests cover `IndicatifReporter` lifecycle behavior when OCI or HTTP features are enabled. Most command behavior is not tested here directly. Strong signals should come from integration tests for repo path/hash resolution, init idempotency, no-repo compute/dump, compatibility subcommand forwarding, varlink activation, bootable transforms, OCI ref resolution, prepare-boot side effects, mount option construction, GC, and fsck JSON/text behavior.
