# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-x86.c

## Purpose
Implements x86 perf annotate support. It supplies a sorted mnemonic table, CPU-family dependent macro-fusion detection, cpuid parsing, x86 objdump syntax configuration, and libdw-backed type-state tracking for register, stack, global, per-CPU, and call-return data types.

## Important APIs, Types, and Functions
`arch__new_x86()` allocates and configures the `x86` descriptor, validates sorted instructions in debug builds, sets objdump chars (`%`, `(`, `$`, `#`), sets AT&T suffix stripping (`bwlq`), and installs `update_insn_state_x86()` with libdw.
`x86__instructions[]` maps many x86 mnemonics to generic `mov_ops`, `jump_ops`, `call_ops`, `ret_ops`, `lock_ops`, `nop_ops`, and `dec_ops`.
`x86__cpuid_parse()` extracts family/model/stepping and selects AMD or Intel fusion logic.
`amd__ins_is_fused()` and `intel__ins_is_fused()` decide when memory access attribution can fall back from a branch to the previous fused instruction.
`update_insn_state_x86()` updates `struct type_state` across calls, adds/subs, `lea`, moves, stack stores, PC-relative/global accesses, per-CPU accesses, stack canary accesses, and pointer-invalidating arithmetic.

## Control Flow
Architecture initialization parses cpuid and configures disassembly conventions. During disassembly, the common parser searches `x86__instructions` and handles suffixes. During data-type annotation, `annotate-data.c` walks basic blocks and calls `update_insn_state_x86()` for each instruction before checking the sampled memory operand. Calls invalidate caller-saved registers except preserved DWARF-lifetime registers and may seed the return register from DWARF function return type. Move and address-generation instructions propagate or derive type information through registers and stack slots.

## State and Persistence
Per-architecture state includes family/model and fusion callback. Per-analysis state is transient `type_state` in `annotate-data.c`. Register entries track kind, type DIE, offset, immediate value, lifetime, and copied-from relation. Stack variables are maintained in a linked list by offset. No persistent disk state is written.

## Dependencies and Integration Points
Depends on DWARF helpers, DSO/map/symbol facilities, `annotate-data.h`, and common disassembly operations. It is central to `hist_entry__get_data_type()` because x86 supports instruction tracking and PC-relative/per-CPU special cases. It also affects common annotate rendering through the instruction table and fusion detection.

## Risks
This is a high-complexity heuristic path. Operand parsing assumes AT&T objdump syntax. Per-CPU and stack-canary rules are kernel/x86-specific. Register invalidation and pointer arithmetic can produce false negatives or stale types if a mnemonic is missing from the invalidation list. Fusion logic depends on family/model thresholds and substring matching.

## Test Signals
Tests should cover annotate output for sorted table lookup, suffixed mnemonics, jumps/calls/returns, Intel and AMD cpuid fusion cases, `%gs` per-CPU accesses, stack canaries, `lea`, immediate moves, register copies, calls with return types, stack stores/loads, and pointer arithmetic invalidation.
