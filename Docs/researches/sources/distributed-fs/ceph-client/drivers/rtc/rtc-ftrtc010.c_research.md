# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ftrtc010.c

Purpose: supports the Faraday FTRTC010/Gemini SoC RTC, including a workaround for hardware that cannot directly store full absolute time. The driver derives current time from hardware day/hour/min/sec counters plus a software offset register.

Important APIs/types/functions: `struct ftrtc010_rtc` stores MMIO base, IRQ, and PCLK/EXTCLK handles. `ftrtc010_rtc_read_time()` reads counters and `FTRTC010_RTC_RECORD` offset. `ftrtc010_rtc_set_time()` computes and writes a new offset and triggers control register bit `0x01`. `ftrtc010_rtc_probe()` enables clocks, maps MMIO, computes RTC range from current counters, requests IRQ, and registers the RTC.

Control flow: probe enables optional clocks with explicit unwind, obtains IRQ and memory resource, maps registers, allocates the RTC, samples the current counter baseline to set `range_min`/`range_max`, requests a shared IRQ, then registers the RTC. The IRQ handler currently acknowledges nothing and always returns handled.

State and persistence: persistent time is represented by hardware counters plus the offset record register. Runtime state includes clocks and the mapped base. The clocks are disabled on remove or probe failure.

Dependencies and integration: depends on platform/OF matching (`cortina,gemini-rtc`, `faraday,ftrtc010`), clk framework, MMIO, IRQ, and RTC core.

Risks and test signals: the IRQ handler is a stub, so alarm/interrupt behavior is not implemented. `devm_clk_get()` failures are logged but treated as optional; cleanup checks `IS_ERR`. Test clock enable/unwind, offset math after long uptime, range calculations, IRQ request, remove cleanup, and read/set round trips.
