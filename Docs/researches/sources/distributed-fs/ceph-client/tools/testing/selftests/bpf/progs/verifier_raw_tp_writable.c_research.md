# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_raw_tp_writable.c

## Purpose
This file verifies that writable raw tracepoint buffers cannot be written through a variable offset.

## Important APIs, Types, And Functions
It defines a small hash map `map_hash_8b` and one `SEC("raw_tracepoint.w")` naked program. The test uses `bpf_map_lookup_elem` to obtain an unknown scalar from a map value, then adds it to the writable tracepoint buffer pointer.

## Control Flow
The program reads the tracepoint buffer pointer from context, looks up a map value, exits on null, adds a variable map-derived offset to the buffer pointer, and attempts an 8-byte store.

## State And Persistence
The hash map is a fixture for producing a variable offset. Verifier state tracks raw tracepoint writable buffer pointer class, variable offset, and allowed store constraints.

## Dependencies And Integration Points
It integrates with raw writable tracepoint verifier rules and generic map lookup nullability.

## Risks
Allowing arbitrary variable-offset writes into tracepoint buffers could corrupt event payloads outside the intended writable range.

## Test Signals
The expected failure is `R6 invalid variable buffer offset: off=0, var_off=(0x0; 0xffffffff)` with `BPF_F_ANY_ALIGNMENT`.
