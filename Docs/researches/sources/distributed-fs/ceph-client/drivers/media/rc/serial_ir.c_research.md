# sources/distributed-fs/ceph-client/drivers/media/rc/serial_ir.c

Purpose: legacy serial-port IR receiver/transmitter driver using modem-control pins on 8250-compatible UARTs. It supports homebrew, IRdeo, IRdeo Remote, AnimaX, and IgorPlug hardware variants.

Important APIs and functions: `struct serial_ir_hw` describes per-hardware pin polarity, UART control values, optional transmit callbacks, and lock. `struct serial_ir` stores timestamp, rc device, synthetic platform device, timeout timer, carrier, and duty cycle. Core functions include `hardware_init_port`, `serial_ir_irq_handler`, `frbwrite`, `serial_ir_timeout`, `serial_ir_probe`, open/close, TX helpers, suspend/resume, and module parameter initialization.

Control flow: module init validates `type`, fills default I/O and IRQ, registers a platform driver and synthetic platform device. Probe allocates a raw rc device, requests IRQ and I/O or MMIO resources, initializes the UART, autodetects receive polarity if needed, and registers rc-core. Open enables modem-status interrupts. The ISR reads UART status until no interrupt is pending, measures time between modem pin changes, filters spikes/noise through `frbwrite`, arms a timeout timer, and wakes raw decoding. TX iterates alternating pulse/space durations, toggling UART control pins or sending IRdeo serial bytes while maintaining target edge timing.

State and persistence: global module parameters define hardware type, I/O base, IRQ, mapped I/O, polarity, shared IRQ, and carrier behavior. Runtime state is global single-device state in `serial_ir`; no persistent storage exists. UART registers are reinitialized after resume.

Dependencies and integration points: depends on UART register definitions, port/MMIO I/O helpers, platform bus, interrupts, timers, rc-core raw RX/TX, and optional `CONFIG_IR_SERIAL_TRANSMITTER`. It often conflicts with the normal serial driver unless the port is reserved for IR.

Risks and edge cases: single global state prevents multiple instances. Busy-wait loops in TX and IRdeo send paths can burn CPU and depend on UART timing. IRQ handler has a pass limit but shared IRQ false positives are possible. Polarity autodetection can be wrong with noisy receivers. Resource acquisition requests IRQ before reserving port region. Softcarrier timing uses `ndelay`/`udelay` and can be imprecise under scheduling latency.

Test signals: loading with each hardware type, port existence test, active-high/low autodetection, raw pulse capture from a known remote, timeout event generation, TX waveform validation for homebrew/IRdeo, shared IRQ behavior, suspend/resume, and coexistence checks with disabled serial console/8250 ownership.
