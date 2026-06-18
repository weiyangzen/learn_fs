<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/Makefile

## Purpose
This Makefile wires the Open vSwitch network selftest directory into the kernel kselftest build system. It declares the shell test program, supporting Python file, compiler flags, and cleanup target for generated artifacts.

## Important APIs, Types, And Functions
It sets `top_srcdir`, appends to `CFLAGS`, declares `TEST_PROGS := openvswitch.sh`, `TEST_FILES := ovs-dpctl.py`, `EXTRA_CLEAN := test_netlink_checks`, and includes `../../lib.mk`.

## Control Flow
There is no runtime control flow. During kselftest build/install, `lib.mk` interprets `TEST_PROGS` as executable tests to run/install, `TEST_FILES` as support files to stage, `CFLAGS` for local compilations, and `EXTRA_CLEAN` for cleanup.

## State, Persistence, And Dependencies
Build state is limited to generated test binaries or helper artifacts in the openvswitch selftest directory. The flags depend on kernel UAPI headers under `$(top_srcdir)/usr/include` and any `KHDR_INCLUDES` supplied by the parent build.

## Integration Points
This file integrates Open vSwitch selftests with the broader `tools/testing/selftests/net` kselftest infrastructure. It ensures `openvswitch.sh` can find `ovs-dpctl.py` when staged.

## Risks
Incorrect `top_srcdir` depth or missing `lib.mk` would break builds. `-Wl,--no-as-needed` affects linker behavior for local binaries and should remain aligned with helper requirements. `EXTRA_CLEAN` must match generated artifact names.

## Test Signals
Signals are build-system level: `make -C tools/testing/selftests/net/openvswitch` should stage `openvswitch.sh` and `ovs-dpctl.py`, and `make clean` should remove `test_netlink_checks` if generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/Makefile -->
