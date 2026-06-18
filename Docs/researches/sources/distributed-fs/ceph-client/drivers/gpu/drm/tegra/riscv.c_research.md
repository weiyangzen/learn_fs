# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/riscv.c

Purpose: provides shared helpers for Tegra DRM engines that boot firmware through a RISC-V bootrom, currently used by Tegra234 NVDEC.

Important APIs/functions: `tegra_drm_riscv_read_descriptors()` reads bootloader and OS manifest/code/data offsets from device-tree properties into `tegra_drm_riscv_descriptor` structs and rejects an all-zero descriptor set. `tegra_drm_riscv_boot_bootrom()` selects the RISC-V core, programs shifted physical addresses for manifest, code, and data, programs secure DMA config with GSC ID, locks DMA config, starts the CPU, and polls bootrom return code for PASS.

Control flow and state: callers initialize `dev` and `regs`; descriptors persist in `struct tegra_drm_riscv`. Boot is stateless per descriptor except for hardware registers. NVDEC sequences bootloader then resets and boots OS.

Dependencies/integration: depends on OF property reading, MMIO writes, `readl_poll_timeout()`, and consumers that provide carveout physical base addresses.

Risks: descriptor `code_size` and `data_size` fields exist but are not populated by the current reader. Address programming shifts physical addresses by 8, so alignment and carveout base correctness are critical. Poll timeout reports raw return code.

Test signals: DT property validation, bad/all-zero descriptor rejection, bootrom timeout/error paths, and Tegra234 NVDEC runtime resume.
