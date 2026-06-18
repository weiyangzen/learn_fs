# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c313.c

Purpose: supports the Ricoh RS5C313 RTC on SH LANDISK-style hardware through board-specific bit-banged serial GPIO/control lines. It provides basic time read/write and resets invalid oscillator-stop state to 1 Jan 2000.

Important APIs/types/functions: the `CONFIG_SH_LANDISK` block defines serial port and CE line operations. `rs5c313_init_port()` configures SCL/SDA GPIO-like pins. `rs5c313_write_data()` and `rs5c313_read_data()` bit-bang 8-bit command/data cycles. `rs5c313_read_reg()` and `rs5c313_write_reg()` send RTC address/data commands. `rs5c313_rtc_read_time()` and `rs5c313_rtc_set_time()` read/write decimal digit registers while checking `ADJ_BSY`. `rs5c313_check_xstp_bit()` clears oscillator-stop state and seeds a default date.

Control flow: platform probe initializes board ports, checks and repairs XSTP, then registers an RTC with read/set time only. Runtime reads and writes assert CE, force 24-hour control mode, wait for adjustment not busy, transfer digit nibbles, then deassert CE.

State and persistence: the hardware stores BCD digit nibbles and control/test flags. There is no driver-private state except global `scsptr1_data` for SH LANDISK port shadowing. Invalid oscillator state is cleared by writing a default date.

Dependencies and integration: depends on platform driver registration, RTC core, SH LANDISK memory-mapped port definitions when enabled, BCD helpers, delays, and raw I/O. The machine-independent portion assumes the board-specific bit-bang helpers/macros exist.

Risks: the file is only meaningful for `CONFIG_SH_LANDISK`; otherwise helper macros/functions are absent. `rs5c313_check_xstp_bit()` calls `rs5c313_rtc_set_time(NULL, &tm)`, which is currently safe because the function only uses `dev` for errors, but fragile. There is no spinlock around global bit-bang state. Test signals include LANDISK build coverage, ADJ_BSY timeout, XSTP reset path, CE timing, 1970/2069 year pivot, and concurrent RTC access.
