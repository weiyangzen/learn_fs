<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/Makefile

Purpose: builds SH-2A CPU support.

Important APIs/types/functions: common `ex.o`/`entry.o`, probe/opcode helper, optional FPU, subtype setup/clock files, and pinmux resources.

Control flow: Kbuild maps subtype configs to setup/clock/pinmux object files.

State and persistence: build-time only.

Dependencies/integration: integrates SH-2A entry, FPU emulation, clocks, pinmux, and platform-device setup.

Risks: shared files for SH7203/SH7263 and MX-G can be omitted by config mistakes.

Test signals: build all listed SH2A subtype configs with and without FPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/Makefile -->
