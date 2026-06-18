<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/Makefile

Purpose: Build definition for the `/dev/papr-vpd` ioctl/read ABI selftest.

Important APIs and types: Defines `TEST_GEN_PROGS := papr_vpd`, includes common make fragments, links harness/utils, and adds `$(KHDR_INCLUDES)` for `<asm/papr-vpd.h>`.

Control flow: Normal kselftest builds the `papr_vpd` binary.

State and persistence: No runtime state here.

Dependencies and integration points: Depends on kernel UAPI headers and `papr_vpd.c`.

Risks: Header include configuration is the main risk; without it, local builds may fail despite source being correct.

Test signals: Build success and emitted test name are validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/Makefile -->
