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
