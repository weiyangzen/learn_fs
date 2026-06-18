# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-sram.c

Purpose: configures FlexCop SRAM chip type, SRAM destination routing, WAN speed, and SRAM/DMA control flags.

Important APIs/functions: `flexcop_sram_init()` selects SRAM type by chip revision. Exported `flexcop_sram_set_dest()` routes NET/CAI/CAO/MEDIA destinations to USB/WAN, DMA1, DMA2, or FlexCopIII CA. Exported `flexcop_wan_set_speed()` and `flexcop_sram_ctrl()` update WAN speed and SRAM control bits. A large `#if 0` block preserves obsolete SRAM read/write/detect experiments and is not compiled.

Control flow: initialization maps FlexCopII/IIB to one 32 KiB chip and FlexCopIII to one 48 KiB chip. Destination programming reads `sram_dest_reg_714`, validates FlexCopIII-only target use, updates selected destination fields according to the bitmask, writes the register, then delays.

State/persistence: all state is volatile hardware register state. There is no persistent software cache aside from `fc->rev`.

Dependencies/integration: uses `flexcop-reg.h` enums/bitfields, `fc->read_ibi_reg`/`write_ibi_reg`, `ibi_zero` conventions, and exported APIs called by bus-specific streaming/DMA setup.

Risks/test signals: destination routing mistakes can silently send TS data to the wrong engine. The 1 ms `udelay` is a latency risk. Tests should cover revision validation, bitmask combinations, FC3-only target rejection on older chips, WAN speed field updates, and that dead `#if 0` code remains uncompilable/irrelevant.
