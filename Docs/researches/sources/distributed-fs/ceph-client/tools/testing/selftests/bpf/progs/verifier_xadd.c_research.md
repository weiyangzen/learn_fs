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
