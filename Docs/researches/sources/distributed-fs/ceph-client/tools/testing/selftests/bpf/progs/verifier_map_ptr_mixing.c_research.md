# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ptr_mixing.c

## Purpose
This file validates verifier behavior when control flow merges different map pointer identities or map types before helper use, including tail-call program-array cases.

## Important APIs, Types, And Functions
It defines array, hash, array-of-maps, and two program-array maps. Dummy socket programs populate program arrays. Tests use subprograms returning map pointers, `bpf_map_lookup_elem`, and `bpf_tail_call`.

## Control Flow
One test merges hash and array map pointers before lookup and succeeds because both are acceptable map helper arguments. Another merges hash and map-in-map in a way that triggers invalid direct metadata access. Tail-call tests compare branches producing different versus same program arrays.

## State And Persistence
The declared maps are static fixtures. Verifier state is the key subject: map pointer identity, map type, helper-compatible unioning at joins, and special handling for program-array tail-call map pointers.

## Dependencies And Integration Points
The suite depends on verifier join logic for map pointers and tail-call validation for program arrays. It is integrated through socket and tc selftest sections.

## Risks
Over-permissive merging can let a helper receive an incompatible map type. Over-strict merging can reject valid branches that preserve helper-compatible map pointer classes.

## Test Signals
Expected outcomes include successful return values for compatible merges, `only read from bpf_array is supported` for incompatible joins, and unprivileged `tail_call abusing map_ptr` diagnostics.
