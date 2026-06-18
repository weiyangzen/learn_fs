# sources/control-plane/mayastor/io-engine/tests/ftl_mount_fs.rs

Purpose: feature-gated NVMe PCI FTL filesystem tests. It creates an FTL bdev from base/cache NVMe devices, exports it through a nexus over NVMf, and verifies repeated mount/unmount and fio data verification.

Important APIs/types/functions: `create_connected_nvmf_nexus` creates the FTL-backed nexus, claims `ftl0` with `UntypedBdevHandle`, shares by `Protocol::Nvmf`, connects using `libnvme_rs::NvmeTarget`, and returns the block device path. `csal_fio_run_verify` runs fio with crc32 verify. `create_nexus` builds an `ftl:///ftl0?bbdev=...&cbdev=...` URI.

Control flow: `ftl_mount_fs_multiple` connects and mount/unmounts ten times, then disconnects/unshares/destroys. `ftl_mount_fs_fio` runs fio verification before cleanup. The whole file is behind `#[cfg(feature = "nvme-pci-tests")]`.

State and persistence: uses real PCI devices by default (`pcie:///0000:82:00.0` and `pcie:///0000:83:00.0`) with required LBA formats. Commented AIO fallback notes FTL minimum capacity and metadata constraints. Runtime state is FTL and NVMf target state.

Dependencies and integration points: FTL bdev URI handling, SPDK NVMe PCI devices, NVMf target/initiator, libnvme-rs, filesystem mount helpers, fio, and Mayastor compose harness.

Risks and edge cases: hardware-specific and feature-gated. Requires exact NVMe formatting and large capacity. Claiming/dropping `UntypedBdevHandle` around share is sensitive to bdev ownership.

Test signals: provides high-value end-to-end signal for FTL over NVMf with filesystem/fio workloads when the hardware feature is available.
