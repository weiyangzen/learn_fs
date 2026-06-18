
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-7.c

## Purpose
Implements VFE 4.7 gen1 ops for later dual-VFE platforms. It extends the gen1 model with revised register offsets, per-instance UB sizes, realign buffer support for packed YUV, data-shaper/QoS programming, and updated scaling/cropping formulas.

## Important APIs, Types, and Functions
Exports `vfe_ops_4_7` and `vfe_ops_gen1_4_7`. Important helpers mirror VFE 4.1: reset/halt, WM enable/frame/line setup, word-per-line calculations, UB config, bus xbar/RDI connection, realign config, RDI CID, reg update, IRQ enables, demux/scale/crop/clamp, QoS/DS, CAMIF config/cmd/wait, ISR read, and violation read.

## Control Flow
The gen1 core invokes this vtable during stream enable/disable. RDI streaming programs MIPI enable, RDI stream select, xbar, WM dimensions and addresses, IRQs, and reg updates. PIX streaming configures demux, scale, crop, clamp, realign when needed, module enables, CAMIF frame/window/subsample registers, composite masks, and CAMIF start/stop. Interrupt flow is status read/clear, reset/violation/halt handling, reg-update and SOF callbacks, composite done with PIX WM suppression, then WM done.

## State and Persistence
All state is common VFE in-memory state and volatile registers. UB size depends on VFE instance id: VFE0 and VFE1 have different RDI partition sizes.

## Dependencies and Integration Points
Depends on gen1 helper code, V4L2 pixel formats, CAMSS PM and media plumbing, and buffer queue helpers. It is selected by SoC resource tables for VFE 4.7 hardware.

## Risks and Test Signals
Register formulas differ subtly from 4.1, especially word-per-line and scaler phase. Realign only applies to packed YUV and must match xbar swap bits. Test both VFE instances, NV12/NV16 and packed YUYV variants, RDI0-2, CAMIF stop, composite and WM IRQs, bus overflows, QoS/DS writes, and no stale `reg_update` bits.
