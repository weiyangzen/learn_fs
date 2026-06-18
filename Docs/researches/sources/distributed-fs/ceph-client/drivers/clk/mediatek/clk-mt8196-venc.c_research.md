# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-venc.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-venc.c

### Purpose
`clk-mt8196-venc.c` registers MT8196 video encoder clocks for three encoder domains: main VENC, VENC C1, and VENC C2. It gates LARB, VENC, JPEG encode/decode, GALS, ADAB/XPC controls, GALS SRAM, and RES_FLAT clocks.

### Important APIs, Types, And Functions
The file defines direct and HWV gate macros for VEN1, VEN2, and VEN_C2 banks. Descriptors `ven1_mcd`, `ven2_mcd`, and `ven_c2_mcd` set `.need_runtime_pm = true`. Some gates use direct inverted set/clear operations; most core gates use HWV inverted operations. `ven1_venc_xpc_ctrl` is marked `CLK_IGNORE_UNUSED`.

### Control Flow, State, And Persistence
OF matching selects one descriptor and the simple helper registers a runtime-PM-aware provider. Gate state is controlled through VENC CG registers and HWV done/set/clear registers. The driver contains no custom sequencing beyond table selection.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `venc`, encoder/JPEG drivers, runtime PM, and MT8196 OF bindings. Risks include mixed direct/HWV semantics, inverted set/clear mistakes, unused XPC control handling, and multi-core descriptor mismatches. Test signals include VENC and JPEG encode/decode on all domains, runtime PM cycles, HWV completion, GALS clock behavior, and unbind cleanup.
