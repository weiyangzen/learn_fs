# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rk3x.c

Purpose: Rockchip RK3xxx-family I2C platform driver. It supports multiple SoCs, normal and atomic/polling transfers, combined register-read acceleration, clock-rate notifier timing updates, and GRF configuration for controllers with selectable new/old interfaces.

Important APIs/types/functions: `struct rk3x_i2c` keeps adapter, device, SoC timing callbacks, MMIO, clocks, notifier, IRQ, parsed timings, spinlock, wait queue, active message, mode, state, processed count, and error. `struct rk3x_i2c_soc_data` selects GRF offset and either `rk3x_i2c_v0_calc_timings()` or `rk3x_i2c_v1_calc_timings()`. `rk3x_i2c_algorithm` exposes `.xfer`, `.xfer_atomic`, and functionality. Transfer control is in `rk3x_i2c_setup()`, `rk3x_i2c_start()`, IRQ handlers for start/write/read/stop, and `rk3x_i2c_xfer_common()`.

Control flow: probe parses firmware timings, configures GRF if needed, gets clocks/IRQ, registers a clock notifier, computes dividers, and adds the adapter. `rk3x_i2c_xfer_common()` enables clocks and loops through messages. `rk3x_i2c_setup()` either lets hardware handle a short write followed by read using MRXADDR/MRXRADDR, or sets plain TX/RX mode per message. The start IRQ disables START and transitions to write or read. Write IRQ fills up to the 32-byte transmit buffer; read IRQ drains up to 32-byte receive chunks and schedules the next chunk. Stop IRQ clears STOP and wakes waiters. Atomic mode disables the IRQ line and polls by calling the IRQ handler.

State and persistence: persistent SoC data chooses timing formula and GRF behavior. Active transfer state is guarded by `lock` and represented by `busy`, `state`, `msg`, `processed`, `is_last_msg`, and `error`. Clock notifier state persists so divider changes track rate transitions pre/post/abort.

Dependencies/integration: Linux I2C core, platform/OF, clk framework including notifiers, syscon/regmap for GRF, spinlocks/wait queues, and MMIO FIFOs. Functionality advertises I2C, SMBus emulation, and protocol mangling.

Risks: hardware cannot do true repeated START; driver approximates it by resetting internal state and issuing a new START. Combined register-read mode only supports writes shorter than four bytes before a read. NACK handling must respect `I2C_M_IGNORE_NAK`. Timing calculations are complex and can silently clamp when target rate is unreachable. Clock notifier updates dividers under lock and enabled pclk; misuse can race with active transfers.

Test signals: test write, read, multi-chunk >32-byte reads/writes, short write-read combined transfers, fallback repeated-start sequencing, NACK with and without ignore flag, timeout forced STOP, atomic polling, GRF setup on rv1126/rk3066/rk3188, v0/v1 timing edge rates, clock rate changes, and suspend/resume divider reprogramming.
