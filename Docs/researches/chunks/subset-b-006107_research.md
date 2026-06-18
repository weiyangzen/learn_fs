# sources/distributed-fs/ceph-client/lib/test_bpf.c lines 1-10902

## Scope

This chunk covers the opening 10,902 lines of `sources/distributed-fs/ceph-client/lib/test_bpf.c`, a Linux kernel module test suite for the classic BPF interpreter and eBPF/JIT execution paths. The covered range includes the file header, constants, `struct bpf_test`, all dynamic instruction-stream fill helpers, and the first large section of the global `tests[]` table.

The chunk ends in the middle of a fragmented-SKB classic BPF load test, so the final per-file report must merge this with the next chunk before treating the `tests[]` table as complete. Harness functions that allocate sk_buffs, compile filters, run tests, handle module parameters, and register the module are outside this line range.

## Purpose

The code defines a regression workload for kernel BPF execution. It supplies both classic BPF socket-filter programs and internal/eBPF programs, then associates each with input packet data, expected return values, stack depth, custom run counts, verifier/checker failure expectations, and optional dynamically generated instruction buffers.

The covered tests stress:

- Classic BPF accumulator/index-register behavior, memory slots, branches, ancillary skb loads, absolute/indirect packet loads, and tcpdump-generated filters.
- eBPF ALU32 and ALU64 operations across immediate and register forms, including wraparound, sign extension, zero extension, signed division/modulo encodings, byte swapping, endian conversion, and sign-extending loads.
- eBPF jump families for 32-bit and 64-bit unsigned/signed comparisons, immediate and register operands, forward and backward jumps, and `ldimm64` instruction-pair offset accounting.
- Memory loads/stores using stack and large externally supplied memory, including byte/halfword/word/doubleword sizes, unaligned offsets, negative offsets, endianness-dependent expectations, and sign-extending load instructions.
- Atomic operations, including `BPF_ADD`, `BPF_AND`, `BPF_OR`, `BPF_XOR`, `BPF_XCHG`, `BPF_CMPXCHG`, fetch side effects, source/destination register aliasing, and stack preservation.
- JIT stress patterns for maximum instruction counts, branch conversion, long relative jumps, staggered jumps, repeated helper-like classic transformations, and architecture-specific immediate/register encoding hazards.
- Fragmented SKB absolute and indirect loads at the end of the chunk.

## Important APIs, Types, and Functions

- `struct bpf_test` is the central descriptor. It carries a description, one of several instruction representations (`struct sock_filter`, `struct bpf_insn`, or an allocated pointer plus length), `aux` flags, inline packet data, up to three subtest expected results, an optional `fill_helper`, an expected error code for intentional failures, fragment data, eBPF stack depth, and optional run-count override.
- `MAX_SUBTESTS`, `MAX_TESTRUNS`, `MAX_DATA`, `MAX_INSNS`, and `MAX_K` size the static test descriptors and test data payloads.
- `FLAG_NO_DATA`, `FLAG_EXPECTED_FAIL`, `FLAG_SKB_FRAG`, `FLAG_VERIFIER_ZEXT`, and `FLAG_LARGE_MEM` annotate how the later harness should prepare input, compile the filter, and interpret success.
- `CLASSIC` and `INTERNAL` distinguish classic `struct sock_filter` programs from internal/eBPF `struct bpf_insn` programs. `TEST_TYPE_MASK` isolates this type information from other `aux` flags.
- `R0` through `R10` are local aliases for eBPF registers, reducing noise in the table.
- `bpf_fill_maxinsns1()` through `bpf_fill_maxinsns13()` generate large programs near or over `BPF_MAXINSNS`. They cover maximum-length classic filters, excessive-length rejection, long jumps, `LDX|MSH`, repeated ancillary loads, eBPF backward jumps, and jump-heavy layouts.
- `__bpf_fill_ja()` and `bpf_fill_ja()` generate repeated classic unconditional jumps with gap patterns that force JIT offset recalculation.
- `bpf_fill_ld_abs_get_processor_id()` builds a max-length classic program alternating packet byte loads and `SKF_AD_CPU` loads.
- `__bpf_fill_stxdw()`, `bpf_fill_stxw()`, and `bpf_fill_stxdw()` generate long eBPF atomic add loops against stack memory and set `stack_depth`.
- `__bpf_ld_imm64()` is a small helper that emits the two-instruction `BPF_LD_IMM64()` sequence and returns its instruction count.
- `__bpf_fill_max_jmp()` and its wrappers generate extremely long eBPF programs with a branch over many ALU instructions. The wrappers cover taken, not-taken, always-taken, and never-taken branches for ALU32 and ALU64 filler paths.
- `__bpf_alu_result()` is the local reference implementation for ALU result calculation. It covers move, bitwise operations, shifts, arithmetic, division, and modulo, and reports false for divide/modulo by zero so generators can skip invalid checks.
- `__bpf_fill_alu_shift()` and `__bpf_fill_alu_shift_same_reg()` generate shift tests across all legal shift amounts for 32-bit and 64-bit left, logical right, and arithmetic right shifts, including source and destination register aliasing.
- `value()`, `__bpf_fill_pattern()`, and the `PATTERN_BLOCK*` constants implement a reusable power-of-two-magnitude operand generator. ALU, jump, and atomic exhaustive-style tests plug emitter callbacks into this generator.
- `__bpf_emit_alu64_imm()`, `__bpf_emit_alu32_imm()`, `__bpf_emit_alu64_reg()`, and `__bpf_emit_alu32_reg()` emit compare-against-reference instruction snippets for pattern-generated ALU tests. Wrappers such as `bpf_fill_alu64_add_imm()` and `bpf_fill_alu32_mod_reg()` bind individual operations.
- `__bpf_fill_alu_imm_regs()` and `__bpf_fill_alu_reg_pairs()` test all destination registers and all destination/source register pairs for ALU operations, mainly to catch JIT register allocation and helper-call ABI bugs.
- `__bpf_emit_atomic64()`, `__bpf_emit_atomic32()`, `__bpf_emit_cmpxchg64()`, and `__bpf_emit_cmpxchg32()` emit reference checks for atomic stack operations. Wrappers bind width and operation combinations.
- `__bpf_fill_atomic_reg_pairs()` exhaustively tests atomic register aliasing across `R0` through `R9`, including fetch behavior and `CMPXCHG` use of `R0`.
- `bpf_fill_ld_imm64_magn()` and `__bpf_fill_ld_imm64_bytes()` stress two-instruction 64-bit immediate loads across magnitude boundaries, byte patterns, sign patterns, and deterministic pseudo-random byte filling.
- `__bpf_match_jmp_cond()` is the local predicate reference for BPF jump operations. The jump emitters use it to decide whether a generated snippet should fall through or skip an exit.
- `__bpf_emit_jmp_imm()`, `__bpf_emit_jmp32_imm()`, `__bpf_emit_jmp_reg()`, and `__bpf_emit_jmp32_reg()` plug jump predicates into the generic pattern generator. Wrappers bind every unsigned, signed, equality, inequality, and bit-test jump flavor.
- `__bpf_fill_staggered_jumps()` and its many wrappers build large forward/backward jump sequences to force native JIT branch-conversion passes, especially on architectures with limited branch displacement.
- The `tests[]` table begins at line 3083 and is the primary integration point between generated/static programs and the later runner.
- `BPF_ATOMIC_OP_TEST1` through `BPF_ATOMIC_OP_TEST4` are local table-generation macros that expand many static atomic stack tests checking result values, `r10` side effects, `r0` side effects, and fetch return values.

## Control Flow

The dynamic fill helpers all share the same basic pattern: allocate an instruction array with `kmalloc_objs()` or `kmalloc_array()`, populate it with classic or eBPF instruction macros, write `self->u.ptr.insns` and `self->u.ptr.len`, optionally adjust `self->stack_depth`, and return either `0` or `-ENOMEM`. Several helpers use `BUG_ON()` to assert their calculated instruction count exactly matches the allocation size.

The maximum-instruction helpers generate large classic/eBPF buffers for later compilation. Some are expected to pass, while `bpf_fill_maxinsns4()` deliberately allocates `BPF_MAXINSNS + 1` instructions and is paired with `FLAG_EXPECTED_FAIL`. Jump-heavy helpers encode both straight-line returns and unreachable or backward paths to catch offset, verifier, and JIT codegen mistakes.

The ALU and jump pattern generators perform a two-pass style calculation. First, emitters are called with `insns == NULL` to report the maximum instruction count per generated case. `__bpf_fill_pattern()` uses that to size the buffer. Then it iterates deterministic operand grids around power-of-two magnitudes and signs, calling the same emitter to append executable checks. Each generated snippet computes an operation, compares the result to a precomputed reference, and exits early with failure if the comparison does not match. A final `R0 = 1; exit` marks success.

The atomic generators use stack slots as the memory target and compare both memory and register side effects. For non-`FETCH` operations, the source register should stay as the update value. For `FETCH` operations, the source register should receive the old memory value. For `CMPXCHG`, `R0` is part of the operation contract, so the code carefully handles aliasing between `R0`, destination pointer register, and source register.

The staggered-jump generator derives `size` from `self->test[0].result - 1`, creates a preamble, jumps into the middle of a sequence, and alternates conditional error exits with jumps whose offsets walk forward and backward through the sequence. Successful execution produces `size + 1`; wrong branch conversion typically jumps to an early exit with a different result.

The `tests[]` table is declarative. Static entries embed either `.u.insns` classic filters or `.u.insns_int` eBPF programs, set `aux` to `CLASSIC` or `INTERNAL` plus flags, provide input data, and list expected `{ data_size, result }` pairs. Generated entries leave the inline instruction union empty and set `.fill_helper` to a function that constructs the real instruction stream at runtime.

In the covered table range, control-flow coverage progresses from classic basics (`TAX`, `TXA`, ALU, packet loads, skb ancillary loads, memory spills, conditional branches, tcpdump filters) into extensive internal/eBPF operation families. Many eBPF tests are self-checking programs: they set `R0` to an error value or exit early on failure and return `1` or another expected sentinel only after all embedded checks pass.

## State and Persistence Behavior

Most state in this chunk is static test metadata in `tests[]`. It persists for the module lifetime and is later consumed by the runner outside this chunk. The static descriptors are mutable in practice only through their `fill_helper`, which writes allocated instruction buffers and stack depth into the `struct bpf_test` instance before execution.

Dynamic instruction buffers are allocated per test setup by fill helpers and stored in `self->u.ptr`. The release path is outside this chunk, but this chunk's convention is clear: generated programs must expose both pointer and length through the descriptor so later code can compile and free them.

`struct bpf_test` stores inline packet data in `data[MAX_DATA]` and optional fragment data in `frag_data[MAX_DATA]`. For normal tests, the later harness can build a packet from `data`; for `FLAG_SKB_FRAG`, it must combine head data and fragment bytes to test non-linear skb reads.

`stack_depth` is a per-test declared property used for eBPF programs because these module tests do not call the verifier in the normal way. Any test that touches `R10` stack offsets must declare enough stack for the interpreter/JIT setup path.

`nr_testruns` allows expensive generated tests to reduce repetitions. `NR_PATTERN_RUNS` and `NR_STAGGERED_JMP_RUNS` are used in table entries beyond and within this chunk to keep exhaustive-style tests from dominating runtime.

No filesystem state, Ceph client state, network state, or persistent kernel configuration is mutated by this chunk. Side effects are limited to memory allocation, local descriptor updates, and the eventual pass/fail behavior when the later module harness runs the tests.

## Dependencies and Integration Points

- Kernel BPF definitions from `<linux/filter.h>` and `<linux/bpf.h>` provide `struct sock_filter`, `struct bpf_insn`, classic instruction macros (`BPF_STMT`, `BPF_JUMP`, `__BPF_STMT`, `__BPF_JUMP`), eBPF instruction macros (`BPF_ALU64_IMM`, `BPF_JMP_REG`, `BPF_LDX_MEM`, `BPF_ATOMIC_OP`, `BPF_EXIT_INSN`, and many others), register constants, opcode constants, and `BPF_MAXINSNS`.
- SKB and network dependencies from `<linux/skbuff.h>`, `<linux/netdevice.h>`, and `<linux/if_vlan.h>` support classic ancillary loads such as `SKF_AD_PKTTYPE`, `SKF_AD_MARK`, `SKF_AD_RXHASH`, `SKF_AD_QUEUE`, `SKF_AD_PROTOCOL`, `SKF_AD_VLAN_TAG`, `SKF_AD_IFINDEX`, and packet offset handling.
- Random and math helpers include `struct rnd_state`, `prandom_seed_state()`, `prandom_u32_state()`, `div64_u64()`, and `div64_u64_rem()` for deterministic generated programs and reference arithmetic.
- Memory allocation uses kernel allocation helpers (`kmalloc_objs()`, `kmalloc_array()`, `GFP_KERNEL`) and normal memory helpers (`memcpy()`).
- Endian-sensitive tests use `__BIG_ENDIAN`, `cpu_to_be16()`, `cpu_to_be32()`, `cpu_to_be64()`, `cpu_to_le16()`, `cpu_to_le32()`, and `cpu_to_le64()` to set expected low-word return values portably.
- The later runner outside this chunk must understand `CLASSIC` versus `INTERNAL`, `FLAG_EXPECTED_FAIL`, `FLAG_LARGE_MEM`, `FLAG_SKB_FRAG`, `stack_depth`, `nr_testruns`, and allocated `.u.ptr` instruction buffers.
- Build integration is kernel module based; this chunk begins module source content but the `module_init()`, `module_exit()`, and module metadata appear after the covered range.

## Tests Covered in the Table

The first classic tests validate basic accumulator/index behavior (`TAX`, `TXA`), arithmetic and bitwise opcodes, immediate loads, bounds checking for absolute and indirect packet loads, link-layer and network-layer offset helpers, skb ancillary fields, netlink attribute access, payload offset, `SKF_AD_ALU_XOR_X`, spill/fill memory slots, conditional branch families, tcpdump-generated filters, and uninitialized register zero behavior.

The early internal/eBPF tests validate trivial arithmetic, multiplication variants, all-register add/sub/xor/mul paths, move and 64-bit immediate handling, mixed ALU control flow, shift-by-register behavior, and a 32-bit-only context pointer zero-extension case under `CONFIG_32BIT`.

Checker-negative classic entries intentionally fail compilation or validation: missing `RET`, division by zero, unsupported/unknown socket-filter instruction, out-of-range spill/fill, invalid `RET X`, invalid `LDX + RET X`, and invalid `SKF_AD_MAX`. These set `FLAG_EXPECTED_FAIL` with `expected_errcode = -EINVAL`.

The ALU section exercises MOV, MOVSX, ADD, SUB, MUL, DIV, MOD, signed DIV/MOD encodings, AND, OR, XOR, LSH, RSH, ARSH, NEG, endian conversion, and byte swapping. The tests deliberately use boundary constants such as `0xffffffff`, `0x80000000`, `0x7fffffff`, negative immediates, zero shifts, shifts equal to 32, shifts greater than 32, and values whose high word must be checked separately.

The memory section exercises `BPF_LDX_MEM` for byte, halfword, word, and doubleword widths; sign-extending `BPF_LDX_MEMSX`; `BPF_STX_MEM`; immediate `BPF_ST_MEM`; and large-memory offsets marked with `FLAG_LARGE_MEM`. Endianness guards select which byte/word from a stored doubleword should be visible at stack offsets.

The atomic table section first uses generated fill helpers for long `STX_XADD` loops, then expands macros for many width/op/fetch combinations, and finally supplies explicit `CMPXCHG` success, failure, store, return, and side-effect checks for word and doubleword operations.

The jump section covers `JMP32` comparisons for equality, inequality, bit set, unsigned greater/greater-equal/less/less-equal, signed greater/greater-equal/less/less-equal, immediate and register sources, small/large/negative immediates, and then the 64-bit `JMP` equivalents. It also includes unconditional exit behavior, forward/backward unconditional jumps, signed value-walk control flow, and `ldimm64` jump-offset accounting.

Near the end of the chunk, generated max-instruction entries bind the helper functions to named tests and expected sentinels. The final visible entries begin fragmented SKB coverage for `LD_IND` and `LD_ABS` byte/halfword/word loads, including mixed head/fragment reads. The last entry visible in this chunk, `LD_ABS halfword mixed head/frag`, is incomplete at line 10902 and continues in the next chunk.

## Risks and Edge Cases

- The assigned range stops inside a `tests[]` entry. Any summary of fragmented SKB tests or total table coverage is incomplete until the next chunk is merged.
- The file is not Ceph-specific despite living under `sources/distributed-fs/ceph-client/lib/`; it is kernel BPF test code. Folder-level research should avoid inferring Ceph runtime coupling from this path alone.
- Many generators use calculated lengths plus `BUG_ON()`. A future edit that changes emitted instruction counts without updating formulas can panic the test module rather than produce a normal assertion failure.
- Fill helpers allocate large instruction arrays. Allocation failures return `-ENOMEM`; the later harness must treat that as setup failure and release any successfully allocated buffers.
- Some generated tests are intentionally expensive. The table uses custom run counts for pattern and staggered jump tests to limit execution time, but increasing `PATTERN_BLOCK*` or max jump sizes can make module load tests very slow.
- `__bpf_alu_result()` is a reference model embedded in the test. Bugs in that model can cause generated tests to encode the wrong expected result. Division/modulo by zero are skipped, but signed division/modulo off=1 tests in the static table depend on kernel instruction semantics rather than this helper.
- The code assumes verifier-inserted zero extension in places, especially atomic 32-bit `CMPXCHG` paths and tests flagged with `FLAG_VERIFIER_ZEXT` outside this immediate range. Because these module tests bypass normal verifier behavior in some paths, the harness must explicitly emulate or arrange required zero-extension behavior.
- Endianness-specific expectations are embedded with preprocessor branches. Cross-architecture regressions can hide if only little-endian machines run this module.
- `FLAG_LARGE_MEM` tests use `R1` as a memory base rather than stack pointer. The later data-generation path must allocate and initialize enough external memory for offsets as high as 32768 bytes.
- Atomic register-pair tests intentionally combine aliasing of destination pointer, source register, and `R0`. Small changes to eBPF atomic ABI assumptions can break multiple tests at once.
- Classic BPF ancillary loads depend on skb fields initialized by later harness code (`mark`, `hash`, queue mapping, vlan tag, device ifindex/type, protocol). If the harness setup drifts, these tests fail even when the interpreter/JIT is correct.
- The static table contains hand-authored expected constants. The line-range table is large enough that copy/paste mistakes are a realistic maintenance risk, especially in repeated ALU64 sign-extension and jump descriptor names.

## Test Signals

- Successful execution of classic basic tests returns the listed scalar values for each packet length subtest, for example `TAX`, `TXA`, arithmetic, packet load, branch, tcpdump, memory-slot, and skb ancillary cases.
- Expected checker failures should reject at setup with `-EINVAL` and not be treated as runtime BPF failures.
- Generated max-instruction tests should distinguish accepted `BPF_MAXINSNS` programs from the intentionally oversized program.
- ALU/JMP pattern-generated programs should return `1` after all embedded comparisons pass; early exits or line-number sentinel returns indicate the first failed embedded check.
- Memory and atomic tests typically return `0`, `1`, or a specific low word after comparing stored and loaded data. Nonzero unexpected values often identify register clobbering, missing zero/sign extension, endian mismatch, or wrong fetch semantics.
- Staggered jump tests should return `size + 1` according to their table result, proving branch-conversion passes preserved relative control flow.
- Fragmented SKB tests should return bytes/halfwords/words that span skb head and fragment boundaries; this chunk only shows the start of that group.

## Chunk Boundary Notes

Earlier chunks are not needed for this source file because this chunk begins at line 1. Later chunks contain the remainder of the fragmented-SKB tests, additional generated pattern table entries, the module runtime harness, tail-call tests, module parameters, init/exit paths, and module metadata.

The final per-file report should treat this chunk as the foundational descriptor/generator/table chunk and reconcile it with later chunks for the complete `tests[]` array and execution harness.
