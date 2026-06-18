# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu.c

Purpose: implements the PMU system controller driver for Apple PowerBooks and some PowerMacs. The PMU controls power, battery charging, ADB, NVRAM/RTC, brightness-related events, sleep/wake, and user-visible `/dev/pmu` plus `/proc/pmu` interfaces.

Important APIs and functions: exported APIs include `pmu_request()`, `pmu_queue_request()`, `pmu_poll()`, `pmu_poll_adb()`, `pmu_wait_complete()`, `pmu_suspend()`, `pmu_resume()`, `pmu_unlock()`, and on PPC32 battery/IR LED exports. ADB integration is `via_pmu_driver` with `pmu_send_request()`, `pmu_adb_autopoll()`, and `pmu_adb_reset_bus()`. Core transport is `pmu_start()`, `pmu_sr_intr()`, and `via_pmu_interrupt()`. Power/RTC helpers are `pmu_get_time()`, `pmu_set_rtc_time()`, `pmu_restart()`, and `pmu_shutdown()`.

Control flow: `find_via_pmu()` locates and maps VIA/optional GPIO registers, determines PMU kind, initializes interrupt masks, and calls `init_pmu()`. `via_pmu_start()` requests VIA/GPIO IRQs early and drains pending PMU work. Requests are validated against `pmu_data_len`, queued under `pmu_lock`, and byte-framed through VIA shift-register handshakes. `via_pmu_interrupt()` handles SR and CB1/GPIO events, completes normal requests outside the lock, acknowledges PMU interrupt packets into two buffers, then decodes ADB, tick, environment, brightness, and battery events.

State and persistence: global PMU state machine, current/last request queue, awaiting ADB reply, interrupt buffers, IRQ stats, battery cache, PMU model/version, proc entries, sleep flags, server/lid wake options, and `/dev/pmu` per-open ring buffers. RTC, server mode, wake events, and power actions affect hardware persistence.

Dependencies and integration: tightly integrated with unified ADB, PMac feature calls, OF/IRQ mapping, GPIO, procfs, miscdevice, suspend/syscore, PMac backlight, input PMU events, low-level sleep assembly, PCI/cache/MMU helpers, and battery/APM consumers.

Risks: this is timing-sensitive VIA protocol code with shared interrupt and polling paths. Many globals are protected only by `pmu_lock` or local IRQ disabling, and request structures must outlive completion. `/dev/pmu` is an old ABI with a small interrupt ring. Sleep paths are hardware-specific and manipulate cache, MMU, ASIC power, IRQs, and PMU locks. `pmu_data_len` must match firmware command framing exactly.

Test signals: PMU detection across Ohare/Heathrow/Paddington/KeyLargo and m68k PB2, ADB keyboard/mouse via PMU, request queue completion, PMU interrupt stats, battery proc updates, RTC get/set, `/dev/pmu` read/poll/ioctl and compat ioctl, backlight and PMU event integration, server-mode proc option, restart/shutdown commands, suspend/resume on supported PPC32 systems, and no interrupt-loop stalls.
