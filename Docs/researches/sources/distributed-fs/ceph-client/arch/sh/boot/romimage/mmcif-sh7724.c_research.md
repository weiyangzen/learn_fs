# sources/distributed-fs/ceph-client/arch/sh/boot/romimage/mmcif-sh7724.c



Source read size: 78 lines, 2086 bytes.



Purpose: SH7724-specific MMCIF boot loader used by ROM images to fetch the zImage payload from an MMC card.

Important APIs/types/functions: `mmcif_loader()`, `mmcif_update_progress()`, `sh_mmcif_boot_init()`, `sh_mmcif_boot_do_read()`, register constants for MSTPCR2, pin control, Hi-Z, drive strength, and `MMCIF_BASE`.

Control flow: reports progress, enables the MMCIF clock, configures D0-D7/CLK/CMD pinmux and drive state, initializes the MMCIF block, reads blocks starting at sector 512 into the caller-provided buffer, disables the clock, and reports completion.

State and persistence: mutates SoC clock, pinmux, drive-strength, and MMCIF controller registers during the boot phase only.

Dependencies and integration points: depends on SH7724 `mach/romimage.h`, platform MMCIF boot helpers, raw MMIO accessors, and the ROM image layout documented by the `dd ... seek=512` comment.

Risks and test signals: hard-coded sector 512, pinmux values, and clock register bits must match the boot medium and board wiring. Test with an MMC image at the documented offset, progress hooks, and failed-card timeout scenarios.
