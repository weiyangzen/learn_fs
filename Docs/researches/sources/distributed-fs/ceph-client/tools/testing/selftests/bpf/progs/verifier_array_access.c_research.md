# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_array_access.c

## Purpose
This array-map verifier suite covers constant, register, variable, signed, read-only, write-only, per-CPU, elided lookup, and stack-key access paths for array values. The source is 731 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`, `tc`. Map definitions are `map_array_ro`, `map_array_wo`, `map_array_pcpu`, `map_array`, `map_hash_48b`. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include `bpf_map_lookup_elem`, `bpf_probe_read_user`, `bpf_get_prandom_u32`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 15 success markers and 28 failure markers across 29 loadable sections. Test descriptions include `valid map access into an array with a constant`, `valid map access into an array with a register`, `valid map access into an array with a variable`, `valid map access into an array with a signed variable`, `invalid map access into an array with a constant`, `invalid map access into an array with a register`, `invalid map access into an array with a variable`, `invalid map access into an array with no floor check`, `invalid map access into an array with a invalid max check`, `valid read map access into a read-only array 1`, plus 17 more. Expected verifier diagnostics include `R0 leaks addr`, `invalid access to map value, value_size=48 off=48 size=8`, `R0 min value is outside of the allowed memory range`, `R0 unbounded memory access, make sure to bounds check any such access`, `R0 unbounded memory access`, `invalid access to map value, value_size=48 off=44 size=8`, `R0 pointer += pointer`, `write into map forbidden`, plus 5 more.
