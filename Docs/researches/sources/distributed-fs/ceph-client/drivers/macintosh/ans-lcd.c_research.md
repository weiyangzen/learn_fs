# sources/distributed-fs/ceph-client/drivers/macintosh/ans-lcd.c

Purpose: implements the `/dev/anslcd` misc driver for the front-panel LCD on Apple Network Server hardware. It probes for an Open Firmware node named `lcd` under parent `gc`, maps the fixed LCD MMIO window at `0xf301c000`, registers minor `LCD_MINOR`, initializes the controller, and writes an 80-character boot logo.

Important APIs and functions: `anslcd_write_byte_ctrl()` and `anslcd_write_byte_data()` write command/data bytes to offsets `ANSLCD_CTRL_IX` and `ANSLCD_DATA_IX` with controller-specific `udelay()` timing. `anslcd_write()` copies userspace bytes to the LCD data port and advances `*ppos`. `anslcd_ioctl()` implements `ANSLCD_CLEAR`, `ANSLCD_SENDCTRL`, `ANSLCD_SETSHORTDELAY`, and `ANSLCD_SETLONGDELAY`. `anslcd_fops` exposes `.write`, `.unlocked_ioctl`, `.open`, and `default_llseek`; `anslcd_init()` and `anslcd_exit()` own misc registration and `ioremap()` lifetime.

Control flow: module init verifies hardware via OF, maps MMIO, registers the misc device, then sends initialization commands and the logo under `anslcd_mutex`. Writes and ioctls serialize all controller access through the same mutex. Clear sends a fixed command sequence; send-control walks a NUL-terminated userspace command string.

State and persistence: global state is the MMIO pointer, short and long delay tunables, and the mutex. Delay changes persist only until module unload. No kernel-side display buffer is retained.

Dependencies and integration: depends on PowerPC OF discovery, `asm/io.h` 8-bit MMIO access, the misc-device subsystem, and ioctl constants from `ans-lcd.h`. Userspace ABI is `/dev/anslcd` plus private ioctls.

Risks: `ANSLCD_SENDCTRL` uses `__get_user()` without checking each fault result and relies on a userspace NUL terminator, so a bad pointer can produce partial/undefined command dispatch. Delay ioctls require `CAP_SYS_ADMIN` but accept unbounded values. The fixed physical address and ANS-specific OF check make this unsuitable for generic probing.

Test signals: on ANS hardware, expect `/dev/anslcd`, an initialized boot logo, correct clear/write behavior, and no oops on unload/reload. Negative tests should cover missing OF node, `misc_register()` failure, invalid ioctl numbers, non-admin delay writes, and userspace pointer faults.
