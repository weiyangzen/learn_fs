# Research: subset-b-006820

Grouped source research for BPF selftest verifier, XDP, helper, and build-test files. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_unpriv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_unpriv.c

## Purpose
This converted verifier selftest suite exercises how the BPF verifier treats privileged versus unprivileged programs, especially pointer disclosure, pointer arithmetic, stack spill integrity, helper argument leakage, tail calls, and speculative execution mitigations. Most programs are naked inline assembly snippets with `__description`, `__success`, `__failure_unpriv`, `__msg_unpriv`, `__retval`, and optional `__xlated_unpriv` annotations consumed by the BPF selftest loader.

## Important APIs, Types, and Functions
The file defines `map_hash_8b`, a one-entry hash map with 64-bit key/value, and `map_prog1_socket`, a `BPF_MAP_TYPE_PROG_ARRAY` containing auxiliary socket programs. `BPF_SK_LOOKUP(func)` builds a zeroed `struct bpf_sock_tuple` on stack and calls `bpf_sk_lookup_tcp` or a compatible lookup helper. Important helpers include `bpf_tail_call`, `bpf_map_update_elem`, `bpf_map_lookup_elem`, `bpf_trace_printk`, `bpf_get_hash_recalc`, `bpf_sk_lookup_tcp`, `bpf_sk_release`, and `bpf_skb_load_bytes_relative`.

## Control Flow
The auxiliary socket programs return fixed values or self-tail-call through the program array. The main tests are independent BPF programs. Early cases directly return pointers, add/compare/negate pointers, pass stack or context pointers to helpers, corrupt pointer spills, and write pointer values to map values or context. Middle cases merge different pointer types through stack slots and then attempt context or socket access. Later cases check map pointer comparisons, frame pointer immutability, stack pointer arithmetic, and Spectre v1/v4 sanitizer behavior by asserting translated `nospec` placement under `SPEC_V1` and `SPEC_V4`.

## State and Persistence
Runtime persistent state is limited to map definitions and any transient map updates performed during verifier load/run tests. The primary state under test is verifier register and stack metadata: pointer provenance, reference ownership, spilled pointer classes, read_ok flags, scalar taint, and speculation barriers. Socket lookup tests acquire references and must release them on accepted paths.

## Dependencies and Integration Points
The suite depends on `linux/bpf.h`, libbpf helper macros, `../../../include/linux/filter.h` for raw instruction helpers, and `bpf_misc.h` annotation macros. It integrates with the verifier selftest harness that compiles each SEC program, loads it with privileged/unprivileged expectations, checks verifier log substrings, return values, and optionally translated instruction text.

## Risks
The tests are tightly coupled to exact verifier diagnostics and sanitizer output, so harmless verifier wording or code-generation changes can break expectations. Inline assembly intentionally creates unsafe patterns; any compiler, assembler, or macro change that rewrites instruction layout can invalidate the intended verifier paths. Socket reference tests are sensitive to release analysis and can change if kfunc/helper semantics evolve.

## Test Signals
Strong signals are the annotated `__success`/`__failure_unpriv` outcomes, expected `__msg`/`__msg_unpriv` strings such as pointer leak and stack corruption diagnostics, and `__xlated_unpriv` `nospec` assertions. The file is itself a verifier regression corpus rather than production datapath code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_unpriv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_unpriv_perf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_unpriv_perf.c

## Purpose
This small verifier test covers unprivileged pointer type consistency for perf-event context fields. It verifies that one load instruction cannot safely read from stack slots holding different pointer classes across branches.

## Important APIs, Types, and Functions
The single naked `SEC("perf_event")` program `fill_of_different_pointers_ldx` uses `struct bpf_perf_event_data` offsets, specifically `sample_period`, through `offsetof`. It depends on `bpf_misc.h` annotations and `linux/bpf.h`.

## Control Flow
The program conditionally stores either a frame-pointer-derived stack pointer or the perf-event context pointer into a common stack slot, reloads it, then reads a field as if it were a perf-event context. The test is annotated as verifier failure with `same insn cannot be used with different pointers`.

## State and Persistence
There is no persistent map or global state. The tested state is verifier tracking of a spilled stack slot whose possible values have incompatible pointer types.

## Dependencies and Integration Points
It integrates with the BPF verifier selftest harness and the perf-event program type. The test relies on kernel UAPI definitions for `struct bpf_perf_event_data`.

## Risks
The test is sensitive to exact verifier log wording and to any verifier enhancement that changes how merged pointer types are diagnosed. Because the code is inline assembly, instruction ordering must remain stable.

## Test Signals
Expected failure with the annotated message is the key signal. A load acceptance would indicate a regression in pointer provenance enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_unpriv_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value.c

## Purpose
This verifier suite tests map value pointer handling: use of cleared call registers, unaligned loads/stores under `BPF_F_ANY_ALIGNMENT`, and preservation of adjusted map value pointers across stack spilling.

## Important APIs, Types, and Functions
It defines `struct test_val { unsigned int index; int foo[MAX_ENTRIES]; }` and `map_hash_48b`, a hash map whose value is that structure. All programs use `bpf_map_lookup_elem`; test annotations from `bpf_misc.h` declare expected privileged and unprivileged outcomes.

## Control Flow
Each naked socket program initializes a stack key, looks up `map_hash_48b`, null-checks the returned value pointer, and then performs the operation under test. Cases store a cleared call register back into a map value, perform deliberately unaligned 64-bit accesses around adjusted map value offsets, and spill/reload an adjusted pointer to verify that verifier bounds and pointer identity are retained.

## State and Persistence
Runtime writes target map value memory, but persistence is incidental to verifier validation. The important state is verifier knowledge of map value bounds, pointer adjustment, stack spill metadata, and whether a pointer may be leaked to unprivileged code.

## Dependencies and Integration Points
The file integrates with libbpf skeleton-style map declarations and BPF verifier selftests. `offsetof(struct test_val, foo)` is passed as an immediate to validate adjusted access within the map value.

## Risks
Unaligned access behavior depends on `BPF_F_ANY_ALIGNMENT` and architecture/verifier policy. Unprivileged expectations include pointer leak diagnostics, so verifier error wording changes can affect tests.

## Test Signals
Signals include success for privileged unaligned/preserved pointer cases, `R1 !read_ok` for storing an unreadable cleared call register, and unprivileged pointer leak rejections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_adj_spill.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_adj_spill.c

## Purpose
This file narrows verifier coverage to map value pointer spill/fill behavior, especially whether `PTR_TO_MAP_VALUE` and `PTR_TO_MAP_VALUE_OR_NULL` states survive stack storage and reload correctly.

## Important APIs, Types, and Functions
It uses the same `struct test_val` and one-entry hash map pattern as nearby value tests. The two naked socket programs call `bpf_map_lookup_elem` and then use stack slots to spill/reload the returned pointer.

## Control Flow
`is_preserved_across_register_spilling` null-checks the lookup result, writes through it, spills it to stack, reloads into `r3`, and writes through the reloaded pointer. `is_marked_on_register_spilling` spills the nullable result before the null check, then after checking `r0` reloads from the stack and dereferences the copied pointer.

## State and Persistence
Map writes are secondary. The tested state is the verifier's stack spill record and ID propagation for nullable map value pointers through a null check.

## Dependencies and Integration Points
The programs are BPF verifier selftests using libbpf map declarations and `bpf_misc.h` annotations. They are loaded as socket programs by the verifier harness.

## Risks
Verifier state-ID and nullability logic is subtle; future verifier improvements may accept or reject with different diagnostics. Unprivileged rejections are tied to pointer-leak protection.

## Test Signals
Expected privileged success and unprivileged pointer-leak failure signal correct spill/fill tracking and conservative unprivileged policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_adj_spill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_illegal_alu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_illegal_alu.c

## Purpose
This verifier suite rejects illegal ALU operations on map value pointers, map pointers, and flow dissector `flow_keys` pointers, and validates reserved offset fields in raw ALU instructions.

## Important APIs, Types, and Functions
It defines `map_hash_48b` with `struct test_val` values and uses `bpf_map_lookup_elem`, `bpf_get_prandom_u32`, and raw instruction generation through `BPF_RAW_INSN` from `filter.h`. `DEFINE_BAD_OFFSET_TEST` emits raw ALU instructions with invalid offset fields.

## Control Flow
Lookup-based socket tests null-check a map value pointer and then apply invalid operations such as bitwise AND, 32-bit ALU on a pointer, division, endian conversion, lock-add corruption through stack, negating a map pointer, or pointer arithmetic before dereference. The flow dissector test takes a `flow_keys` pointer from `__sk_buff`, applies a random variable offset, and tries to read through it. Macro-generated tests load a raw ALU instruction and expect reserved-field rejection.

## State and Persistence
No intended persistent state exists. Map definitions provide pointer types; verifier state tracks whether ALU operations preserve pointer validity or turn a register into unsafe scalar data.

## Dependencies and Integration Points
The file integrates with socket and flow-dissector verifier program types. It relies on kernel instruction encoding helpers and exact verifier messages for illegal pointer arithmetic and reserved ALU fields.

## Risks
Because some tests encode raw instructions, changes to instruction validation or reserved offset semantics can shift expected outcomes. Exact diagnostic matching is brittle.

## Test Signals
Expected messages include `bitwise operator &= on pointer`, `32-bit pointer arithmetic prohibited`, `pointer arithmetic with /= operator`, `pointer arithmetic on flow_keys prohibited`, and `BPF_ALU uses reserved fields`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_illegal_alu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_or_null.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_or_null.c

## Purpose
This verifier test suite validates nullable map value pointer identity, null-check propagation, and rejection of arithmetic or unsafe access on `PTR_TO_MAP_VALUE_OR_NULL` values.

## Important APIs, Types, and Functions
It defines both `map_hash_48b` and `map_hash_8b`. Programs use `bpf_map_lookup_elem` and, in one state-frequency test, `bpf_ktime_get_ns`. Annotations declare success/failure outcomes across tc, socket, and cgroup/skb program types.

## Control Flow
The first test copies a lookup result to another register, null-checks one copy, and writes through the other to prove shared ID propagation. Several tests mutate the copied nullable pointer using add, bitwise AND, or shift before the null check and expect rejection. Other tests perform multiple lookup calls to show that a null check on one result does not validate an older independent result. Later cases test bounded map index logic from an else branch, branch prediction over contradictory null checks, and `regsafe()` behavior when two nullable map values may or may not share an ID.

## State and Persistence
Map values can be written, but persistent state is not the goal. The relevant state is verifier ID equivalence for nullable pointers, branch-derived nullability, and state merging under `BPF_F_TEST_STATE_FREQ`.

## Dependencies and Integration Points
The file integrates with the verifier harness through `bpf_misc.h` annotations and uses multiple program types to exercise type-specific verifier paths.

## Risks
Verifier ID propagation and state pruning behavior are complex and can change as verifier precision improves. Log messages and state-frequency behavior are particularly sensitive.

## Test Signals
Expected success for shared checked lookup copies, failure for arithmetic on nullable pointers, failure for stale unchecked lookup access, and failure in the `check_ids()`/`regsafe()` scenario are the core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_or_null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_ptr_arith.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_ptr_arith.c

## Purpose
This large verifier suite exercises arithmetic on map value pointers across constant and unknown scalar offsets, different maps with compatible/incompatible value shapes, lower and upper out-of-bounds cases, scalar/pointer state merging, and 32-bit packet pointer arithmetic.

## Important APIs, Types, and Functions
It declares `map_array_48b`, `map_hash_16b`, and `map_hash_48b` with different map types and value sizes. Programs use `bpf_map_lookup_elem`, `bpf_map_delete_elem`, `bpf_get_prandom_u32`, `errno` constants, and `__sk_buff` offsets for skb length and packet data/data_end.

## Control Flow
Early programs choose between maps based on skb length, load a value pointer, derive either constant or unknown scalar offsets from map content or random data, and add those offsets to the pointer. They test whether verifier can prove equal offsets or compatible map value properties across branches. Middle programs mix pointer and scalar alternatives through a common ALU instruction to verify unprivileged sanitization and nospec insertion. Further cases probe upper and lower out-of-bounds arithmetic, legal known offsets, known and unknown scalar additions/subtractions, pointer-plus-pointer and scalar-minus-pointer rejections, tainted destination leakage, and 32-bit ALU on packet pointers.

## State and Persistence
The maps are fixtures for pointer provenance and value-size information. Some tests write values, but the durable artifact is verifier state: pointer min/max bounds, map ID, fixed/variable offset, scalar range, and speculative-execution sanitization.

## Dependencies and Integration Points
This file is loaded by the verifier selftest framework as socket and tc programs. It depends on precise map BTF/type declarations, `bpf_misc.h` annotations, and `SPEC_V1`-conditioned translated instruction checks for nospec placement.

## Risks
The suite is sensitive to verifier range analysis improvements, especially when different maps share value layout. Error text for unprivileged arithmetic and out-of-range conditions is also brittle. Inline assembly sequences intentionally preserve specific branch shapes.

## Test Signals
Success on provably safe pointer+scalar cases, failure on negative minimum offsets, max outside value bounds, pointer-pointer arithmetic, and unprivileged mixed pointer/scalar arithmetic are the key signals. `__retval` checks validate accepted execution paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_ptr_arith.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_var_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_var_off.c

## Purpose
This verifier suite tests variable-offset access to contexts and stack memory, including privileged versus unprivileged policy, initialized stack ranges, out-of-bounds min/max checks, zero-sized helper accesses, and clobbering of spilled registers.

## Important APIs, Types, and Functions
It defines `map_hash_8b` for indirect helper calls and uses `bpf_map_lookup_elem`, `bpf_getsockopt`, and `bpf_probe_read_kernel`. Program types include lwt_in, cgroup/skb, socket, and sockops.

## Control Flow
The tests derive unknown offsets from context fields, mask them to small aligned ranges, add them to context or frame pointer bases, and then read, write, or pass them to helpers. Some tests initialize only part of the stack to verify what ranges are safe. The spill-clobber test writes through a variable stack pointer after spilling a map pointer and then reloads the slot, expecting the verifier to forget pointer provenance. Bounds tests deliberately create unbounded, max-out-of-bound, min-out-of-bound, and zero-sized out-of-bound accesses.

## State and Persistence
No persistent runtime state matters. The target state is verifier stack initialization metadata, variable offset ranges, maximum stack depth calculation, spilled register invalidation, and unprivileged variable-stack-access prohibition.

## Dependencies and Integration Points
The file is part of the verifier selftest corpus and depends on `bpf_misc.h` annotations, helper prototypes, and program-type-specific contexts such as `struct bpf_sock_ops`.

## Risks
Stack range analysis changes can affect success/failure outcomes. Some privileged tests intentionally allow reads from a range after variable writes, so overly conservative verifier changes would regress them. Diagnostic text is exact-match sensitive.

## Test Signals
Signals include `variable ctx access`, `variable stack access prohibited for !root`, `stack depth 16`, invalid variable-offset stack read/write messages, and invalid scalar dereference after spilled pointer clobbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_var_off.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_accept.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_accept.c

## Purpose
This LSM verifier acceptance suite checks valid use of VFS-related kfuncs and trusted pointer arguments, including acquiring and releasing task executable files and formatting paths.

## Important APIs, Types, and Functions
The file uses `bpf_get_task_exe_file`, `bpf_get_current_task_btf`, `bpf_put_file`, `bpf_path_d_path`, and `BPF_PROG` tracing wrappers. It declares a static `buf[64]` and uses kernel types `struct file`, `struct path`, `struct task_struct`, `struct inode`, and `struct dentry`.

## Control Flow
Accepted programs acquire a file reference from current task or task argument, null-check it, and release it. Path tests call `bpf_path_d_path` on a trusted path argument or on `&file->f_path`, which remains trusted despite being an embedded member with fixed offset. The inode rename test reads `new_dentry->d_inode`, checks for null, reads `i_ino`, and conditionally denies with `-EACCES`.

## State and Persistence
There is no persistent map state. Reference state is important: acquired `struct file *` references must be released with `bpf_put_file`. The static buffer is used only during helper calls.

## Dependencies and Integration Points
The programs are sleepable and non-sleepable LSM hooks using BTF typed arguments. They depend on `bpf_experimental.h` for kfunc declarations and on verifier trusted-pointer rules.

## Risks
VFS kfunc trust and reference rules are evolving APIs. Changes to which LSM hooks allow specific kfuncs, or to trusted embedded-member recognition, can alter acceptance.

## Test Signals
Every section is annotated `__success`; successful load proves trusted arguments, fixed-offset trusted member access, proper null checking, and reference release are accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_accept.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_reject.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_reject.c

## Purpose
This companion LSM verifier rejection suite validates that VFS kfuncs reject null, untrusted, wrongly typed, unreleased, unacquired, oversized, or disallowed-context arguments.

## Important APIs, Types, and Functions
It uses the same kfunc family as the acceptance file: `bpf_get_task_exe_file`, `bpf_put_file`, and `bpf_path_d_path`. It also uses `PATH_MAX` for an intentionally oversized buffer-size test and `BPF_PROG` for typed LSM/fentry signatures.

## Control Flow
Programs pass null or stack-cast task pointers to `bpf_get_task_exe_file`, walk from a trusted task to an untrusted parent, leak an acquired file reference, release an unacquired `struct file *`, pass null/untrusted/type-mismatched paths to `bpf_path_d_path`, supply a size larger than the static buffer, call an LSM-only kfunc from fentry, and dereference a nullable `d_inode` without a null check.

## State and Persistence
There is no map persistence. Reference ownership and trusted pointer provenance are the central verifier states.

## Dependencies and Integration Points
The file integrates with the verifier harness through exact `__failure` and `__msg` annotations. It relies on BTF type checking, kfunc argument annotations, and LSM hook restrictions.

## Risks
Changes in kfunc availability or verifier wording can cause expected-message failures. Type mismatch diagnostics are especially tied to BTF type names and argument numbering.

## Test Signals
Expected failures include null trusted-arg rejection, untrusted pointer rejection, unreleased reference, release of unacquired pointer, invalid map-value buffer access size, non-LSM kfunc rejection, and nullable trusted pointer dereference rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_vfs_reject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xadd.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xadd.c

## Purpose
This verifier suite tests atomic add (`lock *(...) +=`) alignment and operand preservation for stack, map value, and packet memory.

## Important APIs, Types, and Functions
It defines `map_hash_8b` and uses `bpf_map_lookup_elem`. Inline assembly emits 32-bit and 64-bit atomic add operations on stack slots, map value offsets, and XDP packet pointers.

## Control Flow
The first tests perform unaligned atomic add on stack offset `-7` and map offset `+3`, expecting verifier alignment failures. The XDP test bounds-checks packet data and then attempts atomic writes into packet memory, expecting rejection because atomic stores into packet pointers are not allowed. The final tests perform aligned stack atomics and verify that source and destination registers are not mangled, returning the expected accumulated value.

## State and Persistence
The map is only a typed memory target. Runtime state exists in stack slots and possible map values, but the primary verifier state is alignment, packet write class, and register preservation across atomic instructions.

## Dependencies and Integration Points
This file integrates with tc and XDP verifier selftests and uses `BPF_F_ANY_ALIGNMENT` where packet alignment policy is part of the test.

## Risks
Atomic instruction validation or diagnostic wording changes can break expected messages. Packet atomic policy must remain conservative for the negative test.

## Test Signals
Expected failure messages for misaligned stack/map access and forbidden packet atomic stores, plus return value `3` for register-preserving aligned xadd tests, are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xadd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp.c

## Purpose
This small verifier file checks basic XDP context access and use of `bpf_xdp_store_bytes` with data sourced from a read-only map.

## Important APIs, Types, and Functions
It declares `map_array_ro`, an array map with `BPF_F_RDONLY_PROG`, and uses `bpf_map_lookup_elem` and `bpf_xdp_store_bytes`. Programs read `struct xdp_md` fields including `ingress_ifindex`.

## Control Flow
`xdp_using_ifindex_from_netdev` reads `xdp_md.ingress_ifindex` and returns 1 if it is positive. `xdp_store_bytes_from_ro_map` looks up key 0 in the read-only map and, if present, writes 8 bytes from that map value into the packet at offset 0 using the XDP store helper.

## State and Persistence
The map stores the source bytes for `bpf_xdp_store_bytes`, but the programs do not update persistent state. Packet mutation through the helper is the runtime effect.

## Dependencies and Integration Points
The file is loaded by verifier tests for the XDP program type and depends on helper support for `bpf_xdp_store_bytes`.

## Risks
Helper availability and read-only map semantics are kernel-version dependent. Packet store bounds are enforced by the helper rather than explicit packet pointer checks.

## Test Signals
Both programs are annotated successful, with return values 1 and 0 respectively. Successful load validates ifindex field access and read-only map value use as helper input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp_direct_packet_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp_direct_packet_access.c

## Purpose
This large generated-style verifier suite validates direct XDP packet and metadata access bounds reasoning. It covers data/data_end and data_meta/data comparisons using all common relational operators, corner-case offsets, and intentionally good and bad loads.

## Important APIs, Types, and Functions
All tests are naked `SEC("xdp")` programs using inline assembly. They read `xdp_md.data`, `xdp_md.data_end`, and `xdp_md.data_meta` via `offsetof` immediates and then perform packet loads. `BPF_F_ANY_ALIGNMENT` appears because access alignment is not the focus.

## Control Flow
Each program loads a base pointer and bound pointer, adjusts the base by 6, 7, 8, or 9 bytes, branches with `>`, `<`, `>=`, `<=`, or reversed comparisons, and then performs a load from `base - N`. Good cases prove the accessed byte range is within `[data, data_end)` or `[data_meta, data)`. Bad cases either load too wide for the proven range or perform the load on an unproven branch. The first cases also reject arithmetic on `pkt_end` itself.

## State and Persistence
There is no persistent state. The verifier state under test is packet pointer range, fixed offset, known safe byte window, and separate tracking of packet data versus metadata regions.

## Dependencies and Integration Points
The file is part of the BPF verifier selftest corpus. It relies on exact `__success`/`__failure` annotations and expected messages such as pointer arithmetic on `pkt_end`, offset outside packet, or min/max outside allowed range.

## Risks
Any verifier range-analysis precision improvement or diagnostic rewrite may alter expected results. Because the suite uses many near-duplicate cases, accidental edits can create inconsistent coverage.

## Test Signals
The key signals are that exact corner cases at the proven boundary succeed, one-byte-short ranges fail, loads outside the checked branch fail, and pointer arithmetic on `data_end` is rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp_direct_packet_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/vrf_socket_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/vrf_socket_lookup.c

## Purpose
This functional BPF program tests socket lookup helpers from both tc and XDP contexts, including behavior under VRF/current-netns lookup and the choice between `bpf_sk_lookup_tcp` and `bpf_skc_lookup_tcp`.

## Important APIs, Types, and Functions
Globals `lookup_status`, `test_xdp`, and `tcp_skc` are controlled by userspace tests. `socket_lookup()` parses Ethernet and IPv4 headers, builds a `struct bpf_sock_tuple` view over IP addresses/ports, and calls `bpf_sk_lookup_tcp`, `bpf_skc_lookup_tcp`, or `bpf_sk_lookup_udp` with `BPF_F_CURRENT_NETNS`. Entry points are `tc_socket_lookup` and `xdp_socket_lookup`.

## Control Flow
Both entry points extract packet data pointers and gate execution on `test_xdp`. The shared parser validates Ethernet, IPv4, tuple bounds, and protocol. For TCP it chooses SKC or full socket lookup based on `tcp_skc`; for UDP it uses UDP lookup. It clears `lookup_status` before lookup and sets it to 1 only if a socket is found and released.

## State and Persistence
Persistent BSS globals expose test controls and outcome. Socket references returned by lookup helpers are released immediately with `bpf_sk_release`.

## Dependencies and Integration Points
The program integrates with network selftests that attach it at tc or XDP and then inspect global data. It depends on packet header definitions, endian helpers, and socket lookup helper availability.

## Risks
The tuple is formed by casting `&iph->saddr`, so layout assumptions must match IPv4 tuple layout. Missing release would leak references, but current code releases all non-null lookups.

## Test Signals
Userspace can toggle `test_xdp` and `tcp_skc`, send TCP/UDP IPv4 traffic, and observe `lookup_status` to confirm helper behavior in the selected hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/vrf_socket_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq.c

## Purpose
This BPF workqueue test validates successful `struct bpf_wq` use from array, hash, no-prealloc hash, and LRU maps, with both sleepable and non-sleepable callbacks.

## Important APIs, Types, and Functions
It defines map value types `struct hmap_elem` and `struct elem`, maps `hmap`, `hmap_malloc`, `array`, and `lru`, and global bitmasks `ok` and `ok_sleepable`. It uses experimental helpers `bpf_wq_init`, `bpf_wq_set_callback`, `bpf_wq_start`, plus test kfuncs `bpf_kfunc_common_test` and `bpf_kfunc_call_test_sleepable`.

## Control Flow
`test_elem_callback()` and `test_hmap_elem_callback()` initialize or look up a map value, locate its embedded workqueue, initialize it with the owning map, set the callback, and start it. Callback `wq_callback` marks `ok`; callback `wq_cb_sleepable` validates the key against `ok_offset`, calls a sleepable kfunc, and marks `ok_sleepable`. Several tc/syscall entry points test each map flavor with a unique key. `test_map_no_btf` attempts lookup of a missing key and only initializes if present.

## State and Persistence
Persistent state lives in maps containing embedded workqueue objects and in BSS bitmasks recording callback completion. Hash/LRU map updates create elements before workqueue initialization.

## Dependencies and Integration Points
The file depends on `bpf_experimental.h`, `bpf_misc.h`, and `bpf_testmod_kfunc.h`. It integrates with workqueue selftests that load programs, invoke entry points, and check callback side effects.

## Risks
Workqueue behavior is asynchronous; tests must account for callback timing. Correctness depends on the workqueue pointer being an embedded field in the map value and the map pointer matching that value. Sleepable callback support depends on kfunc and context rules.

## Test Signals
Entry points return negative error codes for setup failures. The strongest signals are zero return from setup programs and bit transitions in `ok`/`ok_sleepable` after callbacks run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq_failures.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq_failures.c

## Purpose
This verifier rejection suite checks invalid `struct bpf_wq` helper usage, including wrong map argument, mismatched owner map, invalid workqueue pointer, invalid offset, and non-constant workqueue offsets.

## Important APIs, Types, and Functions
It defines `struct elem { struct bpf_wq w; }`, array and LRU maps, callbacks `wq_callback` and `wq_cb_sleepable`, and uses `bpf_wq_init`, `bpf_wq_set_callback`, `bpf_get_prandom_u32`, plus test kfuncs.

## Control Flow
Each tc program looks up an array value and then intentionally violates a workqueue rule: passing `&key` instead of a map, initializing a workqueue from one map with another map, passing the address of the local workqueue pointer rather than the embedded field, adding offset 1 to the field, or computing the field address with an unknown offset. All are annotated verifier failures with anchor messages around the helper call.

## State and Persistence
There is no intended runtime persistence. Map declarations provide typed values for verifier pointer checks.

## Dependencies and Integration Points
The file integrates with the verifier selftest harness and depends on helper-specific verifier diagnostics for `bpf_wq_init` and `bpf_wq_set_callback`.

## Risks
Verifier diagnostics include map UID text and helper numbers, which can be brittle. Any change in workqueue helper contract or BTF field-offset validation can alter expectations.

## Test Signals
Expected failures include `pointer in R2 isn't map pointer`, workqueue/map UID mismatch, argument not pointing to map value, bad offset to `struct bpf_wq`, and non-constant offset rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq_failures.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_dummy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_dummy.c

## Purpose
This minimal XDP program is a pass-through fixture used by tests that only need a valid attachable XDP program.

## Important APIs, Types, and Functions
The single `SEC("xdp")` function `xdp_dummy_prog` takes `struct xdp_md *` and returns `XDP_PASS`. It declares GPL license metadata.

## Control Flow
There is no parsing or branching; every packet is passed to the network stack.

## State and Persistence
No maps, globals, or packet mutations are present.

## Dependencies and Integration Points
It depends on `linux/bpf.h` and `bpf_helpers.h` and integrates with any selftest needing a simple XDP attachment target.

## Risks
The main risk is not behavioral but fixture availability: attach failures would usually reflect environment or kernel support rather than this source.

## Test Signals
Successful load and attach are the only meaningful signals; runtime action is always `XDP_PASS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_features.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_features.c

## Purpose
This XDP feature test program validates different XDP actions and redirect paths using recognizable UDP echo packets exchanged between tester and device-under-test addresses.

## Important APIs, Types, and Functions
It defines stats maps `stats` and `dut_stats`, `cpu_map`, and `dev_map`, plus volatile config globals `tester_addr` and `dut_addr`. Helpers include `bpf_redirect_map`, tracepoint BPF_PROG wrappers, and atomic `__sync_add_and_fetch`. Shared helpers `xdp_process_echo_packet()` and `xdp_update_stats()` parse IPv4/IPv6 UDP packets carrying `CMD_ECHO` from `xdp_features.h`.

## Control Flow
Tester programs count TX/RX echo packets and pass them. DUT programs pass, drop, abort, TX by swapping Ethernet addresses, or redirect to CPUMAP/DEVMAP after validating the echo packet. Tracepoint programs for `xdp_exception` and `xdp_cpumap_kthread` increment DUT stats. The cpumap program swaps MAC addresses and redirects to a devmap.

## State and Persistence
Array maps persist counters. Volatile global addresses configure packet matching. Packet mutation occurs in TX and cpumap redirect paths through Ethernet MAC swaps.

## Dependencies and Integration Points
The program integrates with XDP feature selftests, CPUMAP/DEVMAP infrastructure, and BTF tracepoints. It depends on `xdp_features.h` for TLV command definitions and ports.

## Risks
Strict packet matching means unrelated packets are ignored or passed. The code assumes simple IPv4/IPv6 UDP without extension headers. Counters are updated atomically but are simple 32-bit values.

## Test Signals
Userspace should see expected stats increments in `stats`/`dut_stats` for pass/drop/aborted/tx/redirect paths and tracepoint activity for exceptions or cpumap processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_flowtable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_flowtable.c

## Purpose
This XDP fragments program tests `bpf_xdp_flow_lookup` kfunc integration by parsing IPv4/IPv6 TCP/UDP packets into a `bpf_fib_lookup` tuple and counting successful flowtable lookups.

## Important APIs, Types, and Functions
It declares local kfunc prototype `bpf_xdp_flow_lookup`, local options type `bpf_flowtable_opts___local`, and `stats` array map. Helpers validate IPv4 fragmentation/options/TTL and TCP FIN/RST state. Entry point is `xdp_flowtable_do_lookup`.

## Control Flow
The entry point parses Ethernet, dispatches IPv4 or IPv6, validates transport header bounds, filters out unsupported fragments, options, TTL/hop-limit exhaustion, and TCP FIN/RST. It fills `struct bpf_fib_lookup` fields including family, L4 protocol, addresses, ports, lengths, and ifindex, calls the kfunc, and increments `stats[0]` on a non-null result.

## State and Persistence
Persistent state is a single stats counter updated atomically. Packet data is read-only; no packet mutation or redirect occurs.

## Dependencies and Integration Points
It depends on BTF kfunc availability for flowtable lookup, XDP frags support, and kernel networking structs from `vmlinux.h`. Selftests populate flowtable state externally.

## Risks
The parser intentionally handles only direct transport headers and simple IPv4/IPv6. Unsupported extension headers, fragmentation, or TCP teardown packets are passed without lookup. Kfunc availability depends on kernel configuration.

## Test Signals
Successful flowtable hits increment `stats[0]`; all unsupported or miss cases return `XDP_PASS` without increment, while malformed Ethernet returns `XDP_DROP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_flowtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_hw_metadata.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_hw_metadata.c

## Purpose
This XDP fragments program collects hardware/software RX metadata for UDP port 9091 packets, stores it in XDP metadata space, and redirects matching packets to AF_XDP.

## Important APIs, Types, and Functions
It declares an `XSKMAP` named `xsk`, BSS counters `pkts_skip`, `pkts_fail`, and `pkts_redir`, and kfuncs `bpf_xdp_metadata_rx_timestamp`, `bpf_xdp_metadata_rx_hash`, and `bpf_xdp_metadata_rx_vlan_tag`. It uses `struct xdp_meta` and field flags from `xdp_metadata.h`.

## Control Flow
The `rx` program parses Ethernet with up to two VLAN tags, then IPv4/IPv6 UDP. Non-UDP or non-9091 packets increment skip and pass. Matching packets reserve metadata with `bpf_xdp_adjust_meta`, validate the metadata area, initialize `hint_valid`, write a TAI timestamp, attempt each metadata kfunc, set error fields or validity bits, increment redirect counter, and redirect to `xsk[rx_queue_index]`.

## State and Persistence
Persistent BSS counters track skipped, failed, and redirected packets. The XSK map persists AF_XDP socket bindings. Packet metadata is written before packet data and consumed by userspace.

## Dependencies and Integration Points
It integrates with AF_XDP hardware metadata selftests and driver support for XDP metadata kfuncs. It depends on `vmlinux.h`, `xdp_metadata.h`, endian helpers, and XDP frags support.

## Risks
Metadata kfuncs can fail depending on driver support; the code records errors but still redirects matching packets when metadata reservation succeeds. VLAN parsing is bounded but simple. Incorrect metadata size validation would corrupt packet data, but the code checks `meta + 1 > data`.

## Test Signals
Counters distinguish skip/fail/redirect paths, and userspace can inspect `struct xdp_meta` for timestamp/hash/VLAN validity bits and error codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_hw_metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata.c

## Purpose
This XDP metadata test redirects UDP port 8080 packets to AF_XDP after reserving custom metadata and populating RX timestamp, hash, and VLAN fields. It also provides a devmap redirect program.

## Important APIs, Types, and Functions
Maps are `xsk`, `prog_arr`, and `dev_map`. Kfuncs are `bpf_xdp_metadata_rx_timestamp`, `bpf_xdp_metadata_rx_hash`, and `bpf_xdp_metadata_rx_vlan_tag`. Entry points are `rx` and `redirect`.

## Control Flow
`rx` parses basic Ethernet IPv4/IPv6 UDP and passes non-UDP or non-8080 packets. For matches it calls `bpf_xdp_adjust_meta`, validates metadata space, writes metadata fields, substitutes timestamp 1 when veth returns zero, and redirects to `xsk[rx_queue_index]`. `redirect` redirects to `dev_map` by RX queue index.

## State and Persistence
Map state persists AF_XDP sockets, optional program-array entries, and devmap entries. Per-packet metadata is written transiently for userspace consumption.

## Dependencies and Integration Points
The program integrates with XDP metadata and AF_XDP tests. It depends on `xdp_metadata.h` layout shared with userspace and driver/kfunc support.

## Risks
Parser support is intentionally simple and does not handle VLANs here. Metadata kfunc return values are mostly ignored, so userspace must tolerate absent metadata except for the timestamp fallback behavior.

## Test Signals
Successful redirect to AF_XDP with a populated metadata prefix is the core signal; nonmatching packets pass and metadata adjustment failures drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata2.c

## Purpose
This freplace program tests that calling XDP metadata kfuncs from a replacement program attached to `rx` is safe and does not crash.

## Important APIs, Types, and Functions
It declares `bpf_xdp_metadata_rx_hash` as a kfunc and a global `called` counter. Entry point `freplace_rx` is placed in `SEC("freplace/rx")`.

## Control Flow
The replacement program initializes local hash/type variables, calls the metadata hash kfunc, increments `called`, and returns `XDP_PASS`.

## State and Persistence
Persistent state is the BSS `called` counter observed by userspace. No packet metadata or maps are modified.

## Dependencies and Integration Points
It integrates with freplace attachment to the `rx` program from the metadata test and depends on metadata kfunc availability in replacement context.

## Risks
The program intentionally ignores kfunc return value; it only validates safe invocation. Attachment target naming must match the original program.

## Test Signals
Userspace should observe `called` increment after packets execute the replacement path, and the load/attach should not fail due to metadata kfunc use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_map.c

## Purpose
This XDP program suite supports redirect-map tests by redirecting to fixed devmap entries, counting received IPv4 packets, and storing source MAC addresses.

## Important APIs, Types, and Functions
It declares `tx_port` devmap, `rxcnt` array counter map, and `rx_mac` array map. Entry points are `xdp_redirect_map_0/1/2`, `xdp_count_0/1/2`, and `store_mac_1/2`; helpers include `bpf_redirect_map`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, and `bpf_printk`.

## Control Flow
Redirect programs immediately redirect to a fixed devmap key. Counting programs validate Ethernet header bounds, increment per-key counters only for IPv4, and pass. MAC storage programs validate Ethernet, copy IPv4 source MAC into a 64-bit map value, log with `bpf_printk`, and pass.

## State and Persistence
Devmap entries are populated by userspace. `rxcnt` persists packet counts and `rx_mac` persists observed source MACs.

## Dependencies and Integration Points
It integrates with XDP redirect selftests that configure devmaps, attach different programs to devices, and inspect maps after traffic.

## Risks
Counters use non-atomic `*count += 1`; tests should avoid high-concurrency ambiguity. Only IPv4 packets affect counters/MAC storage.

## Test Signals
Successful redirects return XDP redirect actions via helper; map counters and stored MACs confirm traffic path and receiving interface behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_multi_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_multi_kern.c

## Purpose
This program tests multi-target XDP redirect behavior with devmap and devmap-hash, protocol-specific redirect flags, and second-stage devmap programs.

## Important APIs, Types, and Functions
Maps include `map_all` devmap, `map_egress` devmap-hash, `mac_map`, and `redirect_flags`. Entry points are `xdp_redirect_map_multi_prog`, `xdp_redirect_map_all_prog`, and `xdp_devmap_prog`. It uses `bpf_redirect_map` and `bpf_map_lookup_elem`.

## Control Flow
The main XDP program validates Ethernet bounds, reads EtherType, optionally reads redirect flags by protocol, and redirects IPv4 with broadcast/exclude-ingress defaults, IPv6 to ingress ifindex with default flags 0, and other protocols with broadcast default. The second XDP program redirects all packets through the devmap-hash. The devmap program runs on egress, looks up MAC by egress ifindex, and overwrites Ethernet source MAC if present.

## State and Persistence
Userspace populates devmaps, MAC map, and flags map. The devmap egress program mutates packet Ethernet source address.

## Dependencies and Integration Points
The file integrates with XDP redirect multi selftests and kernel devmap/devmap-hash infrastructure. It depends on devmap program attachment for `SEC("xdp/devmap")`.

## Risks
The code uses `bpf_htons(eth->h_proto)` into a host-order-looking protocol variable; behavior is tied to test expectations and endian macros. Missing map entries fall back to default flags or no MAC rewrite.

## Test Signals
Packet fanout/exclusion, protocol-specific flag override, and source-MAC rewrite on devmap egress are observable through traffic and map state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_multi_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_synproxy_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_synproxy_kern.c

## Purpose
This XDP/tc SYN proxy program implements SYN-cookie based TCP SYN flood protection for IPv4 and IPv6, using conntrack lookup to pass established flows and generating SYNACK packets for allowed ports.

## Important APIs, Types, and Functions
Maps are `values` for packed MSS/window-scale/TTL and SYNACK count, and `allowed_ports` for port allowlist. It declares conntrack kfuncs `bpf_xdp_ct_lookup`, `bpf_skb_ct_lookup`, and `bpf_ct_release`. Helpers/kfuncs include `bpf_tcp_raw_gen_syncookie_ipv4/ipv6`, `bpf_tcp_raw_check_syncookie_ipv4/ipv6`, `bpf_csum_diff`, `bpf_xdp_adjust_tail`, `bpf_skb_change_tail`, `bpf_redirect`, and `bpf_loop`.

## Control Flow
Packet processing starts in `syncookie_xdp` or `syncookie_tc`. `syncookie_part1` dissects Ethernet/IP/TCP, checks conntrack, rejects non-SYN/non-ACK unknown flows, and grows tail room to `TCP_MAXLEN`. `syncookie_part2` refreshes pointers after tail adjustment, validates TCP length, then dispatches SYNs to `syncookie_handle_syn` or ACKs to `syncookie_handle_ack`. SYN handling verifies checksums, checks allowed destination ports, generates a raw syncookie, parses timestamp/SACK/window-scale options with bounded `bpf_loop`, rewrites Ethernet/IP/TCP into a SYNACK, recalculates checksums, adjusts tail length, increments the SYNACK counter, and returns XDP_TX or tc redirect. ACK handling verifies the cookie and passes only valid ACKs.

## State and Persistence
Persistent state is in the `values` map and `allowed_ports` map. The SYNACK counter is incremented atomically at key 1. Packet state is heavily mutated for SYNACK generation, including MAC/IP/port swaps, TCP flags/options, sequence/ack numbers, checksums, and packet length.

## Dependencies and Integration Points
The program integrates with XDP and tc selftests for SYN proxy behavior and requires conntrack BPF kfuncs plus raw TCP syncookie helpers. It depends on `vmlinux.h`, `bpf_compiler.h`, endian helpers, and kernel networking definitions.

## Risks
The code intentionally does not support VLANs, IPv6 extension headers, or fragmented TCP in XDP, and comments identify those bypasses. It relies on verifier-sensitive constructs such as volatile pointers and bounded loops. Incorrect checksum or tail adjustment logic would drop or corrupt packets. Conntrack module configuration can affect kfunc availability.

## Test Signals
Allowed SYNs should produce SYNACK TX/redirect and increment the SYNACK counter, valid cookie ACKs should pass, established conntrack flows should pass, blocked ports/bad checksums/fragments should drop, and malformed verifier-sensitive paths should not fail load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_synproxy_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_tx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_tx.c

## Purpose
This minimal XDP fixture transmits every received packet back out the ingress device.

## Important APIs, Types, and Functions
The single `SEC("xdp")` entry point `xdp_tx` returns `XDP_TX`.

## Control Flow
No parsing or branching occurs; all packets take the XDP_TX action.

## State and Persistence
No maps, globals, or packet mutations are present.

## Dependencies and Integration Points
It depends only on BPF headers and is used by XDP tests requiring a simple TX action program.

## Risks
Runtime behavior depends on driver support for XDP_TX. Because no bounds checks are needed, source risk is minimal.

## Test Signals
Successful load/attach and observed packet reflection are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdping_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdping_kern.c

## Purpose
This XDP ping implementation supports a kernel-space ping client/server test by converting ICMP echo replies into subsequent requests on the client side and converting requests into replies on the server side.

## Important APIs, Types, and Functions
It defines `ping_map`, keyed by remote IPv4 address with `struct pinginfo` values from `xdping.h`. Helpers include `bpf_ktime_get_ns` and `bpf_csum_diff`. Internal helpers swap MACs, fold checksums, compute IPv4/ICMP checksum, and validate ICMP packet shape in `icmp_check`.

## Control Flow
`icmp_check` validates minimum packet length, IPv4 EtherType, ICMP protocol, expected payload length, and ICMP type. `xdping_client` accepts echo replies, looks up ping state, records elapsed time in the first empty slot, stops if count is complete, rewrites the packet into the next echo request with swapped MAC/IP addresses and incremented sequence, updates checksum and start time, and returns XDP_TX. `xdping_server` rewrites echo requests into replies and returns XDP_TX.

## State and Persistence
`ping_map` persists per-peer sequence, start time, count, and timing samples. Packets are mutated in place for source/destination MACs, IPv4 addresses, ICMP type, sequence, and checksum.

## Dependencies and Integration Points
It integrates with userspace xdping selftests that seed `ping_map` and inspect timings. It depends on fixed ICMP echo length and definitions from `xdping.h` and `bpf_compiler.h`.

## Risks
Only simple IPv4 ICMP packets with exact payload length are handled. The unrolled loop over timing slots is verifier-friendly but capped by `XDPING_MAX_COUNT`.

## Test Signals
Client-side map timing entries and continuing XDP_TX requests confirm progress; server-side reflected echo replies validate packet rewrite and checksum logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdping_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdpwall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdpwall.c

## Purpose
This XDP firewall/parser test inspects IPv6 and IPv6/GUE-encapsulated traffic, consults multiple maps for source IP and transport-port matches, and enforces a simple policy that only passes ICMPv6 and non-SYN TCP after filtering.

## Important APIs, Types, and Functions
Maps include IPv6 and IPv4 exact-match hash maps, IPv4 LPM trie, TCP port array, and UDP port array. Important structs are `pkt_info`, `fw_match_info`, `v4_lpm_key`, and `v4_lpm_val`. Helpers parse Ethernet, IPv6/GUE, TCP, UDP, and map-backed filters.

## Control Flow
`edgewall` parses Ethernet and drops non-IPv6. `parse_ipv6_gue` initializes outer IPv6 state and, for UDP destination 6666, `parse_gue_v6` switches to inner IPv4 or IPv6 headers and marks `TUNNEL`. ICMPv6 passes. Non-TCP/UDP drops. The program then records IP match metadata, computes the transport header by bounded offset, parses TCP/UDP, records port matches, and finally passes only TCP packets that are not pure SYN; everything else drops.

## State and Persistence
Persistent state lives in filter maps configured by userspace. The program does not update maps or mutate packets. `fw_match_info` is local and currently affects only the final decision via TCP/SYN status.

## Dependencies and Integration Points
It integrates with XDP verifier/runtime selftests and uses Linux network header definitions plus BPF map lookups. The LPM trie requires `BPF_F_NO_PREALLOC`.

## Risks
The policy is intentionally narrow: non-IPv6, malformed GUE, UDP, TCP SYN, and most unmatched cases drop. Offset is capped at 255, limiting parser depth. GUE detection uses a simple first-byte IP-version heuristic.

## Test Signals
Packet outcomes are the signal: ICMPv6 passes, established-style TCP ACK/RST passes, TCP SYN drops, malformed/unsupported traffic drops, and map lookups exercise exact and LPM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdpwall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xfrm_info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xfrm_info.c

## Purpose
This tc program tests BPF kfuncs for setting and retrieving XFRM metadata on skb contexts.

## Important APIs, Types, and Functions
It declares local `struct bpf_xfrm_info___local` with `if_id` and `link`, globals `req_if_id` and `resp_if_id`, and kfuncs `bpf_skb_set_xfrm_info` and `bpf_skb_get_xfrm_info`. Entry points are `set_xfrm_info` and `get_xfrm_info`.

## Control Flow
`set_xfrm_info` creates an info struct from `req_if_id`, calls the set kfunc, and returns `TC_ACT_SHOT` on failure or `TC_ACT_UNSPEC` on success. `get_xfrm_info` calls the get kfunc, drops on failure, stores returned `if_id` in `resp_if_id`, and otherwise leaves packet processing unspecified.

## State and Persistence
BSS globals persist requested and observed interface IDs for userspace assertions. XFRM metadata is attached to or read from the packet context.

## Dependencies and Integration Points
The file depends on BTF kfunc availability, tc program context, `bpf_tracing_net.h`, and XFRM-enabled kernel support. Userspace tests configure globals and inspect `resp_if_id`.

## Risks
Kfuncs are configuration and kernel-version dependent. The local struct must stay compatible with the kernel BTF layout under preserve-access-index expectations.

## Test Signals
Successful set/get should return `TC_ACT_UNSPEC` and copy the expected interface ID into `resp_if_id`; kfunc failures produce `TC_ACT_SHOT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xfrm_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xsk_xdp_progs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xsk_xdp_progs.c

## Purpose
This AF_XDP test program collection redirects packets to XSKMAP sockets and exercises drop behavior, custom metadata population, shared UMEM routing, and XDP tail adjustment.

## Important APIs, Types, and Functions
It declares XSKMAP `xsk`, static/global counters `idx`, `adjust_value`, and `count`, and uses `bpf_redirect_map`, `bpf_xdp_adjust_meta`, `bpf_xdp_get_buff_len`, `bpf_xdp_adjust_tail`, and `bpf_xdp_store_bytes`. Metadata layout comes from `xsk_xdp_common.h`.

## Control Flow
`xsk_def_prog` redirects all packets to socket 0. `xsk_xdp_drop` drops every other packet using a static counter. `xsk_xdp_populate_metadata` reserves metadata, validates it, writes incrementing `count`, and redirects. `xsk_xdp_shared_umem` parses Ethernet, chooses socket index from the last destination MAC byte divided by two, validates it, and redirects. `xsk_xdp_adjust_tail` records current length, adjusts tail by `adjust_value`, handles `-EOPNOTSUPP` specially by writing it back to the global, validates new length, optionally writes a sequence number near the new packet end, and redirects.

## State and Persistence
Persistent state includes XSKMAP bindings, global `adjust_value`, static drop index, selected `idx`, and `count`. Packet metadata and tail bytes are modified in specific programs.

## Dependencies and Integration Points
It integrates with AF_XDP/xsk selftests and shared UMEM tests. It depends on XDP frags support for most entry points and shared definitions such as `MAX_SOCKETS` and `PKT_HDR_ALIGN`.

## Risks
Socket index bounds depend on `MAX_SOCKETS`; if the computed index equals the map max it may rely on helper fallback action. Tail adjustment support varies by driver and frame mode, hence the explicit `-EOPNOTSUPP` path.

## Test Signals
Userspace observes redirect/drop cadence, metadata counts, selected socket routing by destination MAC, `adjust_value` updates on unsupported tail adjustment, and final packet length/sequence marker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xsk_xdp_progs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt-config.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt-config.h

## Purpose
This generated configuration header tells `sdt.h` whether the assembler supports autogrouping with `?` in `.pushsection` directives.

## Important APIs, Types, and Functions
It defines a single macro, `_SDT_ASM_SECTION_AUTOGROUP_SUPPORT`, set to `1`.

## Control Flow
There is no runtime control flow. The macro is consumed at preprocessing time by SDT macro generation.

## State and Persistence
No runtime state exists. The macro affects emitted assembly section attributes for compiled objects.

## Dependencies and Integration Points
It is included by `sdt.h`, which uses the value to choose `_SDT_ASM_AUTOGROUP`.

## Risks
If the configured value does not match assembler capabilities, generated SystemTap note sections may fail to assemble or may not group correctly with COMDAT sections.

## Test Signals
Successful compilation of code including `sdt.h` is the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt.h

## Purpose
This public-domain SystemTap static probe header defines `STAP_PROBE*`, `DTRACE_PROBE*`, and assembly probe macros that emit NOP probe sites plus `.note.stapsdt` metadata describing provider, probe name, semaphore, and argument locations.

## Important APIs, Types, and Functions
Public macros include `STAP_PROBE`, `STAP_PROBE1` through `STAP_PROBE12`, optional `STAP_PROBEV`, `STAP_PROBE_ASM`, `STAP_PROBE_ASM_TEMPLATE`, `STAP_PROBE_ASM_OPERANDS`, and DTrace-compatible aliases. Internal macros format argument size/sign/type, choose constraints (`STAP_SDT_ARG_CONSTRAINT`), emit `.note.stapsdt`, emit `.stapsdt.base`, and optionally include semaphore addresses.

## Control Flow
For C/C++, `STAP_PROBEn` expands to inline assembly that references optional semaphores, emits a probe NOP and note section, then emits the base section. For assembler use, `_SDT_PROBE` emits similar assembly directly. Argument handling computes signedness and size via C++ templates or C builtins and encodes operand templates selected by architecture-specific macros.

## State and Persistence
No runtime mutable state is required unless `_SDT_HAS_SEMAPHORES` is defined, in which case semaphore symbols are referenced. The persistent artifact is ELF note metadata and probe-site NOP instructions in compiled objects.

## Dependencies and Integration Points
It includes `sdt-config.h` and integrates with SystemTap, GDB, and DTrace-compatible tooling that reads `.note.stapsdt`. It depends on GNU inline assembly features, assembler section support, compiler constraints, and architecture-specific register naming behavior.

## Risks
The macros are compiler/assembler-sensitive. Operand constraints can fail for complex argument lists, register alias notes may require consumer heuristics, and incorrect autogroup support can break C++ COMDAT scenarios. C99 support is needed for variadic assembly probe helpers.

## Test Signals
Compilation of probe users, presence of `.note.stapsdt` and `.stapsdt.base` sections, and consumer tools discovering provider/probe/argument metadata are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.c

## Purpose
This userspace helper file provides small functions for selftests to change sysctl files while optionally recording the previous value and reporting failures through the test harness.

## Important APIs, Types, and Functions
`sysctl_set()` opens a sysctl path with `fopen(path, "r+")`, optionally reads the old value with `fscanf`, compares it to the requested value, seeks to the start, and writes the new value with `fprintf`. `sysctl_set_or_fail()` wraps it and calls `PRINT_FAIL` from `test_progs.h` on error.

## Control Flow
`sysctl_set` returns `-errno` if open or write fails, `-ENOENT` if old-value reading fails, otherwise 0. It avoids writing when `old_val` is provided and already equals `new_val`. `sysctl_set_or_fail` propagates the error after logging a formatted message.

## State and Persistence
The helper mutates kernel sysctl files, so state persists outside the process until tests restore old values. If `old_val` is supplied, the caller can preserve prior configuration for cleanup.

## Dependencies and Integration Points
It depends on C stdio/errno/string APIs, local `sysctl_helpers.h`, and `test_progs.h` for reporting. It is linked into userspace BPF selftest binaries.

## Risks
The read uses `%s`, so values containing whitespace are not preserved fully. The function does not truncate after writing shorter values unless sysctl semantics handle it. Callers must restore old settings to avoid cross-test contamination.

## Test Signals
Return 0 indicates the sysctl is open and set or already correct. Nonzero return plus `PRINT_FAIL` from the wrapper signals setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.h

## Purpose
This header exposes the sysctl helper API for BPF userspace selftests.

## Important APIs, Types, and Functions
It declares `int sysctl_set(const char *sysctl_path, char *old_val, const char *new_val);` and `int sysctl_set_or_fail(const char *sysctl_path, char *old_val, const char *new_val);`.

## Control Flow
The header has only include guards and declarations; behavior is implemented in `sysctl_helpers.c`.

## State and Persistence
No state is defined in the header. Callers use the API to mutate sysctl filesystem state.

## Dependencies and Integration Points
It is included by userspace selftests that need temporary sysctl changes and links with `sysctl_helpers.c`.

## Risks
ABI is a simple C declaration contract; mismatched implementation signatures would break builds. Callers must understand that `old_val` is an output buffer.

## Test Signals
Compilation and linkage against the helper implementation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sysctl_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/task_local_storage_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/task_local_storage_helpers.h

## Purpose
This userspace helper header provides a portable inline wrapper for the `pidfd_open` syscall used by task local storage selftests.

## Important APIs, Types, and Functions
It conditionally defines `__NR_pidfd_open` as 544 on alpha or 434 otherwise when libc headers lack it, and defines `static inline int sys_pidfd_open(pid_t pid, unsigned int flags)`.

## Control Flow
The wrapper directly calls `syscall(__NR_pidfd_open, pid, flags)` and returns the kernel result.

## State and Persistence
No persistent state is held. Successful calls return a pidfd file descriptor owned by the caller.

## Dependencies and Integration Points
It includes `unistd.h`, `sys/syscall.h`, and `sys/types.h`. It is used by userspace BPF selftests that need pidfds on systems whose libc may not expose the syscall number.

## Risks
Hard-coded syscall numbers must match architecture; the header handles alpha specially and assumes 434 for others. Callers must close returned fds.

## Test Signals
Successful compilation on older headers and successful pidfd creation at runtime indicate the helper is working.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/task_local_storage_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_bpftool_build.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_bpftool_build.sh

## Purpose
This shell selftest verifies that bpftool can be built through several supported make entry points and output-directory modes from the kernel tree.

## Important APIs, Types, and Functions
The script supports `-h|--help` and forwards all other arguments to make as `J`, typically `-j`. Helper functions are `return_value` for cleanup and exit, `check` for locating an executable `bpftool`, `make_and_clean` for in-tree builds, and `make_with_tmpdir` for `OUTPUT`/`O` builds in a temporary directory.

## Control Flow
The script computes the kernel root relative to its own path, skips with KSFT code 4 if bpftool sources are absent, traps exit for tempdir cleanup, and then tries builds through top-level kbuild, `tools/bpf/bpftool`, `tools/`, and the bpftool directory. Unsupported `OUTPUT` combinations are printed as skips. Any failed make or missing binary sets `ERROR=1`, but the script continues through remaining cases before exiting with accumulated status.

## State and Persistence
It creates temporary directories with `mktemp -d`, removes them after checks, and runs `make clean` in build directories. It mutates build outputs transiently in the kernel tree or temp output roots.

## Dependencies and Integration Points
It depends on bash, GNU make, `realpath`, `find`, kernel source layout, and bpftool Makefiles. It integrates with kselftest through skip exit code 4 and human-readable build logs.

## Risks
Running `make clean` affects build artifacts under the tested directories. The script assumes it is launched from a location where `realpath --relative-to=$PWD $0` resolves under `tools/testing/selftests/bpf`. Unsupported output modes are explicitly skipped.

## Test Signals
For each attempted build, the script prints the command and expects an executable named `bpftool` under the relevant output directory. Final exit status is nonzero if any attempted build failed or no binary was found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_bpftool_build.sh -->
