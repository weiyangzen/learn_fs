# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/access_map_in_map.c

## Purpose

BPF program object that stresses access to inner maps stored in array-of-maps and hash-of-maps containers from kprobe and sleepable fentry contexts. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

Map definitions for `inner_map`, `outer_array_map`, `outer_htab_map`; `bpf_map_lookup_elem()`, `bpf_map_update_elem()`, `bpf_get_current_pid_tgid()`, and SEC programs `access_map_in_array`, `sleepable_access_map_in_array`, `access_map_in_htab`, `sleepable_access_map_in_htab`.

## Control Flow

Each entry calls `acc_map_in_map()`, filters by configured `tgid`, verifies a missing key returns no inner map, retrieves key 0, then repeatedly updates the inner map while userspace may replace map-in-map entries.

## State and Persistence Behavior

Persistent BPF maps are the inner array and two outer map-in-map containers. Global `tgid` controls activation; updates are kernel map state only.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here.

## Risks and Edge Cases

This is concurrency-oriented: repeated updates while userspace replaces inner maps can expose lifetime/refcount bugs. Sleepable and non-sleepable attach contexts must both be legal for map access.

## Test Signals

Verifier/load success for all attach sections and absence of crashes/refcount issues while userspace replacement tests run.
