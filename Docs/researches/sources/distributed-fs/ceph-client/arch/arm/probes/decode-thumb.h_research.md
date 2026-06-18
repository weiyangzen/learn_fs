# sources/distributed-fs/ceph-client/arch/arm/probes/decode-thumb.h

Purpose: Declares Thumb probe decode action IDs, IT block helper macros, decode tables, and Thumb16/Thumb32 decode entry points.

Important APIs/macros/types: `in_it_block(cpsr)` checks CPSR ITSTATE bits, and `current_cond(cpsr)` extracts the current IT condition. `enum probes_t32_action` and `enum probes_t16_action` enumerate action IDs used by Thumb action/checker arrays. Extern decode tables are `probes_decode_thumb32_table` and `probes_decode_thumb16_table`; decode functions are `thumb16_probes_decode_insn()` and `thumb32_probes_decode_insn()`.

Control flow/state: The enums drive table action IDs and must stay synchronized with action/checker arrays. IT macros are pure bit operations on CPSR and contain no state.

Dependencies/integration: Includes `decode.h` and is consumed by `decode-thumb.c` plus Thumb kprobes actions/checkers/tests.

Risks/tests: ITSTATE bit masks are architecture-specific and must match ARM CPSR encoding. Enum changes require coordinated updates. Tests should compile Thumb-2 kprobes and run decode/action coverage for IT blocks and every Thumb action class.
