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
