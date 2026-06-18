# sources/distributed-fs/ceph-client/drivers/ata/pata_imx.c

`pata_imx.c` is the platform driver for the Freescale i.MX PATA block, matching `fsl,imx27-pata`. It is PIO-only and uses 32-bit SFF data transfers. The driver programs timing registers from the enabled peripheral clock, deasserts controller resets, enables ATA interrupts, and preserves control state across suspend/resume.

`struct pata_imx_priv` stores the enabled `clk`, mapped host registers, and saved `ata_ctl`. `pata_imx_set_timing()` computes PIO timing with `ata_timing_compute()` and writes i.MX timing registers including setup, active, and mode-specific constants. `pata_imx_set_piomode()` updates timings and toggles `PATA_IMX_ATA_CTRL_IORDY_EN`. `pata_imx_setup_port()` maps standard ATA taskfile registers into the controller's shifted register layout.

Probe gets the IRQ, allocates state, enables the clock, allocates a one-port host, maps resource 0, assigns command/control windows, fills taskfile addresses, deasserts FIFO and ATA reset bits, enables `ATA_INTRQ2`, and activates with `ata_sff_interrupt()`. Remove detaches the host and disables interrupts. Suspend disables interrupts, saves control, and disables the clock; resume reenables the clock, restores control, reenables interrupts, and resumes libata.

Dependencies are platform/OF probing, common clock framework, MMIO, and libata SFF helpers. Runtime state is the register base, clock, and saved control word. Risks include invalid clock rates, shifted address mistakes, and lost interrupt/control state after PM. Tests should cover PIO0-4, IORDY transitions, missing IRQ or clock failures, probe/remove, interrupt delivery, and suspend/resume with an attached device.
