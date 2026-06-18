<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sme.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sme.c

Purpose: tiny helper program that prints the current SME streaming vector length in bytes.

Important APIs and functions: `main` calls `rdvl_sme()` declared in `rdvl.h` and implemented in `rdvl.S`, then prints the integer.

Control flow and state: no branching or persistent state; read VL and exit 0.

Dependencies and integration: used by `vec-syscfg.c` to verify default and inherited SME vector length across exec.

Risks: must only be run when SME/RDSVL is supported or under a build/runtime setup that can handle the instruction.

Test signals: stdout contains one decimal VL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sme.c -->
