# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwbus.h

Purpose: Defines the bus abstraction used by CW1200 common code to run over SDIO or SPI.

Important APIs and types: Forward-declares `struct hwbus_priv`, declares `cw1200_irq_handler` and `__cw1200_irq_enable`, and defines `struct hwbus_ops` with copy-from-I/O, copy-to-I/O, lock, unlock, align-size, and power-management callbacks.

Control flow: Bus modules instantiate `hwbus_ops` and pass them to `cw1200_core_probe`. Common `hwio`, BH, firmware, and PM code call through the ops without knowing the physical bus.

State and persistence: No direct state; bus-private state is opaque and owned by SDIO/SPI modules.

Dependencies and integration: Bridges core code to SDIO/SPI implementations. The comment on `__cw1200_irq_enable` requires callers to hold `hwbus_ops->lock`.

Risks: The ops contract is small but strict. Incorrect alignment, missing lock coverage, or IRQ enable without bus lock can corrupt transfers or race interrupts. PM callback semantics must match wake-capable IRQ setup for each bus.

Test signals: Run identical core tests over SDIO and SPI, including aligned/unaligned frame sizes, IRQ enable/disable paths, and suspend wake configuration.
