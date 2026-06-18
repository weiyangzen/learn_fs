# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/check_mtu.c

## Purpose
Tests `bpf_check_mtu()` helper behavior for XDP and TC programs, including direct test-run execution, ifindex lookup, XDP link attach metadata, and `BPF_MTU_CHK_SEGS`.

## Important APIs, types, and functions
Uses `test_check_mtu.skel.h`, `pkt_v4`, `bpf_prog_test_run_opts()`, `bpf_program__attach_xdp()`, `bpf_link_get_info_by_fd()`, and `bpf_tc`-style return expectations. `read_mtu_device_lo()` reads `/sys/class/net/lo/mtu`. XDP and TC helpers set rodata constants (`GLOBAL_USER_MTU`, `GLOBAL_USER_IFINDEX`) before load, then inspect BSS results `global_bpf_mtu_xdp` and `global_bpf_mtu_tc`.

## Control flow and state
`test_ns_check_mtu()` checks XDP attach, reads loopback MTU, then runs XDP and TC subtests with and without explicit ifindex. `test_chk_segs_flag()` temporarily lowers loopback MTU to 10 and restores it. State includes skeleton rodata/BSS, link info, loopback MTU, and transient link MTU modification.

## Dependencies and integration points
Requires loopback device, XDP attach support, TC helper support in prog test-run, and network helper packet fixtures. This is likely run in a network namespace selftest context because it can change `lo` MTU.

## Risks and test signals
Changing loopback MTU is risky if cleanup is interrupted. Attach can fail on kernels without XDP link support. Passing signals are expected retval (`XDP_PASS` or `BPF_OK`), BSS MTU equals user-space MTU, XDP link info reports `BPF_LINK_TYPE_XDP` and ifindex 1, and segs-flag run succeeds after MTU restore.
