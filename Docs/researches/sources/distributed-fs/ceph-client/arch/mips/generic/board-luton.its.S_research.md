<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-luton.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-luton.its.S

**Purpose:** FIT fragment embedding the Microsemi Luton PCB091 FDT.

**Important APIs/types/functions:** Defines `fdt-luton_pcb091` from `boot/dts/mscc/luton_pcb091.dtb` and `pcb091` configuration using the shared kernel.

**Control flow:** Pure image metadata consumed at FIT build and boot selection time.

**State, dependencies, integration:** Tied to `FIT_IMAGE_FDT_LUTON` and SOC_VCOREIII configuration.

**Risks and test signals:** DTB rename or missing hash generation breaks image assembly. Test FIT generation and boot with U-Boot on Luton hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-luton.its.S -->
