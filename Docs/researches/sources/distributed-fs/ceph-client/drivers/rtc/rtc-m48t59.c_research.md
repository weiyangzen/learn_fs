# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t59.c

Purpose: supports ST M48T59/M48T02/M48T08 Timekeeper RTC/NVRAM devices across memory-mapped and platform-supplied I/O access modes, including optional alarm IRQs, battery status, and NVMEM exposure.

Important APIs and types: `struct m48t59_private` stores I/O base, IRQ, RTC device, and a spinlock. Platform data `struct m48t59_plat_data` supplies type, offset, and read/write callbacks. RTC callbacks cover time, alarm, proc battery output, and alarm IRQ enable. `m48t59_nvram_read()` and `m48t59_nvram_write()` back `devm_rtc_nvmem_register()`.

Control flow: probe chooses MEM or IO resource mode, fills default platform data and callbacks for memory resources, maps registers if needed, obtains optional IRQ, selects chip offset and alarm support by type, registers NVMEM for bytes before the RTC window, then registers the RTC. Reads/writes set READ/WRITE bits around BCD field access under the spinlock. Alarm writes support wildcard-ish invalid fields and are disabled on chips without alarm support or IRQ.

State and persistence: time, alarm, flags, and NVRAM are battery-backed hardware state. Software only serializes access. `pdata->offset` determines which address range is RTC registers versus NVRAM.

Dependencies and integration: depends on platform data for I/O-mapped chips, `linux/rtc/m48t59.h`, optional platform IRQ, NVMEM provider registration through RTC, and RTC class/proc hooks.

Risks: NVRAM read/write loops ignore the `offset` argument and use `cnt` directly, which is a correctness risk for nonzero-offset NVMEM accesses. Alarm methods return `-EIO` without IRQ. Century handling applies only M48T59 CEB/CB bits. Platform data defaults are mutable through `pdev->dev.platform_data`.

Test signals: each chip type offset and alarm feature behavior, memory versus I/O callback paths, NVMEM reads/writes with nonzero offsets, IRQ shared handling, battery flag proc output, century-bit rollover, and missing platform callbacks.
