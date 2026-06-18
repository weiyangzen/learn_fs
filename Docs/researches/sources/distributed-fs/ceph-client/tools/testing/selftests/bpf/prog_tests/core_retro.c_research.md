# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_retro.c

## Purpose
Validates backwards-compatible CO-RE behavior in `test_core_retro` by attaching a kprobe-like program, filtering by current TGID, and checking result map state after a trigger.

## Important APIs, types, and functions
Uses `test_core_retro.skel.h`, `bpf_map__update_elem()` on `exp_tgid_map`, skeleton attach, and result map/BSS checks.

## Control flow and state
The test opens/loads the skeleton, writes current PID into a map keyed by zero, attaches probes, triggers execution, reads expected result, and closes the skeleton. State is map-backed expected TGID and runtime skeleton output.

## Dependencies and integration points
Depends on generated BPF object and kernel probe/CO-RE support. Integrated as `test_core_retro()`.

## Risks and test signals
Risk is that process filtering or probe trigger does not fire. Passing signals are successful map update/attach and expected result value after trigger.
