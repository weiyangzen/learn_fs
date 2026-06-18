# sources/distributed-fs/ceph-client/arch/arm/probes/decode-thumb.c

Purpose: Provides Thumb-2 and Thumb-16 instruction decode tables and decode entry points for ARM probe support in Thumb kernels.

Important APIs/functions: Exports `probes_decode_thumb32_table` and `probes_decode_thumb16_table` for tests, and implements `thumb16_probes_decode_insn()` and `thumb32_probes_decode_insn()`. Internal single-step functions advance PC by 2 or 4, invoke the selected handler, and call `it_advance()` to update IT block state. `thumb_check_cc()` uses ITSTATE-derived condition codes when inside an IT block.

Control flow: Thumb-32 tables classify load/store multiple, dual/exclusive/table branch, shifted-register data processing, modified/plain immediates, branch/control, memory hints, single load/store, register data processing, multiply/long multiply, and reject unsupported coprocessor/SIMD/state-changing classes. Thumb-16 tables classify ALU, high-register, literal load, load/store, ADR/SP-relative, miscellaneous, push/pop, IT/hints, LDM/STM, conditional and unconditional branches. Like the ARM decoder, table order and masks are intentionally structured from narrower exclusions to broader matches.

State and dependencies: No persistent mutable state. Depends on `decode.h`, `decode-thumb.h`, generic decode/action/checker infrastructure, `probes_condition_checks`, and CPSR ITSTATE helpers/macros.

Integration points: Used by kprobes on `CONFIG_THUMB2_KERNEL` builds. The decoded action IDs map to Thumb-specific action and checker arrays. The `emulate` flag and checker array determine whether a matched instruction is accepted, emulated, simulated, or rejected.

Risks/tests: IT block condition handling is central; missing `it_advance()` or wrong `current_cond()` behavior would misexecute probed conditional instructions. Table rejection rules protect against PC/SP misuse and processor-state changes; broadening them is risky. Tests should exercise Thumb16/Thumb32 decode coverage, IT blocks, 16-vs-32 PC advancement, branch/interworking actions, register constraints, and unsupported coprocessor/SIMD/exclusive instruction rejection.
