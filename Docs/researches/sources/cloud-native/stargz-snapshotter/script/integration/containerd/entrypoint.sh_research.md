# sources/cloud-native/stargz-snapshotter/script/integration/containerd/entrypoint.sh

Purpose: Large end-to-end integration entrypoint covering registry auth, optimized image formats, lazy pulls, IPFS, mirror fallback, filesystem equivalence, external TOC, and graceful restart.
Important APIs/types/functions: helpers `retry`, `kill_all`, `wait_all`, `reboot_containerd`, `optimize`, `convert`, `copy`, `copy_out_dir`, `dump_dir`, `run_and_check_remote_snapshots`, and `check_cache_empty`.
Control flow: sets up cgroups, logs into TLS registry, boots containerd/snapshotter, verifies plugin health, prepares original/eStargz/zstd/external-TOC images, optionally tests IPFS pulls, verifies mirror/refresh behavior with iptables blocks, compares root filesystems from overlayfs and stargz for multiple formats, tests namespace pulls, missing-config startup, and graceful SIGINT/SIGTERM restarts.
State and persistence: creates many temporary rootfs directories, registry images, IPFS repo, daemon state, logs, iptables rules, and content-store/snapshotter data; cleanup removes temp dirs/logs.
Dependencies and integration points: depends on containerd, ctr-remote, stargzify, IPFS, authenticated registries, `utils.sh`, FUSE, iptables, jq/tar/diff, and optional builtin snapshotter config.
Risks: very environment-sensitive; failed iptables cleanup can affect later steps; several tests depend on exact log messages and registry hostnames. It is intentionally broad and should run in disposable privileged containers.
Test signals: primary integration signal for lazy-pull correctness across formats and operational restart behavior.
