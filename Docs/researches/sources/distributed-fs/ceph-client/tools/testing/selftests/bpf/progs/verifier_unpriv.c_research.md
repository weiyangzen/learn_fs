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
