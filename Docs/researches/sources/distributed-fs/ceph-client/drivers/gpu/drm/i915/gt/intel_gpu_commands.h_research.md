# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gpu_commands.h

## Purpose
This header centralizes i915 command-stream opcode and bit-field definitions used by kernel command emitters, the command parser, BLT helpers, pipe-control/cache flush code, media/GSC command paths, and address canonicalization helpers.

## Important APIs, Types, and Functions
The file defines instruction client fields (`INSTR_MI_CLIENT`, `INSTR_BC_CLIENT`, `INSTR_RC_CLIENT`, `INSTR_GSC_CLIENT`) and construction macros such as `MI_INSTR()`, `GFX_INSTR()`, `MEDIA_INSTR()`, and `GSC_INSTR()`. MI commands include no-op, interrupts, waits, flushes, arbitration control, context setup, semaphores, immediate/register stores, atomics, `MI_LOAD_REGISTER_IMM`, `MI_UPDATE_GTT`, register-memory commands, batch-buffer start, and math instructions.

3D and BLT definitions include pipe-control flags, render/cache invalidation bits, 3D state opcodes, color/source copy BLT commands, fast-copy tiling/MOCS fields, control-surface copy constants, and display flip encodings. GSC definitions include `GSC_FW_LOAD`, HECI limit flags, and `GSC_HECI_CMD_PKT`. Inline helpers are `gen8_canonical_addr()`, `gen8_noncanonical_addr()`, and `__gen6_emit_bb_start()`.

## Control Flow
The header has no runtime control flow except simple inline helpers. It is used by engine emit functions to compose command buffers and by parser code to recognize and validate command lengths, clients, and fields.

## State and Persistence Behavior
It stores no mutable state. Its macros encode the binary command ABI consumed by GPU command streamers across generations; those values persist as hardware contracts.

## Dependencies and Integration Points
Consumers include execlists request allocation (`MI_UPDATE_GTT`, arbitration control), engine emit helpers, command parser tables, BLT/copy paths, display flip paths, pipe-control/cache flush code, PXP/GSC HECI command submission, and GGTT binding through GPU commands.

## Risks
Opcode or bit-field mistakes can generate invalid command streams, hang the GPU, bypass command-parser restrictions, or perform cache/TLB operations incorrectly. Some bits have generation-specific meanings, such as GGTT/PPGTT addressing and GSC client aliasing with BLT client encoding. Pipe-control flags are restricted by engine/platform capabilities and must not be blindly reused on CCS or non-3D engines.

## Test Signals
Build coverage across i915, command-parser selftests, GPU hang-free batch submission, BLT copy and CCS control-surface tests, cache/TLB flush correctness, display flip tests, PXP/GSC HECI command operation, and validation of canonical address handling are useful signals.
