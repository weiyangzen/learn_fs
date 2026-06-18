
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/udbg_scc.c

Purpose: provides early `udbg` console support for Apple Zilog SCC serial ports on PowerMac, including a real-mode PPC64 path.

Important APIs/functions: `udbg_scc_init(int force_scc)` locates the ESCC device, selects the Open Firmware stdout channel or channel A when forced, maps SCC control/data registers, initializes the serial port, and installs `udbg_scc_putc`, `udbg_scc_getc`, and `udbg_scc_getc_poll`. `udbg_init_pmac_realmode()` hardwires real-mode SCC addresses on PPC64 and installs a real-mode putc callback using `real_readb`/`real_writeb`.

Control flow: normal init finds `escc`, parent `mac-io`, and the `linux,stdout-path` chosen node. It computes physical MMIO from `reg` and `assigned-addresses`, enables/locks the SCC through `pmac_call_feature(PMAC_FTR_SCC_ENABLE)`, maps one page, resets the selected side, preserves baud rate from OF when SCC was stdout, otherwise chooses 57600 for Xserve/G5 or 38400 for older machines, writes the init table, and prints a test string.

State and persistence: global `sccc` and `sccd` hold mapped control/data register addresses. No persistent state is written.

Dependencies and integration points: depends on Open Firmware nodes, mac-io assigned addresses, PMac feature control, raw MMIO accessors, `udbg` global callbacks, and PPC64 real-mode access helpers.

Risks: busy-wait getc/putc can hang if hardware is absent after partial initialization. The forced fallback to channel A can conflict with firmware or another user if the port is not intended for debugging. Real-mode fixed addresses are platform-specific.

Test signals: early serial output and input on OF-selected SCC, forced channel-A debug on supported machines, newline CR handling, PPC64 real-mode output before virtual mappings, and clean no-op behavior when ESCC is absent.
