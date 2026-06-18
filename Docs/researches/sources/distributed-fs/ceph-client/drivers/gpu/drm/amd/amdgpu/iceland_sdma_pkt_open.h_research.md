# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_sdma_pkt_open.h

## Purpose
`iceland_sdma_pkt_open.h` is a generated-style packet layout header for Iceland SDMA command streams. It exposes opcode/sub-opcode constants and bitfield packing macros used by SDMA ring emitters to build 32-bit packet DWORDs without open-coded masks and shifts.

## Important APIs, Types, And Macros
The file has no C functions or types. Its API is the macro set: top-level `SDMA_OP_*` values for NOP, COPY, WRITE, INDIRECT, FENCE, TRAP, SEM, POLL_REGMEM, COND_EXE, ATOMIC, CONST_FILL, GEN_PTEPDE, TIMESTAMP, SRBM_WRITE, and PRE_EXE; sub-op values for timestamp, copy, and write; and per-packet macros such as `SDMA_PKT_COPY_LINEAR_HEADER_OP(x)`, `SDMA_PKT_COPY_TILED_DW_5_ARRAY_MODE(x)`, `SDMA_PKT_FENCE_DATA_DATA(x)`, and `SDMA_PKT_POLL_REGMEM_DW5_RETRY_COUNT(x)`. Packet sections cover linear copy, broadcast linear copy, linear sub-window copy, tiled copy, linear-to-tiled broadcast, tiled-to-tiled copy, tiled sub-window copy, structured copy, untiled/tiled/incremental writes, indirect buffers, semaphores, fences, SRBM writes, pre-execute, conditional execute, constant fill, poll reg/mem, timestamp set/get/global get, trap, and NOP.

## Control Flow
There is no runtime control flow. Including code composes packet DWORDs by ORing opcode/sub-opcode macros with field macros, then emits those values into an SDMA command buffer in hardware-defined DWORD order.

## State And Persistence
The header owns no persistent state. Its constants define a stable userspace/kernel command ABI for this SDMA generation; mistakes persist indirectly as malformed command buffers submitted to hardware.

## Dependencies And Integration Points
The header is self-contained except for consumers that understand the SDMA packet ABI. It integrates with amdgpu SDMA ring construction code and with GPU firmware/hardware packet parsers. The include guard is `__ICELAND_SDMA_PKT_OPEN_H_`.

## Risks
The macros do not validate value ranges beyond masking, so oversized inputs silently truncate. Several fields share DWORDs, making incorrect OR composition easy. Packet layout drift against hardware documentation would cause GPU hangs or data corruption. There is also a duplicated `SDMA_PKT_COPY_BROADCAST_LINEAR_SRC_ADDR_LO_src_addr_31_0_shift` macro definition, apparently benign but a signal that generated-header hygiene matters.

## Test Signals
Useful signals are SDMA ring selftests, copy/fill/fence tests, GPUVM memory movement tests, command submission stress, and compile coverage for all consumers. Static checks should watch duplicate macro definitions and verify packet emitted DWORD counts against the packet specification.
