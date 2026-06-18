# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_regs.h

## Purpose
This header declares the legacy MDP helpers that fill VPU shared processing state from a V4L2 context.

## Important APIs, Types, and Functions
It declares setters for input/output addresses, source/destination sizes, source/destination image formats, rotation/flip, and global alpha.

## Control Flow
The mem2mem worker includes this header and calls all setters before sending a VPU process message.

## State and Persistence
No state is stored here; the declared functions mutate `ctx->vpu.vsi`.

## Dependencies and Integration Points
The declarations depend on `struct mtk_mdp_ctx` and `struct mtk_mdp_addr` from the core header.

## Risks and Edge Cases
The API assumes `ctx->vpu.vsi` has been mapped by VPU init before calls. There is no static protection against calling setters out of order.

## Test Signals
Compile/link coverage plus process tests that inspect populated VPU shared data validate the interface.
