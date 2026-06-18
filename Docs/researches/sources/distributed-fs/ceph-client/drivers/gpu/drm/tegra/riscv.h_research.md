# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/riscv.h

Purpose: declares RISC-V firmware descriptor and boot helper state for Tegra DRM engines.

Important APIs/types: `struct tegra_drm_riscv_descriptor` stores manifest, code, and data offsets plus size fields. `struct tegra_drm_riscv` stores caller-provided device/MMIO pointers and bootloader/OS descriptors. Public functions read descriptors from DT and execute a descriptor through the bootrom.

Control flow and state: descriptors are read during probe and reused during runtime resume boot sequences.

Dependencies/integration: consumed by `nvdec.c` for Tegra234. Requires device tree properties matching the reader in `riscv.c`.

Risks: size fields are part of the ABI but currently unused/unfilled by the helper implementation, which can mislead future callers.

Test signals: compile coverage, DT descriptor parsing tests, and RISC-V boot smoke tests through NVDEC.
