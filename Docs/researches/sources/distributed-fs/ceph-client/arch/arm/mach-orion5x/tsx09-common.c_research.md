<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.c

Purpose: common support code for QNAP TS-x09 Orion5x NAS boards. It provides PIC-mediated poweroff and discovery of the Ethernet MAC address from a flash-resident NAS configuration area.

Important APIs and functions: `qnap_tsx09_power_off()` reprograms UART1 to 19200 8N1 and writes the PIC command byte `A`. `qnap_tsx09_eth_data` exports `mv643xx_eth_platform_data` with PHY address 8. MAC parsing is split across `qnap_tsx09_parse_hex_nibble()`, `qnap_tsx09_parse_hex_byte()`, and `qnap_tsx09_check_mac_addr()`. `qnap_tsx09_find_mac_addr()` scans a memory range in 1 KiB increments using `ioremap()`.

Control flow: board code calls `qnap_tsx09_find_mac_addr(mem_base, size)` with the flash partition bounds. Each mapped page is checked for strict `xx:xx:xx:xx:xx:xx\n` format; the first match copies six bytes into `qnap_tsx09_eth_data.mac_addr`. Poweroff is called through board-level `pm_power_off` style integration.

State and persistence: the MAC lives persistently in flash, but this file only reads it at init and stores it in static Ethernet platform data. Poweroff is a one-way hardware command through UART1 registers.

Dependencies and integration: uses Orion5x UART virtual base and `orion5x_tclk`, Linux PCI/Ethernet headers, `serial_reg.h` register offsets, and `mv643xx_eth`. It is shared by board files that provide flash ranges and install poweroff.

Risks and test signals: MAC scanning assumes a plaintext ext2 file appears at a 1 KiB-aligned offset and validates only the first bytes of each page. UART1 is hijacked during poweroff, so any active serial use is intentionally overridden. Test with boot log `tsx09: found ethernet mac address`, expected `eth_data.mac_addr`, and actual PIC shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.c -->
