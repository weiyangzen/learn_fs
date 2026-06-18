<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sa1100_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sa1100_wdt.c

Purpose: legacy miscdevice watchdog for SA11x0/PXA2xx OS timer channel 3 watchdog functionality.

Important APIs, types, and functions: global state stores OS timer frequency, open bit, `pre_margin`, boot status, MMIO base, module margin, and clock. Key routines are `sa1100dog_open()`, release/write/ioctl handlers, probe, and remove.

Control flow: probe maps OS timer registers, gets and enables `OSTIMER0`, derives `oscr_freq`, sets bootstatus from platform data, computes default margin, and registers `/dev/watchdog`. Open enforces single user, sets match register 3 to current counter plus margin, clears status, enables watchdog match and interrupt. Writes and keepalive update the match register. Timeout ioctl validates the counter product fits 32 bits and updates `pre_margin`.

State and persistence behavior: watchdog cannot be disabled once activated according to comments; release only logs and clears open state. Hardware state is OSMR3, OSSR, OWER, and OIER. Software state is precomputed margin and bootstatus.

Dependencies and integration points: depends on platform MMIO resource, legacy clock name lookup, platform data boot flag, miscdevice ABI, and SA/PXA OS timer hardware.

Risks and edge cases: no nowayout parameter or magic close is implemented because stop is unavailable. Timeout arithmetic can overflow without the explicit check. Clock lookup uses `clk_get(NULL, "OSTIMER0")`, which is global and platform-specific.

Test signals: single-open behavior, match register refresh, timeout bounds around 32-bit counter wrap, platform bootstatus, clock enable/disable, and release while active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sa1100_wdt.c -->
