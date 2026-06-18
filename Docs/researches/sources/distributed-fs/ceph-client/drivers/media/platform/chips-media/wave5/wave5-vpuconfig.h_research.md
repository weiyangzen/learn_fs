# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuconfig.h

## Purpose
Defines Wave5 product codes, supported product macro, instance limits, default/min/max dimensions, timeouts, command queue depth, common memory sizes, work-buffer sizes, remap sizes, and AXI IDs.

## Important APIs, Types, and Functions
Key macros include `PRODUCT_CODE_W_SERIES()`, product codes such as `WAVE521C_CODE`, `MAX_NUM_INSTANCE`, encoder/decoder picture dimension limits, `VPU_ENC_TIMEOUT`, `VPU_DEC_TIMEOUT`, `WAVE521_COMMAND_QUEUE_DEPTH`, and common memory size formulas.

## Control Flow
No runtime control flow. The values constrain validation and allocation in platform/API/frontend code.

## State and Persistence
No state. These constants influence memory allocation sizes, firmware timeout behavior, and V4L2 frame-size negotiation.

## Dependencies and Integration Points
Included by `wave5-vpu.h`, `wave5-vpuapi.h`, platform code, and frontend format handling. Hardware backend code depends on product and memory constants.

## Risks
Incorrect size constants can cause firmware memory corruption or under-allocation. Dimension and step constants directly affect userspace-advertised capabilities. The `PRODUCT_CODE_W_SERIES()` statement expression is GCC-specific, which is acceptable in kernel code.

## Test Signals
Compile on supported configs, validate advertised frame sizes with `v4l2-compliance`, stress max resolution encode/decode allocations, and run firmware initialization on each product code variant.
