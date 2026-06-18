<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.h -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.h

### Purpose
This header exposes the FHCTL variant enum, register-offset layout, and operation accessors for MediaTek PLL frequency hopping support.

### Important APIs, Types, And Functions
It defines `enum fhctl_variant` with `FHCTL_PLLFH_V1` and `FHCTL_PLLFH_V2`, `struct fhctl_offset`, and declarations for `fhctl_get_offset_table()`, `fhctl_get_ops()`, and `fhctl_hw_init()`.

### Control Flow, State, And Persistence
The header has no runtime flow. It provides the data contract used by PLLFH registration code to map logical FH registers to per-variant offsets and to initialize hardware through `struct mtk_fh`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-pllfh.h` for FH types. Risks are ABI drift with FHCTL implementation or missing fields for future register variants. Test signals are compile coverage under `CONFIG_COMMON_CLK_MEDIATEK_FHCTL` and successful variant table lookup on FH-enabled SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.h -->
