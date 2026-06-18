<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/Makefile

Purpose: Build definition for the `/dev/papr-sysparm` ioctl ABI selftest.

Important APIs and types: Defines `TEST_GEN_PROGS := papr_sysparm`, includes common make fragments, links shared harness/utils, and adds `$(KHDR_INCLUDES)` for kernel UAPI headers.

Control flow: The default target recurses to the parent; normal builds produce `papr_sysparm`.

State and persistence: No runtime persistence.

Dependencies and integration points: Depends on `<asm/papr-sysparm.h>` availability through kernel headers and the local test source.

Risks: Missing `KHDR_INCLUDES` would break builds on systems without installed headers.

Test signals: Compile success and test enumeration validate the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/Makefile -->
