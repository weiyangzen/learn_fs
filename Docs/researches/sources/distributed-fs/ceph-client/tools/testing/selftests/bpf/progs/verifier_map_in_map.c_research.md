# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_in_map.c

## Purpose
This file tests map-in-map pointer behavior, inner map lookup typing, map pointer non-null facts, state pruning, and ring-buffer inner-map integration through dynptr reservation.

## Important APIs, Types, And Functions
It defines `map_in_map` as `BPF_MAP_TYPE_ARRAY_OF_MAPS` containing array maps, and `rb_in_map` as an array-of-maps containing ring buffers. It uses `bpf_map_lookup_elem`, `bpf_ringbuf_reserve_dynptr`, `bpf_ringbuf_submit_dynptr`, and helper wrappers `__rb_event_reserve` and `__rb_event_submit`.

## Control Flow
Positive tests look up an inner map and use it as a map pointer for a second lookup. Negative tests do pointer arithmetic on map pointers or pass a nullable inner pointer without a null check. Additional tests show map pointers are never null, including after spill/fill, and exercise state pruning across repeated lookup branches.

## State And Persistence
Maps are static fixtures, but no user data persistence is central to the test. Verifier state tracks map pointer versus map-value-or-null, non-null map pointer invariants, spilled map pointer types, and dynptr lifetime.

## Dependencies And Integration Points
The file integrates with map-in-map BTF/map-definition support, ringbuf dynptr helpers, and verifier map pointer type rules.

## Risks
Confusing inner map values with map pointers can lead to unsafe helper calls or pointer arithmetic on kernel map objects. Dynptr tests guard against verifier regressions around inner ringbuf maps.

## Test Signals
Signals include success/unprivileged success for valid lookup chains, `processed 15 insns` for pruning, and failures such as `pointer arithmetic on map_ptr prohibited` and `map_value_or_null expected=map_ptr`.
