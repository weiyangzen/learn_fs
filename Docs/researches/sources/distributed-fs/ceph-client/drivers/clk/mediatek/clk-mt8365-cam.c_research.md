# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-cam.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-cam.c

### Purpose
`clk-mt8365-cam.c` registers MT8365 image/camera system gates for LARB2, camera core, CAMTG, SENIF, CAMSV0/1, FDVT, and WPE.

### Important APIs, Types, And Functions
The file defines `cam_cg_regs`, `GATE_CAM`, `cam_clks`, `cam_desc`, and an OF match table for `mediatek,mt8365-imgsys`. All gates use `mtk_clk_gate_ops_setclr`; probe/remove are delegated to `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

### Control Flow, State, And Persistence
OF matching supplies `cam_desc` to the common helper, which registers the gate clocks and provider. Clock state lives in set/clear/status registers at 0x4/0x8/0x0. No persistent state is maintained.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `mm_sel`, camera sensor and image processing drivers, and MT8365 DT bindings. Risks include camera pipeline failures if LARB or SENIF gates are wrong, parent-rate mismatches for CAMTG, and incomplete coverage of WPE/FDVT use. Test signals include camera capture, CAMSV paths, FDVT/WPE activity, SMI/LARB access, and clock debugfs.
