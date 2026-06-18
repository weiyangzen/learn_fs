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
