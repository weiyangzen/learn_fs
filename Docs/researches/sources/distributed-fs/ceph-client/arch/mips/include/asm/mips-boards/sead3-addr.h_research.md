# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/sead3-addr.h

Purpose: Physical address map for the MIPS SEAD-3 board.

Important APIs/types/functions: Defines major regions for FPGA registers, SDRAM, SRAM, optional SRAM, boot flash, user expansion, Ethernet, UART channels, PIC32 registers, LCD registers, CPLD switches/LEDs, USB status bits, soft endian register, reset bits, and revision register. Notable constants include `SEAD3_SDRAM`, `SEAD3_FPGA`, `SEAD3_PI_PIC32_USB_STATUS_*`, `SEAD3_CPLD_*`, `SEAD3_UART_CH_0/1`, `SEAD3_ETHERNET`, and `SEAD3_REVISION_REGISTER`.

Control flow, state, and persistence: No functions. Board drivers and setup code use these constants for MMIO accesses; state persists in FPGA/CPLD/PIC32/peripheral registers.

Dependencies and integration: Integrates with SEAD-3 early platform setup, UART, Ethernet, LCD, USB/PIC32 support, and endian selection code.

Risks and test signals: The map uses fixed uncached physical addresses, so wrong constants can crash during early boot or hit the wrong device. Test early console, revision read, LED/switch access, Ethernet, UARTs, and PIC32 USB interrupt/status handling.
