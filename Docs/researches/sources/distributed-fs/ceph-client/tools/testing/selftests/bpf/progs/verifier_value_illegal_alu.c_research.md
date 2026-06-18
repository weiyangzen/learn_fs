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
