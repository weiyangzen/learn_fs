# subset-b-006823 grouped research

This grouped report covers Linux eBPF verifier selftest fragments under `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier`. Each section preserves its source path and is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_cmpxchg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_cmpxchg.c

Purpose: exercises verifier and runtime semantics for `BPF_ATOMIC_OP(..., BPF_CMPXCHG, ...)` on stack memory, including 64-bit and 32-bit compare-exchange success and failure paths, returned old values, and post-operation memory contents.

Important APIs/types/functions: uses verifier-test macros `BPF_ST_MEM`, `BPF_MOV64_IMM`, `BPF_MOV32_IMM`, `BPF_ATOMIC_OP`, `BPF_LDX_MEM`, `BPF_JMP_IMM`, `BPF_JMP32_IMM`, and `BPF_EXIT_INSN`. The tests rely on `BPF_DW`, `BPF_W`, `BPF_CMPXCHG`, `BPF_REG_10` as frame pointer, and special treatment of `BPF_REG_0` as both compare input and returned old value.

Control flow: the smoke tests initialize a stack slot to `3`, attempt a non-matching compare-exchange, assert that the old value and memory remain `3`, then attempt a matching exchange to `4`. Later cases drive verifier rejection or privileged/unprivileged divergence by placing stack or frame-pointer-derived pointers in `R0`, copying only 32 bits of pointers, and loading through the cmpxchg return value.

State and persistence behavior: all mutable state is transient verifier test state in registers and stack slots. The file specifically checks verifier register state after cmpxchg: `BPF_W` cmpxchg must zero the upper 32 bits of `R0`, pointer-typed returned values may remain usable for privileged programs, and unprivileged mode must reject pointer leaks into memory.

Dependencies and integration points: integrated by inclusion into the BPF verifier test harness, which interprets `.insns`, `.result`, `.result_unpriv`, `.errstr`, `.errstr_unpriv`, and `.flags`. No standalone functions are exported.

Risks: changes to atomic return typing, 32-bit zero-extension, or pointer-leak diagnostics can silently weaken verifier guarantees. The `F_NEEDS_EFFICIENT_UNALIGNED_ACCESS` case is architecture-sensitive and should be preserved when adjusting expected failures.

Test signals: expected outcomes include `ACCEPT`, `REJECT`, unprivileged rejection with `R0 leaks addr into mem` or `R10 partial copy of pointer`, normal rejection with `invalid size of register fill` or `R0 invalid mem access`, and successful 32-bit zero-extension.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_cmpxchg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_fetch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_fetch.c

Purpose: validates atomic fetch operations that both update memory and return the old value into the source register. It covers pointer-leak handling for fetch-and with map pointers and a macro-generated matrix for add, and, or, xor, and xchg fetch semantics across register pairs.

Important APIs/types/functions: key macros are `BPF_LD_MAP_FD`, `BPF_LD_IMM64`, `BPF_STX_MEM`, `BPF_ATOMIC_OP`, `BPF_EMIT_CALL(BPF_FUNC_map_lookup_elem)`, and `__ATOMIC_FETCH_OP_TEST`. It uses map fixups via `.fixup_map_array_48b` and operations `BPF_ADD | BPF_FETCH`, `BPF_AND | BPF_FETCH`, `BPF_OR | BPF_FETCH`, `BPF_XOR | BPF_FETCH`, and `BPF_XCHG`.

Control flow: the first four explicit tests store a map pointer on the stack, atomically mask it with `-1`, retrieve either the stack slot or the returned source register, then attempt to store that value into a map element. The macro-generated tests write an operand to a stack slot, run an atomic fetch op through a selected destination pointer and source register, assert the source register contains the old value, and assert memory contains the expected result.

State and persistence behavior: state is limited to stack slots, register metadata, and harness-created array maps. The important verifier state transition is whether pointer identity survives an atomic fetch and whether unprivileged mode rejects leaking that pointer.

Dependencies and integration points: relies on verifier harness fixups for array maps and on map lookup helper semantics. It is a fragment consumed by the upstream selftest table rather than a standalone C module.

Risks: regressions here usually indicate incorrect source-register clobbering, wrong old-value return semantics, pointer-leak bypasses, or mishandled 32-bit fetch into a 64-bit typed slot. Error-string drift matters because the selftest checks exact verifier diagnostics.

Test signals: privileged 64-bit pointer fetch tests accept while unprivileged mode rejects with `leaking pointer from stack off -8`; 32-bit pointer fetch variants reject with `invalid size of register fill`; all macro-generated arithmetic/bitwise/xchg fetch tests accept with expected old and final values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_fetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_fetch_add.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_fetch_add.c

Purpose: focused tests for `BPF_ADD | BPF_FETCH`, checking correct old-value return, stack update, read-initialization requirements, frame-pointer immutability, and rejection of atomic writes to kernel memory exposed through tracing contexts.

Important APIs/types/functions: uses `BPF_ATOMIC_OP`, stack stores and loads, `BPF_PROG_TYPE_TRACING`, `BPF_TRACE_FENTRY`, and `.kfunc = "bpf_fentry_test7"` to exercise read-only kernel memory.

Control flow: accepted 64-bit and 32-bit smoke tests store `3`, add `1`, check that the source register receives old value `3`, then check the stack slot is `4`. Rejection cases try to use `R10` as the atomic source, use uninitialized source or destination registers, or perform fetch-add through an fentry argument pointer.

State and persistence behavior: mutable state is stack memory except the kernel-memory test, where verifier state must tag the traced object as read-only. `R10` must remain a read-only frame pointer even when used as the atomic fetch source.

Dependencies and integration points: integrated with tracing verifier support and kfunc attachment metadata. The `.prog_type`, `.expected_attach_type`, and `.kfunc` fields are necessary for the kernel-memory test path.

Risks: weakening these checks could allow atomic modification of frame pointers, uninitialized register use, or mutation of read-only kernel memory from tracing programs.

Test signals: accepted smoke tests return zero on success; expected rejections include `frame pointer is read only`, `!read_ok`, unprivileged `R10 leaks addr into mem`, and `only read is supported`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_fetch_add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_invalid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_invalid.c

Purpose: compact negative matrix proving every supported atomic opcode form rejects when the destination is a scalar rather than a pointer.

Important APIs/types/functions: defines `__INVALID_ATOMIC_ACCESS_TEST(op)`, which emits `BPF_ATOMIC_OP(BPF_DW, op, BPF_REG_1, BPF_REG_0, -8)` after making `R1` a scalar zero. It instantiates add, fetch-add, and, fetch-and, or, fetch-or, xor, fetch-xor, xchg, and cmpxchg variants.

Control flow: each generated test sets `R0 = 1`, `R1 = 0`, performs an atomic operation through `R1 - 8`, then would exit if accepted. The verifier should reject before runtime.

State and persistence behavior: no persistent state; the only relevant state is verifier register typing. `R1` must remain scalar and cannot be converted to a memory pointer by atomic addressing syntax.

Dependencies and integration points: included by the verifier test harness; all outcomes are `.result = REJECT` with the same diagnostic.

Risks: if any new atomic opcode is added without this scalar-pointer rejection coverage, invalid memory access could slip through. The duplicate add instantiations also make exact macro edits easy to disturb.

Test signals: every case rejects with `R1 invalid mem access 'scalar'`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_invalid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_or.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_or.c

Purpose: validates atomic OR behavior with and without fetch, including source-register preservation without `BPF_FETCH`, old-value return with `BPF_FETCH`, 32-bit operation behavior, and upper-32-bit zeroing.

Important APIs/types/functions: uses `BPF_ATOMIC_OP` with `BPF_OR`, `BPF_OR | BPF_FETCH`, `BPF_DW`, and `BPF_W`; compares with `BPF_JMP_IMM` and `BPF_JMP32_IMM`.

Control flow: the no-fetch test ORs `0x011` into `0x110`, verifies memory becomes `0x111`, and verifies `R1` remains `0x011`. Fetch tests verify `R1` receives old value `0x110`, memory becomes `0x111`, and `R0` is not clobbered. The final test starts with all bits set and ensures a word-sized fetch OR returns `0x00000000ffffffff`.

State and persistence behavior: state is stack-local and register-local. The core verifier/runtime state signal is whether source register clobbering depends on `BPF_FETCH` and whether word atomics zero-extend returned values.

Dependencies and integration points: included in the verifier selftest atomic suite. No map or helper fixups are required.

Risks: JIT back ends can mishandle atomic fetch registers or clobber `R0`; this file explicitly guards that behavior. 32-bit zero-extension mistakes can leak stale high bits.

Test signals: all four entries accept; runtime exit codes distinguish wrong old value, wrong memory result, source clobbering, and `R0` clobbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_or.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_xchg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_xchg.c

Purpose: smoke-tests atomic exchange for 64-bit and 32-bit stack slots.

Important APIs/types/functions: uses `BPF_ATOMIC_OP` with `BPF_XCHG`, stack stores, loads, and 64-bit or 32-bit conditional jumps.

Control flow: each case initializes a stack slot to `3`, exchanges in `4` through `R1`, checks that `R1` receives old value `3`, then loads memory to confirm it is now `4`.

State and persistence behavior: only stack and register state is involved. The important property is that xchg always fetches the old value into the source register, unlike non-fetch bitwise atomic ops.

Dependencies and integration points: harness-only test fragment, no helper or map fixups.

Risks: incorrect JIT lowering could either fail to store the new value or fail to return the old value. 32-bit comparisons must use `BPF_JMP32_IMM`.

Test signals: both tests expect `ACCEPT`; nonzero runtime exits identify old-value or final-memory mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_xchg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_xor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_xor.c

Purpose: validates atomic XOR behavior, mirroring the OR coverage but expecting `0x110 ^ 0x011 == 0x101`.

Important APIs/types/functions: uses `BPF_ATOMIC_OP` with `BPF_XOR` and `BPF_XOR | BPF_FETCH`, plus `BPF_DW` and `BPF_W` size variants.

Control flow: the no-fetch case verifies memory changes and `R1` is not clobbered. Fetch cases verify `R1` receives old memory, the stack slot receives the XOR result, and `R0` remains unchanged. The word-sized fetch case uses a signed `-1` sentinel in `R0` to catch unexpected clobbering.

State and persistence behavior: transient stack/register state; key metadata behavior is source-register old-value return only when fetch is requested and correct 32-bit execution without high-bit corruption.

Dependencies and integration points: verifier selftest fragment with no map/helper dependencies.

Risks: atomic XOR JIT lowering can share paths with OR/AND but still have operation-specific register-clobber bugs. The file preserves x86 JIT regression coverage called out in comments.

Test signals: all three tests accept and return zero only if old value, final memory, and non-clobber checks pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_xor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic.c

Purpose: minimal verifier sanity tests for program termination and initialized return register requirements.

Important APIs/types/functions: uses empty `.insns`, `BPF_EXIT_INSN`, and `BPF_ALU64_REG(BPF_MOV, ...)`.

Control flow: one test has no instructions, one exits without initializing `R0`, and one ends with a non-exit instruction.

State and persistence behavior: no runtime state persists. The file validates initial verifier state for `R0` and final-instruction structural checks.

Dependencies and integration points: consumed by the generic verifier selftest table.

Risks: these tiny cases catch broad verifier acceptance regressions that would otherwise allow malformed programs.

Test signals: all reject, with diagnostics `last insn is not an exit or jmp`, `R0 !read_ok`, and `not an exit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_call.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_call.c

Purpose: validates basic helper-call instruction decoding, helper ID validation, and argument register initialization across consecutive helper calls.

Important APIs/types/functions: uses raw `BPF_JMP | BPF_CALL` encodings, `BPF_FUNC_get_cgroup_classid`, `BPF_PROG_TYPE_SCHED_CLS`, and callee-saved `R6` for preserving context.

Control flow: invalid cases use a call with `BPF_X`, a call with reserved `off`, an unknown helper ID, and repeated helper calls without restoring `R1`. The accepted case saves `R1` in `R6`, calls the helper, restores `R1`, and calls again.

State and persistence behavior: focuses on register liveness after helper calls. The helper clobbers argument registers, so `R1` must be restored before reuse.

Dependencies and integration points: depends on helper availability for scheduler classifier programs. No map fixups.

Risks: call decoder changes can accidentally accept reserved fields; helper ABI changes can invalidate the liveness expectation.

Test signals: expected errors include `unknown opcode 8d`, `BPF_CALL uses reserved`, `invalid func unknown#1234567`, and `R1 !read_ok`; restored-argument case accepts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_instr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_instr.c

Purpose: covers ordinary ALU, shift, move, and endian instruction semantics, especially 32-bit zero-extension and shift-by-zero behavior.

Important APIs/types/functions: uses ALU macros such as `BPF_ALU64_IMM`, `BPF_ALU64_REG`, `BPF_ALU32_REG`, `BPF_MOV32_IMM`, `BPF_LD_IMM64`, and a raw invalid `BPF_ALU64 | BPF_END | BPF_TO_BE` encoding.

Control flow: accepted tests compute fixed return values for add/sub/mul, XOR zero-extension, arithmetic right shifts, and zero-distance left/right/arithmetic shifts with immediate and register shift counts. Negative coverage rejects an invalid 64-bit endian opcode. Final move tests confirm `mov64 src == dst` and `src != dst` acceptance in scheduler classifier programs.

State and persistence behavior: no persistent state. Tests are register-dataflow checks, with `.retval` values acting as runtime proofs for arithmetic semantics.

Dependencies and integration points: consumed by the verifier test harness; some cases specify `BPF_PROG_TYPE_SCHED_CLS`.

Risks: ALU verifier range tracking and JIT lowering frequently share implementation paths; regressions can show up as wrong return values rather than verifier rejection.

Test signals: mostly `ACCEPT` with expected `.retval`; the invalid endian case rejects with `unknown opcode df`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_instr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_stx_ldx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_stx_ldx.c

Purpose: verifies that load/store instruction register fields reject register numbers outside the valid eBPF range.

Important APIs/types/functions: uses raw `BPF_STX`, `BPF_ST`, and `BPF_LDX` encodings with invalid source or destination register IDs such as `R15`, `R14`, `R12`, and `R11`.

Control flow: each case emits one invalid memory instruction followed by exit. Rejection should happen during instruction validation.

State and persistence behavior: no persistent state; validates decoder/register-number state before memory safety analysis.

Dependencies and integration points: generic verifier selftest entries.

Risks: accepting invalid register encodings can corrupt verifier state arrays or produce backend-specific behavior.

Test signals: all reject with exact diagnostics `R15 is invalid`, `R14 is invalid`, `R12 is invalid`, or `R11 is invalid`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_stx_ldx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/bpf_loop_inline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/bpf_loop_inline.c

Purpose: tests verifier/JIT handling of `bpf_loop` helper inlining decisions and stack layout for loop callback state.

Important APIs/types/functions: uses `BPF_FUNC_loop`, pseudo/subprogram call macros, tracepoint program type, callback function bodies, stack slots for callback context, and `F_NEEDS_JIT_ENABLED`.

Control flow: accepted cases include a simple inline loop call, non-inlined calls when flags are nonzero or callback is non-constant, a loop with a dead function, loop-variable stack-location checks, and a big-program inline case. The callback and main program bodies are encoded as instruction arrays with relative calls and exits.

State and persistence behavior: state is verifier stack-frame metadata and callback/callee state. The stack-location test is specifically about separating loop helper bookkeeping from program stack slots and preserving callback argument state.

Dependencies and integration points: requires tracepoint program type and JIT enabled because the feature under test is inline expansion. The harness marks `.runs = 0` for several verifier-only cases.

Risks: incorrect inlining can change verifier complexity, break callback identity checks, or corrupt stack slot layout. Non-constant callbacks and nonzero flags must remain accepted without forcing inline conversion.

Test signals: all listed cases accept under `BPF_PROG_TYPE_TRACEPOINT` with `F_NEEDS_JIT_ENABLED`; failures would surface as verifier rejection or runtime mismatch in loop variable handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/bpf_loop_inline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/bpf_st_mem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/bpf_st_mem.c

Purpose: validates immediate stores to stack memory, including nonzero values, zero initialization, variable-offset zero stores, and verbose sign formatting.

Important APIs/types/functions: uses `BPF_ST_MEM`, `BPF_ALU64_IMM` for variable offsets, `BPF_PROG_TYPE_SK_LOOKUP`, `BPF_SK_LOOKUP`, and `VERBOSE_ACCEPT`.

Control flow: tests store immediates into stack slots and exit. The variable-offset case builds a bounded variable pointer off `R10` before storing zero, relying on verifier rules that zero writes can initialize stack ranges. The sign test checks verbose verifier output for a negative immediate store.

State and persistence behavior: all state is verifier stack-slot initialization metadata. Zero stores are important because initialized stack state can influence later helper calls and pruning.

Dependencies and integration points: uses sk_lookup program type and attach type, with `.runs = -1` to avoid runtime execution where context is not material.

Risks: stack initialization tracking for immediate stores is foundational; regressions can either reject valid stack initialization or allow reads from uninitialized stack bytes.

Test signals: first three cases accept; sign case is `VERBOSE_ACCEPT` and checks the verbose log contains the expected stored value annotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/bpf_st_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/calls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/calls.c

Purpose: large subprogram and kfunc verifier suite. It covers kfunc prototype validation, subprogram call graph rules, register argument passing, stack-frame isolation and combined depth, map-value pointer propagation across frames, packet pointer spills, pruning/liveness across frames, and reference-object argument constraints.

Important APIs/types/functions: uses raw `BPF_CALL` encodings with `BPF_PSEUDO_KFUNC_CALL`, `BPF_CALL_REL`, many helpers (`map_lookup_elem`, `xdp_adjust_head`, `get_prandom_u32`, `ktime_get_ns`, `ringbuf_reserve`, `tcp_raw_gen_syncookie_ipv4`), fixups (`fixup_kfunc_btf_id`, `fixup_map_hash_8b`, `fixup_map_hash_48b`, `fixup_map_ringbuf`), and program types including tracepoint, sched cls/act, XDP, socket filter, cgroup skb, and extension programs.

Control flow: early entries verify kfunc rejection for uneliminated invalid calls, wrong pointer-to-memory struct shapes, non-context arguments, void pointers without size args, bad release offsets, member type mismatches, variable/negative `PTR_TO_BTF_ID` offsets, missing attach metadata for freplace, and refcounted argument requirements. The middle section exercises normal subprogram calls, unprivileged restrictions, recursion and invalid destinations, conditional calls, call targets crossing function bodies, fallthrough rules, `ld_abs` interaction, and callee return typing. Later tests cover stack writes through caller-provided frame pointers, combined stack-depth accounting across two or three frames, call-stack depth limit, dead-code stack handling, ambiguous returns, map-value and map-value-or-null propagation through caller stack slots and arguments, packet pointer spill safety, stack zero initialization and pruning, cross-frame liveness propagation, state ID comparison across frames, and rejecting multiple args with `ref_obj_id`.

State and persistence behavior: no persistent external state, but this file is primarily about verifier abstract state: call graph reachability, frame-local stack state, callee-saved registers, returned pointer IDs, nullable map-value refinement, packet range proofs, reference lifetime IDs, and pruning state equivalence across frames.

Dependencies and integration points: heavily integrated with verifier internals and harness fixup machinery. Kfunc cases require BTF ID fixups; map-value cases require hash-map fixtures; ring-buffer reference tests require ringbuf map fixtures. Some accepted runtime cases use `.retval`, while many are verifier-only negative tests.

Risks: this is high-blast-radius verifier coverage. Seemingly local changes to function-call validation, kfunc trusted-argument rules, stack-depth calculation, pointer ID equivalence, helper clobber rules, or pruning can alter many outcomes. Exact error strings are part of the test contract.

Test signals: mixed `ACCEPT`/`REJECT` and privileged/unprivileged splits. Key diagnostics include `invalid kernel function call not eliminated in verifier pass`, `recursive call`, `jump out of range`, `combined stack`, `call stack`, `cannot return stack pointer`, `R0 invalid mem access 'scalar'`, `invalid access to packet`, `same insn cannot be used with different`, `R8 invalid mem access 'map_value_or_null'`, and `more than one arg with ref_obj_id`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/calls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ctx_sk_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ctx_sk_lookup.c

Purpose: validates allowed and disallowed direct context accesses for `struct bpf_sk_lookup` programs.

Important APIs/types/functions: uses `offsetof(struct bpf_sk_lookup, ...)`, `sizeof(struct bpf_sk_lookup)`, `BPF_LDX_MEM`, `BPF_STX_MEM`, `BPF_PROG_TYPE_SK_LOOKUP`, and `BPF_SK_LOOKUP`.

Control flow: the first large accepted test performs all permitted byte, halfword, word, and doubleword reads from `family`, `protocol`, IPv4/IPv6 addresses, ports, ingress interface, and `sk`. Negative tests reject oversized 8-byte reads from 4-byte fields, undersized reads from the 8-byte `sk` pointer, out-of-bounds reads, unaligned reads, and writes of every size.

State and persistence behavior: no persistent state. The tests validate verifier context-field access metadata: width, alignment, read/write permissions, and end-of-struct bounds.

Dependencies and integration points: must run as `BPF_PROG_TYPE_SK_LOOKUP` with expected attach type `BPF_SK_LOOKUP`; most entries use `.runs = -1` or verifier-only behavior.

Risks: context ABI field size or offset changes can break these tests. Accidentally allowing writes or partial pointer reads would expose unsafe context mutation or pointer disclosure.

Test signals: valid multi-size reads accept; invalid reads/writes reject with `invalid bpf_context access`. Some unaligned cases require `F_NEEDS_EFFICIENT_UNALIGNED_ACCESS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ctx_sk_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ctx_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ctx_skb.c

Purpose: broad `struct __sk_buff` context access matrix covering sockets, sk_skb, tc cls/act, cgroup skb, and direct packet access.

Important APIs/types/functions: uses `offsetof(struct __sk_buff, ...)`, `offsetofend`, `BPF_LDX_MEM`, `BPF_STX_MEM`, direct packet `data` and `data_end`, program types `BPF_PROG_TYPE_SK_SKB`, `SCHED_CLS`, `SCHED_ACT`, `CGROUP_SKB`, and `CGROUP_SOCK`.

Control flow: early cases accept common skb field reads and reject invalid negative offsets or pointer comparisons. The SK_SKB section distinguishes socket tuple fields that are valid only for SK_SKB, rejects `tc_classid` and `mark`, permits selected writes (`tc_index`, `priority`), and verifies direct packet read/write after bounds checks. The `cb[]` section tests byte, half, word, and doubleword reads/writes, misalignment, out-of-bounds access, and wrong program type. Later cases cover writable fields in socket and tc programs, partial loads from fields such as `hash`, read-only `gso_segs`, `gso_size`, `hwtstamp`, padding after `gso_size`, and `wire_len` visibility. Final packet tests prove equivalent `pkt > pkt_end` and `pkt_end < pkt` checks refine packet safety.

State and persistence behavior: verifier state includes context field permissions, packet pointer bounds, endianness-sensitive partial loads, and unprivileged pointer-leak checks. No external state persists.

Dependencies and integration points: tied to `__sk_buff` ABI and per-program-type access tables in the kernel verifier. Some cases are architecture/alignment sensitive through `F_LOAD_WITH_STRICT_ALIGNMENT` and `F_NEEDS_EFFICIENT_UNALIGNED_ACCESS`.

Risks: field permission drift can expose writes from wrong program types or reject valid tc/sk_skb programs. Packet-bound equivalence is subtle and guards verifier range reasoning.

Test signals: expected diagnostics include `invalid bpf_context access`, `misaligned context access`, `different pointers`, and unprivileged `R1 leaks addr`; accepted cases often depend on explicit `.prog_type`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ctx_skb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/dead_code.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/dead_code.c

Purpose: verifies verifier handling of unreachable instructions and dead subprogram regions without rejecting otherwise safe programs.

Important APIs/types/functions: uses jumps, exits, relative subprogram calls, and `.retval` checks; unprivileged paths validate restrictions on calls to other BPF functions.

Control flow: tests place dead code at the start, middle, and end of main programs, at function tails, inside and before subprograms, and around calls. The final zero-extension case ensures dead-code elimination does not disturb 32-bit register semantics.

State and persistence behavior: state is verifier reachability and liveness information. Dead instructions should not contribute invalid state, stack depth, or bad return values when unreachable.

Dependencies and integration points: included in verifier harness with privileged/unprivileged split for subprogram-call tests.

Risks: overly strict reachability checks can reject valid optimized programs; overly loose checks can hide reachable unsafe paths.

Test signals: most cases accept with return values `7`, `1`, `2`, or `0`; unprivileged subprogram cases reject with `loading/calling other bpf or kernel functions are allowed for`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/dead_code.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/direct_value_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/direct_value_access.c

Purpose: validates direct map-value pointer loads via `BPF_PSEUDO_MAP_VALUE`, including bounds, signed offsets, small maps, and invalid `ld_imm64` encodings.

Important APIs/types/functions: uses `BPF_LD_MAP_VALUE`, `BPF_LD_IMM64_RAW_FULL`, map fixups `fixup_map_array_48b` and `fixup_map_array_small`, and memory load/store macros over direct map values.

Control flow: write tests 1-5 accept in-bounds doubleword stores across a 48-byte array value. Tests 6-13 reject out-of-range base or access offsets, including negative and huge offsets. Tests 14-17 check cross-byte/halfword loads and stores at the end of a 48-byte value. Tests 18-20 repeat boundary logic on a small map. Invalid instruction tests mutate reserved fields and pseudo kinds to confirm decoder rejection.

State and persistence behavior: harness-created maps provide backing state, but the test focus is verifier pointer offset metadata. Accepted runtime cases use `.retval` to prove writes and reads hit expected bytes.

Dependencies and integration points: depends on map fixup machinery for direct value pseudo-loads.

Risks: direct map-value access bypasses helper lookup, so offset validation and instruction decoding must be precise. Off-by-one bugs at value-size boundaries are the main risk.

Test signals: accepted cases return `1`, `0xff`, or `0xffff`; rejections include `R1 min value is outside of the allowed memory range`, `invalid access to map value pointer`, `invalid access to map value`, `invalid bpf_ld_imm64 insn`, `BPF_LD_IMM64 uses reserved fields`, and `unrecognized bpf_ld_imm64 insn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/direct_value_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/event_output.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/event_output.c

Purpose: positive coverage for `bpf_perf_event_output` helper availability across program types using a common instruction sequence that emits an 8-byte stack payload.

Important APIs/types/functions: defines `__PERF_EVENT_INSNS__`, which stores `5` at `fp-8`, passes `ctx`, a perf-event-output map, flags `0`, data pointer, and size `8` to `BPF_FUNC_perf_event_output`, then returns `1`. Uses `.fixup_map_event_output = { 4 }`.

Control flow: ten entries reuse the same instruction macro for `SOCK_OPS`, `SCHED_CLS`, `LWT_OUT`, `XDP`, `SOCKET_FILTER`, `SK_SKB`, `CGROUP_SKB`, `CGROUP_DEVICE`, `CGROUP_SYSCTL`, and `CGROUP_SOCKOPT` with `BPF_CGROUP_SETSOCKOPT` attach type.

State and persistence behavior: transient stack payload only; successful runtime execution would emit a perf event sample through the harness-provided map. Verifier state must recognize initialized stack data and helper availability for each program type.

Dependencies and integration points: relies on perf-event-array map fixup at instruction 4. The source comment notes the sequence is embedded here, not in fill helpers, because map fixup is against static instruction indexes.

Risks: helper availability regressions for any supported program type will reject valid observability programs. Changing the macro instruction layout requires updating the fixup index.

Test signals: every entry expects `ACCEPT` with `.retval = 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/event_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jit.c

Purpose: runtime-oriented verifier/JIT regression tests for shifts, 32-bit moves around `ldimm64`, multiplication/division, signed jumps, and jump padding.

Important APIs/types/functions: uses ALU shift/mul/div instructions, `BPF_LD_IMM64`, signed jump predicates, long jump sequences, subprogram calls, and `BPF_PROG_TYPE_SCHED_CLS`.

Control flow: early tests compute expected return value `2` for lsh/rsh/arsh, mov32, multiply, divide, and signed compare cases. Torturous jump tests use large immediate and conditional jump layouts, including a subprogram variant, to catch JIT offset and padding mistakes.

State and persistence behavior: state is register-only runtime state. The verifier accepts these programs; the JIT or interpreter must preserve exact arithmetic and branch behavior.

Dependencies and integration points: included in verifier tests but primarily probes JIT code generation. Some cases set `.prog_type = BPF_PROG_TYPE_SCHED_CLS`.

Risks: architecture JITs can miscompile edge-case shifts, division, or branch padding even when verifier acceptance is correct.

Test signals: all entries accept with specific `.retval` values, mostly `2`, with jump padding cases returning `1`, `2`, or `3`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jmp32.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jmp32.c

Purpose: comprehensive 32-bit jump semantics and verifier range-deduction suite.

Important APIs/types/functions: uses `BPF_JMP32_IMM`, `BPF_JMP32_REG`, predicates `JSET`, `JEQ`, `JNE`, unsigned `JGE/JGT/JLE/JLT`, signed `JSGE/JSGT/JSLE/JSLT`, packet data fixture macros, random extension macros (`BPF_RAND_UEXT_R7`, `BPF_RAND_SEXT_R7`), and map lookup fixups for range-bound memory access tests.

Control flow: for each predicate, BPF_K and BPF_X tests run multiple data inputs to prove upper 32 bits are ignored and signedness is correct. Min/max deduction tests use follow-up 64-bit checks or guarded invalid loads to ensure verifier pruning/range inference follows the 32-bit branch. Final cases verify bounded map-value offsets after 32-bit comparisons and JEQ/JNE bounds behavior.

State and persistence behavior: verifier abstract state is central: 32-bit comparisons must refine lower-word ranges without overtrusting upper bits. Runtime state comes from packet fixture data and helper-returned class IDs.

Dependencies and integration points: depends on scheduler classifier program type, direct packet fixture data, map hash fixups, and architecture flags for unaligned packet loads.

Risks: 32-bit branch range reasoning is easy to mix with 64-bit register state, causing false accepts or false rejects around bounds checks.

Test signals: all listed cases accept; many have `.runs` and `.retvals` arrays proving data-dependent branch behavior. Range tests use inserted nospec loads to expose bad verifier deductions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jmp32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jset.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jset.c

Purpose: validates 64-bit `BPF_JSET` runtime behavior and verifier reasoning for known, unknown, and partially known bit masks.

Important APIs/types/functions: uses `BPF_JMP_REG(BPF_JSET)`, `BPF_JMP_IMM(BPF_JSET)`, direct packet fixture input, `BPF_FUNC_get_prandom_u32`, and socket-filter program type for verifier path tests.

Control flow: functional tests compare packet-loaded values against register and immediate masks, including bit 63, bit 31 sign extension, and missing-bit paths. Later tests use known constants, random values, and `OR`-forced partial constants to verify whether guarded invalid loads are unreachable or reachable.

State and persistence behavior: state is register bitmask knowledge. The verifier must refine tnum/range information after JSET enough to prove some paths safe while rejecting genuinely reachable invalid reads.

Dependencies and integration points: uses packet data fixtures and helper availability for socket filter tests.

Risks: incorrect sign-extension of immediate masks or overly aggressive pruning can either miscompile runtime checks or accept unsafe invalid reads.

Test signals: functional cases accept with `.retvals` over multiple `.data64` inputs; negative reasoning cases reject with `!read_ok`; half-known and range cases accept due to proven branch constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jump.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jump.c

Purpose: tests general jump validation, stack-state merging, loop/back-edge handling, call/jump boundary validation, and dead-code elimination.

Important APIs/types/functions: uses conditional jumps, `BPF_JMP_IMM(BPF_JA)`, raw subprogram calls, map delete helper, scheduler classifier program type, and stack stores through frame pointers.

Control flow: early tests branch through many paths storing to stack slots and merging pointer state, with unprivileged pointer comparison rejections. Mid-file tests exercise long forward/backward jump layouts that are accepted as bounded. Call/jump tests distinguish valid jump loops from invalid subprogram call targets or missing exits. Final test uses signed/unsigned range checks and dead-code elimination to prove the safe return path.

State and persistence behavior: verifier state includes stack-slot initialization, pointer comparison restrictions, reachability, loop recognition, and cross-instruction state merging.

Dependencies and integration points: some tests require hash-map fixups and scheduler classifier program type; unprivileged expected errors are part of the contract.

Risks: jump target validation interacts with subprogram boundaries and dead-code pruning. Off-by-one target changes can accept jumps into invalid instruction regions.

Test signals: accepted cases return expected values or `-ENOENT`; rejected cases report `jump out of range from insn ...`, `last insn is not an exit or jmp`, or unprivileged `R1 pointer comparison`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/junk_insn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/junk_insn.c

Purpose: confirms the verifier rejects malformed or unknown raw instruction encodings.

Important APIs/types/functions: uses `BPF_RAW_INSN` with opcode `0`, invalid `BPF_LDX` reserved fields, opcode `-1`, and `0x7f`.

Control flow: every test emits one malformed instruction followed by exit. Structural validation must reject before execution.

State and persistence behavior: no state beyond instruction decoder validation.

Dependencies and integration points: generic verifier selftest fragment.

Risks: accepting junk opcodes creates undefined interpreter/JIT behavior and can compromise verifier assumptions.

Test signals: all reject with `unknown opcode 00`, `BPF_LDX uses reserved fields`, `unknown opcode ff`, or `BPF_ALU uses reserved fields`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/junk_insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_abs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_abs.c

Purpose: validates legacy packet `LD_ABS` and `LD_IND` semantics, calling convention clobbers, packet reload after skb-mutating helpers, invalid sizes, arithmetic interaction, VLAN helper-generated programs, and jumping around absolute loads.

Important APIs/types/functions: uses `BPF_LD_ABS`, `BPF_LD_IND`, `BPF_FUNC_skb_vlan_push`, fill helpers `bpf_fill_ld_abs_vlan_push_pop` and `bpf_fill_jump_around_ld_abs`, packet `.data`, and `BPF_PROG_TYPE_SCHED_CLS`.

Control flow: calling-convention tests zero specific registers before `LD_ABS` and then read them to prove `R1`-`R5` are clobbered while `R7` survives. Valid helper tests save context in `R6/R7`, perform absolute loads, call VLAN push, reload context, and load again. Negative cases reject doubleword absolute/indirect loads. Other tests combine division with abs/ind loads, parse ARP-like data, and rely on fill helpers for generated VLAN/jump programs.

State and persistence behavior: packet data fixture is runtime input. Verifier state must model `LD_ABS` clobbers and context reload requirements after helpers that may adjust skb data.

Dependencies and integration points: scheduler classifier program type, packet data fixtures, and external fill helpers in the verifier harness.

Risks: `LD_ABS` is legacy but still security-sensitive because it has special implicit context and register-clobber semantics. Mis-modeling clobbers can allow use of invalid register state.

Test signals: expected rejections include `R1 !read_ok` through `R5 !read_ok` and `unknown opcode`; accepted cases return values such as `42`, `256`, `10`, `0`, `0xbef`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_abs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_dw.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_dw.c

Purpose: stress-tests 64-bit immediate load handling through randomized/generated `ld_dw` instruction streams.

Important APIs/types/functions: uses empty `.insns` filled by `bpf_fill_rand_ld_dw`, scheduler classifier program type, and expected `.retval` values.

Control flow: five tests delegate instruction generation to the fill helper, then execute XOR-style semi-random immediate-load sequences that return known values.

State and persistence behavior: register-only runtime state. The verifier must accept the generated `ld_imm64` pairs and the JIT/interpreter must preserve exact 64-bit constants.

Dependencies and integration points: depends on harness fill helper `bpf_fill_rand_ld_dw`; not standalone.

Risks: immediate-pair encoding or JIT relocation bugs can corrupt high/low halves of constants.

Test signals: all accept with return values `4090`, `2047`, `511`, `5`, and `1000000 - 6`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_dw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_imm64.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_imm64.c

Purpose: validates 64-bit immediate-load instruction pair encoding, reserved-field handling, missing second halves, and malformed second-half immediates.

Important APIs/types/functions: uses `BPF_LD_IMM64`, raw full immediate macros, and verifier diagnostics for `BPF_LD_IMM64` reserved fields and invalid instruction sequencing.

Control flow: accepted tests load constants into registers and exit or compare expected values. Negative tests mutate the second instruction, reserved source/destination/off fields, or pair structure so the verifier rejects the malformed immediate load.

State and persistence behavior: register-only state. The important invariant is that a 64-bit immediate load is a two-instruction unit with constrained metadata in both slots.

Dependencies and integration points: generic verifier instruction-decoder tests.

Risks: accepting malformed `ld_imm64` pairs can desynchronize verifier instruction walking and JIT decoding.

Test signals: mixture of accepts and rejects; key diagnostic for the final case is `invalid bpf_ld_imm64 insn` when the second immediate is not zero where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_imm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/map_kptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/map_kptr.c

Purpose: validates verifier rules for kptr fields stored in map values, including allowed zero stores, disallowed stores to referenced kptrs, constant-offset requirements, untrusted pointer propagation, and `bpf_kptr_xchg` behavior.

Important APIs/types/functions: uses `BPF_FUNC_map_lookup_elem`, `BPF_FUNC_kptr_xchg`, `BPF_FUNC_this_cpu_ptr`, `BPF_FUNC_map_delete_elem`, `fixup_map_kptr`, `fixup_kfunc_btf_id`, and scheduler classifier program type.

Control flow: common tests reject nonzero immediate stores to kptrs, non-DW accesses, variable offsets, unaligned offsets, and helper indirect access. Unreferenced pointer tests check type mismatch, untrusted/null loaded pointer access, struct-size bounds, untrusted propagation through struct walking, no reference-state creation, and xchg rejection on unreferenced kptrs. Referenced pointer tests reject unsafe helper use, nonzero offsets, leaked reference after xchg, and raw ST/STX into referenced kptr fields.

State and persistence behavior: harness map values hold kptr fields, but the core state is verifier pointer trust, RCU/reference annotations, constant offset proofs, and reference lifetime tracking. The acquire kfunc case must create a reference that is detected as unreleased.

Dependencies and integration points: requires map-kptr fixture setup and BTF/kfunc fixups. Strongly tied to kernel BTF type names such as `prog_test_ref_kfunc` and `ptr_prog_test`.

Risks: kptr verifier bugs can allow storing arbitrary kernel pointers, bypassing reference tracking, or passing untrusted pointers to helpers.

Test signals: almost all cases reject with precise diagnostics such as `BPF_ST imm must be 0 when storing to kptr`, `kptr access size must be BPF_DW`, `kptr access cannot have variable offset`, `store to referenced kptr disallowed`, and `kptr cannot be accessed indirectly by helper`; one unreferenced no-reference-state case accepts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/map_kptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/perf_event_sample_period.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/perf_event_sample_period.c

Purpose: validates direct reads from `bpf_perf_event_data->sample_period` for all supported access widths.

Important APIs/types/functions: uses `BPF_LDX_MEM` from `struct bpf_perf_event_data`, `offsetof(..., sample_period)`, and `BPF_PROG_TYPE_PERF_EVENT`.

Control flow: four tests load byte, halfword, word, and doubleword values from the `sample_period` context field, then exit.

State and persistence behavior: no persistent state. The relevant verifier state is context-field read permission and width handling for perf event programs.

Dependencies and integration points: must be loaded as `BPF_PROG_TYPE_PERF_EVENT`; relies on the perf-event context ABI.

Risks: context access table drift could reject valid observability programs or allow invalid partial accesses elsewhere.

Test signals: all four cases accept for `BPF_PROG_TYPE_PERF_EVENT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/perf_event_sample_period.c -->
