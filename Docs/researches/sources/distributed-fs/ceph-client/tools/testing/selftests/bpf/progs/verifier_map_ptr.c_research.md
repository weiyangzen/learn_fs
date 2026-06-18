# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ptr.c

## Purpose
This file verifies direct verifier access to `bpf_map` pointer metadata: which offsets are readable, which are rejected, whether writes are forbidden, and how zero-offset arithmetic interacts with map pointers.

## Important APIs, Types, And Functions
It defines an array map with `struct test_val` values and a hash map with `struct other_val`. Tests use map address immediates, `bpf_map_lookup_elem`, strict/unprivileged annotations, and direct loads/stores from map pointers.

## Control Flow
Negative cases read a negative offset, write through a map pointer, or read a non-existent field around the internal `ops` member boundary. Positive cases read allowed metadata and perform map lookup after adding zero to map pointers in both operand orders.

## State And Persistence
The maps are static test fixtures. The relevant verifier state is pointer class `map_ptr`, fixed offset, access size, privilege gating, and whether ALU with zero preserves a usable map pointer.

## Dependencies And Integration Points
It integrates with verifier BTF/metadata rules for `struct bpf_map` and map helper argument validation.

## Risks
Permitting map pointer writes or arbitrary metadata reads would expose kernel internals. Rejecting zero arithmetic too aggressively could break valid compiler output that normalizes pointers.

## Test Signals
Expected logs include negative offset rejection, `only read from bpf_array is supported`, non-existent field diagnostics, and unprivileged capability messages.
