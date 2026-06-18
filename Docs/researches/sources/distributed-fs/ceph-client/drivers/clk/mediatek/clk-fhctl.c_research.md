<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.c

### Purpose
`clk-fhctl.c` implements Frequency Hopping Controller operations for MediaTek PLLFH clocks. It supports spread-spectrum clocking and DDS hopping flows that temporarily hand PLL control to FHCTL hardware.

### Important APIs, Types, And Functions
Public APIs are `fhctl_get_offset_table()`, `fhctl_get_ops()`, and `fhctl_hw_init()`. Important internals include `struct fhctl_offset` tables for V1/V2 register layouts, `fhctl_set_ssc_regs()`, `hopping_hw_flow()`, `fhctl_hopping()`, `fhctl_ssc_enable()`, `__get_postdiv()`, and `__set_postdiv()`.

### Control Flow, State, And Persistence
`fhctl_get_offset_table()` selects register offsets by variant. `fhctl_hopping()` optionally raises postdiv before entering a spinlocked hardware flow, writes current DDS into FHCTL, enables soft-start and hopping control, triggers DVFS DDS, polls monitor DDS for stability, copies the observed DDS back to PLL PCW, and releases FHCTL control. SSC enable programs df/dt/up-down limits and stores `state->ssc_rate`, disabling and restoring SSC around hopping when needed.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-pllfh.h`, `clk-fhctl.h`, `clk-mtk.h`, MMIO, `readl_poll_timeout_atomic()`, PLL postdiv encoding, and caller-provided spinlocks. Risks include timeout during DDS convergence, incorrect offset variant, SSC percentage math errors, postdiv ordering glitches, and lock misuse around MMIO polling. Test signals include successful PLL rate changes, SSC enable/disable persistence, timeout diagnostics from `dump_hw()`, and boot on platforms using `CONFIG_COMMON_CLK_MEDIATEK_FHCTL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.c -->
