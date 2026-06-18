# sources/distributed-fs/ceph-client/drivers/clocksource/mmio.c

Purpose: provides a small reusable helper for registering simple MMIO-backed clocksources whose counter can be read directly from a 16- to 64-bit register.

Important APIs, types, and functions: `struct clocksource_mmio` wraps the target MMIO register and embedded `struct clocksource`. Exported-style helper functions are `clocksource_mmio_readl_up()`, `clocksource_mmio_readl_down()`, `clocksource_mmio_readw_up()`, and `clocksource_mmio_readw_down()`. `clocksource_mmio_init()` allocates the wrapper, validates bit width, fills clocksource fields, marks it continuous, and calls `clocksource_register_hz()`.

Control flow: clients call `clocksource_mmio_init(base, name, hz, rating, bits, read)`. The chosen read callback converts a 32-bit or 16-bit MMIO read into an increasing cycle value, either directly for up-counters or by inverting and masking down-counters. The helper does no mapping or clock enabling; callers must prepare hardware first.

State and persistence: only one allocated wrapper is created per call, and the state is owned by the clocksource core after successful registration. There is no cleanup on registration failure beyond normal allocation lifetime concerns visible in callers.

Dependencies and integration points: depends on `clocksource_register_hz()`, relaxed MMIO read accessors, and kernel allocation. It is used by many platform timer drivers in this group as their clocksource registration primitive.

Risks: callers must pass the actual readable counter register, a correct width, an accurate frequency, and a read function matching counter direction and access size. Passing `NULL` only works when the callback ignores the wrapper register, as EP93xx does. Bit widths below 16 or above 64 are rejected. Test signals are downstream: clocksource registration succeeds, `clocksource` debugfs shows the expected name/rating/mask, and monotonicity tests match the counter direction.
