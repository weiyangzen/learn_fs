# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/platsmp.c

Purpose: MMP3 SMP boot support using the CIU software branch register and SCU.

Important APIs/types/functions: Defines `mmp3_boot_secondary()`, `mmp3_smp_prepare_cpus()`, `mmp3_smp_ops`, and CPU method `marvell,mmp3-smp`.

Control flow: Prepare enables the SCU at the statically mapped PGU/SCU base. Boot writes the physical `secondary_startup` address to `CIU_REG(0x24)`, which the boot ROM on the second core polls; no IPI is required.

State and persistence: Hardware state is SCU enable and the CIU software branch register. No persistent software state.

Dependencies and integration points: Depends on static PGU/SCU mapping from `mmp2_map_io()`, ARM SCU helpers, and the MMP3 boot ROM protocol.

Risks: Only the boot-ROM-polled branch register is programmed, so platforms with a different secondary-release protocol will fail. There is no timeout or CPU id validation beyond the caller.

Test signals: Boot MMP3 SMP, verify the second core enters Linux, and test that the `marvell,mmp3-smp` CPU method is present in DT.
