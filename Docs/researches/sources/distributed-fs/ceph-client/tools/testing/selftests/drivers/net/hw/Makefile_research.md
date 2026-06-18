# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/Makefile

Purpose: Build/install manifest for hardware-focused network driver selftests.

Important APIs/variables: `HAS_IOURING_ZCRX` compile probe, `COND_GEN_FILES`, `TEST_GEN_FILES`, `TEST_PROGS`, `TEST_FILES`, `TEST_INCLUDES`, `YNL_GEN_FILES`, `YNL_GENS`, `../../../lib.mk`, `../../../net/ynl.mk`, `../../../net/bpf.mk`, and `LDLIBS += -luring` for `iou-zcrx`.

Control flow: The Makefile probes whether installed liburing exposes `io_uring_register_ifq`; if yes, it builds `iou-zcrx`, otherwise warns and excludes io_uring zero-copy receive tests. It registers many Python/shell hardware tests, YNL-generated `ncdevmem` and `toeplitz` helpers, BPF objects, and shared ethtool library files.

State and persistence: Produces generated binaries, YNL userspace headers/helpers, and BPF objects in the kselftest output tree.

Dependencies and integration points: Depends on liburing, kernel headers, YNL, BPF build support, net/forwarding libraries, and hardware-capable test environment.

Risks and test signals: Missing liburing silently reduces coverage. Incorrect YNL/BPF ordering breaks generated helper builds.
