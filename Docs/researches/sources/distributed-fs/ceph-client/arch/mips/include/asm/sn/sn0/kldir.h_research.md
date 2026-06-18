<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/kldir.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/kldir.h

Purpose: Defines SN0/IP27-specific KLDIR entry offsets, sizes, counts, and strides for launch, KLCONFIG, NMI, PI error, symmon stack, free memory, GDA, and NMI register frames.

Important APIs/types/functions: `SYMMON_STACK_SIZE`, `IP27_LAUNCH_*`, `IP27_KLCONFIG_*`, `IP27_NMI_*`, `IP27_PI_ERROR_*`, `IP27_SYMMON_STK_*`, `IP27_FREEMEM_*`, `IO6_GDA_*`, `IP27_NMI_KREGS_OFFSET`, and `IP27_NMI_EFRAME_*`.

Control flow: Generic KLDIR code uses these constants to seed or interpret KLDIR entries, and address macros use the resulting entries to locate per-CPU launch/NMI areas and firmware/kernel handoff blocks.

State and persistence: The constants describe fixed boot memory reservations in each node's low memory and IO6 PROM area.

Dependencies and integration points: Included by generic `asm/sn/kldir.h` and used by SN0 address macros.

Risks: Offsets overlap boot-critical PROM/kernel areas if changed incorrectly. Negative/variable free-memory sizing is an ABI convention with PROM.

Test signals: KLDIR dump validation, secondary launch, NMI frame capture, GDA discovery, and boot memory reservation tests are relevant.

Source read size: 186 lines, 7005 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/kldir.h -->
