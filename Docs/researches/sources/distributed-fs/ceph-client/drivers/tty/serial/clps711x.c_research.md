# sources/distributed-fs/ceph-client/drivers/tty/serial/clps711x.c

Purpose: CLPS711x/EP7209 UART serial driver exposing two `ttyCL` ports through serial core, backed by UART MMIO registers, CLPS711x syscon bits, optional modem-control GPIOs, and optional console support.

Important APIs/types/functions: `struct clps711x_port` embeds `uart_port` and stores TX-enabled state, a separate RX IRQ, `regmap *syscon`, and `mctrl_gpios *gpios`. `uart_clps711x_ops` provides serial callbacks. Key routines are `uart_clps711x_int_rx()`, `uart_clps711x_int_tx()`, `uart_clps711x_startup()`, `uart_clps711x_shutdown()`, `uart_clps711x_set_termios()`, `uart_clps711x_set_ldisc()`, and `uart_clps711x_probe()`.

Control flow: init optionally attaches console, registers UART/platform drivers. Probe allocates state, gets clock/MMIO/TX IRQ/RX IRQ/syscon, initializes GPIO modem control, adds the port, disables non-console hardware, and requests both IRQs. RX IRQ drains until `SYSFLG_URXFE`, classifies errors, handles SysRq, and pushes flip data. TX IRQ writes `x_char`, then drains xmit FIFO until `SYSFLG_UTXFF`, disabling TX IRQ when idle.

State/persistence: per-device state and syscon/hardware registers hold the live configuration. `tx_enabled` mirrors IRQ state. Termios lives in `UBRLCR` plus serial-core masks. No disk persistence.

Dependencies/integration: DT compatible `cirrus,ep7209-uart`, syscon phandle, clocks, regmap, platform resources, `serial_mctrl_gpio`, serial core, TTY flip buffers, and console core.

Risks: DT IRQ order is critical because TX and RX are separate. `tx_enabled` must stay synchronized with IRQ calls. Shared syscon state affects UART enable and IrDA mode. Unsupported termios flags are modified in place.

Test signals: both IRQs, syscon enable/disable, GPIO modem control, IrDA line discipline on line 0, console setup with/without options, RX error paths, TX wakeups, and remove after active use.
