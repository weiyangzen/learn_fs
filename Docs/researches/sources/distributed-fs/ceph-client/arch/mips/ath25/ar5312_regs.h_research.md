## sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312_regs.h

Purpose: defines the AR5312/AR2312/AR2313 hardware interface: CPU interrupt lines, misc interrupt numbers, MMIO address map, reset/timer register offsets, reset bits, enable bits, revision fields, clock control fields, flash controller fields, and SDRAM sizing fields.

Important definitions: CPU IRQs include WLAN0, ENET0, ENET1, WLAN1, and MISC. Misc IRQs cover timer, AHB processor/DMA errors, GPIO, UART, watchdog, local bus, and SPI. Address constants define WMAC, Ethernet, SDRAM, flash controller, UART, GPIO, reset, and flash windows. Clock macros split AR5312/AR2312 and AR2313 multiplier/predivider bit layouts. Flash macros describe width, wait states, address check sizes, and enable/write protect bits.

Control flow: none. It is consumed by C code to configure hardware and decode revision/clock state.

State and persistence: none directly.

Dependencies and integration: included by `ar5312.c` and ATH25 early printk. It works with `ATH25_REG_MS()` from `devices.h` for bit extraction.

Risks: register headers are high-impact because incorrect masks or shifts affect memory size, clocks, and flash access. The AR5312 clock macros are duplicated in the file, which is harmless to the preprocessor but a maintenance smell.

Test signals: compile warnings for duplicate/inconsistent macros, plus boot validation for RAM sizing, flash width/timing, UART base, IRQ routing, and SoC revision classification.
