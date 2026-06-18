
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-8.c

## Purpose
Implements VFE 4.8 gen1 ops for SDM845-class CAMSS. It is close to VFE 4.7 but uses another register map, equal UB size across instances, a WM command register for enable/disable, and specific QoS/data-shaper programming.

## Important APIs, Types, and Functions
Exports `vfe_ops_4_8` and `vfe_ops_gen1_4_8`. Key functions cover reset/halt, WM frame/line programming, bus reload, address programming, ping-pong status, RDI xbar, realign, RDI CID, register update, IRQ masks, demux/scale/crop/clamp, CAMIF, QoS/DS, ISR read, and violation read.

## Control Flow
Generic gen1 code calls the vtable. Start paths program bus write interface, WMs, UB, xbar/RDI or PIX pipeline modules, then issue register updates and CAMIF commands. `vfe_wm_enable()` writes enable/disable commands through `VFE_0_BUS_IMAGE_MASTER_CMD` and barriers before later commands. ISR dispatch matches 4.7: reset, violation, halt, per-line reg update, CAMIF/RDI SOF, composite done, and WM ping-pong done.

## State and Persistence
Uses generic `vfe_device` state and volatile VFE registers. `vfe_get_ub_size()` returns a common RDI UB partition regardless of VFE id.

## Dependencies and Integration Points
Integrates with gen1 helpers and V4L2 formats, CAMSS PM domains, buffer queues, and SoC resource tables selecting `vfe_ops_4_8`.

## Risks and Test Signals
WM enable semantics changed from bit set/clear to command values, so ordering barriers are important. Scale formulas use minus-one dimensions and can underflow on invalid zero dimensions if upstream validation fails. Test WM command ordering, RDI and PIX streams, realign for packed YUV, UB partitioning, QoS/DS values, CAMIF halt, and interrupt completion ordering.
