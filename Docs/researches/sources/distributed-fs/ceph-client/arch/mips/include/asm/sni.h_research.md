<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sni.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sni.h

Purpose: Defines Siemens-Nixdorf MIPS board identifiers, CPU identifiers, platform register addresses, interrupt mappings, IDPROM offsets, and board initialization declarations.

Important APIs/types/functions: `sni_brd_type`; board constants `SNI_BRD_*`; CPU constants `SNI_CPU_*`; MMIO address macros for PCIMT/PCIT/A20R registers; interrupt constants for A20R, PCIT, PCIMT, EISA, SCSI, Ethernet, power/button/temperature; IDPROM offsets; init declarations `sni_*_init`, `sni_*_irq_init`, optional `sni_eisa_root_init`, `sni_hwint`, and `sni_isa_irq_handler`.

Control flow: Platform setup identifies the board from IDPROM, selects board-specific register maps and IRQ initialization, sets hardware interrupt dispatch, and exposes EISA/ISA handlers where configured.

State and persistence: State is global board type, board MMIO registers, interrupt pending/selection registers, IDPROM contents, and selected hardware interrupt handler.

Dependencies and integration points: Depends on Linux IRQ return type and MIPS `CKSEG1ADDR`/CPU IRQ constants through includers. Integrated by SNI platform setup and interrupt code.

Risks: Several register offsets differ under `CONFIG_SNI_RM` versus other PCIMT variants. Wrong board type or endian XOR for IDPROM offsets can misread hardware and route IRQs incorrectly.

Test signals: SNI board defconfig builds, IDPROM detection, IRQ routing smoke tests, EISA root init, and platform boot on RM200/PCIT/PCIMT variants are relevant.

Source read size: 243 lines, 7439 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sni.h -->
