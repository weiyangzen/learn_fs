# Research: subset-b-006813

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta.h

Purpose: Shared Strobelight metadata BPF program body used by the small configuration wrappers; it samples stacks on `raw_tracepoint/kfree_skb` and conditionally copies thread-local integer, string, and map metadata into perf-event samples.

Important APIs/types/functions: Defines strobe value/map/config/payload/sample structs, `samples`, `stacks_0`, `stacks_1`, `sample_heap`, `strobemeta_cfgs`, TLS helpers `calc_location`, readers `read_int_var`, `read_str_var`, `read_map_var`, optional `read_var_callback`, `read_strobe_meta`, and `on_event`.

Control flow: `on_event` fetches a per-CPU sample, records pid/comm/time, resolves current task as TLS base, calls `read_strobe_meta`, alternates stack-trace maps by epoch bit, and submits the used sample prefix. Metadata reading looks up pid config, walks configured int/string/map slots through unrolled loops, no-unroll loops, or `bpf_loop`, and maintains a packed payload offset.

State and persistence: Persistent state is entirely in BPF maps and globals: per-pid metadata configs, stack trace tables, per-CPU heap sample, and perf output ring. It reads user TLS/GOT/dtv memory but does not mutate user state.

Dependencies and integration: Depends on BPF helpers for map lookup, user reads, stack ids, current task, comm, ktime, perf output, plus `bpf_compiler.h` loop pragmas and wrapper-provided `STROBE_MAX_*` constants.

Risks: Verifier-sensitive pointer arithmetic, payload bounds, TLS ABI assumptions for x86-64/aarch64, `bpf_probe_read_user_str` error casting, large loop bounds, and exact sample-size calculation are the main hazards.

Test signals: Wrapper variants should load successfully and report expected metadata, stack ids, and payload lengths; negative signals include verifier rejection for imprecise offsets or out-of-bounds payload writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_bpf_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_bpf_loop.c

Purpose: Builds the Strobelight metadata program with `USE_BPF_LOOP`, 2 ints, 25 strings, 100 maps, and 20 map entries to exercise helper-driven bounded iteration.

Important APIs/types/functions: Provides only preprocessor constants and includes `strobemeta.h`; the exported BPF maps/programs come from the header, especially `read_var_callback` and `on_event`.

Control flow: The included header routes int, string, and map scans through three `bpf_loop` calls with a shared callback context and payload offset.

State and persistence: State is the common strobemeta maps; this wrapper changes only compile-time loop strategy and capacities.

Dependencies and integration: Depends on kernels/verifier support for `bpf_loop` and the common strobemeta header.

Risks: Large map-slot count stresses callback precision, `payload_off` tracking, and `bpf_loop` return-count validation.

Test signals: Expected signal is successful load and metadata extraction with high map capacity; verifier failures around imprecise scalar offsets are regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_bpf_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll1.c

Purpose: Builds strobemeta with non-unrolled loops and moderate map count to test verifier handling without forced loop unrolling.

Important APIs/types/functions: Defines `STROBE_MAX_INTS=2`, `STROBE_MAX_STRS=25`, `STROBE_MAX_MAPS=13`, `STROBE_MAX_MAP_ENTRIES=20`, `NO_UNROLL`, then includes `strobemeta.h`.

Control flow: The included `read_strobe_meta` uses pragma no-unroll loops for ints, strings, maps, and per-map entries.

State and persistence: Uses the common strobemeta BPF maps and perf output; no local state beyond compile-time bounds.

Dependencies and integration: Depends on bounded-loop verifier support and the shared header.

Risks: Verifier loop bound inference and payload bounds must survive without unrolling.

Test signals: Load success and correct sample metadata for the 13-map configuration are the primary test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll2.c

Purpose: Second non-unrolled strobemeta build with larger map count to extend bounded-loop stress coverage.

Important APIs/types/functions: Sets 2 ints, 25 strings, 30 maps, 20 entries, `NO_UNROLL`, and includes `strobemeta.h`.

Control flow: Same header control flow as the first no-unroll variant, but with a larger outer map loop.

State and persistence: No unique persistence; all runtime data remains in `strobemeta_cfgs`, stack maps, sample heap, and perf events.

Dependencies and integration: Depends on common strobemeta code and verifier bounded-loop support.

Risks: Higher map count increases payload-capacity and loop-state pressure.

Test signals: Verifier load success and absence of payload-bound failures distinguish this variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_subprogs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_subprogs.c

Purpose: Builds strobemeta with no-unroll loops and selected helpers emitted as BPF subprograms to exercise call-stack and subprog verification.

Important APIs/types/functions: Defines the nounroll constants plus `SUBPROGS`, causing `calc_location`, `read_int_var`, and `read_strobe_meta` to be `__noinline`.

Control flow: Runtime flow is the common strobemeta path, but metadata collection crosses BPF-to-BPF calls instead of being fully inlined.

State and persistence: Common strobemeta maps and sample state only.

Dependencies and integration: Depends on BPF subprogram support and the shared header.

Risks: Private stack usage, pointer/refinement preservation across calls, and loop bounds across subprograms are the important verifier risks.

Test signals: Successful program load with metadata enabled validates call-boundary tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_subprogs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc.c

Purpose: Tests association between multiple `bpf_testmod_multi_st_ops` struct_ops maps and kfunc dispatch from syscall and tracepoint contexts.

Important APIs/types/functions: Defines two `.struct_ops.link` maps, `test_1_a`/`test_1_b`, syscall programs, tp_btf `sys_enter` programs, magic return globals, and error counters.

Control flow: Each struct_ops callback returns its map-specific magic. The syscall and tracepoint programs call `bpf_kfunc_multi_st_ops_test_1_assoc` and compare the result against the map they are associated with.

State and persistence: Persistent state is limited to global `test_pid`, `test_err_a`, and `test_err_b`; struct_ops maps are linked objects.

Dependencies and integration: Integrates with `bpf_testmod` multi struct_ops and its kfunc association machinery.

Risks: Wrong map-to-program association, pid filtering mistakes, or kfunc dispatch returning the other map magic would indicate regression.

Test signals: User tests load both maps, trigger syscall/tracepoint paths for `test_pid`, and expect zero error counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc_in_timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc_in_timer.c

Purpose: Verifies a struct_ops-associated kfunc can be called from a BPF timer callback scheduled by a struct_ops operation.

Important APIs/types/functions: Defines `array_map` with `struct bpf_timer`, timer callback `timer_cb`, struct_ops callback `test_1`, `syscall_prog`, and counters `recur`, `timer_cb_run`, `timer_test_1_ret`, `test_err`.

Control flow: `test_1` starts a timer unless already recursing; `timer_cb` calls the associated kfunc and records its return; syscall path performs a direct association check.

State and persistence: The array map persists timer storage, and globals record callback execution and errors.

Dependencies and integration: Depends on BPF timers, struct_ops link maps, and bpf_testmod association kfuncs.

Risks: Timer recursion protection and correct association in timer context are the key risks.

Test signals: A passing test observes timer callback execution, magic return value, and no syscall error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc_in_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc_reuse.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc_reuse.c

Purpose: Checks reusing the same struct_ops program in more than one linked map while preserving each map association.

Important APIs/types/functions: Defines callbacks and syscall programs for map A and B, with two `.struct_ops.link` instances using associated test callbacks.

Control flow: Syscall programs invoke the association kfunc and verify map-specific magic values, similar to `struct_ops_assoc.c` but focused on reuse behavior.

State and persistence: Globals hold error counters; linked struct_ops maps persist attachment identity.

Dependencies and integration: Uses bpf_testmod multi struct_ops and association kfunc support.

Risks: A reused program must not inherit stale association metadata from another map.

Test signals: Tests load both links and verify no map-specific error counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_assoc_reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate.c

Purpose: Exercises libbpf auto-create and optional handling for module struct_ops maps with compatible and incompatible local type flavors.

Important APIs/types/functions: Defines `test_1`, `test_2`, v1/v2 local `bpf_testmod_ops` shapes, two required `.struct_ops.link` maps, and optional `?.struct_ops` maps.

Control flow: Callbacks are simple; the load path is the behavior under test, especially whether libbpf creates/link maps and skips optional ones correctly.

State and persistence: Global `test_1_result` records callback execution; map existence/link state is managed by libbpf.

Dependencies and integration: Depends on struct_ops section naming, BTF type compatibility, and optional section semantics.

Risks: Incompatible callback fields or optional map handling can cause unexpected load failures.

Test signals: Expected signals are successful skeleton open/load and callback setting `test_1_result=42` where invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate2.c

Purpose: Companion auto-create test using optional `?struct_ops/test_1` program sections and a required link map.

Important APIs/types/functions: Defines two optional test callbacks and a `.struct_ops.link` `bpf_testmod_ops` map.

Control flow: Load-time section processing determines whether optional callbacks are accepted; runtime callback flow is trivial.

State and persistence: No durable state beyond struct_ops link objects and callback return values.

Dependencies and integration: Depends on libbpf optional program sections and bpf_testmod ops BTF.

Risks: Optional callback resolution must not fail the whole object when a target is unavailable.

Test signals: Tests validate load/link behavior rather than complex runtime state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_detach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_detach.c

Purpose: Tests detach behavior when a linked struct_ops map references a callback/subprogram that should become dangling after detach.

Important APIs/types/functions: Defines `dangling_subprog` and a `.struct_ops.link` map for `bpf_testmod_ops`.

Control flow: There is no active BPF program flow in the file; loader/link detach operations exercise lifetime handling.

State and persistence: Struct_ops link lifetime is the persistent state under test.

Dependencies and integration: Depends on bpf_testmod ops and libbpf struct_ops link detach handling.

Risks: Dangling callback references after detach can cause use-after-free or verifier/link cleanup bugs.

Test signals: A passing test detaches without kernel warnings and rejects or cleans dangling references correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_detach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_forgotten_cb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_forgotten_cb.c

Purpose: Verifies behavior when a struct_ops map omits or forgets expected callback wiring.

Important APIs/types/functions: Defines one `struct_ops/test_1` callback and a linked `bpf_testmod_ops` map.

Control flow: Load/link path checks callback discovery and map initialization; callback body itself is trivial.

State and persistence: State is the struct_ops link object only.

Dependencies and integration: Depends on bpf_testmod ops BTF and libbpf callback-to-field assignment.

Risks: Missing callback registration or wrong field assignment is the risk.

Test signals: Test signal is successful expected attach semantics or intended loader rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_forgotten_cb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_id_ops_mapping1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_id_ops_mapping1.c

Purpose: One half of a pair testing stable id-to-ops mapping for `bpf_testmod_multi_st_ops`.

Important APIs/types/functions: Defines one struct_ops callback, a tp_btf `sys_enter` verifier, syscall verifier, a linked map, and an error counter.

Control flow: Verifier programs call the association kfunc and compare returned magic against the callback selected by the linked ops id.

State and persistence: Globals persist test pid and error count; map link holds ops identity.

Dependencies and integration: Depends on bpf_testmod multi ops ids and kfunc dispatch.

Risks: Ops-id mapping collisions or ordering changes can make the wrong callback run.

Test signals: Run with mapping2 to validate independent objects produce correct per-id behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_id_ops_mapping1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_id_ops_mapping2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_id_ops_mapping2.c

Purpose: Second mapping object for the multi struct_ops id-to-ops mapping regression test.

Important APIs/types/functions: Same shape as mapping1: struct_ops callback, tracepoint/syscall checkers, linked map, and error globals.

Control flow: It independently exercises association dispatch so userspace can load two objects and compare ids.

State and persistence: Global counters and struct_ops link state are the only persistence.

Dependencies and integration: Depends on bpf_testmod multi ops and libbpf struct_ops linking.

Risks: Wrong id assignment across separately loaded objects is the primary risk.

Test signals: Passing tests see each object return its own magic and no error increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_id_ops_mapping2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return.c

Purpose: Positive test for returning a referenced kernel pointer from a struct_ops callback.

Important APIs/types/functions: Defines a `struct_ops/test_return_ref_kptr` callback returning a `struct task_struct *` and a linked `bpf_testmod_ops` map.

Control flow: The callback returns an accepted referenced kptr in the shape expected by the testmod op.

State and persistence: No mutable state beyond the link map.

Dependencies and integration: Depends on verifier support for struct_ops kptr return types and task kptr lifetime rules.

Risks: The verifier must enforce exact trusted referenced pointer return semantics.

Test signals: Success is load/attach without verifier complaints and correct testmod callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__invalid_scalar.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__invalid_scalar.c

Purpose: Negative verifier test returning an invalid scalar where a referenced kptr is required.

Important APIs/types/functions: Contains a `struct_ops/test_return_ref_kptr` callback annotated with expected verifier messages and a linked map.

Control flow: The callback deliberately produces the wrong return kind to force verifier rejection.

State and persistence: No runtime state should persist because load is expected to fail.

Dependencies and integration: Depends on `bpf_misc.h` failure annotations and testmod kptr-return op BTF.

Risks: If accepted, verifier kptr return validation is broken.

Test signals: Expected test signal is the annotated verifier error, not runtime execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__invalid_scalar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__local_kptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__local_kptr.c

Purpose: Negative test for returning a local kptr/object instead of an allowed referenced kernel pointer.

Important APIs/types/functions: Defines a failing struct_ops kptr-return callback and link map.

Control flow: Control flow constructs or selects a local pointer and returns it to the struct_ops ABI.

State and persistence: No successful runtime persistence is expected.

Dependencies and integration: Depends on verifier return-type tracking for local kptrs.

Risks: Accepting stack/local kptr returns would violate lifetime safety.

Test signals: Verifier rejection with the expected message is the pass condition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__local_kptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__nonzero_offset.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__nonzero_offset.c

Purpose: Negative test for returning a referenced kptr with a nonzero offset.

Important APIs/types/functions: Defines a failing `test_return_ref_kptr` callback and linked map.

Control flow: The callback returns an offset pointer rather than the base kptr.

State and persistence: No runtime state should exist after expected load failure.

Dependencies and integration: Depends on struct_ops return verifier and BTF pointer-offset tracking.

Risks: Nonzero-offset kptr returns can corrupt object lifetime/type interpretation if accepted.

Test signals: Expected verifier rejection mentions invalid offset or pointer type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__nonzero_offset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__wrong_type.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__wrong_type.c

Purpose: Negative test for returning the wrong referenced kptr type from a struct_ops callback.

Important APIs/types/functions: Declares local kernel types such as `cgroup` and `task_struct`, then wires a failing callback into `bpf_testmod_ops`.

Control flow: Callback return value has reference semantics but not the exact expected BTF type.

State and persistence: No persistent runtime state is expected.

Dependencies and integration: Depends on BTF type identity checks for struct_ops kptr returns.

Risks: Type-compatible-looking but wrong kptrs must be rejected.

Test signals: Pass signal is expected verifier error for wrong return type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__wrong_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_maybe_null.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_maybe_null.c

Purpose: Positive test for struct_ops callback arguments that may be NULL.

Important APIs/types/functions: Defines `struct_ops/test_maybe_null` callback and linked `bpf_testmod_ops` map.

Control flow: Callback checks or tolerates the nullable task argument and returns according to testmod expectations.

State and persistence: No durable state beyond link map.

Dependencies and integration: Depends on bpf_testmod nullable argument annotation and verifier nullability tracking.

Risks: Verifier must allow guarded nullable access but preserve NULL checks.

Test signals: Successful load and callback execution are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_maybe_null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_maybe_null_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_maybe_null_fail.c

Purpose: Negative nullable-pointer test for a struct_ops callback that dereferences maybe-NULL data unsafely.

Important APIs/types/functions: Defines a `struct_ops/test_maybe_null_struct_ptr` callback with expected failure behavior and a link map.

Control flow: The callback uses a maybe-null struct pointer without sufficient validation.

State and persistence: No successful runtime state is expected.

Dependencies and integration: Depends on verifier nullable pointer diagnostics.

Risks: If accepted, struct_ops nullable argument enforcement regressed.

Test signals: Expected test signal is verifier rejection with the annotated diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_maybe_null_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_module.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_module.c

Purpose: Covers module-backed bpf_testmod struct_ops loading, multiple callback signatures, optional callbacks, zeroed fields, and incompatible local struct flavors.

Important APIs/types/functions: Defines `test_1`, `test_2`, optional `test_3`, v2/zeroed/incompatible local ops structs, and several `.struct_ops.link` maps.

Control flow: Callbacks update globals or return computed values; most behavior is in load/link type matching and how zeroed/missing fields are interpreted.

State and persistence: Globals `test_1_result` and `test_2_result` persist callback effects; linked maps persist selected ops variants.

Dependencies and integration: Depends on bpf_testmod module BTF, libbpf CO-RE flavor matching, and struct_ops link creation.

Risks: Module BTF absence, incompatible callback prototypes, or optional section handling can change expected outcomes.

Test signals: Tests load valid maps, expect incompatible maps to fail when intended, and verify callback result globals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_multi_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_multi_args.c

Purpose: Negative test around struct_ops refcounted callback with many arguments and a tail-call map present.

Important APIs/types/functions: Defines `prog_array`, a `test_refcounted_multi` callback annotated for expected verifier failure, and a linked map.

Control flow: The callback path is crafted to expose verifier restrictions for multi-argument referenced kptr handling.

State and persistence: No successful runtime state is intended.

Dependencies and integration: Depends on bpf_testmod refcounted multi-argument op, prog-array map, and failure annotations.

Risks: Verifier must not lose reference ownership across argument slots or helper/tail-call possibilities.

Test signals: Pass signal is expected verifier rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_multi_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_multi_pages.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_multi_pages.c

Purpose: Stress object containing a very large struct_ops map definition spanning many pages.

Important APIs/types/functions: Defines a large `bpf_testmod_ops` instance in `.struct_ops.link` with many fields or padding generated by source layout.

Control flow: No complex callback flow; load/link size handling is the target.

State and persistence: Persistent state is the large linked struct_ops map object.

Dependencies and integration: Depends on libbpf/kernel handling of multi-page struct_ops value data.

Risks: Large value copying, BTF layout, or page-boundary bugs are the risks.

Test signals: Successful load/link without truncation or kernel fault is the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_multi_pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_nulled_out_cb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_nulled_out_cb.c

Purpose: Verifies a struct_ops callback field that is nulled out behaves as intended.

Important APIs/types/functions: Defines `struct_ops/test_1` and a linked `bpf_testmod_ops` map with callback configuration under test.

Control flow: Callback execution is simple; loader/map initialization around NULL callback fields is the focus.

State and persistence: State is link-map callback table plus any result global.

Dependencies and integration: Depends on bpf_testmod ops and struct_ops link initialization.

Risks: Incorrectly accepting or invoking nulled callbacks can hide loader/kernel bugs.

Test signals: Test expects the chosen callback to be invoked or absent according to map setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_nulled_out_cb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack.c

Purpose: Positive test for private stack accounting across struct_ops callbacks and BPF subprogram calls.

Important APIs/types/functions: Defines `subprog1`, `subprog2`, callbacks `test_1`/`test_2`, globals `val_i`/`val_j`, and a `.struct_ops` map.

Control flow: `test_1` allocates a 400-byte stack array, calls `subprog1`, then invokes another testmod op; `test_2` uses a 200-byte stack path.

State and persistence: Globals persist computed values; struct_ops map stores callback pointers.

Dependencies and integration: Depends on bpf_testmod ops3 and verifier private-stack support for struct_ops programs.

Risks: Stack depth across callbacks/subprogs must be accounted without false sharing or overflow.

Test signals: Passing tests see load success and expected values after testmod invokes both callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_fail.c

Purpose: Negative counterpart for private-stack verifier limits in struct_ops programs.

Important APIs/types/functions: Same broad shape as the positive private-stack test, with stack usage arranged to exceed allowed limits or violate private-stack rules.

Control flow: Nested callbacks/subprograms drive the excessive stack scenario.

State and persistence: No successful runtime persistence is expected.

Dependencies and integration: Depends on private-stack verifier diagnostics and bpf_testmod ops3.

Risks: If accepted, stack-depth enforcement for struct_ops callbacks is too weak.

Test signals: Expected signal is verifier rejection rather than callback output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_recur.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_recur.c

Purpose: Tests recursive/private-stack interaction for struct_ops callbacks and subprograms.

Important APIs/types/functions: Defines `subprog1`, `subprog2`, a struct_ops callback, and a `.struct_ops` map.

Control flow: The callback/subprogram call graph is intentionally recursive or recursion-like to exercise verifier call graph handling.

State and persistence: Only globals and the link map would persist on successful load.

Dependencies and integration: Depends on verifier recursion detection and private-stack allocation logic.

Risks: Recursive struct_ops subprograms must not bypass stack limits.

Test signals: Expected test signal is the loader outcome encoded by the selftest annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_recur.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted.c

Purpose: Positive verifier test for referenced `task_struct *` arguments passed into struct_ops callbacks.

Important APIs/types/functions: Defines a `test_refcounted` callback that releases the task on both branches and a linked map.

Control flow: The callback receives a referenced task pointer and releases exactly once regardless of branch.

State and persistence: No durable state aside from the map link.

Dependencies and integration: Depends on bpf_testmod refcounted op and `bpf_task_release` kfunc.

Risks: Reference ownership must be tracked across branch joins.

Test signals: Pass signal is verifier acceptance and no reference leak.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__global_subprog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__global_subprog.c

Purpose: Negative test for releasing a refcounted struct_ops argument through a global subprogram.

Important APIs/types/functions: Defines `subprog_release`, failure log-level annotation, callback, and link map.

Control flow: The callback hands the referenced task to a global subprogram, exercising verifier restrictions on global subprog reference ownership.

State and persistence: No runtime state should persist after expected rejection.

Dependencies and integration: Depends on refcounted struct_ops args and verifier global-function reference rules.

Risks: Global subprograms must not obscure release ownership.

Test signals: Expected verifier log indicates the reference handling violation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__global_subprog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__ref_leak.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__ref_leak.c

Purpose: Negative test where a refcounted struct_ops argument is leaked.

Important APIs/types/functions: Defines a failing `test_refcounted` callback and link map.

Control flow: The callback exits without releasing the referenced task.

State and persistence: No successful runtime state is expected.

Dependencies and integration: Depends on verifier reference leak detection.

Risks: Accepting the program would leak task references from struct_ops callbacks.

Test signals: Expected verifier message reports unreleased reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__ref_leak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__tail_call.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__tail_call.c

Purpose: Negative test for tail calls while holding a refcounted struct_ops argument.

Important APIs/types/functions: Defines `prog_array`, failing refcounted callback, and link map.

Control flow: The callback attempts or exposes a tail-call path before reference ownership is safely released.

State and persistence: No runtime persistence is expected after failed load.

Dependencies and integration: Depends on prog-array tail-call verifier and struct_ops reference tracking.

Risks: Tail calls must not bypass mandatory release of referenced args.

Test signals: Pass signal is expected verifier rejection for reference leak/tail-call hazard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__tail_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization.c

Purpose: Verifier summarization test object for packet-data mutation and sleepable-state summaries across optional tc and uprobe programs.

Important APIs/types/functions: Defines helpers `changes_pkt_data`, `does_not_change_pkt_data`, sleep helpers, and main programs in `?tc` and `?uprobe.s` sections.

Control flow: Main programs call subprograms that either mutate packet data or may sleep, allowing verifier summary propagation to be observed.

State and persistence: No persistent maps; state is verifier metadata and return values.

Dependencies and integration: Depends on optional section annotations and verifier function-summary logic.

Risks: Incorrect summaries can allow invalid packet access after mutation or reject safe programs.

Test signals: Expected signals are section-specific verifier accept/reject outcomes from selftest annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization_freplace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization_freplace.c

Purpose: Freplace companion to `summarization.c`, replacing summarized functions to test update of verifier summaries through freplace attachments.

Important APIs/types/functions: Defines replacement functions for packet mutation and sleep behavior in `?freplace` sections.

Control flow: Each replacement body provides a simple mutation/sleeping or non-mutating/non-sleeping behavior for the target program.

State and persistence: No BPF maps or persistent runtime state.

Dependencies and integration: Depends on freplace attachment and verifier summary recomputation.

Risks: Wrong target summary can make freplace load outcomes unsound.

Test signals: Tests attach replacements and check expected verifier compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization_freplace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/syscall.c

Purpose: Exercises BPF syscall programs that invoke `bpf_sys_bpf`/`bpf_sys_close` to create BTF, maps, programs, and update map-in-map entries from BPF context.

Important APIs/types/functions: Defines `bpf_attr_array`, `inner_map`, `outer_array_map`, raw BTF construction helpers, `load_prog`, and `update_outer_map`.

Control flow: `load_prog` builds minimal BTF, creates a BTF-typed hash map, updates it, patches a raw instruction with the map fd, then loads an XDP program. `update_outer_map` obtains an outer map fd by id, creates a new inner map, updates then deletes the outer entry, and closes fds.

State and persistence: Persistent state includes created fds returned in `struct args`, the outer map contents during the update, and the attr scratch array.

Dependencies and integration: Depends on syscall program type, `union bpf_attr`, raw BTF layout, map-in-map support, and close semantics.

Risks: Fd lifetime, attr zeroing, BTF type ids, and map-in-map update/delete permissions are the main risks.

Test signals: Tests expect positive return, valid fds, no leaked fds, and successful outer-map update/delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall1.c

Purpose: Tests static tail-call patching when the same prog-array index appears at many call sites.

Important APIs/types/functions: Defines `jmp_table`, three tc classifiers returning 0/1/2, and `entry` with repeated static calls to indexes 0, 1, and 2.

Control flow: `entry` attempts each static tail call in order; a successful tail call transfers to the target classifier, otherwise it eventually returns 3.

State and persistence: Persistent state is the prog-array map populated by userspace.

Dependencies and integration: Depends on static tail-call patching in tc programs.

Risks: All call sites for the same index must be patched consistently.

Test signals: Tests populate indexes and assert observed return values match the selected classifier or fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall2.c

Purpose: Exercises chained static tail calls, multi-program updates, and tail-call limit behavior.

Important APIs/types/functions: Defines five classifiers and a five-entry `jmp_table`; classifiers 0/1 chain to 1/2 and 3/4 loop between each other.

Control flow: `entry` starts at index 0, then has fallback checks for index 2 and a 3/4 loop intended to hit limits.

State and persistence: State is the prog-array map only.

Dependencies and integration: Depends on static tail-call chaining and runtime tail-call count enforcement.

Risks: Improper call-limit handling can loop indefinitely or return wrong fallback.

Test signals: Tests update prog-array entries and check returns for chain and limit cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall3.c

Purpose: Small static tail-call test focused on a single populated target and fallback.

Important APIs/types/functions: Defines `jmp_table`, `classifier_0`, and `entry` in tc sections.

Control flow: `entry` tail-calls index 0 and otherwise returns its fallback value.

State and persistence: Prog-array contents are the only runtime state.

Dependencies and integration: Depends on tc static tail-call support.

Risks: Risk is incorrect patching or fallback path after missing entry.

Test signals: Pass signals are target return when present and fallback when absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall4.c

Purpose: Static tail-call edge-case test with a compact tc object and prog-array map.

Important APIs/types/functions: Defines a `jmp_table` and tc entry/classifier pair.

Control flow: Entry attempts a static tail call to a configured index and falls through on miss.

State and persistence: State is the prog-array map.

Dependencies and integration: Depends on static tail-call relocation and tc loading.

Risks: Map index or relocation mistakes change the observed return.

Test signals: Tests validate both populated and unpopulated prog-array behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall5.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall5.c

Purpose: Tail-call test variant covering static call behavior with a different map capacity/control path.

Important APIs/types/functions: Defines `jmp_table` and tc entry/classifier programs.

Control flow: The entry path attempts static tail calls and returns a fallback if no transfer occurs.

State and persistence: Only prog-array state persists.

Dependencies and integration: Depends on BPF prog-array and static tail-call patching.

Risks: Wrong max_entries or key relocation can reject or misroute calls.

Test signals: Return-code checks after populating the map are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall6.c

Purpose: Tail-call test variant combining a classifier target and entry fallback in tc context.

Important APIs/types/functions: Defines `classifier_0`, `entry`, and `jmp_table`.

Control flow: Entry calls the prog-array target and falls through if the target is absent.

State and persistence: State is map population by the harness.

Dependencies and integration: Depends on tc program loading and static tail-call helper.

Risks: Verifier/JIT must preserve fallback logic and target transfer.

Test signals: Tests compare populated and unpopulated map outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf1.c

Purpose: Tests static tail calls issued from a BPF subprogram called by a tc entry program.

Important APIs/types/functions: Defines `subprog_tail`, `entry`, and `jmp_table`.

Control flow: `entry` calls `subprog_tail`; the subprogram attempts a static tail call and returns a fallback derived from skb state on miss.

State and persistence: Prog-array map is persistent test state.

Dependencies and integration: Depends on BPF-to-BPF calls plus static tail-call support.

Risks: Verifier/JIT must handle tail-call patching inside subprograms.

Test signals: Expected results distinguish successful target transfer from subprogram fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf2.c

Purpose: Adds a classifier target to the BPF-to-BPF tail-call pattern.

Important APIs/types/functions: Defines `subprog_tail`, `classifier_0`, `entry`, and `jmp_table`.

Control flow: Entry calls a subprogram that tail-calls index 0; classifier returns the target value.

State and persistence: State is prog-array contents.

Dependencies and integration: Depends on subprogram call graph and static tail-call relocation.

Risks: A wrong target or lost skb context across the call boundary is the risk.

Test signals: Tests populate index 0 and verify classifier return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf3.c

Purpose: Tests nested BPF-to-BPF tail-call helpers and multiple classifier targets.

Important APIs/types/functions: Defines `subprog_tail2`, `subprog_tail`, classifiers 0/1, entry, and a prog-array.

Control flow: Entry enters subprograms that can tail-call into classifiers, with fallbacks on miss.

State and persistence: State is the prog-array map and any global counters.

Dependencies and integration: Depends on subprogram tail-call support in tc programs.

Risks: Nested call depth plus tail-call transfer must maintain verifier state.

Test signals: Tests exercise each map index and fallback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf4.c

Purpose: Stress test for tail calls from subprograms with extra map lookups and chained target programs.

Important APIs/types/functions: Defines `nop_table`, `jmp_table`, globals `count`/`noise`, subprograms `subprog_tail*`, classifiers 0/1/2, and entry.

Control flow: Entry calls `subprog_tail`, which tail-calls index 0; targets call deeper subprograms and may use `nop_table` before further tail calls.

State and persistence: Persistent state includes prog-array, nop array, and global counters.

Dependencies and integration: Depends on BPF-to-BPF calls, map lookups, static tail calls, and tc context.

Risks: JIT patching must survive subprograms with unrelated helper calls and counter mutation.

Test signals: Tests verify expected chain depth, counter increments, and fallback values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf6.c

Purpose: BPF-to-BPF tail-call variant that checks classifier-to-subprogram transfer ordering.

Important APIs/types/functions: Defines `classifier_0`, `subprog_tail`, `entry`, and prog-array map.

Control flow: Entry invokes a subprogram or classifier path that attempts a static tail call and returns fallback on miss.

State and persistence: Prog-array is the durable state.

Dependencies and integration: Depends on static tail calls through subprogram call graph.

Risks: Misordered patching or context loss can change return values.

Test signals: Harness return-code checks validate the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fentry.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fentry.c

Purpose: Fentry probe used to observe or validate the `subprog_tail` function from BPF-to-BPF tail-call tests.

Important APIs/types/functions: Defines a `fentry/subprog_tail` BPF program via `BPF_PROG`.

Control flow: The program runs on entry to the target subprogram and records/returns a simple value for the harness.

State and persistence: No maps; any state is through globals if present.

Dependencies and integration: Depends on fentry attachment to BPF subprogram symbols.

Risks: Attachment name must match the target subprog and coexist with tail-call tests.

Test signals: Test signal is successful fentry attach and expected invocation count/result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fexit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fexit.c

Purpose: Fexit companion for observing `subprog_tail` return behavior in BPF-to-BPF tail-call tests.

Important APIs/types/functions: Defines `fexit/subprog_tail` using `BPF_PROG`.

Control flow: Runs after the target subprogram when the subprogram returns normally rather than tail-calling away.

State and persistence: No persistent maps.

Dependencies and integration: Depends on fexit attachment to BPF subprograms.

Risks: Tail calls can bypass normal returns, so expected invocation semantics are delicate.

Test signals: Tests verify fexit fires only on appropriate fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fexit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy1.c

Purpose: Tests hierarchical BPF-to-BPF tail-call setup with static prog-array initialization.

Important APIs/types/functions: Defines `jmp_table`, `subprog_tail`, and tc entry.

Control flow: Entry calls a subprogram that tail-calls through the initialized prog-array hierarchy.

State and persistence: Prog-array values embedded in the map definition persist after load.

Dependencies and integration: Depends on libbpf map-initializer support for prog arrays and tc tail calls.

Risks: Initializer order and subprogram target resolution are the risks.

Test signals: Expected retval/counter checks validate hierarchy setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy2.c

Purpose: Hierarchy test with two auxiliary tc classifiers that recursively tail-call themselves through a static prog-array.

Important APIs/types/functions: Defines initialized `jmp_table`, counters `count0`/`count1`, `subprog_tail0/1`, auxiliary classifiers, and main `tailcall_bpf2bpf_hierarchy_2` with expected retval 33.

Control flow: Main calls both subprograms after clobbering registers/stack; each target increments a counter and attempts another tail call until limits apply.

State and persistence: Counters and initialized prog-array are persistent state.

Dependencies and integration: Depends on auxiliary program sections, static prog-array values, and tail-call limit accounting.

Risks: Register clobbering and recursive hierarchy must not corrupt tail-call count or stack state.

Test signals: Pass signal is verifier success and return value `(count1 << 16) | count0 == 33`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy3.c

Purpose: Hierarchy test using two prog-array maps to validate cross-map tail-call chains.

Important APIs/types/functions: Defines `jmp_table0`, `jmp_table1`, subprogram tail path, auxiliary classifiers, counters, and expected retval annotations.

Control flow: Control alternates through two maps/classes to exercise hierarchical tail-call accounting.

State and persistence: Persistent state is both prog arrays and counters.

Dependencies and integration: Depends on static map value initialization and tc tail-call semantics.

Risks: Cross-map chains must still honor global tail-call limits.

Test signals: Expected retval and counter assertions are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy_fentry.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy_fentry.c

Purpose: Fentry-based hierarchy test that performs a tail call from a tracing program context.

Important APIs/types/functions: Defines initialized `jmp_table`, `subprog_tail`, and `fentry/dummy` program.

Control flow: The fentry program calls a subprogram that attempts a static tail call to a tc-like target in the prog-array.

State and persistence: Prog-array map persists target configuration.

Dependencies and integration: Depends on fentry program type, BPF-to-BPF calls, and tail-call compatibility rules.

Risks: Not all program-type combinations allow tail calls, so attach/load outcome is the key risk.

Test signals: Selftest checks expected load and invocation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy_fentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_fail.c

Purpose: Negative verifier tests for tail calls in forbidden critical regions or with live references.

Important APIs/types/functions: Defines private spin lock, `jmp_table`, and optional tc programs annotated with failures for spin lock, RCU lock, preempt-disable, and reference leak cases.

Control flow: Each program enters a forbidden state then attempts `bpf_tail_call_static`; one allocates an object and tail-calls before dropping it.

State and persistence: No successful runtime state expected; the private lock and prog-array exist only for verifier setup.

Dependencies and integration: Depends on verifier lock/RCU/preempt/reference-state checks.

Risks: Accepting any program would allow tail calls to escape cleanup/critical-section constraints.

Test signals: Expected signals are exact annotated verifier messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_freplace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_freplace.c

Purpose: Tests tail calls inside a freplace program replacing an entry point.

Important APIs/types/functions: Defines a prog-array `jmp_table` and `entry_freplace` in `freplace` section.

Control flow: Replacement attempts a static tail call and falls back if the prog-array entry is absent.

State and persistence: Prog-array map is persistent state.

Dependencies and integration: Depends on freplace attachment plus static tail-call support.

Risks: Compatibility of replacement context and tail-call map patching is the main risk.

Test signals: Tests attach replacement and validate target/fallback return behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_freplace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_poke.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_poke.c

Purpose: Tests tail-call poke/update behavior for fentry programs and prog-array mutation.

Important APIs/types/functions: Defines `jmp_table` and multiple optional/required `fentry/bpf_fentry_test1` programs.

Control flow: Fentry programs exercise tail-call transfer and runtime map update/poke paths.

State and persistence: Prog-array map persists target program slots.

Dependencies and integration: Depends on fentry attach, tail-call poke machinery, and libbpf optional sections.

Risks: Runtime prog-array updates must patch JIT call sites without stale targets.

Test signals: Test signals include successful attach, map update, and expected invocation/return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_poke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_sleepable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_sleepable.c

Purpose: Checks tail-call behavior between normal and sleepable uprobe programs.

Important APIs/types/functions: Defines a one-entry `jmp_table`, optional normal and sleepable uprobes, plus globals `executed` and `my_pid`.

Control flow: Normal and sleepable programs attempt tail calls; `uprobe_sleepable_2` increments `executed` only for `my_pid`.

State and persistence: Persistent state is prog-array plus execution counters.

Dependencies and integration: Depends on sleepable uprobe sections and tail-call compatibility rules.

Risks: Tail calls between sleepable and non-sleepable contexts must enforce program-type constraints.

Test signals: Tests set `my_pid`, trigger uprobes, and inspect `executed`/load outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_sleepable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_common.h

Purpose: Shared header for task kfunc tests that defines a map storing referenced task kptrs and helper insertion logic.

Important APIs/types/functions: Defines `struct __tasks_kfunc_map_value`, `__tasks_kfunc_map`, weak task kfunc declarations, `tasks_kfunc_map_value_lookup`, and `tasks_kfunc_map_insert`.

Control flow: Insertion reads task pid, creates a map value, acquires a task reference, and stores it with `bpf_kptr_xchg`; lookup returns the value for later tests.

State and persistence: Persistent state is the hash map keyed by pid containing `struct task_struct __kptr *` references.

Dependencies and integration: Depends on task kfuncs, map kptr support, and BTF task_struct access.

Risks: Reference leaks, wrong pid keys, and stale kptr replacement are key risks.

Test signals: Included success/failure tests validate acquire/release and map ownership behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_failure.c

Purpose: Negative verifier suite for task kfunc reference, trust, NULL, context, and direct-field access rules.

Important APIs/types/functions: Defines many `tp_btf/task_newtask`, kretprobe, lsm, and fentry programs annotated with expected failures; uses shared task-kfunc map helpers.

Control flow: Each program deliberately violates one rule: acquiring untrusted/NULL/frame pointers, releasing unacquired or maybe-null refs, leaking refs, calling in unsafe contexts, or accessing `comm` unsafely.

State and persistence: Expected successful runtime state is none; map mutations are setup for verifier scenarios.

Dependencies and integration: Depends on `bpf_task_acquire`, `bpf_task_release`, pid/vpid kfuncs, RCU trust annotations, and `bpf_misc.h` failure annotations.

Risks: The risk is verifier unsoundness around trusted task pointers and reference ownership.

Test signals: Pass condition is rejection with each expected verifier message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_success.c

Purpose: Positive suite for task kfunc acquisition, release, flavored kfunc relocation, map kptr exchange, pid/vpid lookup, and trusted walked fields.

Important APIs/types/functions: Defines success programs on `tp_btf/task_newtask` and `syscall`, globals `err`/`pid`, weak/flavored kfunc declarations, and helpers for lookup/compare.

Control flow: Programs gate on `pid`, acquire/release task refs from arguments/current task/map kptrs, test kfunc flavor resolution, exchange refs through local/map kptrs, and validate pid/vpid lookup results.

State and persistence: State includes error globals and the shared task kfunc map containing task kptrs.

Dependencies and integration: Depends on task kfuncs, kptr maps, RCU read locks, CO-RE ksym flavor resolution, and pid namespace semantics.

Risks: Reference count deltas, missing kfuncs, incompatible flavored symbols, and namespace assumptions are the main risks.

Test signals: Tests trigger task creation/syscall paths and expect `err==0` with valid map/ref cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_data.bpf.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_data.bpf.h

Purpose: Reusable task-local data implementation for tests that need metadata, key lookup, and per-task storage values.

Important APIs/types/functions: Defines metadata/data/key unions and structs, `tld_data_map`, `tld_key_map`, `tld_object_init`, and `__tld_fetch_key`, plus a struct_ops hook section.

Control flow: Initialization stores object metadata and fetch helpers derive keys for task-local storage scenarios.

State and persistence: Persistent state lives in the task-local data maps and any task-local storage values created by including tests.

Dependencies and integration: Depends on BPF map definitions, struct_ops support, and task-local storage APIs used by consumers.

Risks: Key/value BTF layout and object lifetime must match consumers; stale keys can hide storage bugs.

Test signals: Compile/include tests and consumers validate map layout and helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_data.bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage.c

Purpose: Tests task local storage creation and lookup across syscall enter/exit tracepoints.

Important APIs/types/functions: Defines `enter_id` map and `tp_btf/sys_enter`/`sys_exit` programs.

Control flow: Sys-enter stores data keyed by current task; sys-exit reads/removes or validates the stored value.

State and persistence: Persistent state is task-local storage plus the `enter_id` map/counters.

Dependencies and integration: Depends on task storage helpers and tracepoint BTF context.

Risks: Storage lifetime across syscall boundaries and task identity are the risks.

Test signals: Tests trigger syscalls and verify expected stored id/counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage_exit_creds.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage_exit_creds.c

Purpose: Tests task storage access from the `exit_creds` fentry hook.

Important APIs/types/functions: Defines `task_storage` map and `fentry/exit_creds` program.

Control flow: The hook accesses task storage while credentials are exiting to validate lifetime/deadlock behavior.

State and persistence: Persistent state is task storage associated with tasks.

Dependencies and integration: Depends on fentry attachment and task storage helpers.

Risks: Credential teardown is a sensitive lifetime point for task storage lookup/update.

Test signals: Pass signal is successful hook execution without verifier/runtime deadlock issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage_exit_creds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_recursion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_recursion.c

Purpose: Tests recursion protection for task local storage when storage helper internals are traced.

Important APIs/types/functions: Defines two maps, an `fentry/bpf_local_storage_update` program, and `tp_btf/sys_enter` program.

Control flow: The sys_enter path updates task storage; the fentry hook observes helper execution and tries guarded storage interactions to ensure recursion is handled.

State and persistence: Persistent state is `map_a`, `map_b`, and globals/counters.

Dependencies and integration: Depends on task local storage helpers and fentry tracing of helper-like kernel functions.

Risks: Uncontrolled recursion can deadlock or corrupt storage state.

Test signals: Tests expect bounded execution and correct counters rather than recursive failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_recursion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_uptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_uptr.c

Purpose: Tests task local storage values containing user pointers.

Important APIs/types/functions: Defines `datamap`, local task/task_struct declarations, and `tp_btf/sys_enter` handler `on_enter`.

Control flow: Handler associates data with the current task and manipulates or checks a user pointer stored in map value.

State and persistence: Persistent state is the task local storage map.

Dependencies and integration: Depends on task storage helper support for values with user-pointer fields.

Risks: Verifier must track user pointers in storage without treating them as trusted kernel pointers.

Test signals: Test signal is successful load and expected storage value behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_uptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_storage_nodeadlock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_storage_nodeadlock.c

Purpose: Tests task storage operations from sleepable LSM `socket_post_create` context for deadlock avoidance.

Important APIs/types/functions: Defines `task_storage` and `lsm.s/socket_post_create` program.

Control flow: The LSM hook performs task storage access when sockets are created.

State and persistence: Persistent state is task storage bound to current task.

Dependencies and integration: Depends on sleepable LSM hooks and local storage locking.

Risks: Lock ordering between task storage and socket/LSM paths is the risk.

Test signals: Passing tests create sockets and see no deadlock plus expected storage result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_storage_nodeadlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work.c

Purpose: Positive tests for scheduling BPF task work from perf-event programs using hash, array, and LRU maps.

Important APIs/types/functions: Defines maps `hmap`, `arrmap`, `lrumap`, `process_work`, and perf_event programs `oncpu_*`.

Control flow: Perf-event handlers look up map elements and schedule task work; callback processes the element later.

State and persistence: Persistent state is map elements with embedded task-work state/counters.

Dependencies and integration: Depends on BPF task-work kfuncs/helpers and perf_event context.

Risks: Object lifetime between perf handler and deferred work is critical.

Test signals: Tests expect scheduled callbacks to run and map/counter state to reflect processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_fail.c

Purpose: Negative verifier suite for invalid task-work scheduling patterns.

Important APIs/types/functions: Defines hash/array maps, `process_work`, and perf_event programs annotated for expected failures.

Control flow: Programs try disallowed contexts, duplicate scheduling, or invalid object lifetime transitions around task work.

State and persistence: No successful runtime state expected for failing sections.

Dependencies and integration: Depends on task-work verifier rules and map value lifetime tracking.

Risks: Accepting invalid scheduling can lead to use-after-free or duplicate callbacks.

Test signals: Expected verifier messages are the pass criteria.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_stress.c

Purpose: Stress test for scheduling and deleting BPF task work through syscall programs.

Important APIs/types/functions: Defines hash map `hmap`, callback `process_work`, and syscall programs `schedule_task_work` and `delete_task_work`.

Control flow: One syscall path schedules task work from map values; the other deletes entries to stress cancellation/lifetime races.

State and persistence: Persistent state is the hash map and scheduled task-work objects.

Dependencies and integration: Depends on syscall program type and task-work kfunc support.

Risks: Races between deletion and deferred callback are the main risk.

Test signals: Stress harness repeatedly schedules/deletes and checks for stable execution/errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_bpf2bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_bpf2bpf.c

Purpose: Minimal tc BPF-to-BPF call test.

Important APIs/types/functions: Defines subprogram `subprog_tc` and tc entry `entry_tc`.

Control flow: Entry calls the subprogram and returns its result or transformed value.

State and persistence: No persistent maps or globals.

Dependencies and integration: Depends on tc program type and BPF subprogram call support.

Risks: Verifier/JIT must preserve context and return values across the call.

Test signals: Expected signal is successful load and deterministic return value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_bpf2bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_dummy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_dummy.c

Purpose: Minimal dummy tc program for attach/load plumbing tests.

Important APIs/types/functions: Defines `entry` in `tc` section returning a simple code.

Control flow: No internal branching; it validates basic tc skeleton handling.

State and persistence: No persistent state.

Dependencies and integration: Depends on tc program loading and license metadata.

Risks: Main risk is section naming or attach-type mismatch.

Test signals: Test signal is successful load/attach and expected return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_incompl_cong_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_incompl_cong_ops.c

Purpose: Negative struct_ops test for incomplete TCP congestion-control ops.

Important APIs/types/functions: Defines partial `tcp_congestion_ops` callbacks in struct_ops sections and a `.struct_ops` map.

Control flow: Load/link validates required callback coverage rather than runtime congestion behavior.

State and persistence: State would be the TCP CA struct_ops registration if accepted.

Dependencies and integration: Depends on TCP congestion-control struct_ops verifier.

Risks: Missing required ops must be rejected to avoid invalid TCP CA registration.

Test signals: Expected signal is load failure or specific selftest outcome for incomplete ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_incompl_cong_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_kfunc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_kfunc.c

Purpose: Tests BPF TCP congestion-control struct_ops callbacks and allowed TCP CA kfunc access.

Important APIs/types/functions: Defines many `struct_ops` callbacks for a `tcp_congestion_ops` map.

Control flow: Callbacks call or validate TCP congestion-control helper/kfunc behavior across init, cong_avoid, ssthresh, undo, state, cwnd event, and related hooks.

State and persistence: Persistent state is TCP CA registration and globals updated by callbacks.

Dependencies and integration: Depends on TCP stack struct_ops, kfuncs, and BTF `sock`/`tcp_sock` types.

Risks: Wrong callback prototypes or unsafe socket field access are key risks.

Test signals: Tests register the CA, drive TCP traffic, and inspect callback results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_kfunc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_unsupp_cong_op.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_unsupp_cong_op.c

Purpose: Negative test for unsupported TCP congestion-control operation in BPF struct_ops.

Important APIs/types/functions: Defines a callback for an unsupported op and a `.struct_ops` map.

Control flow: Load/link should reject or skip the unsupported operation according to selftest expectations.

State and persistence: No intended persistent runtime registration if unsupported.

Dependencies and integration: Depends on TCP CA struct_ops allowlist.

Risks: Accepting unsupported hooks can expose unverified call contexts.

Test signals: Expected signal is annotated load failure or unsupported-op diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_unsupp_cong_op.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_update.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_update.c

Purpose: Tests updating/replacing TCP congestion-control struct_ops links.

Important APIs/types/functions: Defines several TCP CA callback variants and multiple `.struct_ops.link` maps plus a base `.struct_ops` map.

Control flow: Callbacks return distinct values so userspace can verify which linked ops instance is active after updates.

State and persistence: Persistent state is registered TCP CA links and result globals.

Dependencies and integration: Depends on struct_ops link update/detach for TCP congestion ops.

Risks: Update ordering and stale callback pointers are the risks.

Test signals: Tests attach/update links and confirm the active callback variant changes as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_write_sk_pacing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_write_sk_pacing.c

Purpose: Tests writes to socket pacing-related fields from TCP congestion-control struct_ops callbacks.

Important APIs/types/functions: Defines helper-like calculations `tcp_left_out`, `tcp_packets_in_flight`, TCP CA callbacks, and a `.struct_ops` map.

Control flow: Callbacks inspect TCP state and write pacing fields during congestion-control events.

State and persistence: Persistent state is socket TCP state modified during test traffic and callback globals.

Dependencies and integration: Depends on TCP struct_ops verifier field-access permissions.

Risks: Verifier must allow only safe socket writes and preserve TCP invariants.

Test signals: Traffic-driven selftests validate pacing field updates and callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_write_sk_pacing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_rtt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_rtt.c

Purpose: Sockops test storing TCP RTT information in socket local storage.

Important APIs/types/functions: Defines `struct tcp_rtt_storage`, `socket_storage_map`, and sockops program `_sockops`.

Control flow: Sockops handler reads RTT-related fields/events and updates socket storage for the connection.

State and persistence: Persistent state is per-socket storage map values.

Dependencies and integration: Depends on sockops context, socket storage helpers, and TCP sock fields.

Risks: Socket lifetime and field availability across callbacks are the risks.

Test signals: Tests create TCP connections and check stored RTT data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_rtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_assign_reuse.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_assign_reuse.c

Purpose: Tests `bpf_sk_assign` and reuseport socket selection interaction for TCP/UDP and tc paths.

Important APIs/types/functions: Defines `sk_map`, reuseport accept/drop programs, helpers `assign_sk`, `maybe_assign_tcp`, `maybe_assign_udp`, and `tc_main`.

Control flow: Reuseport programs accept/drop based on selected socket; tc path parses packet protocol and conditionally assigns sockets from `sk_map`.

State and persistence: Persistent state is the socket map populated by userspace.

Dependencies and integration: Depends on sk_reuseport, tc, socket map, and `bpf_sk_assign` helpers.

Risks: Protocol parsing, socket ref lifetime, and assign/reuseport ordering are risks.

Test signals: Tests send TCP/UDP packets and verify accept/drop/assignment behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_assign_reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_kprobe_sleepable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_kprobe_sleepable.c

Purpose: Small test for attaching a sleepable kprobe-style program.

Important APIs/types/functions: Defines `handle_kprobe_sleepable` with sleepable attachment attributes.

Control flow: The handler runs on the selected kprobe and returns without complex state.

State and persistence: No persistent maps; any result is via globals if present.

Dependencies and integration: Depends on sleepable kprobe attach support.

Risks: Program type/attach flag mismatch is the key risk.

Test signals: Load/attach success and invocation are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_kprobe_sleepable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe.c

Purpose: Comprehensive auto-attach probe test for ksyscall/kretsyscall, uprobes/uretprobes by name, ref counters, and sleepable user-copy helpers.

Important APIs/types/functions: Defines result globals, kprobe/retprobe handlers, uprobe/uretprobe handlers, `verify_sleepable_user_copy`, and `verify_sleepable_user_copy_str`.

Control flow: Handlers set distinct globals; sleepable handlers copy user buffers and validate truncation, zero padding, dynamic sizes, invalid flags, and fault behavior.

State and persistence: Persistent state is result globals and `user_ptr`/`dynamic_sz` inputs set by userspace.

Dependencies and integration: Depends on libbpf auto-attach section parsing, probe macros, weak `bpf_copy_from_user_str`, and sleepable uprobe support.

Risks: User pointer safety, mixed sleepable/non-sleepable arrays, and section-name parsing are risks.

Test signals: Tests trigger nanosleep and process-local functions, then inspect all result globals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe_manual.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe_manual.c

Purpose: Manual attach counterpart for kprobe, kretprobe, uprobe, and uretprobe programs.

Important APIs/types/functions: Defines simple handlers for each probe kind with generic section names.

Control flow: Userspace manually attaches each program to target symbols/functions; handlers update or return known values.

State and persistence: No maps; result globals track invocation.

Dependencies and integration: Depends on manual libbpf attach APIs and probe program types.

Risks: Wrong attach target or program type mismatch causes silent non-invocation.

Test signals: Tests attach manually and verify each handler ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe_manual.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoattach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoattach.c

Purpose: Minimal raw tracepoint auto-attach test.

Important APIs/types/functions: Defines `prog1` on `raw_tp/sys_enter` and `prog2` on `raw_tp/sys_exit`.

Control flow: Each program runs when its raw tracepoint fires.

State and persistence: No maps; globals or invocation counts are external to this file.

Dependencies and integration: Depends on libbpf auto-attach section names for raw tracepoints.

Risks: Section parsing regression would skip one hook.

Test signals: Test signal is successful auto-attach and trigger of both tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoattach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoload.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoload.c

Purpose: Tests libbpf autoload control with loadable and intentionally missing fentry targets.

Important APIs/types/functions: Defines raw tracepoint programs `prog1`/`prog2`, an fentry program `prog3` for a non-existing target, and a fake struct.

Control flow: Userspace disables autoload or expects failure depending on program selection.

State and persistence: No runtime state beyond loaded programs.

Dependencies and integration: Depends on libbpf autoload flags and attach target resolution.

Risks: A disabled failing program must not prevent object load.

Test signals: Tests toggle autoload and confirm only expected programs load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_cookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_cookie.c

Purpose: Exercises `bpf_get_attach_cookie` across many attach types.

Important APIs/types/functions: Defines `update` helper and handlers for kprobe, kretprobe, uprobe, uretprobe, tracepoint variants, perf_event, raw_tp, tp_btf, fentry/fexit/fmod_ret, and LSM.

Control flow: Each handler reads the attach cookie and records it in global slots for userspace validation.

State and persistence: Persistent state is global cookie/result variables.

Dependencies and integration: Depends on attach-cookie support across tracing, perf, and LSM program types.

Risks: Some attach types have distinct cookie plumbing; regressions show as zero or wrong cookie values.

Test signals: Tests attach with known cookies and compare recorded values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_ma.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_ma.c

Purpose: Stress tests BPF memory allocator object and percpu object allocation/free through kptr map values.

Important APIs/types/functions: Defines generated maps for many object sizes, BTF id arrays, batch alloc/free helpers, and fentry tests for batch allocation, free-through-map-free, percpu allocation, and percpu map free.

Control flow: Handlers gated by pid allocate batches with `bpf_obj_new_impl` or `bpf_percpu_obj_new_impl`, exchange into map kptr fields, then free or rely on map cleanup.

State and persistence: Persistent state is many array maps holding kptr/percpu-kptr values plus `err`/`pid` globals.

Dependencies and integration: Depends on experimental allocator helpers, kptr map fields, BTF ids supplied by userspace, and fentry attach.

Risks: Refilling/freeing allocator caches, zero-sized layouts, and map cleanup ownership are risks.

Test signals: Tests set BTF ids/pid, trigger nanosleep, and expect `err==0` after allocation/free cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_ma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf.c

Purpose: Positive netfilter conntrack kfunc test for XDP and TC contexts, including lookup, allocation, insertion, NAT, status, timeout, zones, and existing-entry mutation.

Important APIs/types/functions: Defines local ct option structs, kfunc prototypes, many result globals, helpers `nf_ct_test` and `nf_ct_opts_new_test`, and programs `nf_xdp_ct_test`/`nf_skb_ct_test`.

Control flow: Helpers run error-condition lookups, allocate random tuples, set timeout/mark/NAT, insert entries, look them up, validate reply tuple NAT, update timeout/status, and test zone direction/id behavior.

State and persistence: Persistent state includes kernel conntrack entries and result globals; no BPF maps are defined.

Dependencies and integration: Depends on conntrack kfuncs, CONFIG_HZ kconfig extern, XDP/TC contexts, and BTF struct access.

Risks: Reference release of `nf_conn`, netns/zone semantics, random tuple collisions, and NAT field validation are risks.

Test signals: Tests run XDP and TC programs and inspect globals for expected errno values and zero success markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf_fail.c

Purpose: Negative conntrack kfunc verifier suite covering illegal insert/lookup combinations, field writes, and post-insert mutation.

Important APIs/types/functions: Defines failing optional XDP/TC programs with expected messages and local ct option/conn structs.

Control flow: Each program violates a specific rule: double insert, lookup-to-insert, writing disallowed fields, setting timeout/status after insert, or changing status/timeout before insert incorrectly.

State and persistence: No successful runtime state expected.

Dependencies and integration: Depends on conntrack kfunc verifier annotations and `bpf_misc.h` failure metadata.

Risks: Verifier must enforce ownership and mutation windows for `nf_conn`.

Test signals: Expected annotated verifier errors are the pass condition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_decl_tag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_decl_tag.c

Purpose: Tests BTF declaration tag emission and map/value typing.

Important APIs/types/functions: Defines tagged key/value types, `hashmap1`, helper `foo`, and `fentry/bpf_fentry_test1` program.

Control flow: Program and helper exercise tagged declarations so BTF.ext can be inspected by userspace.

State and persistence: Persistent state is the hash map and emitted BTF metadata.

Dependencies and integration: Depends on compiler BTF decl_tag support and fentry attachment.

Risks: Tags can be dropped by compiler/libbpf changes or misassociated with fields.

Test signals: Tests inspect BTF tags and load the fentry program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_decl_tag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_ext.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_ext.c

Purpose: Minimal BTF.ext function/line info test for XDP with a global function.

Important APIs/types/functions: Defines `f0` XDP program and `global_func`.

Control flow: XDP program calls the global function or exposes it for BTF.ext metadata validation.

State and persistence: No maps; state is emitted BTF.ext records.

Dependencies and integration: Depends on compiler BTF.ext generation and libbpf load.

Risks: Missing line/function info can break introspection tests.

Test signals: Tests load object and inspect BTF.ext records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_map_in_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_map_in_map.c

Purpose: Comprehensive BTF-defined map-in-map test covering array/hash outer maps, dynamic inner specs, and sockmap/sockhash variants.

Important APIs/types/functions: Defines many inner/outer map structs and raw_tp handler `handle__sys_enter`.

Control flow: The handler exists mainly to keep maps/program loadable; userspace validates map definitions and map-in-map creation.

State and persistence: Persistent state is the set of inner/outer maps and their initial values.

Dependencies and integration: Depends on BTF map definitions, inner-map templates, and socket map types.

Risks: Inner map size/type mismatch and dynamic template handling are common risks.

Test signals: Tests inspect created maps and update/lookup nested maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_map_in_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_newkv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_newkv.c

Purpose: BTF map test using new-style key/value declarations.

Important APIs/types/functions: Defines `ipv_counts`, BTF map `btf_map`, long-named helper functions, and dummy tracepoint program.

Control flow: Tracepoint calls helpers so symbols/BTF are preserved while map key/value BTF is checked.

State and persistence: Persistent state is `btf_map` and BTF metadata.

Dependencies and integration: Depends on BTF map key/value inference.

Risks: Long function names and map BTF layout must remain stable.

Test signals: Tests load and inspect BTF map metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_newkv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_nokv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_nokv.c

Purpose: BTF map test intentionally lacking explicit key/value typing in the legacy/no-kv style.

Important APIs/types/functions: Defines `btf_map`, helper functions, and dummy tracepoint program.

Control flow: Program provides load coverage while userspace validates how missing key/value BTF is represented.

State and persistence: Persistent state is the map definition and BTF metadata.

Dependencies and integration: Depends on libbpf compatibility with no-kv map declarations.

Risks: Loader behavior for old map syntax can regress.

Test signals: Tests inspect map metadata and successful load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_nokv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_skc_cls_ingress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_skc_cls_ingress.c

Purpose: TC ingress test for syncookie helpers and BTF socket tuple handling.

Important APIs/types/functions: Defines local sockaddr structs, helpers `test_syncookie_helper`, `handle_ip_tcp`, and tc `cls_ingress`.

Control flow: Program parses IPv4/IPv6 TCP packets, fills socket addresses, and calls syncookie/check helpers.

State and persistence: No persistent maps; return codes and helper results are observed by packet tests.

Dependencies and integration: Depends on tc direct packet access, TCP/IP header parsing, and syncookie BPF helpers.

Risks: Malformed packet bounds and address-family handling are risks.

Test signals: Tests send crafted packets and check tc verdict/helper outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_skc_cls_ingress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_build_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_build_id.c

Purpose: Tests build-id stack collection from normal and sleepable uprobe.multi attachments.

Important APIs/types/functions: Defines local `bpf_stack_build_id` structs and `uprobe_nofault`/`uprobe_sleepable`.

Control flow: Uprobe handlers collect or validate build-id stack data in different faulting/sleepable modes.

State and persistence: State is result globals/stack buffers in BSS.

Dependencies and integration: Depends on uprobe.multi section syntax and build-id stack helper behavior.

Risks: Sleepable versus nofault user memory behavior can diverge.

Test signals: Tests attach to `./uprobe_multi:uprobe` and inspect build-id results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_build_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup1_hierarchy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup1_hierarchy.c

Purpose: Tests cgroup v1 hierarchy access from LSM and fentry programs.

Important APIs/types/functions: Defines cgroup local struct declarations, `bpf_link_create_verify`, LSM `bpf`, sleepable LSM, and fentry programs.

Control flow: Programs validate cgroup hierarchy/id properties when BPF links are created.

State and persistence: No maps; globals record validation results if present.

Dependencies and integration: Depends on LSM/fentry hooks and cgroup struct BTF.

Risks: Cgroup v1/v2 hierarchy assumptions and sleepable context differences are risks.

Test signals: Tests create cgroup links and verify expected hierarchy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup1_hierarchy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup_link.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup_link.c

Purpose: Minimal cgroup skb link test with alternate egress programs.

Important APIs/types/functions: Defines `egress` and `egress_alt` in `cgroup_skb/egress` sections.

Control flow: Programs return simple verdicts so userspace can update/replace cgroup links.

State and persistence: No persistent maps.

Dependencies and integration: Depends on cgroup skb attach/link update APIs.

Risks: Link replacement must swap active program without stale execution.

Test signals: Tests attach both programs and verify egress verdict changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_check_mtu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_check_mtu.c

Purpose: Exercises `bpf_check_mtu` helper from XDP and TC contexts with normal, exceeding, negative-delta, input-length, and segmented-SKB cases.

Important APIs/types/functions: Defines global user MTU/ifindex inputs, BPF-observed MTU globals, six XDP programs and seven TC programs.

Control flow: Each program calls `bpf_check_mtu` with a different delta/input/flag setup and maps helper errno to XDP/TC verdicts.

State and persistence: Persistent state is global MTU result variables set for userspace.

Dependencies and integration: Depends on XDP/TC contexts, ETH header length assumptions, and `BPF_MTU_CHK_RET_FRAG_NEEDED`.

Risks: Data length calculation, direct-access SKB length, negative delta, and segmentation flags are risks.

Test signals: Tests set MTU/ifindex, run packets through each program, and compare verdicts plus stored MTU values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_check_mtu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.c

Purpose: Large Cloudflare TC classifier implementing packet classification and GRE/GUE redirect logic for selftests.

Important APIs/types/functions: Defines metrics map, packet buffer abstraction, IPv4/IPv6/ICMP/TCP/UDP parsers, checksum helpers, classification functions, forwarding helpers, and `cls_redirect`.

Control flow: `cls_redirect` parses L3/L4, rejects malformed/fragmented/unwanted traffic, accepts local SYN/established/ICMP cases, or encapsulates and redirects to the next hop while updating metrics.

State and persistence: Persistent state is `metrics_map`; packet data is modified in-place for encapsulation/redirect.

Dependencies and integration: Depends on tc skb helpers, direct packet access, checksum helpers, endian helpers, and `test_cls_redirect.h` GRE/GUE headers.

Risks: Verifier-sensitive pointer alignment, non-linear SKB reads, checksum correctness, MTU/encap buffer limits, and redirect-loop detection are risks.

Test signals: Packet-driven tests validate metrics increments, verdicts, encapsulated headers, and malformed-packet drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.h

Purpose: Shared header defining GRE/GUE encapsulation structures and constants used by classifier redirect tests.

Important APIs/types/functions: Defines `gre_base_hdr`, `guehdr`, `unigue`, and related packed header layouts.

Control flow: No executable flow; it supplies exact on-wire layout for encapsulation code.

State and persistence: No persistent state.

Dependencies and integration: Included by normal and dynptr classifier implementations.

Risks: Packed layout or bitfield/endian mistakes would produce invalid packets.

Test signals: Compile-time structure size/layout and packet output comparisons are test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_dynptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_dynptr.c

Purpose: Dynptr-based variant of the Cloudflare TC redirect classifier.

Important APIs/types/functions: Defines metrics map and functions paralleling `test_cls_redirect.c`, but uses dynptr packet access and `iphdr_info` helpers where appropriate.

Control flow: Control flow matches the non-dynptr classifier: parse, classify, accept/drop, encapsulate, redirect, and update metrics.

State and persistence: Persistent state is `metrics_map`; packet mutations happen through dynptr/skb helpers.

Dependencies and integration: Depends on dynptr support in skb/tc context, checksum helpers, and shared GRE/GUE header definitions.

Risks: Dynptr bounds, packet mutation invalidation, and parity with direct-access implementation are risks.

Test signals: Tests compare verdicts, metrics, and packet bytes against the non-dynptr classifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_dynptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_subprogs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_subprogs.c

Purpose: Build wrapper that enables subprogram mode for `test_cls_redirect.c`.

Important APIs/types/functions: Defines `SUBPROGS` and includes the full classifier source.

Control flow: The included classifier marks many helpers `__noinline`, so parsing/classification/forwarding crosses BPF subprogram calls.

State and persistence: State remains the classifier `metrics_map` and packet mutations.

Dependencies and integration: Depends on the shared classifier and verifier support for subprogram packet pointer tracking.

Risks: Pointer bounds and packet data refinements must survive call boundaries.

Test signals: Tests expect same behavior as `test_cls_redirect.c` with successful subprogram verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_subprogs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_autosize.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_autosize.c

Purpose: CO-RE autosize tests for reads into local structs whose source/target field sizes differ.

Important APIs/types/functions: Defines local real/samesize/downsize/signed structs and raw tracepoint handlers `handle_samesize`, `handle_downsize`, `handle_probed`, `handle_signed`.

Control flow: Handlers perform CO-RE reads and compare sign/size behavior, writing results for userspace.

State and persistence: Persistent state is BSS data/result globals.

Dependencies and integration: Depends on `BPF_CORE_READ`/CO-RE relocation and clang/BTF typing.

Risks: Autosized reads must not overrun destinations or mishandle sign extension.

Test signals: Tests feed input structs and verify output bytes/values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_autosize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_extern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_extern.c

Purpose: Tests CO-RE extern variables, especially kconfig extern resolution.

Important APIs/types/functions: Defines extern-like globals and raw tracepoint `handle_sys_enter`.

Control flow: Handler reads extern values and records which externs were resolved or defaulted.

State and persistence: State is BSS result globals.

Dependencies and integration: Depends on libbpf extern/kconfig CO-RE relocation.

Risks: Missing externs must follow expected optional/default semantics.

Test signals: Tests inspect loaded global values after triggering sys_enter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_extern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_read_macros.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_read_macros.c

Purpose: Tests `BPF_CORE_READ` macro forms with shuffled local struct layouts.

Important APIs/types/functions: Defines local `callback_head` variants and raw tracepoint `handler`.

Control flow: Handler uses macro variants to read nested fields from CO-RE-relocated structures.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on `bpf_core_read` macros and BTF field relocations.

Risks: Macro expansion must preserve relocation chains and bounds.

Test signals: Tests verify read values match expected fields despite layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_read_macros.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_arrays.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_arrays.c

Purpose: CO-RE relocation test for arrays and nested array fields.

Important APIs/types/functions: Defines input/output structs and raw tracepoint `test_core_arrays`.

Control flow: Program reads array elements and nested substructure arrays through CO-RE relocations.

State and persistence: Persistent state is output map/global data.

Dependencies and integration: Depends on array field relocations in BTF.

Risks: Array bounds and element-size relocation mistakes are risks.

Test signals: Tests compare output values for matching, resized, and missing arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_arrays.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_direct.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_direct.c

Purpose: CO-RE bitfield relocation test using direct BTF-enabled context access.

Important APIs/types/functions: Defines bitfield input/output structs plus tracepoint BTF context types and `test_core_bitfields_direct`.

Control flow: Program reads signed/unsigned bitfields directly and stores normalized outputs.

State and persistence: State is output globals.

Dependencies and integration: Depends on direct bitfield CO-RE access and tp_btf context.

Risks: Bit offset, sign extension, and endian handling are risks.

Test signals: Tests validate all extracted bitfield values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_probed.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_probed.c

Purpose: CO-RE bitfield relocation test using probed/raw tracepoint reads.

Important APIs/types/functions: Defines bitfield structs and `test_core_bitfields`.

Control flow: Handler reads bitfields through probe-read style CO-RE helpers.

State and persistence: Persistent state is output data.

Dependencies and integration: Depends on BPF_CORE_READ_BITFIELD_PROBED-style relocations.

Risks: Sign/width handling and safe probing are risks.

Test signals: Tests compare expected decoded bitfield outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_probed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enum64val.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enum64val.c

Purpose: CO-RE test for 64-bit enum value relocations, signed and unsigned.

Important APIs/types/functions: Defines named 64-bit enum types, output struct, and raw tracepoint `test_core_enum64val`.

Control flow: Program relocates enum value constants and stores comparison/output results.

State and persistence: State is output globals.

Dependencies and integration: Depends on BTF enum64 support.

Risks: Older kernels/toolchains may lack enum64 BTF handling.

Test signals: Tests verify relocated 64-bit enum constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enum64val.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enumval.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enumval.c

Purpose: CO-RE test for regular enum value relocations.

Important APIs/types/functions: Defines named and anonymous enums, output struct, and raw tracepoint `test_core_enumval`.

Control flow: Program uses CO-RE enum value existence/value relocations and records results.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on BTF enum relocation support.

Risks: Renamed/missing enum values must resolve according to CO-RE rules.

Test signals: Tests inspect expected enum value/existence outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enumval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_existence.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_existence.c

Purpose: CO-RE field/type existence relocation test.

Important APIs/types/functions: Defines input/output structs and raw tracepoint `test_core_existence`.

Control flow: Program checks field/type existence and writes booleans/results.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on CO-RE existence relocation builtins.

Risks: False positives for missing fields or false negatives for present fields break portability.

Test signals: Tests run against flavor structs and compare existence flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_existence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_flavors.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_flavors.c

Purpose: CO-RE flavor matching test for local types with suffix variants.

Important APIs/types/functions: Defines `core_reloc_flavors` plus reversed/weird flavors and handler `test_core_flavors`.

Control flow: Program reads fields through a local flavor and relies on libbpf matching compatible target flavors.

State and persistence: State is output globals.

Dependencies and integration: Depends on CO-RE type flavor matching conventions.

Risks: Wrong flavor selection can map fields to incompatible layouts.

Test signals: Tests load with multiple target flavors and validate outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_flavors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ints.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ints.c

Purpose: CO-RE primitive integer relocation test.

Important APIs/types/functions: Defines integer layout struct and raw tracepoint `test_core_ints`.

Control flow: Program reads integer fields with varied widths/signedness.

State and persistence: State is output globals.

Dependencies and integration: Depends on integer field CO-RE relocations.

Risks: Width/sign mismatches are the risk.

Test signals: Tests compare stored integer values across target layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_kernel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_kernel.c

Purpose: Kernel CO-RE test reading current task fields and long nested `group_leader` chains.

Important APIs/types/functions: Defines local `task_struct` flavors, output struct, and raw tracepoint `test_core_kernel`.

Control flow: Handler gates on `my_pid_tgid`, reads pid/tgid, uses variadic `BPF_CORE_READ` up to deep nesting, reads comm string, and checks type matching when clang supports it.

State and persistence: Persistent state is the `data` global with input pid, skip flag, and output buffer.

Dependencies and integration: Depends on kernel BTF, `bpf_get_current_task`, `BPF_CORE_READ`, `BPF_CORE_READ_STR_INTO`, and clang preserve-type-info support.

Risks: Toolchain feature gating, deep relocation chains, and local type mismatch handling are risks.

Test signals: Tests set pid, trigger sys_enter, and validate all `valid[]`, comm length, and type-match/skip fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_kernel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_misc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_misc.c

Purpose: Miscellaneous CO-RE relocation cases for extensible structs and compatible variants.

Important APIs/types/functions: Defines output struct, variants `core_reloc_misc___a/b`, extensible struct, and handler `test_core_misc`.

Control flow: Program reads fields and checks compatibility/existence across miscellaneous layout cases.

State and persistence: State is output globals.

Dependencies and integration: Depends on libbpf CO-RE matching for extensible and flavored types.

Risks: Edge-case matching rules can regress without obvious compile failures.

Test signals: Tests compare output flags/values for each variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_mods.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_mods.c

Purpose: CO-RE relocation test for const/volatile/restrict and typedef modifier chains.

Important APIs/types/functions: Defines output structs, substructs, modified fields, and `test_core_mods`.

Control flow: Handler reads through modifier-wrapped types and records values.

State and persistence: Persistent state is output data.

Dependencies and integration: Depends on BTF modifier stripping/preservation during relocation.

Risks: Incorrect modifier handling can fail type compatibility.

Test signals: Tests validate relocated reads across modifier variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_mods.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_module.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_module.c

Purpose: CO-RE relocation test against bpf_testmod module BTF using raw_tp and tp_btf program variants.

Important APIs/types/functions: Defines module context/output structs and programs on `bpf_testmod_test_read` raw and BTF tracepoints.

Control flow: Programs read module-provided fields through CO-RE and store output.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on module BTF availability and bpf_testmod tracepoints.

Risks: Module not loaded or mismatched BTF will skip/fail tests; relocation target namespace is sensitive.

Test signals: Tests load bpf_testmod, trigger read hook, and inspect outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_nesting.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_nesting.c

Purpose: CO-RE relocation test for nested structs and unions.

Important APIs/types/functions: Defines nested substruct/subunion and handler `test_core_nesting`.

Control flow: Program reads nested fields through multiple levels of struct/union nesting.

State and persistence: State is output globals.

Dependencies and integration: Depends on nested field path relocations.

Risks: Union member offsets and missing nested fields are risks.

Test signals: Tests compare nested output values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_nesting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_primitives.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_primitives.c

Purpose: CO-RE primitive type relocation test including enum and scalar primitives.

Important APIs/types/functions: Defines primitive enum/struct and handler `test_core_primitives`.

Control flow: Program checks primitive type sizes/compatibility and reads scalar fields.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on primitive BTF type relocations.

Risks: Primitive signedness/size compatibility can vary by target.

Test signals: Tests validate values and type checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_primitives.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ptr_as_arr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ptr_as_arr.c

Purpose: CO-RE test treating pointer fields as arrays for relocation reads.

Important APIs/types/functions: Defines pointer-as-array struct and handler `test_core_ptr_as_arr`.

Control flow: Program reads indexed data through a pointer-like field using CO-RE access.

State and persistence: State is output globals.

Dependencies and integration: Depends on verifier-safe pointer/array CO-RE handling.

Risks: Bounds and pointer-to-array compatibility are risks.

Test signals: Tests validate indexed values or expected relocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ptr_as_arr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_size.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_size.c

Purpose: CO-RE field/type size relocation test.

Important APIs/types/functions: Defines output and input structs plus handler `test_core_size`.

Control flow: Program uses size relocations to record field/type sizes and compare expected layout.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on CO-RE size relocation builtins.

Risks: Wrong size values break portable allocation/copy logic.

Test signals: Tests inspect recorded sizes across target flavors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_size.c -->
