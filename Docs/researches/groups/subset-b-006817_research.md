# subset-b-006817 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_storage.c

## Purpose

`verifier_cgroup_storage.c` is a BPF verifier selftest focused on `bpf_get_local_storage()` for cgroup-local and percpu-cgroup-local storage. It checks that the verifier accepts valid storage lookups and rejects wrong map types, invalid pseudo-fds, out-of-bounds map-value accesses, negative offsets, non-zero helper flags, and unprivileged pointer leaks.

## Important APIs, Types, and Functions

The file defines three maps with BTF-style map declarations: `cgroup_storage` using `BPF_MAP_TYPE_CGROUP_STORAGE`, `percpu_cgroup_storage` using `BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE`, and `map_hash_8b` as a deliberately wrong `BPF_MAP_TYPE_HASH`. All programs are `SEC("cgroup/skb")` naked assembly tests. The key helper API under test is `bpf_get_local_storage`, invoked with `BPF_PSEUDO_MAP_FD` operands and flag register `r2`. The `bpf_misc.h` metadata macros declare expected verifier success, unprivileged behavior, return values, flags, and exact diagnostic fragments.

## Control Flow

The valid tests load the cgroup-storage map pseudo-fd, pass zero flags, call `bpf_get_local_storage`, then read and write a word inside the 64-byte value. Invalid variants change one verifier precondition at a time: using the hash map, using a raw immediate in place of a map pseudo-fd, accessing offset 256, accessing a negative offset, or passing non-zero flags through either an immediate or a pointer-like register. The percpu half repeats the same pattern against `percpu_cgroup_storage`.

## State and Persistence Behavior

Persistent state is limited to map definitions. Runtime local-storage state belongs to the cgroup attachment context and is not initialized in this file. The tests depend on verifier-side tracking of map type, local-storage helper flags, returned map-value bounds, pointer offsets, and unprivileged pointer-leak restrictions.

## Dependencies and Integration Points

This file depends on libbpf section handling, selftest verifier metadata, kernel cgroup/skb program loading, and the BPF helper prototype for local storage. It integrates with the verifier test harness in `tools/testing/selftests/bpf`, which compiles the naked inline assembly, loads each SEC program, and matches verifier logs against `__msg` expectations.

## Risks and Test Signals

Risks are diagnostic drift, map-type changes, and altered unprivileged policy. Strong test signals are one accepted normal cgroup-storage case, one accepted percpu case, and all invalid variants producing the expected errors: wrong map type, invalid map fd, map-value bounds violation, negative offset, non-zero flags, and unprivileged address leakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_const.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_const.c

## Purpose

`verifier_const.c` verifies verifier enforcement for writes to global-data sections, especially `.rodata` versus mutable `.bss` and `.data`. The tests ensure helpers and direct stores cannot mutate read-only global map values while equivalent writes to mutable globals are accepted.

## Important APIs, Types, and Functions

The file uses `vmlinux.h`, libbpf helpers, tracing helpers, and `bpf_misc.h`. It defines global variables in normal C rather than explicit map structs, relying on libbpf to materialize `.rodata`, `.bss`, and `.data` maps. Helper coverage includes `bpf_strtol`, `bpf_check_mtu`, `bpf_get_prandom_u32`, and `bpf_copy_from_user`. Programs are mostly `SEC("tc/ingress")`; the final dynamic-write test is an LSM sleepable section `SEC("lsm.s/bprm_committed_creds")`.

## Control Flow

The test matrix writes through helper output pointers or direct pointer arithmetic. `tcx1` and `tcx4` attempt helper writes into rodata-backed globals and must fail with `write into map forbidden`. Parallel `.bss` and `.data` variants pass. The dynamic cases compute an unknown offset or address using `bpf_get_prandom_u32` and still expect rodata rejection, proving the verifier does not require a fully constant store target to protect read-only map values.

## State and Persistence Behavior

Global variables persist as BPF global data maps for the lifetime of the loaded object. The key state is the verifier's map mutability bit: `.rodata` must remain immutable even when accessed through helper pointer arguments or uncertain register offsets, while `.bss` and `.data` remain writable.

## Dependencies and Integration Points

The file integrates with libbpf global-data map creation, tc and LSM program loaders, helper argument verification, and verifier map-value permission checks. It is a regression guard for global data lowering and helper output pointer handling.

## Risks and Test Signals

Main risks are accidentally treating rodata as mutable when helper arguments are involved, or over-restricting mutable global sections. Test signals are four expected `write into map forbidden` failures and successful writes through the same helpers into `.bss` and `.data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_const.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_const_or.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_const_or.c

## Purpose

`verifier_const_or.c` is a small verifier regression test for scalar constant tracking across bitwise OR operations. It ensures that OR-ing constant registers preserves enough constant information for later bounds checks while not letting a wide constant-derived size bypass stack access validation.

## Important APIs, Types, and Functions

The file includes core BPF helper headers and `bpf_misc.h`. It exposes four `SEC("tracepoint")` naked assembly programs: two success cases where `|=` preserves a constant type, and two failure cases where the resulting constant is used as a helper memory size that exceeds stack bounds. The expected failure diagnostic is `invalid write to stack R1 off=-48 size=58`.

## Control Flow

The success programs build constants with immediate-to-register moves and register-to-register ORs, then return. The negative programs initialize a stack pointer around `fp - 48`, produce a constant 58-byte size through immediate or register OR, and call a helper-style memory access that should be rejected because it would write beyond the verified stack slot.

## State and Persistence Behavior

No persistent runtime state is declared. The meaningful state is verifier scalar metadata: constant value, unknown bits, stack pointer offset, and helper memory-size reasoning. The tests require the verifier to retain constant precision after bitwise OR but still apply the normal stack boundary rules.

## Dependencies and Integration Points

This file integrates with the generic verifier scalar tnum/range engine and stack access validator. It is independent of maps or runtime helpers beyond the verifier's interpretation of helper memory arguments in inline assembly.

## Risks and Test Signals

Risks include scalar precision regressions, treating constants as unknown after OR, or treating constant precision as proof of memory safety without range checking. Test signals are two accepted constant-preservation programs and two rejected oversized stack writes with the same stack-boundary diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_const_or.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx.c

## Purpose

`verifier_ctx.c` is a broad verifier test suite for `PTR_TO_CTX` handling. It covers direct context access, atomic stores, modified context pointers passed to helpers, nullable context parameters, field width and alignment rules, syscall context memory access, helper and kfunc memory access to ctx, and non-syscall restrictions.

## Important APIs, Types, and Functions

The file uses `vmlinux.h`, libbpf helpers, `bpf_misc.h`, and test-module kfunc declarations from `bpf_testmod_kfunc.h`. Program sections include tc, socket, cgroup sendmsg/connect/post_bind, and many optional `?syscall` programs. Helper and kfunc coverage includes `bpf_probe_read_kernel`, `bpf_snprintf`, `bpf_strncmp`, `bpf_get_prandom_u32`, and `bpf_kfunc_call_test_mem_len_pass1`. Macros generate invalid narrow-load, unaligned-field, and padding-access cases for context structs.

## Control Flow

Early tests mutate or arithmetically adjust ctx pointers and verify that direct dereference or helper passing is rejected unless the original unmodified ctx is used. The cgroup cases check helper prototypes accepting either ctx or null. The syscall section deliberately treats ctx as a generic memory region: fixed, variable, aligned, unaligned, zero-sized, helper-mediated, and kfunc-mediated access is accepted when bounded and rejected past `U16_MAX`, for negative variable offsets, or for unbounded ranges. The final macro block applies stricter rules to other program types, rejecting modified ctx dereferences and helper/kfunc access through ctx.

## State and Persistence Behavior

The file has no BPF maps. Its state is verifier state: ctx pointer id and offset, variable offset ranges, program-type-specific context access tables, helper/kfunc memory argument classification, and nullable ctx acceptance. Syscall programs are intentionally special because their ctx argument can be treated as trusted kernel memory under bounded access rules.

## Dependencies and Integration Points

The tests integrate with verifier context access callbacks for each program type, BTF-backed kfunc prototype checking, helper argument validators, and the selftest module that exports test kfuncs. Optional sections allow loaders to skip unavailable program types while still validating supported ones.

## Risks and Test Signals

Risks are accepting modified ctx pointers where helpers expect original ctx, rejecting legitimate bounded syscall ctx memory, or allowing out-of-range syscall ctx access. Test signals include exact errors for atomic ctx stores, modified ctx pointer dereference, invalid context access, negative or unbounded memory ranges, and type mismatches such as ctx where stack memory is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx_ptr_param.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx_ptr_param.c

## Purpose

`verifier_ctx_ptr_param.c` tests BTF-based fentry/fexit context parameter inference for pointer-to-pointer arguments. It ensures `void **`, `void ***`, and `struct file **` parameters are not exposed to BPF as trusted kernel object pointers, but as scalar values.

## Important APIs, Types, and Functions

The programs attach to test kernel functions named `bpf_fentry_test_ppvoid`, `bpf_fentry_test_pppvoid`, `bpf_fentry_test_ppfile`, and `bpf_fexit_test_ret_ppfile`. Each program is naked inline assembly and uses `__msg` expectations to assert verifier register types, especially `R1=ctx()` and `R2=scalar()`.

## Control Flow

Each program receives the tracing context, reads the second logical argument from the fentry/fexit ctx layout, and returns zero. There is no data mutation. The point is the verifier log generated during load: the second parameter must remain scalar even when its C type contains kernel pointer-looking layers.

## State and Persistence Behavior

No maps or persistent state exist. The state under test is verifier argument-type materialization from BTF function prototypes and ctx slots. Returning these parameters as scalar prevents accidental direct dereference or trusted pointer use.

## Dependencies and Integration Points

The file depends on BTF for the test functions, libbpf tracing section attachment, and verifier tracing-context argument decoding. It integrates with selftest kfunc/fentry fixtures that provide the target prototypes.

## Risks and Test Signals

The main risk is a BTF decoder regression that marks pointer-to-pointer arguments as kernel pointers. The test signal is successful load with the expected verifier log showing scalar classification for the second argument in all four cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx_ptr_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx_sk_msg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx_sk_msg.c

## Purpose

`verifier_ctx_sk_msg.c` verifies allowed `sk_msg_md` context fields and direct packet access rules for SK_MSG-style programs. It checks valid metadata reads, rejects invalid width and offset accesses, and validates packet data/data_end bounds reasoning.

## Important APIs, Types, and Functions

The file uses `SEC("sk_msg")` and two `SEC("sk_skb")` programs. Test functions cover `family`, IPv4 and IPv6 address fields, remote and local ports, `size`, and packet buffer reads/writes. Metadata macros record success or expected `invalid bpf_context access` failures. The assembly reads context offsets directly rather than using C field names.

## Control Flow

The valid metadata programs read fields at verifier-approved offsets and return. Negative tests attempt a 64-bit read of the 32-bit `size` field, read past the end of the context, or use an invalid offset. Packet tests obtain data and data_end from ctx, check ranges, then read or write packet bytes. The overlapping-check case performs multiple bounds checks that together establish safe direct packet access.

## State and Persistence Behavior

There are no maps. Runtime packet content is transient; verifier state tracks ctx field permissions, packet pointer ids, packet range proofs, and direct-write permission for SK_MSG.

## Dependencies and Integration Points

The file integrates with sk_msg/sk_skb program-type context access callbacks and packet-access verifier logic. It is relevant to sockmap/sk_msg infrastructure because accepted programs can inspect and mutate message data.

## Risks and Test Signals

Risks are accepting context reads at wrong width/offset, rejecting valid SK_MSG metadata fields, or losing range information across overlapping packet checks. Test signals are all valid field accesses loading successfully, the three invalid context reads failing with `invalid bpf_context access`, and packet read/write cases passing only after appropriate data_end checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx_sk_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_d_path.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_d_path.c

## Purpose

`verifier_d_path.c` checks program-type restrictions for the `bpf_d_path` helper. The helper is accepted from a suitable fentry attachment that receives a file/dentry-related object and rejected from a probe context where the helper is not allowed.

## Important APIs, Types, and Functions

Two naked programs are declared: `d_path_accept` in `SEC("fentry/dentry_open")` and `d_path_reject` in `SEC("fentry/d_path")`. Both prepare a stack buffer and call the d_path helper. The expected rejection message is `helper call is not allowed in probe`.

## Control Flow

The accepted program extracts the needed kernel pointer from tracing context, points `r2` at a stack buffer, sets a size, calls the helper, and returns zero. The rejected program performs a similar call shape from a helper-ineligible attachment, proving the verifier checks helper allowlists independently of instruction form.

## State and Persistence Behavior

The only state is stack memory used as the pathname buffer. No maps are declared. Verifier state tracks helper availability by program type and whether the first argument is a suitable kernel pointer.

## Dependencies and Integration Points

The test depends on BTF fentry attachment points, the `bpf_d_path` helper prototype, and verifier helper allowlists. It integrates with filesystem tracing because the accepted path runs at `dentry_open`.

## Risks and Test Signals

Risks are widening helper availability to unsafe probe contexts or accidentally rejecting valid fentry usage. Test signals are one successful load and one failure with the helper-not-allowed diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_d_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_default_trusted_ptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_default_trusted_ptr.c

## Purpose

`verifier_default_trusted_ptr.c` tests default trusted pointer kfunc behavior. It ensures a syscall BPF program can acquire a default trusted pointer from a test kfunc, pass it through helper/kfunc calls that expect trusted pointer semantics, and release it correctly.

## Important APIs, Types, and Functions

The program includes `vmlinux.h`, tracing helpers, `bpf_misc.h`, and `bpf_testmod_kfunc.h`. Its single `SEC("syscall")` program calls `bpf_kfunc_get_default_trusted_ptr_test`, `bpf_get_default_trusted_ptr_test`, and `bpf_kfunc_put_default_trusted_ptr_test`. The section is GPL-licensed because kfunc access may require GPL compatibility.

## Control Flow

The program obtains a trusted pointer, uses the default trusted pointer helper path, releases the pointer, and returns zero. There is no branching or data storage; verifier success is the contract.

## State and Persistence Behavior

No maps are declared. Runtime state is a temporary trusted/refcounted kernel pointer owned by the kfunc protocol. Correct persistence behavior is non-persistence: the pointer must be released and must not escape program execution.

## Dependencies and Integration Points

The file depends on the selftest kernel module exporting the trusted-pointer kfuncs, BTF kfunc metadata, and syscall program support. It integrates with verifier reference tracking and trusted pointer defaulting rules.

## Risks and Test Signals

Risks include verifier regressions in default trusted pointer classification, missing release enforcement, or test-module BTF drift. The test signal is successful verifier load and zero return with no reference leak diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_default_trusted_ptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_direct_packet_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_direct_packet_access.c

## Purpose

`verifier_direct_packet_access.c` is an extensive verifier suite for direct packet access. It checks data/data_end arithmetic, range proofs, packet writes, pruning, alignment, pointer spilling, pointer arithmetic restrictions, subprogram propagation, and error reporting for tc and socket program types.

## Important APIs, Types, and Functions

The file includes Ethernet constants, BPF helpers, and `bpf_misc.h`. It defines 34 programs, mostly `SEC("tc")`, plus one socket program. They use inline assembly to read `__sk_buff` packet metadata offsets, compare packet pointers to data_end, and perform byte/word/dword/qword packet accesses. Expected messages cover invalid context access, invalid packet access, scalar memory access, packet-end arithmetic, and misaligned packet access.

## Control Flow

The early tests establish core rules: `pkt_end - pkt_start` is accepted, accesses after sufficient bounds checks pass, and unchecked or too-wide accesses fail. Middle tests combine comparisons, shifts, AND masks, branch joins, zero additions, xadd/spill interactions, and arithmetic on data_end. Later tests exercise packet pointer marking on good and bad accesses, subprogram handoff of packet/data_end registers, and access ranges near packet boundaries.

## State and Persistence Behavior

No persistent maps are declared. Runtime packet bytes are transient. The verifier state under test includes packet pointer id, fixed and variable offsets, proven range `r`, alignment, stack spills retaining pointer type, and branch-pruned state equivalence.

## Dependencies and Integration Points

The file integrates with tc classifier program loading, direct packet access verifier logic, and subprogram verifier state propagation. It is important for networking because accepted tc programs can read and write packet data directly without helper calls.

## Risks and Test Signals

Risks are accepting out-of-bounds packet reads/writes, rejecting safe access after complex but valid range checks, or losing pointer identity through spills and subprogram calls. Test signals include successful load for well-bounded variants and exact failures for invalid access to packet, bad ctx offset, pkt_end arithmetic, scalar memory access, and misalignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_direct_packet_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_direct_stack_access_wraparound.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_direct_stack_access_wraparound.c

## Purpose

`verifier_direct_stack_access_wraparound.c` tests stack pointer arithmetic near 32-bit wraparound boundaries. It ensures the verifier rejects frame-pointer offsets that would overflow or escape the valid BPF stack range even when arithmetic appears to wrap.

## Important APIs, Types, and Functions

The file has three `SEC("socket")` naked assembly programs. All use frame-pointer arithmetic with large positive constants such as `2147483647` and `1073741823`. Metadata expects verifier diagnostics about frame-pointer arithmetic and stack pointer range violations.

## Control Flow

Each test moves `r10` into a general register, adds or subtracts large constants, and attempts a direct stack access. The variants isolate immediate wraparound, intermediate offset tracking, and final out-of-range access.

## State and Persistence Behavior

There are no maps or external state. The relevant state is verifier stack pointer offset arithmetic, including signed and unsigned overflow avoidance. The frame pointer must remain bounded to the fixed 512-byte BPF stack.

## Dependencies and Integration Points

This file integrates with verifier pointer arithmetic checks and stack access validation. It is a regression guard against integer overflow in verifier offset calculations.

## Risks and Test Signals

Risks are arithmetic overflow allowing invalid stack access or overly broad rejection of legitimate small offsets. Test signals are three failures with diagnostics mentioning impossible frame-pointer arithmetic, large offsets, or stack pointer arithmetic out of range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_direct_stack_access_wraparound.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_div0.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_div0.c

## Purpose

`verifier_div0.c` tests verifier handling of division and modulo by a value that may be zero. It covers 32-bit and 64-bit DIV/MOD in socket and tc contexts and distinguishes safe zero checks from unsafe control-flow patterns.

## Important APIs, Types, and Functions

The file defines 15 naked programs across `SEC("socket")` and `SEC("tc")`. The operations under test are unsigned BPF ALU division and modulo in 32-bit and 64-bit forms. The tests are metadata-driven and generally rely on success/failure outcome rather than exact diagnostic messages.

## Control Flow

Each program constructs a divisor from context or constants, conditionally compares it against zero, and then executes DIV or MOD. Safe variants guard the operation on all paths. Unsafe variants place the zero check on the wrong path, allow a zero-valued path to reach the operation, or test only a related register state. Classifier variants repeat the same logic in a tc program type.

## State and Persistence Behavior

No maps are declared. Verifier state consists of scalar range information for divisor registers, branch refinement after zero comparisons, and the distinction between 32-bit and 64-bit register subranges.

## Dependencies and Integration Points

The file integrates with the verifier ALU safety checks that prevent runtime divide-by-zero traps. It also checks that program-type differences do not change scalar proof requirements.

## Risks and Test Signals

The key risk is accepting a DIV/MOD where zero remains in the divisor range, or rejecting operations after a valid guard. Test signals are accepted guarded cases and rejected unguarded or incorrectly guarded variants across DIV32, DIV64, MOD32, and MOD64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_div0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_div_mod_bounds.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_div_mod_bounds.c

## Purpose

`verifier_div_mod_bounds.c` is a dense scalar-bound regression suite for division and modulo. It verifies the exact verifier range and tnum results after unsigned and signed DIV/MOD for 32-bit and 64-bit operands, including positive, negative, mixed-sign, zero-divisor, and signed-overflow cases.

## Important APIs, Types, and Functions

The file contains 50 `SEC("socket")` naked assembly tests. It includes `<limits.h>` for boundary constants and uses `__log_level`/`__msg` expectations to match verifier state dumps after operations such as `w1 /= 3`, `r1 s/= -3`, and signed/unsigned modulo. The important API is not a helper but the verifier's ALU range engine.

## Control Flow

Each program initializes a scalar register with a constrained range, applies a divisor or modulo operation, then returns. Some variants use constant divisors, some use registers whose range includes zero, and overflow variants exercise signed minimum divided or modulo `-1`. The expected verifier logs encode the resulting signed minimum/maximum, unsigned bounds, 32-bit subbounds, and variable-offset mask.

## State and Persistence Behavior

There is no persistent BPF state. The whole file is about verifier scalar state: `smin/smax`, `umin/umax`, `smin32/smax32`, `umin32/umax32`, constants, and `var_off`. Division by zero collapses known behavior to zero in some verifier paths, while signed overflow cases must avoid unsound narrowing.

## Dependencies and Integration Points

The file integrates with BPF verifier ALU simulation and log formatting. Any change to scalar-bound math or diagnostic rendering can affect it. The tests are foundational for later pointer and memory checks because memory safety depends on correct scalar ranges.

## Risks and Test Signals

Risks are unsound range narrowing after signed operations, loss of precision after safe operations, or incorrect handling of zero divisors and `INT_MIN / -1`. Test signals are the 50 exact verifier log matches that describe post-operation scalar state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_div_mod_bounds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_div_overflow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_div_overflow.c

## Purpose

`verifier_div_overflow.c` tests signed division and modulo overflow behavior around minimum integer values divided or reduced by `-1`. It ensures the verifier and JIT-visible execution semantics remain safe for 32-bit and 64-bit operations.

## Important APIs, Types, and Functions

The file defines eight `SEC("tc")` naked programs: DIV32, DIV64, MOD32, and MOD64, each with two check variants. It includes `<limits.h>` for boundary values. No maps or helpers are used.

## Control Flow

Each program builds an extreme signed value and a `-1` divisor, runs either division or modulo, and returns. The variants cover different ways of setting up the operand and checking branch constraints so the verifier sees both constant and range-derived overflow situations.

## State and Persistence Behavior

There is no persistent state. The state under test is signed ALU modeling and runtime safety around the CPU-defined corner case where signed minimum divided by `-1` overflows in fixed-width arithmetic.

## Dependencies and Integration Points

This file integrates with verifier ALU overflow handling and the tc loader. It complements `verifier_div_mod_bounds.c`, which verifies logged ranges, by focusing on load acceptance and runtime-safe behavior for overflow cases.

## Risks and Test Signals

Risks are verifier/JIT mismatch, unsafe native division traps, or incorrect scalar assumptions after overflow-prone operations. Test signals are all eight programs matching their declared outcomes under tc verifier loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_div_overflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_global_ptr_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_global_ptr_args.c

## Purpose

`verifier_global_ptr_args.c` tests verifier checking of global subprogram pointer argument tags and flavors. It focuses on trusted, nullable, refcounted, untrusted, user-memory, and read-only cast pointer semantics when global functions are called from BPF programs.

## Important APIs, Types, and Functions

The file includes BTF, tracing, CO-RE, `xdp_metadata.h`, and kfunc declarations. It uses task helpers and kfuncs such as `bpf_get_current_task_btf`, `bpf_task_acquire`, `bpf_task_release`, `bpf_core_cast`, `bpf_rdonly_cast`, and `bpf_copy_from_user_task`. Programs attach to tp_btf, kprobe, uprobe, and task_newtask sections. Global subprograms encode contracts such as trusted nullable task, trusted non-null task, pointer flavor, acquire/release, untrusted, and memory-tagged arguments.

## Control Flow

Top-level programs obtain task pointers or external context pointers, then call global subprograms with either correct or intentionally wrong annotations. Success cases pass nullable pointers only to nullable prototypes, non-null trusted pointers after proper checks or acquisition, and untrusted pointers to untrusted-only prototypes. Failure cases pass scalar or nullable pointers where non-null trusted pointers are required, release non-refcounted pointers, combine invalid argument tags, or pass incompatible pointer types.

## State and Persistence Behavior

No persistent maps are declared. Runtime state centers on pointer provenance, nullability, trustedness, flavor, and reference ownership. Refcounted task pointers acquired by kfuncs must be released, while borrowed current-task pointers must not be treated as releasable references.

## Dependencies and Integration Points

The file integrates with global subprogram verification, BTF type-tag parsing, task kfuncs, CO-RE casts, and helper argument checking. It is a regression suite for verifier call-boundary type checking, not for runtime data processing.

## Risks and Test Signals

Risks include allowing untrusted pointers into trusted prototypes, losing nullable information at global-call boundaries, or mishandling refcount ownership. Test signals are expected verifier messages about validating specific subprograms, caller invalid arguments, trusted pointer register types, release requirements, and incompatible tag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_global_ptr_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_global_subprogs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_global_subprogs.c

## Purpose

`verifier_global_subprogs.c` tests global BPF subprogram verification across many program types. It checks when global functions are assumed valid from their prototype, when they are revalidated at call sites, and how ctx, memory, dynptr, tail-call, and unsupported-helper contracts cross global-call boundaries.

## Important APIs, Types, and Functions

The file includes BTF, tracing, `xdp_metadata.h`, kfunc declarations, and `err.h`. It defines a `syscall_prog_array` map for tail calls and struct_ops data for `test_1`. Helpers include `bpf_get_prandom_u32`, `bpf_tail_call`, `bpf_get_stack`, `bpf_dynptr_from_xdp`, `bpf_dynptr_data`, `bpf_dynptr_slice`, and `bpf_for`. Sections span raw_tp, syscall, tracepoint, tp_btf, kprobe, perf_event, iter, lsm, struct_ops, xdp, and tc.

## Control Flow

Some tests call simple global functions that are safe for any matching prototype, while others call global functions that do invalid map-value pointer math, use unsupported helpers, or dereference ctx after modification. The ctx-tag section passes program-specific contexts through subprogram prototypes and checks fixed-offset versus variable-offset behavior. Dynptr and XDP paths verify that global subprograms preserve helper contracts for packet-derived dynptr data.

## State and Persistence Behavior

Persistent state is limited to the prog-array map and struct_ops object. Verifier state includes global function validation summaries, argument type tags, ctx pointer offsets, dynptr initialization, map-value pointer ranges, and tail-call reachability.

## Dependencies and Integration Points

The file integrates with verifier global function analysis, BTF function prototype tags, many program-type context validators, tail calls, struct_ops loading, XDP dynptr helpers, and iterator/LSM support.

## Risks and Test Signals

Risks are assuming unsafe global functions are valid, over-revalidating safe globals, or losing program-type-specific ctx constraints at global-call boundaries. Test signals are verifier logs such as global function assumed valid, validating named functions, unsafe map pointer math, invalid memory access, modified ctx dereference, variable ctx access, and successful multi-program-type loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_global_subprogs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_gotol.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_gotol.c

## Purpose

`verifier_gotol.c` tests the long unconditional jump instruction form introduced for newer BPF CPU versions. It verifies both small and large immediate long jumps when the compiler and JIT support the instruction, with a dummy fallback for unsupported environments.

## Important APIs, Types, and Functions

The file defines `gotol_small_imm`, `gotol_large_imm`, and `dummy_test` in `SEC("socket")`. It uses `bpf_misc.h` feature metadata and raw inline assembly long-jump syntax. No helpers or maps are used.

## Control Flow

The real tests branch over filler instruction ranges using long immediates and return only if the jump target is reached correctly. The large-immediate variant stresses instruction encoding and verifier branch target calculation beyond ordinary short jump ranges. The dummy program allows the suite to compile or run on environments without the required CPU/JIT support.

## State and Persistence Behavior

There is no persistent state. Verifier state is limited to instruction reachability and jump target validation.

## Dependencies and Integration Points

The test depends on assembler/compiler support for the long jump encoding, verifier instruction decoder support, and JIT/interpreter support for the target BPF CPU version.

## Risks and Test Signals

Risks include incorrect long-jump offset calculation, unreachable-code mishandling, or JIT/interpreter divergence. Test signals are successful load and execution of small and large long-jump cases, or the fallback dummy success when the feature is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_gotol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_gotox.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_gotox.c

## Purpose

`verifier_gotox.c` tests indirect jump-table support for `BPF_JA | BPF_X`. It verifies reserved-field rejection, jump table discovery, pointer type checking, map-backed instruction array reads, immutability of jump tables, subprogram boundaries, and duplicate table values.

## Important APIs, Types, and Functions

The file includes `filter.h` for low-level instruction definitions. It declares multiple socket programs that exercise indirect jumps and jump-table maps or readonly data. Expected diagnostics include reserved field use, no jump tables found, expected `PTR_TO_INSN`, invalid reads of `insn_array`, misaligned value access, invalid map-value bounds, negative index values, forbidden writes, and subprogram-boundary violations.

## Control Flow

Positive tests build a valid jump table, compute an index, and use an indirect jump to one of the table destinations. Negative tests deliberately set wrong destination register types, read misaligned or undersized jump entries, access table positions outside map bounds, attempt to modify readonly jump table data, branch outside the current subprogram, or encode non-unique target values.

## State and Persistence Behavior

Persistent state is jump-table data represented as map/global data. The verifier must treat table entries as immutable instruction references and preserve per-subprogram control-flow integrity.

## Dependencies and Integration Points

This file integrates with verifier instruction decoding, jump-table discovery, readonly map-value enforcement, subprogram control-flow validation, and JIT support for indirect BPF jumps.

## Risks and Test Signals

Risks are arbitrary control-flow through writable or malformed tables, crossing subprogram boundaries, and accepting reserved instruction fields. Test signals are successful valid jump-table loads and exact failures for bad register type, misalignment, invalid memory access, negative index, forbidden write, and outside-subprogram targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_gotox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_access_var_len.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_access_var_len.c

## Purpose

`verifier_helper_access_var_len.c` verifies helper argument checking for variable-length memory accesses. It covers stack memory, map values, adjusted map pointers, nullable memory pointers, zero-sized accesses, ring-buffer output, and leak prevention for uninitialized stack bytes.

## Important APIs, Types, and Functions

Maps include `map_hash_48b`, `map_hash_8b`, and `map_ringbuf`. Programs attach to tracepoint, tc, and socket sections. Most tests call helpers that read or write memory via pointer-and-size arguments; the explicit helper call visible in C is `bpf_ringbuf_output`. Metadata captures failures for invalid stack reads/writes, negative sizes, zero-sized invalid reads, unbounded memory, scalar pointer misuse, and map-value bounds.

## Control Flow

The stack tests derive sizes with bitwise AND, unsigned comparisons, signed comparisons, and offset additions, then pass stack pointers to helpers. Map tests repeat the same proof patterns with map-value pointers and adjusted offsets. Nullable pointer tests prove that size zero is allowed with null or non-null pointers, while size greater than zero requires a valid memory pointer. Later tests check that helpers cannot leak uninitialized stack memory and that ring-buffer output applies the same variable-length rules.

## State and Persistence Behavior

Persistent state is the three maps. Runtime verifier state tracks stack slot initialization, pointer base and offset, variable size minimum/maximum, nullable pointer refinement, and whether helper access is read or write.

## Dependencies and Integration Points

The file integrates with helper argument descriptors such as memory, memory-or-null, fixed/variable size, and ringbuf output. It depends on map lookup semantics and stack initialization tracking.

## Risks and Test Signals

Risks are unbounded helper memory reads, uninitialized stack leakage, rejecting valid zero-sized nullable operations, or accepting negative or too-large variable sizes. Test signals are accepted bounded stack/map/ringbuf cases and exact failures for invalid stack access, negative min value, scalar expected stack pointer, map bounds, and unbounded memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_access_var_len.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_packet_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_packet_access.c

## Purpose

`verifier_helper_packet_access.c` tests helper-mediated packet access. It ensures helpers that read or write packet memory receive packet pointers with proven ranges, rejects unchecked or undersized ranges, and verifies helper allowlist behavior for XDP and tc packet contexts.

## Important APIs, Types, and Functions

The file defines `map_hash_8b` for selected helper cases and 21 programs across `SEC("xdp")` and `SEC("tc")`. Inline assembly passes packet pointers, packet_end, stack pointers, and sizes to helper calls. Expected diagnostics include `invalid access to packet`, `helper access to the packet`, negative minimum values, and `R1 type=pkt_end expected=fp`.

## Control Flow

XDP tests start with packet data/data_end and try valid, unchecked, variable, bad-range, and too-short packet helper accesses. TC tests repeat the matrix and add unsuitable-helper checks, helper-ok subprogram calls, helper-fail subprogram calls, range-zero handling, packet_end used as a wrong input pointer, and incorrect register placement.

## State and Persistence Behavior

Persistent state is only the hash map. Runtime packet state is transient. The verifier tracks packet pointer ids, checked ranges, pointer base type, minimum size, helper read/write capability, and subprogram transfer of packet proof state.

## Dependencies and Integration Points

The file integrates with XDP and tc verifier packet-access logic plus helper prototypes that accept packet memory. It complements direct packet access tests by validating the same safety properties at helper call boundaries.

## Risks and Test Signals

Risks include helpers reading past packet_end, accepting packet_end as a data pointer, losing packet range proof in subprograms, or rejecting valid bounded helper access. Test signals are success for valid ranges and exact failures for unchecked packets, bad ranges, unsuitable helpers, negative sizes, and wrong pointer base types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_packet_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_restricted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_restricted.c

## Purpose

`verifier_helper_restricted.c` verifies helper restrictions for tracing program types. It ensures `bpf_ktime_get_coarse_ns` and `bpf_spin_lock` remain forbidden in kprobe, tracepoint, perf_event, and raw_tracepoint programs when policy says they are not available.

## Important APIs, Types, and Functions

The file declares a `map_spin_lock` map value containing a spin lock for spin-lock tests. It defines eight programs across `SEC("kprobe")`, `SEC("tracepoint")`, `SEC("perf_event")`, and `SEC("raw_tracepoint")`. Four call the restricted time helper; four use `bpf_spin_lock` on the map value. Expected messages are helper-not-allowed and tracing-progs-cannot-use-spin-lock diagnostics.

## Control Flow

Each program performs the minimum setup required for the restricted operation and then returns. The time-helper variants call the helper directly. The spin-lock variants look up the map value, derive the lock address, and attempt to lock it from a tracing context.

## State and Persistence Behavior

The spin-lock map is persistent while the object is loaded. The verifier must track map-value lock fields and program-type helper allowlists; no runtime mutation should happen because all programs are rejected.

## Dependencies and Integration Points

The file integrates with helper allowlist tables, spin-lock verifier restrictions, and map-value BTF layout for `struct bpf_spin_lock`. It is a policy regression test rather than an algorithmic runtime test.

## Risks and Test Signals

Risks are accidentally enabling restricted helpers in tracing contexts or changing diagnostics without updating tests. Test signals are eight failures with the expected helper restriction messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_restricted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_value_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_value_access.c

## Purpose

`verifier_helper_value_access.c` tests helper access to map values with fixed, adjusted, and variable offsets and sizes. It verifies range proofs for full, partial, empty, out-of-bounds, negative, and signed/unsigned comparison cases, plus map helper read/write size validation.

## Important APIs, Types, and Functions

Maps include `map_hash_16b`, `map_hash_48b`, and `map_hash_8b`. The 45 tracepoint programs use helper calls such as `bpf_trace_printk` and map lookup/update helpers through inline assembly. Diagnostics cover invalid zero-sized reads, map-value bounds, negative minimum values, unbounded memory access, and wrong value sizes.

## Control Flow

The first group passes map-value pointers and sizes directly to helpers, varying range width and lower bound. The second and third groups adjust the pointer by constants or constant registers before helper access. The variable group adjusts by a runtime value and uses max/min checks to prove or fail safety. Later tests compare `<`, `<=`, signed `<`, and signed `<=` proof quality, then exercise map lookup/update helper arguments and adjusted map pointers with 16-byte values.

## State and Persistence Behavior

Persistent state is the three hash maps. Runtime state is verifier-only: map-value pointer base, fixed offset, variable offset, size ranges, signedness proofs, and whether a helper reads from or writes to map value memory.

## Dependencies and Integration Points

The file integrates with map helper prototypes, generic helper memory validators, and scalar range analysis. It complements variable-length stack tests by focusing on map-value boundaries.

## Risks and Test Signals

Risks are accepting reads/writes beyond a map value, treating possibly empty reads as safe, losing signed range information, or rejecting safe adjusted pointers. Test signals are successes for bounded full/partial accesses and failures for zero-sized invalid reads, negative ranges, unbounded memory, and wrong helper value sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_value_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_int_ptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_int_ptr.c

## Purpose

`verifier_int_ptr.c` tests helper arguments that write an integer-sized result through a pointer, specifically pointer-to-long behavior for `bpf_strtoul`. It distinguishes initialized, uninitialized, partially initialized, misaligned, and undersized stack slots.

## Important APIs, Types, and Functions

The file defines five programs in socket and cgroup/sysctl sections. All relevant helper interactions use `bpf_strtoul`, which parses a string and writes a `long` result to a caller-provided stack pointer. Expected failures cover misaligned stack access and an invalid 8-byte write into too-small stack storage.

## Control Flow

The success cases set up a stack buffer and pass a result pointer that is either uninitialized, half-uninitialized, or fully initialized; because the helper writes the full long, previous initialization is not always required. The negative cases deliberately use an unaligned pointer or reserve less than `sizeof(long)` bytes before passing it to the helper.

## State and Persistence Behavior

No maps are declared. The relevant state is stack slot initialization, alignment, and byte-range availability. The helper overwrites the target long but still requires an aligned and sufficiently large writable stack area.

## Dependencies and Integration Points

The file integrates with cgroup sysctl helper availability, socket program loading, and verifier stack write validation for helper output arguments.

## Risks and Test Signals

Risks are helper writes corrupting adjacent stack memory, accepting unaligned long pointers, or wrongly requiring pre-initialization for full overwrite outputs. Test signals are three successful pointer-to-long cases and two failures for misalignment and insufficient stack size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_int_ptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_iterating_callbacks.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_iterating_callbacks.c

## Purpose

`verifier_iterating_callbacks.c` is a large regression suite for verifier reasoning across iterating callbacks and bounded loop constructs. It covers `bpf_loop`, `bpf_for_each_map_elem`, `bpf_user_ringbuf_drain`, `bpf_find_vma`, numeric open-coded iterators, `may_goto`, loop detection, widening, state pruning, and constant-addition range propagation.

## Important APIs, Types, and Functions

The file includes `bpf_misc.h` and `bpf_experimental.h`. It declares small maps, a ringbuf, and several `.data` arrays. Helpers and kfunc-like iterator APIs include `bpf_loop`, `bpf_for_each_map_elem`, `bpf_user_ringbuf_drain`, `bpf_find_vma`, `bpf_get_current_task_btf`, `bpf_probe_read_user`, `bpf_iter_num_new`, `bpf_iter_num_next`, and `bpf_iter_num_destroy`. Some tests use `BPF_F_TEST_STATE_FREQ` to stress state exploration.

## Control Flow

Callback tests deliberately make memory safe on the first iteration but unsafe on later iterations, unsafe at zero iterations, or widening-sensitive. Other tests verify loop detection through helper callbacks and `may_goto`. Numeric iterator tests create nested iteration limits, validate successful bounded summations, and exercise known corner cases. Later programs check that adding constants to map-value pointers through several registers remains bounded or is rejected when range proofs are insufficient.

## State and Persistence Behavior

Persistent state is map/ringbuf/global data. Verifier state includes callback entry snapshots, iteration count bounds, loop convergence, map-value ranges across repeated callback invocations, iterator lifetime state, and register equivalence after constant additions.

## Dependencies and Integration Points

The file integrates with helper callback verification, open-coded iterator support, ringbuf callbacks, VMA callbacks, may-goto instruction support, and state-pruning heuristics. It is sensitive to verifier complexity limits and state-frequency test flags.

## Risks and Test Signals

Risks include accepting programs safe only on the first callback iteration, false infinite-loop detection, iterator lifetime leaks, or imprecise range widening that hides out-of-bounds map access. Test signals include expected failures for invalid map-value access and infinite loops, plus successful bounded iterator and may-goto cases with declared return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_iterating_callbacks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jeq_infer_not_null.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jeq_infer_not_null.c

## Purpose

`verifier_jeq_infer_not_null.c` tests branch inference that converts nullable pointer types to non-null pointer types after equality or inequality comparisons. It covers socket pointers returned in cgroup/skb programs and map-value pointers in XDP programs.

## Important APIs, Types, and Functions

The file defines an XSKMAP named `map_xskmap` and seven programs. Four cgroup/skb programs check `PTR_TO_SOCKET_OR_NULL` behavior after `JNE` and `JEQ` branches. Three XDP programs check `PTR_TO_MAP_VALUE_OR_NULL` and register-register null comparisons. Expected unprivileged failures mention pointer comparison; expected privileged failures mention invalid access to `sock_or_null`.

## Control Flow

Socket tests obtain a nullable socket pointer, compare it against zero or another register, and then dereference either the branch where non-null can be inferred or the branch where null remains possible. Map-value tests perform lookup-like operations, compare result registers to null, and dereference only after the verifier should have refined the type.

## State and Persistence Behavior

Persistent state is the XSKMAP. Verifier state tracks nullable pointer ids, branch predicates, equality between registers, and type refinement from `*_OR_NULL` to concrete pointer types.

## Dependencies and Integration Points

The file integrates with cgroup socket helpers/context, XDP map-value lookup semantics, and verifier branch-state splitting. It is also tied to unprivileged restrictions on pointer comparisons.

## Risks and Test Signals

Risks are failing to refine non-null pointers on the correct branch, refining the wrong branch, or allowing unprivileged pointer comparisons. Test signals are success for true non-null branches, failure for unchanged nullable dereference, and verifier log messages showing dereference after null-check branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jeq_infer_not_null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jit_convergence.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jit_convergence.c

## Purpose

`verifier_jit_convergence.c` tests a JIT convergence corner case where conditional and unconditional jump layout can change instruction sizes across JIT passes. It guards against a case where `je` and `jmp` relaxation oscillate rather than converging.

## Important APIs, Types, and Functions

The file declares `map_hash` and a single socket program `btf_jit_convergence_je_jmp`. The program uses a long inline-assembly control-flow layout with a map lookup and many branches, designed to stress JIT branch displacement decisions. It returns zero on success.

## Control Flow

The program performs map-related setup, branches through a carefully arranged sequence, and reaches a final return only if the verifier and JIT agree on the control-flow graph. The source is intentionally structural rather than algorithmic; instruction placement is the test vector.

## State and Persistence Behavior

Persistent state is the hash map definition. Runtime map contents are not central. The tested state is JIT compiler pass state, especially branch displacement and instruction-size convergence.

## Dependencies and Integration Points

The file integrates with the verifier, the architecture JIT backend, and selftest execution on JIT-enabled kernels. It is most valuable for backends that perform branch relaxation or multi-pass code generation.

## Risks and Test Signals

Risks are JIT non-convergence, incorrect branch target emission, or interpreter/JIT behavior mismatch. The test signal is successful program load and execution returning zero without JIT convergence errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jit_convergence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jit_inline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jit_inline.c

## Purpose

`verifier_jit_inline.c` is a minimal fentry test for helper inlining/JIT handling of `bpf_get_current_task`. It verifies a tracing program can call the helper and return successfully.

## Important APIs, Types, and Functions

The single program `inline_bpf_get_current_task` attaches to `SEC("fentry/bpf_fentry_test1")`. It includes `vmlinux.h`, libbpf helpers, and `bpf_misc.h`. The only helper is `bpf_get_current_task`.

## Control Flow

The program calls `bpf_get_current_task`, discards or minimally uses the result, and returns zero. The small body is intentional: it isolates helper-call lowering and JIT inline behavior from other verifier concerns.

## State and Persistence Behavior

There are no maps. Runtime state is the current task pointer returned by the helper, which must not persist after program exit.

## Dependencies and Integration Points

The file depends on fentry attachment and helper availability. It integrates with JIT/helper call lowering and tracing selftest targets.

## Risks and Test Signals

Risks are helper inlining regressions or fentry helper availability changes. The test signal is a successful load with return value zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_jit_inline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_kfunc_prog_types.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_kfunc_prog_types.c

## Purpose

`verifier_kfunc_prog_types.c` verifies that selected kfunc families are available across supported program types. It covers task, cgroup, and cpumask kfunc load paths in raw tracepoint, syscall, tracepoint, and perf_event programs.

## Important APIs, Types, and Functions

The file includes common headers for cgroup, cpumask, and task kfunc tests. It defines three reusable test bodies: task kfunc load, cgroup kfunc load, and cpumask kfunc load. APIs include `bpf_get_current_task_btf`, `bpf_task_acquire`, `bpf_task_from_pid`, `bpf_task_release`, `bpf_cgroup_from_id`, `bpf_cgroup_acquire`, `bpf_cgroup_release`, `bpf_cpumask_create`, `bpf_cpumask_acquire`, `bpf_cpumask_set_cpu`, `bpf_cpumask_test_cpu`, and `bpf_cpumask_release`.

## Control Flow

Each program type invokes the same family-specific sequence: acquire or create an object, perform a simple operation, and release it. There are 12 success programs, three kfunc families multiplied by four program types.

## State and Persistence Behavior

No maps are declared. Runtime state is temporary refcounted task, cgroup, or cpumask objects. Correct behavior requires release on all paths and no persistent references after program exit.

## Dependencies and Integration Points

The file integrates with BTF kfunc registration, per-program-type kfunc allowlists, reference tracking, task/cgroup/cpumask kernel subsystems, and selftest common helper headers.

## Risks and Test Signals

Risks are missing kfunc allowlist entries for a supported program type, incorrect reference tracking, or cpumask allocation/release mismatch. Test signals are successful load of all raw_tp, syscall, tracepoint, and perf_event variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_kfunc_prog_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ld_ind.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ld_ind.c

## Purpose

`verifier_ld_ind.c` tests classic packet load instructions `LD_ABS` and `LD_IND`, including calling convention constraints, subprogram early-exit behavior on load failure, and rejection of void-returning subprograms that use these instructions.

## Important APIs, Types, and Functions

The file includes `filter.h` and uses `bpf_gen_ld_abs` for classic load instruction generation. It defines 12 socket programs and several naked subprograms. Expected diagnostics include unreadable registers `R1` through `R5`, `R9 !read_ok`, and `LD_ABS is only allowed in functions that return 'int'`.

## Control Flow

The calling-convention tests arrange register liveness around `LD_IND` and verify that only allowed registers remain readable after the instruction sequence. Subprogram tests call helpers that perform `LD_ABS` or `LD_IND`, then either require early exit on failure or prove both paths safe. Void-return subprograms deliberately violate the rule that classic packet load instructions may only appear in int-returning functions.

## State and Persistence Behavior

There are no maps. Runtime state is packet data accessed by classic load instructions. Verifier state tracks register invalidation/readability after `LD_ABS/LD_IND`, subprogram return type, and failure propagation.

## Dependencies and Integration Points

The file integrates with socket filter program semantics, classic BPF packet load translation, verifier register liveness rules, and subprogram validation.

## Risks and Test Signals

Risks include allowing stale registers after packet loads, failing to enforce early-exit requirements, or accepting classic loads in void subprograms. Test signals are the expected failures for unreadable registers and void returns, plus successes for safe subprogram paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ld_ind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ldsx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ldsx.c

## Purpose

`verifier_ldsx.c` tests signed load-extension (`LDSX`) instructions. It checks S8, S16, and S32 sign extension, verifier range refinement, invalid signed loads from context fields, arena disassembly and exceptions, and CPU-version fallback behavior.

## Important APIs, Types, and Functions

The file includes `bpf_arena_common.h` and defines an `arena` map. Program sections include socket, XDP, tcx ingress, flow_dissector, syscall, and a dummy socket fallback. Helper coverage includes `bpf_arena_alloc_pages`; arena tests use kfunc/root-style setup for allocated arena pages. Expected logs include scalar range after S8 load and invalid context-access messages for sign-extending packet context fields.

## Control Flow

Initial socket programs place negative byte, halfword, or word values on the stack and load them with sign extension, returning negative values. Range tests prove the verifier narrows S8/S16/S32 results. Context tests attempt signed 32-bit loads from fields such as `xdp_md->data`, `data_end`, `data_meta`, and `__sk_buff` equivalents, expecting rejection. Arena syscall programs allocate arena memory and exercise LDSX disassembly, exception, and signed loads from arena pages.

## State and Persistence Behavior

Persistent state is the arena map. Runtime arena pages are allocated during syscall programs and used transiently. Verifier state includes signed load result ranges, context field access permissions, and arena pointer bounds.

## Dependencies and Integration Points

The file depends on compiler/JIT support for the relevant BPF CPU version, arena map support, and program-type context validators for XDP, tcx, and flow dissector.

## Risks and Test Signals

Risks are incorrect sign extension, unsound signed range narrowing, allowing unsupported signed ctx loads, or arena/JIT exception mismatches. Test signals are correct negative return values, expected range log for S8, invalid context access failures, arena successes, and dummy success when CPU v4 support is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ldsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_leak_ptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_leak_ptr.c

## Purpose

`verifier_leak_ptr.c` tests pointer leak prevention to contexts and map values. It distinguishes privileged verifier behavior from unprivileged restrictions and checks atomic stores, direct ctx writes, and map-value writes involving pointer-typed registers.

## Important APIs, Types, and Functions

The file declares `map_hash_8b` and four socket programs. Test cases attempt to store pointer values into ctx memory or map value memory. Metadata records privileged failures for atomic ctx stores and unprivileged failures such as `R2 leaks addr into mem`, `R10 leaks addr into mem`, `R2 leaks addr into ctx`, and `R6 leaks addr into mem`.

## Control Flow

The first two tests use BPF atomic store forms targeting ctx memory, which are rejected in privileged mode and additionally flagged as pointer leaks in unprivileged mode. The third writes a pointer into ctx through a non-atomic path that privileged mode accepts but unprivileged mode rejects. The final test obtains a map value and writes a pointer into it, again permitted only in privileged mode by the declared expectations.

## State and Persistence Behavior

Persistent state is the hash map. Runtime state includes pointer-valued registers such as stack/frame pointers or map-value pointers. The verifier must prevent unprivileged programs from materializing kernel addresses in memory visible after execution.

## Dependencies and Integration Points

The file integrates with unprivileged verifier policy, pointer leak checks, atomic store validation, ctx write permissions, and map-value access rules.

## Risks and Test Signals

Risks are kernel address disclosure to unprivileged BPF, over-restricting privileged programs, or allowing atomic ctx stores. Test signals are the declared privileged and unprivileged outcomes and exact leak diagnostics for memory, ctx, and map-value destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_leak_ptr.c -->
