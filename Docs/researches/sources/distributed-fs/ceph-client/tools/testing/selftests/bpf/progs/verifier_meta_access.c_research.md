# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_meta_access.c

## Purpose
This file validates verifier rules for XDP packet metadata access between `data_meta` and `data`, plus interactions with `data_end`, `bpf_xdp_adjust_meta`, and atomic-derived offsets.

## Important APIs, Types, And Functions
It uses XDP sections, `struct xdp_md` offsets for `data_meta`, `data`, and `data_end`, inline assembly, `bpf_xdp_adjust_meta`, and a locked stack add used to produce a bounded scalar in later tests.

## Control Flow
Tests 1 and 7/8/11/12 establish valid metadata bounds against `data` before reading. Tests 2-4 and 6/9/10 intentionally check the wrong boundary, go below `data_meta`, or use `data_end`/shifted `data` in ways that do not prove metadata safety. Test 5 calls `bpf_xdp_adjust_meta` and then uses the stale metadata pointer, which must be rejected.

## State And Persistence
No persistent state exists. Verifier state tracks packet metadata pointer class, packet pointer range, fixed and variable offsets, helper-induced pointer invalidation, and atomic-result scalar bounds.

## Dependencies And Integration Points
It integrates with verifier packet access logic used by tc/XDP-style programs and depends on context layout definitions from kernel BPF headers.

## Risks
Metadata boundary mistakes can allow packet memory corruption or reject valid metadata manipulation. These tests protect pointer range reasoning across packet meta/data transitions.

## Test Signals
Expected results include `__retval(0)` for valid reads and failures such as `R0 min value is negative`, `invalid access to packet`, and `R3 !read_ok`.
