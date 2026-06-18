# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-hi3798cv200.c

Purpose: provides HiSilicon Hi3798CV200-specific DesignWare MMC extensions for timing mode register programming, sample/drive clock handling, and phase-based tuning.

Important APIs and functions: `dw_mci_hi3798cv200_init` acquires/enables `ciu-sample` and `ciu-drive` clocks. `dw_mci_hi3798cv200_set_ios` sets DDR/phase/HS400 bits and drive clock phase. `dw_mci_hi3798cv200_execute_tuning` scans eight sample phases and chooses the middle of the valid window. Probe/remove wrap `dw_mci_pltfm_register` and shared removal.

Control flow: probe registers the shared DW host with `hi3798cv200_data`. Init allocates private clock state and enables clocks. During `set_ios`, the hook toggles `UHS_REG`, `ENABLE_SHIFT`, and `DDR_REG` based on MMC timing, then chooses drive phase 180 degrees for legacy/HS or 135 degrees for HS200. Tuning iterates 0..315 degrees in 45-degree steps, clears interrupts, sends tuning commands, records rising/falling edges, and sets the selected sample phase.

State and persistence: `struct hi3798cv200_priv` stores sample and drive clock handles. Clock phase and mode bits persist while the controller is powered; remove disables the extra clocks before shared removal.

Dependencies and integration points: depends on common DW MMC platform glue, Linux clock APIs, MMC tuning, OF platform matching, and shared register macros. It declares `MMC_CAP_CMD23` through common caps.

Risks: tuning has only eight phase points, so marginal boards may need finer control. Clock phase changes ignore return values in `set_ios` and tuning. Remove assumes `host->priv` and clocks are valid after successful probe. There is no explicit PM ops table in this driver despite including PM headers.

Test signals: Hi3798CV200 DT probe, clock acquisition failures, HS/HS200/HS400 mode transitions, tuning success/failure logs, phase register inspection, and shared DW read/write stress.
