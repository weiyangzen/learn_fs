<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/gda.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/gda.h

Purpose: Defines the SGI SN Global Data Area layout and PROM operation commands used for boot coordination, partitioning, and PROM control.

Important APIs/types/functions: `GDA_VERSION`, field offsets, `gda_t`, `GDA`, partition GDA version, `PROMOP_*` magic/commands/options, and `PROMOP_REG`.

Control flow: Kernel/PROM code locates the GDA through `GDA_ADDR(get_nasid())`, reads bootmaster/partition/table fields, and writes PROM operation commands such as halt, powerdown, restart, reboot, or imode to the PROM operation register.

State and persistence: The GDA is firmware-provided persistent boot metadata. PROMOP values in PI error-stack space communicate requested PROM actions and boot options.

Dependencies and integration points: Depends on SN address macros and PI register definitions through included address headers. Integrated by SN boot, shutdown, restart, partition, and PROM handoff code.

Risks: Offsets are firmware ABI. Writing the wrong PROMOP command can halt or reboot hardware. The `GDA` macro assumes a valid current NASID.

Test signals: SN boot metadata parsing, reboot/powerdown paths, partition startup, and firmware handoff tests are relevant.

Source read size: 103 lines, 3170 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/gda.h -->
