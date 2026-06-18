<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendorid_list.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendorid_list.h

Purpose: Centralizes numeric RISC-V vendor IDs used by errata and vendor extension code.

Important APIs/types/functions: Defines `ANDES_VENDOR_ID`, `MICROCHIP_VENDOR_ID`, `MIPS_VENDOR_ID`, `SIFIVE_VENDOR_ID`, and `THEAD_VENDOR_ID`.

Control flow: No runtime flow; code compares hardware/SBI vendor IDs against these constants.

State and persistence: No mutable state; constants are hardware identity contracts.

Dependencies and integration points: Used by alternatives, errata, vendor extensions, vector T-Head support, and hwprobe.

Risks: Wrong IDs apply vendor logic to the wrong CPU family.

Test signals: Boot on vendor systems, errata selection tests, and cpufeature/hwprobe validation.

Source read size: 14 lines, 298 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendorid_list.h -->
