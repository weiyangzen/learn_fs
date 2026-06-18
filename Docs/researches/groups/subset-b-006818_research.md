# subset-b-006818 Research

Grouped research for BPF verifier selftest sources under `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/`. Each section is source-tree aligned for reconciliation into the matching per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_linked_scalars.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_linked_scalars.c

## Purpose
This verifier selftest file exercises scalar register linking, ID preservation, ALU32/ALU64 synchronization, pruning, and precision propagation. It is focused on cases where multiple registers share a scalar origin and later comparisons or arithmetic should refine, preserve, or intentionally clear those links.

## Important APIs, Types, And Functions
The file uses `SEC("socket")`, `__naked`, `__success`, `__failure`, `__msg`, `__flag(BPF_F_TEST_STATE_FREQ)`, inline BPF assembly, and helpers such as `bpf_get_prandom_u32`. The C functions `alu32_negative_offset`, `dummy_calls`, and `spurious_precision_marks` complement the naked assembly tests by using compiler-generated BPF around volatile offsets and iterator kfunc calls.

## Control Flow
Most tests seed a scalar, copy it to linked registers, apply signed or unsigned comparisons, then rely on verifier propagation to make a later divide-by-zero or invalid pointer access reachable or unreachable. Examples cover negative offsets, self-add clearing IDs, stale deltas after ID clearing, 32-bit wraparound, cross ALU32/ALU64 interactions, and pruning with base IDs.

## State And Persistence
There is no runtime persistence. State is verifier abstract state: scalar IDs, offsets, tnum ranges, precision marks, stack/frame-pointer relations, and state-pruning cache entries.

## Dependencies And Integration Points
It depends on `linux/bpf.h`, `bpf_helpers.h`, `bpf_misc.h`, and the BPF selftest verifier harness that interprets annotations and expected log messages. Integration is by compiling these annotated sections into BPF objects and asserting verifier accept/reject behavior.

## Risks
The main risk is subtle unsoundness in linked-register propagation: preserved IDs can over-constrain unrelated registers, while cleared IDs can leave stale deltas. The tests intentionally encode impossible paths and invalid accesses to catch both false acceptance and false rejection.

## Test Signals
Expected signals are `__success`, `__failure`, exact messages such as `div by zero`, invalid variable-offset diagnostics, and state-frequency flags that stress pruning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_linked_scalars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_live_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_live_stack.c

## Purpose
This large verifier selftest suite validates stack liveness analysis across direct stack reads/writes, subprogram calls, callbacks, parent-frame forwarding, helper arguments, stack-slot granularity, and pruning. It targets verifier logic that records which stack slots are used, defined, killed, or propagated across frame boundaries.

## Important APIs, Types, And Functions
The file defines a hash map `map`, an array map `array_map_8b`, a `snprintf_u64_fmt` format string, and many `SEC("socket")` naked programs with `__log_level(2)` and `__msg` expectations. It uses `bpf_map_lookup_elem`, `bpf_get_prandom_u32`, `bpf_loop`, iterator kfuncs (`bpf_iter_num_new/next/destroy` through BTF root forcing), `bpf_snprintf`, tail-call program arrays, and inline assembly helper immediates.

## Control Flow
Tests begin with simple same-frame reads/writes, then expand to joins, variable stack offsets, must-write tracking, caller/callee stack propagation, callback contexts, transitive parent reads, dynamic callbacks, spill/reload cases, and multi-offset joins. Several tests deliberately build paths where a callee or helper reads a caller stack slot only on some branch, forcing conservative liveness merging.

## State And Persistence
Only verifier state persists during analysis. Runtime maps are fixtures for pointer/nullability and helper argument typing. The critical state is stack slot liveness bitmaps, stack spill metadata, parent-frame aliases, callback instance state, and pruning records.

## Dependencies And Integration Points
It includes `filter.h` plus BPF helper headers and is tightly coupled to verifier log formatting. The selftest harness checks both accept/reject outcomes and detailed `use:`/`def:` log lines, so it acts as a regression suite for `analyze_subprog()` and stack liveness internals.

## Risks
Unsound stack liveness can let stale pointers, map-value-or-null pointers, or scalar-confused stack values survive pruning. Overly conservative liveness can also block pruning and cause verifier complexity growth. The many log assertions make this file sensitive to intentional verifier diagnostic wording changes.

## Test Signals
Signals include exact liveness log lines (`use: fp...`, `def: fp...`), success/failure annotations, `BPF_F_TEST_STATE_FREQ`, invalid memory access messages, and specific state-pruning `safe` messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_live_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_liveness_exp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_liveness_exp.c

## Purpose
This file is a targeted complexity regression test for exponential behavior in verifier subprogram liveness analysis. It constructs a valid BPF call graph whose liveness recursion would explode without complexity limits.

## Important APIs, Types, And Functions
It uses macros `C(fn, off)` and `CALLS_50(fn)` to generate repeated inline assembly calls with distinct frame-pointer-derived arguments. Static naked subprograms `exp_sub1` through `exp_sub7` form an eight-frame chain, and `liveness_exponential_complexity` is the raw tracepoint entry.

## Control Flow
Each non-leaf subprogram calls the next subprogram fifty times, changing `r1` to a different `r10 - offset` value at each call site. The entry repeats this pattern for `exp_sub1`, producing a theoretical branching factor of 50 across seven recursive levels.

## State And Persistence
There is no runtime state. The important state is verifier `arg_track` identity, callsite/depth instance tracking, and complexity accounting during `analyze_subprog()`.

## Dependencies And Integration Points
It depends on `bpf_misc.h` annotations and the raw tracepoint selftest loader. It integrates directly with verifier complexity guards for liveness analysis.

## Risks
Without bounded analysis or effective caching, this test can cause CPU soft lockups or memory exhaustion. It is intentionally valid BPF, so a simple verifier rejection for structural invalidity would be a regression.

## Test Signals
The expected result is failure with log level 2 and message `liveness analysis exceeded complexity limit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_liveness_exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_load_acquire.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_load_acquire.c

## Purpose
This file verifies BPF load-acquire atomic instruction validation. It confirms supported stack loads for byte, halfword, word, and doubleword widths, then rejects invalid source registers, pointer classes, alignment, and invalid register encodings.

## Important APIs, Types, And Functions
The tests are guarded by `CAN_USE_LOAD_ACQ_STORE_REL`. They emit raw encoded instructions with `__imm_insn(load_acquire_insn, BPF_ATOMIC_OP(... BPF_LOAD_ACQ ...))`. Program types include socket, XDP, flow dissector, and sk_reuseport.

## Control Flow
Positive tests write known values to the stack and use load-acquire to read them back, returning zero on equality. Negative tests attempt load-acquire from unreadable registers, scalars, misaligned stack offsets, context pointers, packet pointers, flow keys, sock pointers, and an invalid register number.

## State And Persistence
No persistent state is used. The relevant state is verifier register type, stack initialization, pointer provenance, access width, and alignment.

## Dependencies And Integration Points
It includes `filter.h` for BPF instruction encoding helpers and depends on architecture/compiler support for load-acquire/store-release. It integrates with verifier atomic memory access checks.

## Risks
Atomic load-acquire incorrectly allowed on packet, context, sock, or flow-key memory would bypass normal helper/prog-type access rules. Incorrect rejection of stack loads would break supported atomic semantics.

## Test Signals
Success cases expect `__retval(0)` including unprivileged success. Rejections assert messages like `!read_ok`, `invalid mem access 'scalar'`, `misaligned stack access`, and `BPF_ATOMIC loads from ... is not allowed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_load_acquire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_loops1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_loops1.c

## Purpose
This converted verifier suite tests bounded loop recognition, infinite loop detection, recursion rejection, back-edge handling, speculative paths, and loop patterns around the first instruction.

## Important APIs, Types, And Functions
It uses socket, XDP, and tracepoint sections, inline assembly, `bpf_get_prandom_u32`, local static naked subprograms for recursion and jump targets, and annotations for privileged/unprivileged differences.

## Control Flow
The tests cover simple count-up loops, loops from unknown scalar starts, equality-terminated loops, loops entered in the middle, forward jumps inside loops, jumps out of loops, conditional infinite loops, recursive calls, two/three-jump infinite patterns, and not-taken or taken back jumps to instruction zero.

## State And Persistence
There is no durable runtime state. Verifier state tracks scalar bounds, loop visitation, instruction exploration limits, speculative stack access safety, call graph cycles, and unprivileged back-edge policy.

## Dependencies And Integration Points
The file depends on the BPF verifier selftest harness and `bpf_misc.h`. It exercises verifier loop analysis across multiple program types and privilege modes.

## Risks
Loop analysis bugs can accept non-terminating programs, reject valid bounded loops, or miss unsafe speculative accesses hidden behind loop paths. The instruction-zero back-jump cases protect edge conditions in CFG traversal.

## Test Signals
Expected messages include `program is too large`, `recursive call from`, `loop detected`, and unprivileged `back-edge` failures, plus explicit return values for successful XDP tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_loops1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_lsm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_lsm.c

## Purpose
This file verifies BPF LSM return-value constraints, disabled hook rejection, and nullable/trusted pointer handling for LSM program contexts.

## Important APIs, Types, And Functions
It uses `vmlinux.h`, `bpf_tracing.h`, `BPF_PROG`, and LSM sections such as `lsm/file_permission`, `lsm/file_mprotect`, `lsm/audit_rule_known`, `lsm/file_free_security`, `lsm/getprocattr`, `lsm/setprocattr`, `lsm/ismaclabel`, and `lsm/mmap_file`.

## Control Flow
Naked tests return constants to validate hook-specific return ranges: errno-or-zero, bool, and void. Later C `BPF_PROG` tests dereference `struct file *` from `mmap_file`, one without a null check and one with a null guard before reading `f_inode`.

## State And Persistence
No application state persists. Verifier state is hook metadata, expected return range, nullable trusted-pointer tracking, and BTF-derived field access.

## Dependencies And Integration Points
The tests integrate with BPF LSM attach-point metadata and BTF type information from `vmlinux.h`. The selftest harness checks that disabled hooks are rejected.

## Risks
Wrong return-range enforcement could let LSM programs return invalid allow/deny values. Nullable pointer mishandling could admit unsafe kernel pointer dereferences.

## Test Signals
Signals include success for valid return ranges and failures with messages such as `should have been in [-4095, 0]`, `should have been in [0, 1]`, `points to disabled hook`, and `trusted_ptr_or_null_`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_lwt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_lwt.c

## Purpose
This file validates verifier context and direct packet access rules for Lightweight Tunnel BPF program types (`lwt_in`, `lwt_out`, and `lwt_xmit`).

## Important APIs, Types, And Functions
It uses `struct __sk_buff` fields `data`, `data_end`, and `tc_classid`, packet direct access, and the helper `bpf_skb_change_head` in the headroom test. Sections cover LWT input, output, transmit, and socket aliases used to exercise invalid context accesses.

## Control Flow
The first tests attempt direct packet writes and show that LWT_IN/LWT_OUT reject writes while LWT_XMIT permits them after bounds checks. Read tests verify packet reads are accepted. Later tests validate overlapping packet bounds checks, headroom adjustment invalidating/revalidating packet pointers, and rejection of `tc_classid` access.

## State And Persistence
No persistent state is kept. Verifier state consists of packet pointer ranges, context field permissions, packet-write capability per program type, and pointer invalidation after helper calls.

## Dependencies And Integration Points
It depends on the BPF selftest harness, `__sk_buff` layout offsets, and verifier program-type access tables for LWT.

## Risks
If packet writes are enabled for the wrong LWT direction, programs could mutate packets where the kernel expects read-only access. Incorrect context permissions could expose unsupported `__sk_buff` fields.

## Test Signals
Expected messages include `cannot write into packet` and `invalid bpf_context access`, while valid read/write cases assert `__retval(0)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_lwt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_in_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_in_map.c

## Purpose
This file tests map-in-map pointer behavior, inner map lookup typing, map pointer non-null facts, state pruning, and ring-buffer inner-map integration through dynptr reservation.

## Important APIs, Types, And Functions
It defines `map_in_map` as `BPF_MAP_TYPE_ARRAY_OF_MAPS` containing array maps, and `rb_in_map` as an array-of-maps containing ring buffers. It uses `bpf_map_lookup_elem`, `bpf_ringbuf_reserve_dynptr`, `bpf_ringbuf_submit_dynptr`, and helper wrappers `__rb_event_reserve` and `__rb_event_submit`.

## Control Flow
Positive tests look up an inner map and use it as a map pointer for a second lookup. Negative tests do pointer arithmetic on map pointers or pass a nullable inner pointer without a null check. Additional tests show map pointers are never null, including after spill/fill, and exercise state pruning across repeated lookup branches.

## State And Persistence
Maps are static fixtures, but no user data persistence is central to the test. Verifier state tracks map pointer versus map-value-or-null, non-null map pointer invariants, spilled map pointer types, and dynptr lifetime.

## Dependencies And Integration Points
The file integrates with map-in-map BTF/map-definition support, ringbuf dynptr helpers, and verifier map pointer type rules.

## Risks
Confusing inner map values with map pointers can lead to unsafe helper calls or pointer arithmetic on kernel map objects. Dynptr tests guard against verifier regressions around inner ringbuf maps.

## Test Signals
Signals include success/unprivileged success for valid lookup chains, `processed 15 insns` for pruning, and failures such as `pointer arithmetic on map_ptr prohibited` and `map_value_or_null expected=map_ptr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_in_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ptr.c

## Purpose
This file verifies direct verifier access to `bpf_map` pointer metadata: which offsets are readable, which are rejected, whether writes are forbidden, and how zero-offset arithmetic interacts with map pointers.

## Important APIs, Types, And Functions
It defines an array map with `struct test_val` values and a hash map with `struct other_val`. Tests use map address immediates, `bpf_map_lookup_elem`, strict/unprivileged annotations, and direct loads/stores from map pointers.

## Control Flow
Negative cases read a negative offset, write through a map pointer, or read a non-existent field around the internal `ops` member boundary. Positive cases read allowed metadata and perform map lookup after adding zero to map pointers in both operand orders.

## State And Persistence
The maps are static test fixtures. The relevant verifier state is pointer class `map_ptr`, fixed offset, access size, privilege gating, and whether ALU with zero preserves a usable map pointer.

## Dependencies And Integration Points
It integrates with verifier BTF/metadata rules for `struct bpf_map` and map helper argument validation.

## Risks
Permitting map pointer writes or arbitrary metadata reads would expose kernel internals. Rejecting zero arithmetic too aggressively could break valid compiler output that normalizes pointers.

## Test Signals
Expected logs include negative offset rejection, `only read from bpf_array is supported`, non-existent field diagnostics, and unprivileged capability messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ptr_mixing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ptr_mixing.c

## Purpose
This file validates verifier behavior when control flow merges different map pointer identities or map types before helper use, including tail-call program-array cases.

## Important APIs, Types, And Functions
It defines array, hash, array-of-maps, and two program-array maps. Dummy socket programs populate program arrays. Tests use subprograms returning map pointers, `bpf_map_lookup_elem`, and `bpf_tail_call`.

## Control Flow
One test merges hash and array map pointers before lookup and succeeds because both are acceptable map helper arguments. Another merges hash and map-in-map in a way that triggers invalid direct metadata access. Tail-call tests compare branches producing different versus same program arrays.

## State And Persistence
The declared maps are static fixtures. Verifier state is the key subject: map pointer identity, map type, helper-compatible unioning at joins, and special handling for program-array tail-call map pointers.

## Dependencies And Integration Points
The suite depends on verifier join logic for map pointers and tail-call validation for program arrays. It is integrated through socket and tc selftest sections.

## Risks
Over-permissive merging can let a helper receive an incompatible map type. Over-strict merging can reject valid branches that preserve helper-compatible map pointer classes.

## Test Signals
Expected outcomes include successful return values for compatible merges, `only read from bpf_array is supported` for incompatible joins, and unprivileged `tail_call abusing map_ptr` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ptr_mixing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ret_val.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ret_val.c

## Purpose
This file tests verifier validation around map helper arguments and map lookup return values, especially null checks and alignment-sensitive map value access.

## Important APIs, Types, And Functions
It defines a hash map `map_hash_8b` and uses `bpf_map_delete_elem` plus `bpf_map_lookup_elem`. Tests are socket programs with strict alignment annotations where needed.

## Control Flow
The invalid-FD test passes literal zero as a map argument. Lookup-return tests access `r0` without checking for null, access with an intentionally misaligned offset, and branch so one path dereferences a null map value.

## State And Persistence
The hash map is a fixture. Verifier state tracks helper argument type, map-value-or-null return state, null refinement, alignment, and unprivileged pointer-leak restrictions.

## Dependencies And Integration Points
It integrates with generic map helper validation and strict-alignment verifier mode.

## Risks
Missing null checks on map lookups can become runtime null dereferences. Incorrect alignment handling can accept loads/stores that are invalid on strict-alignment architectures.

## Test Signals
Failures assert messages such as `fd 0 is not pointing to valid bpf_map`, `map_value_or_null`, `misaligned value access`, and unprivileged `R0 leaks addr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ret_val.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_masking.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_masking.c

## Purpose
This file exercises verifier range reasoning for the classic branchless bounds-mask idiom `mask = -((limit - value) | value) >> 63; value &= mask`. It verifies both 32-bit and 64-bit inputs around zero, `-1`, `0xffffffff`, and ordinary in-range constants.

## Important APIs, Types, And Functions
The tests are socket programs using inline BPF assembly, `__success_unpriv`, and return-value expectations. They manipulate 32-bit and 64-bit scalars with subtraction, OR, negation, signed right shift by 63, and final AND masking.

## Control Flow
The first twelve `test_out_of_bounds_*` cases feed boundary and out-of-range constants into the mask idiom and expect the value to collapse to zero. The eight `masking_test_in_bounds_*` cases use values below the limit and expect the original value to survive, including `0xabcde`, `0xfffffffe`, and values produced by multiplying negative constants by `-1`.

## State And Persistence
No runtime state is persisted. The important state is scalar min/max, tnum masks, signed/unsigned bounds, 32-bit subregister behavior, and how bounds survive the branchless arithmetic mask sequence.

## Dependencies And Integration Points
It integrates with verifier scalar-bound analysis and unprivileged safety checks. The file is converted from older verifier tests into annotation-driven BPF C.

## Risks
Incorrect masking analysis can allow out-of-bounds access when a variable offset is believed bounded, or reject common compiler-generated masking patterns.

## Test Signals
All tests are expected to pass in privileged and unprivileged modes. Out-of-bounds cases return `0`; in-bounds cases return the surviving masked value such as `4`, `0xfffffffe`, `0xabcde`, or `46`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_masking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_may_goto_1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_may_goto_1.c

## Purpose
This file tests verifier and translator handling of raw `may_goto` (`BPF_JMP | BPF_JCOND`) instructions with zero and positive offsets.

## Important APIs, Types, And Functions
It uses raw tracepoint sections, architecture filters for x86_64/s390x/arm64, `__xlated` expectations, and `BPF_RAW_INSN(BPF_JMP | BPF_JCOND, ...)` emitted through `__imm_insn`.

## Control Flow
`may_goto_simple` and `may_goto_batch_0` emit one or more zero-offset conditional jumps that translate down to `r0 = 1; exit`. `may_goto_batch_1` uses offsets 2/1/0 in a batch, and `may_goto_batch_2` checks the expanded translation with internal counter stack slots before normal exit.

## State And Persistence
There is no runtime persistence. Verifier state includes may-goto expansion/accounting, branch reachability, generated counter stack slots, and architecture-specific translated output.

## Dependencies And Integration Points
It integrates with core verifier control-flow validation for newer BPF ISA behavior. The selftest harness checks both accepted and rejected variants.

## Risks
If may-goto is treated as an ordinary jump, valid bounded constructs may fail. If treated too permissively, non-terminating or unsafe paths may be accepted.

## Test Signals
Signals are `__success` plus exact translated instruction snippets, including compact translations for zero-offset batches and the longer counter-based expansion for offset 2/0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_may_goto_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_may_goto_2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_may_goto_2.c

## Purpose
This small companion file covers C-level use of the experimental `can_loop` condition, which lowers to may-goto style verifier control flow.

## Important APIs, Types, And Functions
It includes `bpf_experimental.h`, declares global `gvar`, and defines a raw tracepoint C program `may_goto_c_code`.

## Control Flow
The program runs three bounded `for (i = 0; i < 3 && can_loop; i++)` loops: one zeroes a local stack array, one fills it from `gvar - i`, and one accumulates values back into `gvar`.

## State And Persistence
The global `gvar` persists as BPF global data for the object, while stack array `tmp[3]` is per invocation. Verifier state covers bounded stack indexing, may-goto lowering from `can_loop`, and loop progress.

## Dependencies And Integration Points
It depends on the BPF ISA and verifier support for may-goto instructions and is consumed by the same selftest harness as the other verifier programs.

## Risks
Small may-goto tests are important because parser or codegen regressions can otherwise be hidden by larger suites. Misvalidation here would indicate a control-flow soundness issue.

## Test Signals
The expected signal is `__success` for the raw tracepoint C program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_may_goto_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_meta_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_meta_access.c

## Purpose
This file validates verifier rules for XDP packet metadata access between `data_meta` and `data`, plus interactions with `data_end`, `bpf_xdp_adjust_meta`, and atomic-derived offsets.

## Important APIs, Types, And Functions
It uses XDP sections, `struct xdp_md` offsets for `data_meta`, `data`, and `data_end`, inline assembly, `bpf_xdp_adjust_meta`, and a locked stack add used to produce a bounded scalar in later tests.

## Control Flow
Tests 1 and 7/8/11/12 establish valid metadata bounds against `data` before reading. Tests 2-4 and 6/9/10 intentionally check the wrong boundary, go below `data_meta`, or use `data_end`/shifted `data` in ways that do not prove metadata safety. Test 5 calls `bpf_xdp_adjust_meta` and then uses the stale metadata pointer, which must be rejected.

## State And Persistence
No persistent state exists. Verifier state tracks packet metadata pointer class, packet pointer range, fixed and variable offsets, helper-induced pointer invalidation, and atomic-result scalar bounds.

## Dependencies And Integration Points
It integrates with verifier packet access logic used by tc/XDP-style programs and depends on context layout definitions from kernel BPF headers.

## Risks
Metadata boundary mistakes can allow packet memory corruption or reject valid metadata manipulation. These tests protect pointer range reasoning across packet meta/data transitions.

## Test Signals
Expected results include `__retval(0)` for valid reads and failures such as `R0 min value is negative`, `invalid access to packet`, and `R3 !read_ok`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_meta_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_movsx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_movsx.c

## Purpose
This file tests sign-extension move instructions for BPF CPU v4-style semantics, including 8-, 16-, and 32-bit sign extension into 32- and 64-bit destinations and their effect on range analysis.

## Important APIs, Types, And Functions
It uses socket tests with `__success_unpriv`, explicit `__retval`, and inline assembly mnemonics for sign-extension moves. A fallback `dummy_test` is compiled when CPUv4 support is unavailable.

## Control Flow
Initial tests validate concrete sign-extension results. Range-check tests compare sign-extended values to expected signed bounds. Negative cases attempt sign-extending `r10` frame pointer or create problematic variable-offset loop reasoning.

## State And Persistence
No persistent state exists. Verifier state tracks subregister bounds, sign-bit propagation, pointer/scalar separation, var_off, and loop detection after sign extension.

## Dependencies And Integration Points
It depends on compiler/JIT support for the relevant BPF ISA version. It integrates with verifier ALU and pointer-protection logic for sign-extending moves.

## Risks
Incorrect MOVSX semantics can corrupt verifier ranges and permit unsafe pointer arithmetic or reject valid signed-bound code. Sign-extending pointers must stay forbidden.

## Test Signals
Expected signals include precise return values (`0x23`, negative values, `1`, `0`), pointer sign-extension rejection, `infinite loop detected`, and unprivileged diagnostics for pointer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_movsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_mtu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_mtu.c

## Purpose
This small tc ingress test validates stack initialization behavior around `bpf_check_mtu`.

## Important APIs, Types, And Functions
The main function `tc_uninit_mtu` declares a stack `__u32 mtu`, passes its address to `bpf_check_mtu(ctx, 0, &mtu, 0, 0)`, and returns success. It uses `SEC("tc/ingress")` and unprivileged failure annotation.

## Control Flow
The program gives a helper a pointer to a stack variable intended to be written by the helper. Privileged verification succeeds; unprivileged mode rejects invalid stack reads according to the annotation.

## State And Persistence
There is no persistent state. The verifier tracks stack slot initialization and helper write semantics for the output MTU pointer.

## Dependencies And Integration Points
It depends on tc program context `struct __sk_buff`, `bpf_check_mtu`, and helper argument metadata.

## Risks
Incorrect helper modeling can either expose uninitialized stack data or reject valid helper output-parameter patterns.

## Test Signals
The expected signal is privileged `__success` with unprivileged failure message `invalid read from stack`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_mtu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_mul.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_mul.c

## Purpose
This file verifies abstract multiplication precision for a deliberately small tnum. It checks that multiplying an odd unknown scalar by three does not introduce imprecision in bit 2.

## Important APIs, Types, And Functions
It uses an fentry program `BPF_PROG(mul_precise, int x)` attached to `bpf_fentry_test1`, inline assembly, and `bpf_get_prandom_u32` to construct `(random & 0x2) | 0x1`.

## Control Flow
The program constrains `r0` to tnum-like possibilities `{1,3}`, multiplies by `3`, masks with `0x4`, and returns `0` only if the masked bit is known zero. Extra multiplication imprecision would make the branch appear possibly nonzero.

## State And Persistence
No persistent state is kept. The relevant verifier state is scalar precision, signed/unsigned bounds, and tnum propagation across multiplication and bit masking.

## Dependencies And Integration Points
It integrates with fentry BPF program loading and the verifier's arithmetic precision machinery.

## Risks
Multiplication is range-amplifying; weak precision tracking can hide unsafe offsets, while overly pessimistic tracking can reject valid code.

## Test Signals
The test signal is successful fentry program verification; semantically the intended return path is `0`, while the `r0 = 1` path documents the precision failure that should not be considered reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_mul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_netfilter_ctx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_netfilter_ctx.c

## Purpose
This file validates `SEC("netfilter")` BPF context access rules for `struct bpf_nf_ctx`, including valid reads, invalid short/past-end accesses, forbidden writes, and practical skb/state usage.

## Important APIs, Types, And Functions
It uses `struct bpf_nf_ctx`, `struct nf_hook_state`, `struct __sk_buff`, dynptr helpers `bpf_dynptr_from_skb` and `bpf_dynptr_slice`, `bpf_htons`, and local `NF_DROP`/`NF_ACCEPT` constants.

## Control Flow
Naked negative tests read too-small fields, read past the context, or write to context memory. The C test `with_invalid_ctx_access_test5` reads `state` then writes `state->sk`, which must be rejected. The valid test checks skb length, creates a dynptr, slices IP/TCP headers, checks protocol family, and returns accept/drop based on destination port.

## State And Persistence
No state persists beyond helper calls. Verifier state tracks read-only context fields, trusted state pointers, skb dynptr lifetime, packet slice nullability, and return-code bounds.

## Dependencies And Integration Points
It depends on netfilter BPF program support, context metadata, dynptr helper semantics, and network header BTF/layout definitions.

## Risks
Invalid context writes could mutate kernel hook state. Incorrect dynptr or context typing could permit invalid skb access or reject valid netfilter programs.

## Test Signals
Failures assert `invalid bpf_context access` or `only read is supported`; the valid program expects `__retval(0)` and is marked unprivileged failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_netfilter_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_netfilter_retcode.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_netfilter_retcode.c

## Purpose
This file tests netfilter BPF return-code validation. Netfilter programs must return a known value in the accepted range.

## Important APIs, Types, And Functions
It uses four `SEC("netfilter")` naked programs with success/failure annotations and inline return values.

## Control Flow
The first test returns an unknown context-derived value and fails. The next two return constants `0` and `1` and pass. The final test returns `2` and fails range validation.

## State And Persistence
No persistent state exists. Verifier state tracks whether `R0` is known at exit and whether its signed range is within `[0, 1]`.

## Dependencies And Integration Points
It integrates with netfilter program-type metadata and verifier exit-state checks.

## Risks
Allowing unknown or out-of-range return values could confuse netfilter verdict handling.

## Test Signals
Expected messages include `R0 is not a known value` and `R0 has smin=2 smax=2 should have been in [0, 1]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_netfilter_retcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_or_jmp32_k.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_or_jmp32_k.c

## Purpose
This focused test verifies 32-bit bitwise OR/AND reasoning followed by immediate conditional jumps on an unknown value.

## Important APIs, Types, And Functions
It is a single socket naked program `or_jmp32_k` using inline ALU32 operations, branches, and an intentionally invalid scalar memory access.

## Control Flow
The program builds a 32-bit scalar from `0xffffffff`, masks and ORs it, compares it against constants, then follows branch paths that should prove or disprove reachability of an invalid write through scalar `r0`.

## State And Persistence
There is no runtime state. Verifier state is scalar tnum/range information across ALU32 operations and conditional jump refinement.

## Dependencies And Integration Points
It integrates with verifier ALU32 bound propagation and branch pruning logic.

## Risks
If the verifier mishandles OR-derived tnums, it may either miss an unsafe scalar pointer dereference path or reject safe code.

## Test Signals
The expected failure message is `R0 invalid mem access 'scalar'`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_or_jmp32_k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_precision.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_precision.c

## Purpose
This file is a precision-marking regression suite. It ensures verifier `mark_precise` backtracking works through negation, endian conversions, conditional operations, atomics, stack values, map values, and LSM return constraints.

## Important APIs, Types, And Functions
It defines `precision_map` and many raw tracepoint/LSM naked programs. It emits atomic instructions with raw `.8byte` encodings, uses `bpf_map_lookup_elem`, and asserts detailed `mark_precise:` log output. Conditional-op coverage includes a static subprogram `__bpf_cond_op_r10`.

## Control Flow
Tests transform scalar values and then use them as offsets or return values requiring precision. Atomic tests store/load stack or map values, perform fetch-add, xchg, OR/AND/XOR, cmpxchg, and 32-bit atomics, then force precision marking on the result or argument. LSM tests check whether precise negation yields allowed return ranges.

## State And Persistence
The array map is a fixture for map-value atomic tests. Verifier state includes precise register marks, stack precision marks, parent-state backtracking, atomic result typing, and return-range constraints.

## Dependencies And Integration Points
It depends on `filter.h` instruction helpers, map helper metadata, raw tracepoint and LSM program types, and stable verifier log text.

## Risks
Precision bugs often cause latent unsoundness in variable offsets or excessive false positives. This file also protects against missed precision propagation through atomic read-modify-write instructions.

## Test Signals
The main signals are exact `mark_precise:` log sequences, successful verification for valid precision propagation, and failures where LSM `R0` ranges remain invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_precision.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_prevent_map_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_prevent_map_lookup.c

## Purpose
This file ensures `bpf_map_lookup_elem` rejects map types that are not lookup-able through that helper: stack trace maps and program arrays.

## Important APIs, Types, And Functions
It defines `map_stacktrace` as `BPF_MAP_TYPE_STACK_TRACE` and `map_prog2_socket` as `BPF_MAP_TYPE_PROG_ARRAY`, then calls `bpf_map_lookup_elem` on each.

## Control Flow
Each test initializes a zero key on the stack, passes the relevant map pointer to `bpf_map_lookup_elem`, and exits. The helper call itself must be rejected by map type.

## State And Persistence
Maps are static fixtures. Verifier state tracks map type IDs and helper compatibility.

## Dependencies And Integration Points
It integrates with BPF map helper dispatch rules and program-array semantics used for tail calls rather than lookup.

## Risks
Allowing lookup on these map types would violate helper contracts and could expose unsupported kernel data or confuse program-array control-flow assumptions.

## Test Signals
Expected failures are `cannot pass map_type 7 into func bpf_map_lookup_elem` and `cannot pass map_type 3 into func bpf_map_lookup_elem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_prevent_map_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_private_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_private_stack.c

## Purpose
This file tests private-stack JIT/verifier behavior on supported architectures, including single programs, nested calls, callbacks, exceptions, and async timer callbacks. It includes a fallback dummy test where private stack is unsupported.

## Important APIs, Types, And Functions
It includes `vmlinux.h`, `bpf_experimental.h`, defines `MAX_BPF_STACK`, `struct elem` with `bpf_timer`, and an array map. It uses `bpf_get_smp_processor_id`, `bpf_throw`, `bpf_map_lookup_elem`, `bpf_timer_init`, `bpf_timer_set_callback`, and `bpf_timer_start`. It also uses `__jited` annotations for x86_64 and arm64 expected code patterns.

## Control Flow
Tests write deep stack slots to trigger private stack allocation, call subprograms that make cumulative stack depth exceed `MAX_BPF_STACK`, run callbacks through `bpf_loop`, throw exceptions in main or subprograms, and set timer callbacks that may or may not be nested.

## State And Persistence
The array map and timer objects are runtime fixtures, but the key state is verifier/JIT stack-depth accounting, private-stack eligibility, callback nesting, and exception unwind handling.

## Dependencies And Integration Points
It integrates with architecture-specific JIT output checks, private-stack support, timer kfunc/helper semantics, and experimental exception support.

## Risks
Incorrect private-stack selection can corrupt per-CPU stack storage or generate wrong unwind code. Async callbacks are especially sensitive because potential nesting changes stack safety.

## Test Signals
Signals include `__success`, expected JIT instruction regexes, return values for fentry tests, and fallback dummy success on unsupported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_private_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_raw_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_raw_stack.c

## Purpose
This file validates raw stack initialization and bounds rules around `bpf_skb_load_bytes`, including helper writes into stack memory and later reads from those bytes.

## Important APIs, Types, And Functions
It uses socket and tc sections, `bpf_skb_load_bytes`, stack pointers derived from `r10`, and annotations for strict/unprivileged behavior.

## Control Flow
Tests cover reading stack without helper initialization, negative/zero/unbounded lengths, helper-initialized reads, initialized stack before helper calls, spilled register corruption around helper writes, invalid stack destination offsets, and large but bounded stack writes.

## State And Persistence
No durable state exists. Verifier state tracks stack byte initialization, spilled register metadata versus raw data, helper write ranges, and stack bounds relative to the 512-byte BPF stack.

## Dependencies And Integration Points
It depends on tc skb helper metadata and verifier stack-state modeling. It is a regression suite for helper functions that initialize stack memory.

## Risks
A helper write that fails to clear spilled-register metadata can create type confusion. Weak length/bounds checks can allow writes outside the BPF stack or reads from uninitialized memory.

## Test Signals
Expected signals include success for valid helper-initialized reads and failures such as `R4 min value is negative`, `invalid zero-sized read`, `invalid write to stack`, unbounded memory access guidance, and scalar invalid memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_raw_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_raw_tp_writable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_raw_tp_writable.c

## Purpose
This file verifies that writable raw tracepoint buffers cannot be written through a variable offset.

## Important APIs, Types, And Functions
It defines a small hash map `map_hash_8b` and one `SEC("raw_tracepoint.w")` naked program. The test uses `bpf_map_lookup_elem` to obtain an unknown scalar from a map value, then adds it to the writable tracepoint buffer pointer.

## Control Flow
The program reads the tracepoint buffer pointer from context, looks up a map value, exits on null, adds a variable map-derived offset to the buffer pointer, and attempts an 8-byte store.

## State And Persistence
The hash map is a fixture for producing a variable offset. Verifier state tracks raw tracepoint writable buffer pointer class, variable offset, and allowed store constraints.

## Dependencies And Integration Points
It integrates with raw writable tracepoint verifier rules and generic map lookup nullability.

## Risks
Allowing arbitrary variable-offset writes into tracepoint buffers could corrupt event payloads outside the intended writable range.

## Test Signals
The expected failure is `R6 invalid variable buffer offset: off=0, var_off=(0x0; 0xffffffff)` with `BPF_F_ANY_ALIGNMENT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_raw_tp_writable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ref_tracking.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ref_tracking.c

## Purpose
This large suite verifies BPF reference tracking for sockets, sock_common, key references, ringbuf reservations, tail calls, LD_ABS/LD_IND, subprograms, spills, branches, and use-after-release cases.

## Important APIs, Types, And Functions
It defines `BPF_SK_LOOKUP`, kfunc declarations `bpf_key_put`, `bpf_lookup_system_key`, and `bpf_lookup_user_key`, map fixtures (`map_array_48b`, `map_ringbuf`, `map_prog1_tc`), dummy tail-call programs, and many tc/LSM/socket naked tests. Helper families include `bpf_sk_lookup_tcp`, `bpf_skc_lookup_tcp`, `bpf_sk_release`, socket conversion helpers, `bpf_tail_call`, `bpf_ringbuf_reserve`, and `bpf_ringbuf_discard`.

## Control Flow
Tests acquire nullable references, branch on null checks, spill references to stack, copy/zero them, release in same frame or subprograms, leak them over exits or tail calls, try double release, perform LD_ABS/IND with and without held references, access socket members before and after release, and check kfunc key release rules.

## State And Persistence
Maps and program arrays are fixtures. Verifier state is reference IDs, ownership, nullable-to-non-null refinement, stack spill reference metadata, release invalidation, subprogram transfer of ownership, and prohibited operations while refs are live.

## Dependencies And Integration Points
It integrates with socket lookup helpers, key kfunc BTF records, ringbuf reference-like reservation semantics, and tail-call verifier rules. The `__kfunc_btf_root` function ensures BTF FUNC records are emitted for kfunc linking.

## Risks
Reference tracking bugs cause leaks, double frees, use-after-release, or unsafely retained refs across tail calls and packet access instructions. Conversely, false positives can block valid release-in-subprogram patterns.

## Test Signals
Expected logs include `Unreleased reference`, `type=... expected=sock`, `BPF_LD_[ABS|IND] would lead to reference leak`, `tail_call would lead to reference leak`, `pointer arithmetic on sock prohibited`, invalid member access, and success for correctly released references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ref_tracking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_reg_equal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_reg_equal.c

## Purpose
This file tests when equality/range information from 32-bit subregister operations may be propagated to full 64-bit registers.

## Important APIs, Types, And Functions
It has two socket naked programs using `bpf_ktime_get_ns`, stack spill/reload, `w3 = w2`, and conditional branches.

## Control Flow
The first test stores a helper result to stack and reloads only 32 bits, proving the upper half of `r2` is zero; a `w2 < 9` comparison can safely refine `r3`. The second copies a full 64-bit helper result into `r2`, so `w3 = w2` must not imply full-register equality; an illegal `r1` read remains reachable.

## State And Persistence
No persistent state exists. Verifier state tracks subregister definitions, upper-32 zero knowledge, register IDs, and branch range propagation.

## Dependencies And Integration Points
It integrates with verifier scalar equality and subregister tracking.

## Risks
Incorrect full-register equality from 32-bit operations can make unsafe paths appear unreachable. Overly conservative handling rejects useful compiler-generated code.

## Test Signals
The first program succeeds. The second expects failure `R1 !read_ok`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_reg_equal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_regalloc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_regalloc.c

## Purpose
This file stresses verifier register allocation and range propagation for map value pointers when multiple scalar registers contribute to an offset.

## Important APIs, Types, And Functions
It defines a hash map `map_hash_48b` containing `struct test_val`, uses `bpf_map_lookup_elem`, `bpf_get_prandom_u32`, tracepoint sections, `BPF_F_ANY_ALIGNMENT`, and subprograms for after-call/in-callee scenarios.

## Control Flow
Each test looks up a map value, constrains one or more random scalars, adds them to a map-value pointer, and reads from the resulting address. Positive cases keep the computed offset within the 48-byte value. Negative cases allow off-by-end or too-wide accesses. Subprogram tests verify range facts survive or are recalculated across calls.

## State And Persistence
The map is a static fixture. Verifier state tracks map value bounds, scalar ranges, register copies, spills, source-register marks, and call-clobbered register effects.

## Dependencies And Integration Points
It integrates with verifier pointer arithmetic and map-value bounds checking.

## Risks
Range loss during register allocation can either accept out-of-bounds map value access or reject valid bounded access. Spill and call cases catch regressions in non-local propagation.

## Test Signals
Success cases are annotated with `BPF_F_ANY_ALIGNMENT`; failures expect precise `invalid access to map value, value_size=48 off=... size=...` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_regalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ringbuf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ringbuf.c

## Purpose
This file verifies ring buffer reservation pointer rules: reserved memory must be released with zero offset, cannot be accessed after invalid offset arithmetic, and can be passed to permitted helpers.

## Important APIs, Types, And Functions
It defines `map_ringbuf` as `BPF_MAP_TYPE_RINGBUF` and uses `bpf_ringbuf_reserve` plus `bpf_ringbuf_submit`. The XDP helper test passes ringbuf memory to helper-compatible paths.

## Control Flow
The first negative test reserves 8 bytes, writes through the reservation, then adds an invalid offset before submit. The second adds the invalid offset before the write. The positive XDP test reserves memory, uses it in helper calls, submits it, and exits with zero.

## State And Persistence
The ringbuf map is a fixture. Verifier state tracks ringbuf_mem pointer identity, fixed offset, reservation lifetime, stack spill/fill preservation, and required release.

## Dependencies And Integration Points
It integrates with ringbuf helper verifier rules and memory-region argument validation.

## Risks
Allowing non-zero-offset release or out-of-range writes can corrupt ringbuf reservation accounting. Incorrect spill/fill typing could lose reservation lifetime information.

## Test Signals
Expected failures include `R1 must have zero offset when passed to release func` and `R7 min value is outside of the allowed memory range`; the helper pass-through case expects `__retval(0)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ringbuf.c -->
