# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/unpriv_bpf_disabled.c

## Purpose
Tests behavior when unprivileged BPF is disabled: already accessible pinned maps, perf/ring buffers, and links remain usable without capabilities, while privileged creation, lookup-by-id, enumeration, query, and BTF loading fail with `-EPERM`.

## APIs, Types, and Functions
Important helpers are `process_ringbuf()`, `process_perfbuf()`, `test_unpriv_bpf_disabled_positive()`, `test_unpriv_bpf_disabled_negative()`, and public `test_unpriv_bpf_disabled()`. Uses capability helpers, sysctl helpers, map pinning, perf/ring buffer APIs, BPF program/map/link id APIs, and BTF APIs.

## Control Flow, State, and Persistence
The test opens/loads the skeleton, records the current pid in BSS, pins seven maps under `/sys/fs/bpf/unpriv_bpf_disabled_*`, lowers perf restrictions, sets `unprivileged_bpf_disabled` to disabled-for-unprivileged mode when possible, opens a software perf event, attaches the skeleton, drops effective capabilities, and runs positive and negative subtests. Cleanup restores capabilities and sysctls, closes perf fd, unlinks pins, and destroys the skeleton.

## Dependencies and Integration
Depends on sysctl write permissions, CAP management, bpffs pinning, perf events, libbpf buffer APIs, and `test_unpriv_bpf_disabled.skel.h`.

## Risks and Test Signals
Risks include global sysctl mutation, failure to restore capabilities/sysctls on early errors, map pin path collisions, and distro policy where `unprivileged_bpf_disabled=1` is immutable. Signals include successful use of pinned maps and buffers after cap drop, successful link creation to an existing perf event, and `-EPERM` for all privileged negative operations.
