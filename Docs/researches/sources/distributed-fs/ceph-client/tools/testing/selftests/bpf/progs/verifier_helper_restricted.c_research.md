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
