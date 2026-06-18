# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t35.c

Purpose: implements the SGS-Thomson M48T35 Timekeeper RAM RTC for memory-mapped platforms, with BCD time read/write and SGI IP27 register-layout support.

Important APIs and types: `struct m48t35_rtc` maps the chip layout near the end of the Timekeeper RAM window, with an alternate member order for `CONFIG_SGI_IP27`. `struct m48t35_priv` holds mapped registers and a spinlock. RTC callbacks are `m48t35_read_time()` and `m48t35_set_time()`.

Control flow: probe requests and maps the memory resource, initializes the lock, and registers the RTC. Reads set the READ latch bit under lock, read date/time BCD fields, restore control, convert to `rtc_time`, and normalize 1970-2069/2070-style year handling. Writes validate 1970-2069, convert to BCD, set the SET bit under lock, write fields, and restore control.

State and persistence: battery-backed Timekeeper RAM contains the RTC registers and likely broader RAM content, although this driver exposes only time. Driver state is volatile mapping metadata and lock.

Dependencies and integration: platform memory resource, `readb()`/`writeb()`, BCD helpers, spinlocks, and RTC class registration.

Risks: supported date range is intentionally narrow and rejects dates after 2069. Day-of-week is ignored on read because hardware updates it only after a nonzero initial set. Register layout depends on build-time SGI configuration. No alarm or NVRAM provider is exposed despite the RAM-backed device.

Test signals: both register layouts, read latch/set latch behavior, 1969/1970/2069/2070 boundaries, BCD conversion, and memory-region request failures.
