# sources/control-plane/mayastor/test/python/v1/replica/docker-compose.yml

Purpose: v1 replica test environment with elevated LVM/udev access. It launches one `ms0` service.

Important configuration: environment enables LVM, debug logging, ANA/reservations, ASAN leak suppression, and LVM-aware PATH. Command runs io-engine on core `1` with `--reactor-freeze-detection`. It mounts repo, `/nix`, hugepages, `/tmp`, `/var/tmp`, `/dev`, and `/run/udev`, runs privileged with host IPC, and maps loop devices `/dev/loop0` through `/dev/loop2`.

State and integration: tests create LVS and LVM pools, loop-backed VGs, and replicas. The `/dev` and udev mounts plus privileged mode support LVM discovery and cleanup.

Risks and test signals: privileged host device access increases environmental coupling and cleanup risk. Missing loop devices or LVM tools will fail setup. Downstream replica tests validate creation, destruction, list filtering, pooltype metadata, and reactor stability.
