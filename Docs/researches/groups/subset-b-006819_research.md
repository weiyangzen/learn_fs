# subset-b-006819 grouped research

This grouped report covers the requested BPF verifier selftest sources under `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs`. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_runtime_jit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_runtime_jit.c

## Purpose
`verifier_runtime_jit.c` is a BPF verifier/JIT selftest fixture converted from the older verifier runtime JIT test set. It validates runtime tail-call behavior for socket programs, especially how prog-array maps, tail-call target selection, fallback execution, loop limits, and map pointer provenance behave once programs are JITed and executed. The source is not a Ceph runtime component; it is kernel selftest input compiled into BPF object code and consumed by the BPF test harness.

## Important APIs, Types, and Functions
The file defines two `BPF_MAP_TYPE_PROG_ARRAY` maps, `map_prog1_socket` and `map_prog2_socket`, using libbpf CO-RE style map declaration macros such as `__uint`, `__array`, and `SEC(".maps")`. The maps are pre-populated with auxiliary socket programs: `dummy_prog_42_socket`, `dummy_prog_24_socket`, `dummy_prog_loop1_socket`, and `dummy_prog_loop2_socket`. Each test program is `__naked` and uses inline BPF assembly so the instruction stream is exact. The central helper dependency is `bpf_tail_call`, referenced with `__imm(bpf_tail_call)`, and the branch tests also use `offsetof(struct __sk_buff, cb[0])` through `__imm_const`.

## Control Flow
Auxiliary programs either return fixed values or tail-call back through one of the prog arrays before returning 41 on fallback. Test entrypoints set `r2` to a prog-array map pointer and `r3` to a tail-call key, call `bpf_tail_call`, then return a fallback value if the tail call does not transfer control. The branch variants write to and read from `__sk_buff->cb[0]` to make verifier-visible paths that choose different map/key combinations. The out-of-bounds, negative-index, and wider-than-32-bit index cases assert fallback or architecture-specific behavior.

## State and Persistence
Persistent state is limited to the two prog-array map definitions and their static initial `values` arrays. There is no file or network persistence. Runtime state is verifier state and tail-call counter state: the fixture expects loop prevention and counter semantics to keep recursive tail calls bounded.

## Dependencies and Integration Points
The file depends on `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `bpf_misc.h`, libbpf section annotations, and the selftest loader that understands `__description`, `__success`, `__success_unpriv`, `__failure_unpriv`, `__msg_unpriv`, and `__retval`. It integrates with socket program execution and the verifier's unprivileged restrictions around map pointer abuse.

## Risks and Test Signals
Key risks are verifier/JIT regressions that let a non-prog-array map pointer reach `bpf_tail_call`, mishandle high or negative indices, or fail to preserve branch-specific map pointer identity. Test signals are explicit return contracts: valid calls return 42 or 24 from auxiliary programs, loops fall back to 41, missing or invalid targets fall back to 1 or 2, and unprivileged execution rejects different-map branch cases with `tail_call abusing map_ptr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_runtime_jit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_scalar_ids.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_scalar_ids.c

## Purpose
`verifier_scalar_ids.c` is a focused BPF verifier precision and state-equivalence test suite for scalar IDs. It checks when copied scalar registers share IDs, how range information and precision marks propagate across linked scalar values, how stack-spilled scalar IDs are tracked, and how verifier state pruning compares scalar IDs safely.

## Important APIs, Types, and Functions
The file uses raw socket-section BPF programs, mostly `__naked` inline assembly, with expected verifier log fragments captured by `__msg`. Helper calls to `bpf_ktime_get_ns` and `bpf_get_prandom_u32` create unknown scalars and unpredictable branches. Static subprograms such as `precision_many_frames__foo`, `precision_many_frames__bar`, and `precision_stack__foo` create multi-frame call graphs for precision backtracking. Macros from `bpf_misc.h` provide `__log_level(2)`, `BPF_F_TEST_STATE_FREQ`, `BPF_F_TEST_RND_HI32`, `__xlated`, and success/failure annotations.

## Control Flow
The tests copy helper-returned scalars among registers, perform conditional jumps that propagate bounds, then force precision by using a scalar as a pointer offset from `r10`. Multi-frame tests pass linked IDs through subprogram calls and stack slots, then force precision in callees to verify backtracking into caller frames. Other cases intentionally break ID links, create too many linked registers, test conditional jumps that should not trigger linked precision propagation, and check whether cached verifier states compare unique and nil IDs correctly.

## State and Persistence
No persistent runtime state is stored outside verifier state. The meaningful state is abstract verifier metadata: scalar ID, range bounds, subregister definition, stack slot ID, parent-state chain, and liveness. Stack writes and reads are deliberately used as verifier state carriers.

## Dependencies and Integration Points
The file depends on the verifier's scalar ID implementation, precision backtracking, state pruning, and subregister zero-extension tracking. It integrates with the BPF selftest harness via verifier log matching and translated-instruction expectations. Architecture-sensitive subregister behavior is guarded through `__xlated` expectations.

## Risks and Test Signals
Regression risks include unsound pruning of states with incompatible scalar IDs, lost precision across calls or stack spills, false propagation after broken links, and loss of `subreg_def` metadata under range propagation. Test signals include expected `mark_precise` log paths, deliberate failures such as `div by zero` and `register with unbounded min value`, processed-instruction counts showing pruning behavior, and `BPF_F_TEST_RND_HI32` checks that upper-half randomization is not inserted incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_scalar_ids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sdiv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sdiv.c

## Purpose
`verifier_sdiv.c` validates signed BPF division and modulo instructions for 32-bit and 64-bit operands. It covers immediate and register divisors, positive and negative signs, zero divisors, `INT_MIN`/`LLONG_MIN` overflow with `-1`, and x86 translation rewrites for safe overflow handling.

## Important APIs, Types, and Functions
The file is conditionally compiled for architectures and compiler versions that support CPU v4 signed division/modulo syntax in inline assembly. It uses `<limits.h>` for `INT_MIN` and `LLONG_MIN`, `SEC("socket")` BPF program sections, `__naked` exact assembly, and `__retval` contracts. x86-specific tests include `__arch_x86_64` and multiple `__xlated` expectations to validate verifier/JIT lowering. If the architecture, JIT, or Clang version is unsupported, a dummy successful socket test is emitted instead.

## Control Flow
Most programs are tiny straight-line arithmetic fixtures: load constants into `w0` or `r0`, perform `s/=` or `s%=` with either an immediate or another register, then exit. Zero-divisor tests initialize a divisor register to zero and verify the defined BPF result semantics. Overflow tests preserve the original dividend, execute signed division or modulo by `-1`, and compare or return the result to assert the verifier's rewrite behavior.

## State and Persistence
The file has no persistent maps or external state. State exists only in BPF registers and in compile-time test metadata. The signed arithmetic semantics are deterministic for each program, so return values and translated instruction sequences are the persistence-like contract for regression detection.

## Dependencies and Integration Points
Dependencies include the BPF assembler accepted by Clang, target architecture feature macros, libbpf helper macros, and verifier support for signed ALU operations. It integrates directly with the selftest runner through pass/fail metadata, return-value execution, unprivileged success markers for many simple cases, and translated instruction matching.

## Risks and Test Signals
Risks are high for arithmetic edge cases because C-like signed division overflow is undefined on many platforms while BPF must define verifier and JIT behavior. Incorrect rewrites could return wrong values, trap, or diverge between interpreter and JIT. Test signals include exact `__retval` values for sign rounding toward zero, zero-divisor behavior, modulo sign rules, overflow preservation for min-int divided by `-1`, and `__xlated` sequences that show inserted checks around divisor `-1` and zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sdiv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_search_pruning.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_search_pruning.c

## Purpose
`verifier_search_pruning.c` tests verifier state pruning, liveness screening, parent-chain preservation, precision tracking, and bounded search behavior. The fixtures are designed to catch cases where the verifier incorrectly treats two states as equivalent and skips a branch that should still be checked.

## Important APIs, Types, and Functions
The file declares `struct test_val`, `map_hash_48b`, and `map_hash_8b` hash maps. It uses helpers `bpf_map_lookup_elem`, `bpf_ktime_get_ns`, and `bpf_get_prandom_u32`, exact inline assembly, and low-level filter instruction encoding via `BPF_JMP_IMM` for the short-loop stress case. Test annotations include `BPF_F_ANY_ALIGNMENT`, `BPF_F_TEST_STATE_FREQ`, `__failure_unpriv`, `__msg_unpriv`, and log-level matching.

## Control Flow
Pointer/scalar confusion tests merge a stack pointer path with a scalar-loaded map value path and check that privileged and unprivileged return leakage behavior is correct. Branch coverage tests use map values and random helper calls to create pruning points before invalid memory or stack accesses. Precision tests spill 32-bit values and reload them as 32- or 64-bit values so the verifier must avoid assuming stale precision. The final kprobe case builds a small backward loop that should be rejected as too large rather than taking excessive verification time.

## State and Persistence
Persistent state is limited to two hash map definitions used as verifier-visible map-value sources. The important mutable state is verifier abstract state: pointer type versus scalar type, initialized stack bytes, precision marks, branch parent chains, and allocated stack tracking.

## Dependencies and Integration Points
The source integrates with socket, lwt, tracepoint, and kprobe program-type verifier rules. It depends on stack initialization policy differences between privileged and unprivileged modes and on the selftest runner's ability to match failure messages such as `R0 unbounded memory access`, `invalid read from stack`, and `BPF program is too large`.

## Risks and Test Signals
The primary risk is unsound pruning: a verifier bug could accept pointer leaks, skip invalid branches, or lose initialized-stack provenance after partial writes. Performance risk is also covered by the loop test, which guards against unbounded verifier exploration. Strong test signals are explicit expected failures, unprivileged-only failures, processed-instruction counts, forced checkpointing with `BPF_F_TEST_STATE_FREQ`, and branch-specific verifier messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_search_pruning.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sock.c

## Purpose
`verifier_sock.c` is a broad verifier fixture for socket-related pointer types, helper return types, reference ownership, context field access, packet pointer invalidation, and tail-call side effects. It tests `bpf_sock`, `bpf_tcp_sock`, socket maps, reuseport maps, XSK maps, socket local storage, and packet/XDP contexts.

## Important APIs, Types, and Functions
The file uses `vmlinux.h` types, map declarations for `BPF_MAP_TYPE_REUSEPORT_SOCKARRAY`, `BPF_MAP_TYPE_SOCKHASH`, `BPF_MAP_TYPE_SOCKMAP`, `BPF_MAP_TYPE_XSKMAP`, `BPF_MAP_TYPE_SK_STORAGE`, and `BPF_MAP_TYPE_PROG_ARRAY`. It exercises helpers such as `bpf_sk_fullsock`, `bpf_tcp_sock`, `bpf_sk_release`, `bpf_sk_storage_get`, `bpf_map_lookup_elem`, `bpf_sk_select_reuseport`, `bpf_skc_to_tcp_sock`, `bpf_skc_to_tcp_request_sock`, `bpf_skb_pull_data`, `bpf_xdp_pull_data`, and `bpf_tail_call_static`.

## Control Flow
Early cgroup/skb tests inspect `skb->sk` and verify required null checks before dereferencing or converting to fullsock/tcp_sock types. Middle sections validate allowed and forbidden field offsets, narrow loads, and access past field boundaries. TC, XDP, sk_skb, reuseport, cgroup post-bind, and sock-create sections test helper availability and context-field restrictions. Later global functions call pull-data helpers or static tail calls, then the caller dereferences stale packet pointers to confirm invalidation reaches across global calls and tail-call paths.

## State and Persistence
Persistent state is map-based and verifier-visible: socket maps can return referenced socket pointers; sk-storage values include a spin lock in `struct val`; the prog array supports static tail-call tests. Reference state is critical because sockmap lookups must be released with `bpf_sk_release`.

## Dependencies and Integration Points
The file integrates many BPF program types: `cgroup/skb`, `tc`, `xdp`, `sk_skb`, `sk_reuseport`, `cgroup/post_bind4`, `cgroup/post_bind6`, and `cgroup/sock_create`. It depends on BTF/vmlinux field offsets, helper prototypes, and verifier-specific pointer classes like `sock_common_or_null`, `sock_or_null`, `tcp_sock_or_null`, packet pointers, and map-value pointers.

## Risks and Test Signals
Risks include allowing null socket dereferences, exposing fields not valid for a program type, leaking socket references, failing to reject invalid map/helper combinations, or missing packet pointer invalidation after helpers and tail calls. Test signals include verifier errors such as `invalid mem access`, `invalid sock access`, `invalid tcp_sock access`, `R1 must be referenced when passed to release function`, `Unreleased reference`, and success cases that return zero after properly checked dereferences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sock_addr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sock_addr.c

## Purpose
`verifier_sock_addr.c` validates allowed return ranges for cgroup socket-address program types. It covers IPv4, IPv6, and Unix variants for recvmsg, sendmsg, getpeername, getsockname, bind, and connect hooks.

## Important APIs, Types, and Functions
Each function is a simple C BPF program taking `struct bpf_sock_addr *ctx` and returning a constant. The file includes `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf_sockopt_helpers.h>`, and `bpf_misc.h`. The annotations are the main API: `SEC("cgroup/...")`, `__success`, `__failure`, and `__msg` encode the verifier contract for each hook's allowed return interval.

## Control Flow
Control flow is intentionally straight-line. For recvmsg and getname hooks, success cases return 1 while bad cases return 0, expecting the verifier to require exactly `[1, 1]`. For sendmsg and connect hooks, valid cases return 0 or 1 and invalid cases return 2, expecting `[0, 1]`. For bind hooks, valid cases return 0 through 3 and invalid cases return 4, expecting `[0, 3]`.

## State and Persistence
There is no map state, stack state beyond the function frame, or persistent behavior. The `ctx` parameter is unused in all tests. The only meaningful state is the verifier's exit-register range tracking for `R0`.

## Dependencies and Integration Points
The file integrates with cgroup socket-address verifier policy. It depends on the kernel verifier assigning hook-specific return constraints and the test runner matching errors such as `At program exit the register R0 has smin=... should have been in [...]`.

## Risks and Test Signals
The main risk is accepting an invalid action code for a cgroup hook or rejecting a valid one, which would break program-type semantics for bind/connect/message hooks. Test signals are simple and strong: a successful load for every valid boundary value, and deterministic verifier rejection for one out-of-range return per hook family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sock_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sockmap_mutate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sockmap_mutate.c

## Purpose
`verifier_sockmap_mutate.c` tests which program types may delete from, update, look up, and mutate `sockmap` and `sockhash` maps. It focuses on helper availability and context restrictions for socket-map mutation.

## Important APIs, Types, and Functions
The file declares `sockhash` as `BPF_MAP_TYPE_SOCKHASH` and `sockmap` as `BPF_MAP_TYPE_SOCKMAP`, both keyed by `__u32` and holding `__u64` values. Helpers include `bpf_map_delete_elem`, `bpf_map_update_elem`, `bpf_map_lookup_elem`, `bpf_sk_release`, `bpf_sock_map_update`, and `bpf_sock_hash_update`. Inline helper wrappers such as `test_sockmap_delete`, `test_sockmap_update`, `test_sockmap_lookup_and_update`, `test_sockmap_mutate`, and `test_sockmap_lookup_and_mutate` are reused across program types.

## Control Flow
The action/classifier/socket/XDP/sk_lookup/sk_reuseport paths call delete or update helper wrappers and return success values. Flow dissector and raw tracepoint cases deliberately use mutation or release patterns that should be rejected in some contexts. Sockops includes separate delete, generic update, and dedicated `bpf_sock_map_update`/`bpf_sock_hash_update` paths to distinguish generic map update restrictions from sockops-specific update helpers.

## State and Persistence
State is held in the two socket maps. Some helper paths look up a socket pointer from the map and release it, so reference lifetime is part of the verifier state. There is no external persistence beyond map contents at runtime.

## Dependencies and Integration Points
The file integrates with many program sections: `action`, `classifier`, `flow_dissector`, `iter/sockmap`, `raw_tp/kfree`, `sk_lookup`, `sk_reuseport`, `socket`, `sockops`, and `xdp`. It depends on helper allowlists per program type and verifier reference tracking for `struct bpf_sock *`.

## Risks and Test Signals
Risks include allowing sockmap mutation from unsafe contexts, disallowing supported contexts, or failing to enforce `bpf_sk_release` availability. Expected failure messages include `program of this type cannot use helper bpf_sk_release` and `cannot update sockmap in this context`. Success cases prove that deletes and updates remain permitted in intended hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sockmap_mutate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_spill_fill.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_spill_fill.c

## Purpose
`verifier_spill_fill.c` is a large verifier fixture for stack spill/fill behavior. It validates pointer spills, scalar spills of different widths, partial overwrites, stack byte initialization, precision tracking through stack slots, unprivileged stack restrictions, and ID/range preservation after fills.

## Important APIs, Types, and Functions
The file declares a ring buffer map and small `.data` buffers used as map-value targets for pointer-offset tests. It uses helpers `bpf_ringbuf_reserve`, `bpf_ringbuf_submit`, `bpf_get_prandom_u32`, and `bpf_ktime_get_ns`. Program sections include `socket`, `tc`, `xdp`, and `raw_tp`. Important annotations include `BPF_F_ANY_ALIGNMENT`, `BPF_F_TEST_STATE_FREQ`, `__log_level(2)`, privileged/unprivileged split expectations, and precise `mark_precise` log fragments.

## Control Flow
Early tests spill and reload valid pointers, skb fields, and ring-buffer memory, then corrupt spilled pointer bytes to distinguish privileged pointer leakage from unprivileged rejection. TC/XDP tests spill bounded and unbounded scalars at different widths and reuse them as packet or ctx offsets. Raw tracepoint tests inspect stack slot byte masks and precision backtracking for 8-, 32-, and 64-bit accesses. Later socket tests exercise narrow writes over 64-bit slots, conditional stack initialization, and stack behavior under the no-perfmon unprivileged model.

## State and Persistence
Persistent state is limited to declared maps and `.data` buffers. The important state is stack-slot metadata: initialized bytes, spilled pointer class, scalar ID, range bounds, precision, and whether partial writes should invalidate or preserve the original spill. Ringbuf reservation also introduces nullable pointer state that must be checked and submitted correctly.

## Dependencies and Integration Points
The file integrates with verifier stack modeling, packet pointer arithmetic, XDP context pointer rules, ringbuf pointer rules, map-value bounds, and unprivileged verifier policy. The selftest runner validates both load outcomes and detailed verifier logs.

## Risks and Test Signals
Risks include pointer leaks through corrupted spills, unsafe acceptance of partially initialized stack reads, stale scalar IDs after width-changing fills, and invalid packet/context pointer arithmetic. Test signals include expected verifier errors such as `attempt to corrupt spilled`, `invalid read from stack`, `math between pkt pointer and register with unbounded min value`, `dereference of modified ctx ptr`, and `math between ctx pointer and 4294967295`, plus success logs proving precise stack masks and processed-instruction counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_spill_fill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_spin_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_spin_lock.c

## Purpose
`verifier_spin_lock.c` validates verifier rules for `bpf_spin_lock` fields embedded in map values. It checks legal lock/unlock use, direct access rejection, call restrictions while locked, missing or mismatched unlocks, lock identity tracking across map lookups, and loop behavior inside a locked region.

## Important APIs, Types, and Functions
The file defines `struct val { struct bpf_spin_lock l; int cnt; }` and an array map `map_spin_lock` containing those values. It exercises helpers `bpf_map_lookup_elem`, `bpf_spin_lock`, `bpf_spin_unlock`, `bpf_get_prandom_u32`, and C macro `bpf_for` in the final loop test. One static naked subprogram, `lock_in_subprog_without_unlock__1`, takes a lock without unlocking to test subprogram lock-state accounting.

## Control Flow
Most tests lookup one or more map values, optionally branch to keep state comparison interesting, call lock and unlock helpers, and then exit. Negative tests attempt direct reads/writes of the lock field, helper calls while locked, exits before unlock, unlock without lock, double lock, unlock using a different map-value pointer, LD_ABS under lock, or state-pruned paths with mismatched lock IDs. The final C test locks a map value, runs a bounded `bpf_for` loop incrementing `cnt`, unlocks, and returns.

## State and Persistence
State is map-backed: the array map stores the spin lock and counter field. The verifier tracks lock ownership as abstract state tied to a specific map-value pointer and lock field. There is no filesystem persistence.

## Dependencies and Integration Points
The source depends on verifier support for spin-lock fields in map values and helper restrictions while a lock is held. Program sections include `cgroup/skb` and `tc`, with unprivileged failures expected for many lock operations. It integrates with state equivalence through `BPF_F_TEST_STATE_FREQ` cases that compare lock IDs.

## Risks and Test Signals
Risks include allowing direct lock-field access, permitting helper calls or exits inside locked regions, losing lock identity across state pruning, or rejecting legal bounded loops under lock. Test signals include messages `cannot be accessed directly`, `calls are not allowed`, `without taking a lock`, `unlock of different lock`, `bpf_spin_unlock of different lock`, `inside bpf_spin_lock`, and a final success for `bpf_loop_inside_locked_region`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_spin_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_stack_ptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_stack_ptr.c

## Purpose
`verifier_stack_ptr.c` tests verifier handling of `PTR_TO_STACK` arithmetic, stack bounds, alignment, mixed register/constant offsets, map stores of stack-derived data, and maximum stack size accounting with `may_goto` and JIT behavior.

## Important APIs, Types, and Functions
The file defines `map_array_48b`, an array map with 48-byte values. Programs are mostly `SEC("socket")` naked assembly with one `tc` map lookup/store case. It uses `bpf_map_lookup_elem`, `BPF_MAXINSNS`-style instruction sequences through inline assembly, `INT_MAX`/`limits.h`, and expected verifier messages for stack pointer arithmetic and stack size limits.

## Control Flow
The tests construct stack pointers from `r10`, add immediate or register offsets, perform loads/stores, and exit with known return values when valid. Invalid paths use misaligned accesses, offsets above frame pointer, offsets below the 512-byte stack limit, arithmetic that would overflow, and dynamic pointer math the verifier cannot prove safe. The TC case stores bytes derived from a stack pointer into a map value to verify safe handling. The final cases distinguish stack size >512 rejection from a 512-byte stack with `may_goto` under JIT and non-JIT expectations.

## State and Persistence
Persistent state is limited to `map_array_48b` for the map interaction test. The core state is verifier stack-pointer metadata: fixed offset, variable offset bounds, alignment, stack depth, and whether arithmetic remains within `[fp-512, fp)`.

## Dependencies and Integration Points
The file integrates with socket and TC verifier rules, stack-depth accounting, map-value access, JIT-specific `may_goto` stack accounting, and unprivileged stack pointer range checks. It depends on exact verifier diagnostics such as `misaligned stack access`, `stack pointer arithmetic goes out of range`, `fp pointer offset`, and `stack size 520(extra 8) is too large`.

## Risks and Test Signals
Risks include accepting out-of-frame stack writes, rejecting legal bounded pointer arithmetic, miscomputing dynamic offsets, or accounting `may_goto` stack usage differently between interpreter and JIT. Test signals are valid return values like `0xfaceb00c` and 42 for accepted paths, plus targeted failure messages for alignment, bounds, pointer math, and stack-size violations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_stack_ptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_store_release.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_store_release.c

## Purpose
`verifier_store_release.c` tests verifier support for atomic store-release instructions. It validates legal stack store-release widths, operand initialization checks, destination pointer classes, alignment, pointer leakage through store-release, invalid register encoding, and fallback behavior when atomics support is unavailable.

## Important APIs, Types, and Functions
The file uses low-level BPF instruction encoding from `../../../include/linux/filter.h` and inline assembly. It declares `map_hash_8b` for a map-value pointer leakage test and calls `bpf_map_lookup_elem`. Program types include `socket`, `xdp`, `flow_dissector`, and `sk_reuseport`. An `ENABLE_ATOMICS_TESTS`/toolchain support path emits real tests; otherwise a dummy successful socket program is used.

## Control Flow
Valid stack tests perform 8-, 16-, 32-, and 64-bit store-release operations and return zero. Negative tests omit source or destination initialization, use a scalar destination, use misaligned stack destination, attempt atomic stores into ctx, packet, flow_keys, or sock pointers, or encode invalid register `R15`. Pointer leakage tests store stack and map pointers with release semantics and distinguish privileged success from unprivileged pointer-leak rejection.

## State and Persistence
The only persistent object is the hash map used to obtain a map-value pointer. Otherwise state is stack/register verifier metadata and pointer-type provenance. Store-release itself is a memory-ordering operation but these fixtures do not coordinate with concurrent runtime state.

## Dependencies and Integration Points
The source depends on Clang/JIT atomics support, BPF atomic instruction encoding, verifier memory-class rules, and unprivileged pointer leak policy. It integrates with the selftest runner through exact messages such as `R2 !read_ok`, `BPF_ATOMIC stores into R1 ctx is not allowed`, and `R6 leaks addr into map`.

## Risks and Test Signals
Risks include accepting store-release to read-only or unsafe pointer classes, missing alignment enforcement, failing to detect uninitialized operands, or mishandling pointer leaks via atomics. Test signals are width-specific success cases, deterministic failures for invalid pointer classes and registers, and a dummy success path that prevents unsupported environments from failing unrelated test runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_store_release.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subprog_precision.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subprog_precision.c

## Purpose
`verifier_subprog_precision.c` is a comprehensive precision-backtracking test suite for BPF subprograms, callbacks, stack slots, global functions, and tail calls. It verifies where precision marks originate and how they propagate between callers, callees, callbacks, and spilled data.

## Important APIs, Types, and Functions
The file defines `vals[] SEC(".data.vals")` and a prog-array `map_array`. It uses many static subprograms, including `identity_subprog`, `callback_subprog`, frame-pointer leaking subprograms, `loop_callback_bad`, `subprog_with_precise_arg`, `subprog_spill_reg_precise`, and `identity_tail_call`. Helpers include `bpf_loop` and `bpf_tail_call`. Expected verifier logs heavily use `mark_precise` traces.

## Control Flow
The tests usually set a bounded or unknown index, call a subprogram or callback, multiply by element size, and add it to a map-value pointer. Some tests intentionally leak frame-pointer-derived scalars through subprograms to verify precision remains conservative. `bpf_loop` tests verify callback return range enforcement and the rule that loop callback parameters such as `r1` and `r4` become precise only to the helper call boundary. Later tests spill precise values, mutate stack/map slots, and verify precision propagation through tail-call failure paths.

## State and Persistence
Persistent state is limited to `.data.vals` and the prog array. The main state is verifier precision metadata across frames and stack slots. Stack slots can carry precise scalar requirements, and map-value pointers carry bounds that make precision failures visible as invalid pointer arithmetic.

## Dependencies and Integration Points
The source depends on verifier subprogram call graph analysis, callback modeling for `bpf_loop`, stack precision tracking, map-value bounds, and tail-call helper semantics. It integrates through raw tracepoint-like optional sections `SEC("?raw_tp")`, verbose log matching, and failure messages such as callback return range violations and `math between map_value pointer and register with unbounded min value`.

## Risks and Test Signals
Risks include either under-propagating precision, which can accept unsafe map-value access, or over-propagating precision, which can cause verifier complexity and false rejections. Test signals include detailed `mark_precise` paths across frame numbers, expected `bpf_loop` callback rejection when `R0` returns outside `[0, 1]`, success cases with bounded indices, and a tail-call failure case proving unbounded precision is still rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subprog_precision.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subprog_topo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subprog_topo.c

## Purpose
`verifier_subprog_topo.c` verifies topological ordering of BPF subprogram verification. It covers linear call chains, diamond-shaped call graphs, mixed static/global functions, shared leaves, duplicate calls, `bpf_loop` callbacks, callback-to-subprogram chains, and a no-call program.

## Important APIs, Types, and Functions
The file defines many small static/global subprograms implemented with inline assembly. Main entrypoints are `SEC("?raw_tp")` programs annotated with `__success`, `__log_level(2)`, and `__msg("topo_order[...] = ...")`. It uses `bpf_loop` for callback graph cases and libbpf/BPF helper annotations from `bpf_misc.h`.

## Control Flow
Each test creates a specific call graph and returns. Linear tests call A then B; diamond tests converge on shared leaves; mixed tests combine static and global functions; duplicate tests call the same leaf more than once; callback tests pass a callback to `bpf_loop`, including a callback that calls another leaf. The verifier is expected to log subprogram verification order from leaves toward roots.

## State and Persistence
There is no persistent map or external state. The only state under test is the verifier's call graph, topological sort, and callback subgraph accounting.

## Dependencies and Integration Points
The source depends on verifier logging of `topo_order`, subprogram graph construction, static/global linkage handling, and helper callback recognition for `bpf_loop`. It integrates with optional raw tracepoint test sections and log-level matching.

## Risks and Test Signals
Risks include verifying callers before callees, mishandling shared leaves or duplicate call edges, omitting callback subgraphs, or incorrectly ordering global and static functions. Test signals are precise `topo_order` log lines such as `linear_b`, `diamond_c`, `shared_leaf`, `loop_cb`, and `loop_cb2_leaf` preceding their callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subprog_topo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subreg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subreg.c

## Purpose
`verifier_subreg.c` validates subregister semantics, especially that 32-bit ALU and load operations zero-extend into 64-bit registers when required and that arithmetic right shifts preserve sign-range metadata correctly.

## Important APIs, Types, and Functions
The file uses many socket-section naked assembly functions and helper calls to `bpf_get_prandom_u32` to create unknown 32-bit values. It exercises 32-bit ALU operations: add, sub, mul, div, mod, or, and, xor, lsh, rsh, arsh, neg, mov, endian conversions, and byte/half/word loads. Later unnamed tests cover real-world LLVM-generated patterns, constant/unknown return distinctions, and branch behavior.

## Control Flow
Most tests call `bpf_get_prandom_u32`, perform one 32-bit operation on `w` registers, then shift or compare the corresponding 64-bit register to ensure upper bits are zeroed. ARSH sign-extension tests constrain values, left-shift into high bits, arithmetic-shift back, and use verifier log messages to assert signed min/max ranges. Load tests spill values to stack and reload with `ldx_b`, `ldx_h`, or `ldx_w` to check extension behavior.

## State and Persistence
There are no maps or persistent state. State is the verifier's register metadata: 32-bit bounds, 64-bit bounds, known zero upper bits, sign ranges, and subregister definitions.

## Dependencies and Integration Points
The file depends on verifier subreg tracking, backend zero-extension insertion policy, and selftest return execution. It integrates through `__retval`, `__success_unpriv`, `__log_level(2)`, and detailed range messages for ARSH cases.

## Risks and Test Signals
Risks include stale upper 32 bits after 32-bit operations, lost sign information after arithmetic shifts, inconsistent behavior across JITs, or regressions in compiler-generated idioms such as Cilium-style code. Test signals are zero return values for zero-extension checks, expected 1 or 42 return values for branch cases, and exact verifier range logs showing signed and unsigned bounds before and after shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_tailcall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_tailcall.c

## Purpose
`verifier_tailcall.c` is a narrow negative verifier test for `bpf_tail_call`. It confirms that the helper rejects non-prog-array maps.

## Important APIs, Types, and Functions
The file declares a regular `BPF_MAP_TYPE_ARRAY` named `map_array`, then a single `SEC("socket")` naked test program `invalid_map_for_tail_call`. The program loads `map_array` into `r2`, sets key register `r3` to zero, calls `bpf_tail_call`, and exits.

## Control Flow
Control flow is straight-line and intentionally invalid at helper-check time. There is no fallback return value because the verifier should reject the program before runtime execution.

## State and Persistence
The only persistent state is the array map declaration. No map contents are needed. The state under test is verifier helper argument type checking for `ARG_CONST_MAP_PTR` pointing to a prog-array map.

## Dependencies and Integration Points
The source depends on `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `bpf_misc.h`, and the selftest runner's expected failure matching. It integrates with socket program verification and helper prototype validation.

## Risks and Test Signals
The risk is accepting a non-prog-array map as a tail-call map, which would be unsafe helper dispatch behavior. The test signal is the exact failure `expected prog array map for tail call`, with unprivileged failure also expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_tailcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_tailcall_jit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_tailcall_jit.c

## Purpose
`verifier_tailcall_jit.c` validates x86-64 JIT code generation around tail calls from subprograms. It checks the prologue and tail-call counter storage/restoration sequences needed when a BPF program calls a subprogram that performs `bpf_tail_call`.

## Important APIs, Types, and Functions
The file defines a `BPF_MAP_TYPE_PROG_ARRAY` named `jmp_table` with entry 0 pointing back to `main`. A static auxiliary naked function `sub` loads the prog array and key then calls helper number 12, `bpf_tail_call`. The `main` TC program calls `sub`, returns zero, and is annotated with `__arch_x86_64` plus many `__jited` expected assembly fragments.

## Control Flow
At BPF level, `main` calls `sub`; `sub` attempts a tail call to `main`; if tail-call limits prevent transfer, it exits. At JIT level, the test expects the entry program to establish a tail-call counter on the stack, pass or restore the counter pointer in `rax`, and for the subprogram to increment the shared counter before jumping to the target.

## State and Persistence
Persistent state is the prog-array map binding `main` as a tail-call target. Runtime state is the JIT-managed tail-call counter stored on the native stack and passed through `rax`. No external persistence exists.

## Dependencies and Integration Points
The test is x86-64 specific and depends on the selftest runner's JIT disassembly matcher. It integrates with TC program loading, prog-array tail calls, subprogram calls, and x86 retpoline/rethunk tolerant return matching.

## Risks and Test Signals
Risks include tail-call counter corruption, unbounded recursive tail calls, or subprogram prologues failing to preserve counter pointers across calls. Test signals are exact native assembly fragments: stack slots at `rbp[-8]` and `rbp[-16]`, compare against 33, increment of `*tail_call_cnt_ptr`, and a final jump to the tail-call target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_tailcall_jit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_typedef.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_typedef.c

## Purpose
`verifier_typedef.c` is a compact BTF/CO-RE verifier test that ensures typedef-resolved kernel types can be used for field offset access in an fentry program.

## Important APIs, Types, and Functions
The file includes `vmlinux.h`, `bpf_helpers.h`, and `bpf_misc.h`. Its only test program, `resolve_typedef`, is attached to `SEC("fentry/bpf_fentry_test_sinfo")`. It uses `offsetof(struct skb_shared_info, frags)` through `__imm_const` and naked assembly to load a pointer argument, then load the `frags` field offset from `struct skb_shared_info`.

## Control Flow
The program reads the first argument pointer from `r1`, reads a field at the resolved `frags` offset, sets `r0` to zero, and exits. There are no branches and no helper calls.

## State and Persistence
There is no map or persistent state. The state under test is type-resolution metadata from BTF/vmlinux and the verifier's acceptance of field access after typedef resolution.

## Dependencies and Integration Points
The test depends on BTF definitions for `struct skb_shared_info`, the fentry attachment target `bpf_fentry_test_sinfo`, and libbpf/test macros. It integrates with verifier/BTF field-offset validation rather than runtime data processing.

## Risks and Test Signals
The risk is a regression in typedef resolution or BTF field layout handling that rejects valid field accesses or computes the wrong offset. The signal is a successful verifier load and return value 0 for the fentry program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_typedef.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_uninit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_uninit.c

## Purpose
`verifier_uninit.c` tests basic verifier rejection of uninitialized and invalid register use. It also checks that `R0` must be initialized on every exit path.

## Important APIs, Types, and Functions
The file uses socket-section naked assembly and low-level instruction encoding from `../../../include/linux/filter.h`. It defines four tests: reading uninitialized `R2`, encoding an invalid register move from `R15`, exiting without setting `R0`, and a branch where only one path initializes `R0`.

## Control Flow
Each test is minimal. `read_uninitialized_register` moves `r2` to `r0`. `read_invalid_register` embeds a raw `BPF_MOV64_REG` instruction with source register `-1`, printed as invalid `R15`. `t_init_r0_before_exit` copies `r1` to `r2` then exits with unreadable `R0`. `before_exit_in_all_branches` conditionally skips the instructions that set `r0`.

## State and Persistence
There is no persistent state. The tested state is verifier register initialization and read-ok tracking. The branch test also exercises path-sensitive exit-state merging.

## Dependencies and Integration Points
The file depends on BPF verifier register validity checks, socket program loading, and selftest failure-message matching. Unprivileged behavior is also annotated, including a pointer comparison message for the branch case.

## Risks and Test Signals
Risks include accepting reads from unreadable registers, accepting invalid encoded register numbers, or allowing programs to exit without a defined return value. Test signals are expected messages `R2 !read_ok`, `R15 is invalid`, and `R0 !read_ok`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_uninit.c -->
