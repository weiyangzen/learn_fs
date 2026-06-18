# Research: sources/distributed-fs/ceph-client/lib/test_bpf.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006107`: lines 1-10902, `Docs/researches/chunks/subset-b-006107_research.md`
- `subset-b-006108`: lines 10903-15771, `Docs/researches/chunks/subset-b-006108_research.md`

## Chunk Research

### subset-b-006107: lines 1-10902

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

### subset-b-006108: lines 10903-15771

# sources/distributed-fs/ceph-client/lib/test_bpf.c lines 10903-15771

## Scope

This chunk covers the final portion of the kernel `test_bpf.c` module. It begins inside the large `tests[]` descriptor table and runs through the module init/exit registration. The covered range includes:

- Classic BPF packet access cases for `LD_ABS`, `LD_IND`, and `LDX_MSH`, including skb fragment coverage.
- Classic ALU and jump tests that validate default accumulator and index register initialization.
- eBPF instruction tests for signed immediates, operand aliasing, register clobber preservation, ALU32/JMP32 zero-extension side effects, generated ALU/atomic/jump matrices, conditional jump simplification, short and long jumps, and staggered jump layouts.
- The runtime harness that turns `struct bpf_test` descriptors into classic or internal `struct bpf_prog` instances, generates skb or memory inputs, runs each program repeatedly, and reports pass/fail timing.
- Separate skb segmentation regression tests.
- Tail-call regression tests, including tail-call table preparation, pseudo-call relocation, tail-call failure paths, and tail-call-count preservation across helper/function calls.
- Module parameters for suite, test name, test id, and test range selection, plus `module_init()`, `module_exit()`, and module metadata.

The chunk starts after earlier helpers and the beginning of `tests[]`. The final per-file report should merge this with prior chunks so the helper functions referenced by `.fill_helper` entries are described with their definitions.

## Purpose

This code is a kernel self-test module for the BPF interpreter and JIT compiler. It is not production Ceph client code despite living under the `sources/distributed-fs/ceph-client` snapshot. Its purpose is to compile many small BPF programs, run them through the interpreter or selected JIT runtime, and compare the return values against fixed expectations.

The tests in this range focus on correctness at boundaries that often differ between interpreters and architecture-specific JITs:

- Packet loads from skb linear data and skb fragments, including unaligned byte, halfword, and word reads.
- Negative skb offsets through `SKF_LL_OFF`, out-of-bounds loads, and expected verifier rejection for invalid negative absolute loads.
- Correct initialization of classic BPF accumulator `A` and index register `X`.
- Correct sign extension of eBPF immediates in 32-bit and 64-bit comparisons.
- Operand aliasing for `BPF_LDX_MEM` where destination and base registers are the same.
- Preservation of eBPF registers when a JIT lowers complex ALU or atomic operations through helper calls or internal call sequences.
- Preservation of source operands during ALU32, ATOMIC32, JMP32 immediate, and JMP32 register operations that require zero-extension internally.
- Generated coverage for register pair combinations, operand magnitude patterns, immediate byte patterns, all shift counts, long jumps, and staggered jump sequences.
- Tail-call behavior, including normal chaining, NULL target and invalid-index failure paths, maximum tail-call count enforcement, and preservation of tail-call state across function calls.
- `skb_segment()` behavior for crafted GSO skbs with frag lists, head frags, and linear no-head-frag payload layouts.

## Important APIs, Types, and Functions

- `struct bpf_test` is defined earlier in the file and is the descriptor shape consumed throughout this chunk. Each entry has a description, either classic `struct sock_filter` instructions or internal `struct bpf_insn` instructions, flags in `aux`, input bytes, up to three expected subtest results, optional fill helper, expected verifier error, optional fragment bytes, stack depth, and custom run count.
- `tests[]` is the main test table. This chunk contains the tail of the table, including many inline entries plus entries whose instruction streams are generated by earlier `.fill_helper` callbacks.
- `BPF_TEST_CLOBBER_ALU()` expands many ALU tests that execute an operation and then compare all eBPF registers against themselves/known values to catch JIT register clobbering.
- `BPF_TEST_CLOBBER_ATOMIC()` expands 32-bit and 64-bit atomic operation tests and sets `stack_depth = 8` because the generated programs write temporary atomic memory below `R10`.
- `BPF_ALU32_SRC_ZEXT()`, `BPF_ATOMIC32_SRC_ZEXT()`, `BPF_JMP32_IMM_ZEXT()`, and `BPF_JMP32_REG_ZEXT()` build tests that preserve high 32-bit source/destination state around operations that should compare or compute on 32-bit values without destructively zero-extending operands in place.
- `.fill_helper` entries refer to generator functions defined earlier in the file, such as `bpf_fill_alu64_*`, `bpf_fill_alu32_*`, `bpf_fill_atomic*`, `bpf_fill_jmp*`, `bpf_fill_max_jmp*`, and `bpf_fill_staggered_*`. These allocate large or patterned instruction arrays and set `tests[i].u.ptr.insns` and `u.ptr.len`.
- `populate_skb()` allocates an skb, copies test bytes into its linear data, and fills deterministic skb metadata such as protocol, packet type, mark, hash, queue mapping, VLAN fields, device ifindex/type, and network header.
- `generate_test_data()` maps a test descriptor and subtest index to runtime input data. It returns `NULL` for `FLAG_NO_DATA`, allocates plain memory for `FLAG_LARGE_MEM`, or constructs an skb from `test->data`; with `FLAG_SKB_FRAG`, it adds a page-backed fragment populated from `frag_data`.
- `release_test_data()` frees the data generated by `generate_test_data()` using the matching release path: no-op, `kfree()`, or `kfree_skb()`.
- `filter_length()` and `filter_pointer()` abstract whether a test uses inline instructions or a helper-generated pointer/length pair.
- `generate_filter()` compiles a test descriptor into a `struct bpf_prog`. Classic tests go through `bpf_prog_create()` and can expect verifier rejection via `FLAG_EXPECTED_FAIL`. Internal eBPF tests allocate with `bpf_prog_alloc()`, copy `struct bpf_insn` bytes directly, set `BPF_PROG_TYPE_SOCKET_FILTER`, stack depth, and verifier zero-extension metadata, then call `bpf_prog_select_runtime()`.
- `release_filter()` destroys classic programs with `bpf_prog_destroy()` and internal programs with `bpf_prog_free()`.
- `__run_one()` repeatedly calls `bpf_prog_run()` under `migrate_disable()` and records average nanoseconds per run with `ktime_get_ns()` and `do_div()`.
- `run_one()` iterates up to `MAX_SUBTESTS`, creates input data per subtest, runs the program `MAX_TESTRUNS` or a custom capped count, compares return values, and accumulates errors.
- `build_test_skb()` and `build_test_skb_linear_no_head_frag()` create specialized GSO skb/frag-list layouts for segmentation regressions.
- `struct skb_segment_test`, `skb_segment_tests[]`, `test_skb_segment_single()`, and `test_skb_segment()` run `skb_segment()` against those crafted packets with specific `netdev_features_t` masks.
- `struct tail_call_test` describes tail-call test programs, expected results, flags, stack depth, and whether the JIT should mark tail calls reachable.
- `TAIL_CALL_MARKER`, `TAIL_CALL_NULL`, `TAIL_CALL_INVALID`, and `TAIL_CALL(offset)` encode relocatable tail-call snippets. `prepare_tail_call_tests()` replaces markers with the runtime `struct bpf_array *` address and target program index.
- `bpf_test_func()` is a local BPF-callable function used to clobber many CPU registers. Tail-call tests call it to ensure JIT-maintained internal state, especially tail-call count, survives normal function calls.
- `prepare_tail_call_tests()` allocates a flexible `struct bpf_array`, builds each tail-call program, relocates pseudo tail-call and pseudo helper-call instructions, selects runtime/JIT code, and stores programs in `progs->ptrs`.
- `destroy_tail_call_tests()` frees all prepared tail-call programs and the array.
- `test_tail_calls()` executes each prepared tail-call program, optionally passing state memory, optionally reading the result from that state, and reports timing/pass/fail.
- `find_test_index()`, `prepare_test_range()`, and module parameters `test_suite`, `test_name`, `test_id`, and `test_range` implement selective test execution.
- `test_bpf_init()` validates suite selection, chooses default suite behavior when only filters are provided, prepares ranges, then runs `test_bpf`, `test_tail_calls`, and/or `test_skb_segment`.

## Control Flow

The main BPF suite is table-driven. `test_bpf()` loops over `tests[]`, skips entries outside `test_range`, emits the test description, invokes any `.fill_helper`, calls `generate_filter()`, frees helper-generated instruction memory after program creation, and either treats expected creation failure as a pass or runs the program.

Classic tests go through the kernel classic-BPF creation path. If `FLAG_EXPECTED_FAIL` is set, `generate_filter()` expects `bpf_prog_create()` to fail with `expected_errcode`; that path reports `PASS`, clears the error, and returns `NULL` so the caller counts the descriptor as passed without executing it. If the verifier accepts a test marked as expected failure, `generate_filter()` reports `UNEXPECTED_PASS` and returns `-EINVAL`.

Internal eBPF tests bypass normal user-facing verifier compatibility checks. The harness allocates a raw `struct bpf_prog`, copies test instructions, sets metadata such as `stack_depth` and `verifier_zext`, and then calls `bpf_prog_select_runtime()`. This path directly targets interpreter/JIT execution semantics rather than full verifier admission behavior.

`run_one()` handles data and expected output. It always runs subtest 0, then stops on the first later `{ data_size = 0, result = 0 }` sentinel. Each subtest gets fresh data, is run repeatedly through `__run_one()`, then releases the input. Matching results print average runtime; mismatches print decimal and hex values and increment the per-test error count.

The skb segmentation suite is independent from the BPF instruction table. `test_skb_segment()` loops over `skb_segment_tests[]`, builds each skb shape, calls `skb_segment()` with the declared feature mask, frees resulting segment lists when successful, and summarizes pass/fail counts.

Tail-call setup has a separate prepare/run/destroy lifecycle. `prepare_tail_call_tests()` first creates the program array. For each test, it scans for the instruction length, allocates a program, sets `tail_call_reachable` according to the descriptor, and copies instructions. It then performs relocation:

- `BPF_LD | BPF_DW | BPF_IMM` instructions marked with `TAIL_CALL_MARKER` are patched to load the `struct bpf_array *`.
- `BPF_ALU | BPF_MOV | BPF_K` instructions marked with `TAIL_CALL_MARKER` are patched to the absolute target index, the NULL slot, or an intentionally invalid out-of-range index.
- `BPF_JMP | BPF_CALL` instructions with `BPF_PSEUDO_CALL` are replaced with direct calls to kernel functions such as `numa_node_id`, `ktime_get_ns`, `ktime_get_boot_fast_ns`, `ktime_get_coarse_ns`, `get_jiffies_64`, or `bpf_test_func`. If a direct call immediate cannot represent the target, it is replaced with a NOP jump so the test remains runnable.

`test_tail_calls()` then runs each prepared program. Some tests pass `&state` as input and use in-memory state as the asserted result. This is how recursive tail-call limit and NULL/invalid target failure paths count how many times execution fell through or stopped.

`test_bpf_init()` is the top-level dispatcher. If no `test_suite` is specified, it runs all three suites. If a suite is specified, it runs only that suite after validating range/name/id selection. If a filter is provided without a suite, it defaults to `test_bpf`.

## State and Persistence Behavior

The primary persistent state is static module state: `tests[]`, `dev`, module parameter buffers, and `tail_call_tests[]`. Test descriptors are file-scope data and persist for the module lifetime. Helper-generated instruction buffers are transient: `test_bpf()` calls the fill helper before creating a program, then frees `tests[i].u.ptr.insns` and resets it to `NULL` immediately after `generate_filter()`.

Runtime input data is intentionally short-lived. `populate_skb()` creates a fresh skb for each subtest. `FLAG_SKB_FRAG` adds a page fragment whose page ownership is transferred into the skb via `skb_add_rx_frag()`, so `kfree_skb()` releases it. `FLAG_LARGE_MEM` uses plain `kmalloc()` and `kfree()`. `FLAG_NO_DATA` passes `NULL` to `bpf_prog_run()`.

The fake `net_device dev` is static and reused. `populate_skb()` updates its net namespace, ifindex, and type before assigning it to the skb. This is shared module state, but the test module runs serially in its init path, so there is no concurrent mutation in this harness.

Internal eBPF programs receive metadata through `fp->aux`, especially `stack_depth`, `verifier_zext`, and tail-call reachability. Because these tests bypass the normal verifier path, these fields are part of the test contract: the runtime/JIT relies on them for stack bounds, zero-extension assumptions, and tail-call prologue generation.

Tail-call tests allocate one `struct bpf_array` containing program pointers. Programs can tail-call each other by index, including self-recursive tests. The array is destroyed after `test_tail_calls()` finishes. The last valid map slot is intentionally a NULL program pointer for NULL target testing, while `TAIL_CALL_INVALID` targets one index past that range.

The only externally visible persisted results are kernel log messages and module init success/failure. A failing suite returns `-EINVAL` from init, preventing successful module load.

## Dependencies and Integration Points

- BPF core APIs: `bpf_prog_create()`, `bpf_prog_alloc()`, `bpf_prog_size()`, `bpf_prog_select_runtime()`, `bpf_prog_run()`, `bpf_prog_destroy()`, `bpf_prog_free()`, BPF instruction macros, and BPF program metadata in `struct bpf_prog_aux`.
- Classic BPF and eBPF instruction encodings: `BPF_STMT`, `BPF_JUMP`, `BPF_ALU32_IMM`, `BPF_ALU64_REG`, `BPF_ATOMIC_OP`, `BPF_LDX_MEM`, `BPF_JMP_IMM`, `BPF_JMP32_*`, `BPF_EXIT_INSN()`, `BPF_LD_IMM64()`, and related macros.
- skb/network APIs: `alloc_skb()`, `dev_alloc_skb()`, `__skb_put_data()`, `skb_reserve()`, `skb_put()`, `skb_add_rx_frag()`, `skb_reset_mac_header()`, `skb_reset_network_header()`, `skb_set_network_header()`, `skb_set_mac_header()`, `skb_segment()`, `kfree_skb()`, and `kfree_skb_list()`.
- Page and memory APIs: `alloc_page()`, `__free_page()`, `page_address()`, `kmalloc()`, `kzalloc_flex()`, `kfree()`, and `memcpy()`.
- Kernel timing/scheduling APIs: `cond_resched()`, `migrate_disable()`, `migrate_enable()`, `ktime_get_ns()`, and `do_div()`.
- Helper-call targets used by tail-call tests: `numa_node_id`, `ktime_get_ns`, `ktime_get_boot_fast_ns`, `ktime_get_coarse_ns`, `get_jiffies_64`, and local `bpf_test_func()`.
- Module infrastructure: `module_param_string()`, `module_param()`, `module_param_array()`, `module_init()`, `module_exit()`, `MODULE_DESCRIPTION()`, and `MODULE_LICENSE()`.

## Risks and Edge Cases

- The chunk begins mid-table. The first visible entry belongs to a broader packet-load group whose setup starts before line 10903, so final reconciliation needs the earlier chunk to avoid treating this range as a standalone table definition.
- Internal eBPF tests intentionally bypass the normal verifier. Any change to runtime assumptions normally supplied by the verifier, such as stack depth or zero-extension metadata, can produce false positives or false negatives unless the test metadata is updated with the same contract.
- `filter_length()` finds the last nonzero classic instruction by scanning for nonzero `code` or `k`. Tests that intentionally use zero-valued trailing instructions could be truncated unless they use a fill helper or a nonzero terminating instruction.
- Helper-generated instruction memory is stored back into the global `tests[]` entry until freed by `test_bpf()`. A fill helper failure leaves the entry untouched, while success relies on immediate cleanup after `generate_filter()`.
- `populate_skb()` rejects `size >= MAX_DATA`, not just greater-than. Tests expecting exactly `MAX_DATA` bytes cannot use the skb path.
- `FLAG_SKB_FRAG` copies `MAX_DATA` bytes into the allocated page and adds a `MAX_DATA` fragment regardless of the linear subtest size. That is deliberate for fragment access tests, but it means fragment coverage depends on expected offsets and skb length setup matching BPF load semantics.
- Classic negative-offset packet accesses are split between verifier-rejected direct negatives and `SKF_LL_OFF`-based in-bounds link-layer accesses. JITs must preserve that distinction.
- `__run_one()` returns only the last run's result after repeated execution. Tests with side effects in input state, such as tail-call count tests, intentionally depend on cumulative state; ordinary tests should not accidentally mutate shared input across runs.
- Tail-call tests patch raw instruction streams in allocated program memory. Incorrect marker handling could leave the marker immediate in place and produce a bogus pointer or index.
- Direct call relocation in tail-call tests silently NOPs a call if the target cannot be represented relative to `__bpf_call_base`. That keeps tests portable, but it reduces clobbering coverage on architectures where a call is skipped.
- `destroy_tail_call_tests()` assumes all non-NULL `progs->ptrs[]` are owned test programs and frees them directly.
- `prepare_test_range()` only validates ranges when a known suite is selected. With an empty suite, all suites run and `exclude_test()` applies the same numeric range to tables of different lengths, which is intentional but can be surprising when filtering all suites.
- The skb segmentation builders create artificial packet layouts with manual `len`, `data_len`, `truesize`, GSO, and frag-list manipulation. These are good regression inputs but are sensitive to skb layout invariants changing elsewhere in the networking stack.

## Test Signals

- Main suite log lines have the shape `#<id> <description> jited:<0|1> <avg-ns> PASS` for executable tests, or `PASS` during creation for expected verifier failures.
- The main summary reports passed/failed counts and `[jit_cnt/run_cnt JIT'ed]`. A nonzero failure count returns `-EINVAL` from `test_bpf()`.
- Packet-load tests should return expected big-endian byte/halfword/word values, including unaligned loads and mixed linear/fragment loads. Out-of-bounds loads should return zero, while invalid negative `LD_ABS` cases should be rejected with `-EINVAL`.
- Default-register tests should prove classic `A` and `X` start at zero: arithmetic, division/modulo by zero behavior, and jump comparisons all depend on zero initialization.
- Signed compare tests should distinguish sign-extended immediate comparison from unsigned literal comparison across internal eBPF and classic encodings.
- Operand aliasing tests should load stack values correctly when `BPF_LDX_MEM` uses the same register as destination and base.
- Register clobber tests should return `1` across all generated ALU and atomic operations; any return path other than `1` implies a register was not preserved across a JIT expansion.
- Zero-extension preservation tests should return zero after subtracting saved 64-bit operands from post-operation operands and folding high bits into the result.
- Generated matrix tests should pass for all shift counts, register pair combinations, operand magnitudes, immediate byte patterns, atomic variants, and jump comparison variants.
- Long conditional jump and staggered jump tests should return their expected branch-side values, covering JIT branch expansion and layout-sensitive jump offset handling.
- `test_skb_segment` should pass both `gso_with_rx_frags` and `gso_linear_no_head_frag` cases and report its own summary.
- Tail-call tests should pass normal chains with expected accumulated sums, recursive max-count tests with `(MAX_TAIL_CALL_CNT + 1) * MAX_TESTRUNS`, and NULL/invalid target tests with `MAX_TESTRUNS`.

## Chunk Boundary Notes

Earlier chunks define the file header, `struct bpf_test`, most fill-helper implementations, constants such as `MAX_SUBTESTS`, `MAX_TESTRUNS`, `MAX_DATA`, and the start of `tests[]`. This chunk is the final control and registration section: it closes the table, runs the table, adds skb segmentation and tail-call suites, exposes module parameters, and registers the module.
