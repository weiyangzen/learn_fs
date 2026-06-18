# sources/control-plane/mayastor/test/python/v1/pool/docker-compose.yml

Purpose: single-node v1 pool test environment with LVM support enabled.

Important configuration: `ms0` runs io-engine on `10.1.0.2` with cores `1,2`. Environment includes ANA/reservation settings, `PATH=${LLVM_SYMBOLIZER_DIR:-}:${LVM_BINS:-}`, ASAN leak suppression, and `ENABLE_LVM=true`. The service mounts repo, `/nix`, hugepages, `/tmp`, and `/var/tmp`, and exposes loop devices `/dev/loop0` through `/dev/loop7`.

State and integration: v1 pool tests create aio images and LVM volume groups using loop devices. The extra PATH and devices allow `pvcreate`, `vgcreate`, and related LVM commands invoked through `nix-sudo`.

Risks and test signals: LVM tests depend on host loop device availability and cleanup. Missing device mappings or LVM binaries cause setup failures. Compose correctness is indirectly validated by pool creation, import/export, LVM feature reporting, and list pool assertions.
