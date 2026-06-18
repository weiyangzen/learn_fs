# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xskxceiver.h

## Purpose

This header centralizes AF_XDP xceiver selftest constants and compatibility fallbacks. It keeps common socket family values and test-size constants available to the main xceiver and helper code.

## Important APIs, Types, and Functions

It defines fallback `SOL_XDP`, `AF_XDP`, and `PF_XDP`, plus `MAX_TEARDOWN_ITER`, `MAX_ETH_JUMBO_SIZE`, `SOCK_RECONF_CTR`, `RX_FULL_RXQSIZE`, `UMEM_HEADROOM_TEST_SIZE`, `XSK_UMEM__INVALID_FRAME_SIZE`, `RUN_ALL_TESTS`, and `NUM_MAC_ADDRESSES`. It includes the generated XDP skeleton and `xsk_xdp_common.h`.

## Control Flow

No executable control flow exists. The values parameterize test loops, packet sizes, invalid descriptor cases, and command-line selection.

## State and Persistence Behavior

There is no storage. The constants influence runtime state allocated by `xskxceiver.c` and helper files.

## Dependencies and Integration Points

It depends on generated `xsk_xdp_progs.skel.h`, shared XDP constants, and kernel UAPI values when present. It integrates the main AF_XDP test binary with helper code.

## Risks and Test Signals

Risks include constants drifting from kernel AF_XDP limits or test expectations, especially jumbo and invalid frame sizes. Signals are successful compilation and expected pass/skip behavior across the xceiver test matrix.
