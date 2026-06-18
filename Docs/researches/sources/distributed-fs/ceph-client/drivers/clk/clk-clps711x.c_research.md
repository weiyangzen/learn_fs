# sources/distributed-fs/ceph-client/drivers/clk/clk-clps711x.c


### Purpose
`clk-clps711x.c` is an early OF clock provider for Cirrus CLPS711X/EP7209 systems. It derives fixed CPU, bus, PLL, timer, PWM, SPI, UART, and tick clocks from boot registers and exposes them through a onecell provider.

### Important APIs, Types, And Functions
The main entry point is `clps711x_clk_init_dt()`, registered via `CLK_OF_DECLARE()`. `struct clps711x_clk` holds a spinlock and flexible `clk_hw_onecell_data`. The file uses generic fixed-rate, fixed-factor, and divider-table helpers with `spi_div_table` and `timer_div_table`.

### Control Flow, State, And Persistence
Early init reads `startup-frequency`, maps the syscon region, computes PLL/CPU/bus/timer/SPI/PWM rates from `PLLR`, `SYSFLG2`, and `SYSCON` bits, programs timer mode bits in `SYSCON1`, registers all clocks, logs per-clock registration failures, and adds the onecell provider. State persists in hardware timer-mode bits and the registered static clock graph; there is no remove path because this is early boot infrastructure.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF address mapping, CLPS711X syscon bit definitions, fixed-rate/fixed-factor/divider CCF helpers, and clock IDs from `clps711x-clock.h`. Risks are `BUG_ON()` for mapping/allocation failure, limited recovery if individual clock registration fails, hard-coded oscillator frequencies, and early register mutation of timer modes. Test signals include EP7209 DT provider registration, correct CPU/bus rates in external-clock and PLL modes, timer1/timer2 divider behavior, SPI divider table selection, and no boot failure when optional startup frequency is absent.
