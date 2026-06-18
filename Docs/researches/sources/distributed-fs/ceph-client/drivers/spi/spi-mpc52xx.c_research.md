# sources/distributed-fs/ceph-client/drivers/spi/spi-mpc52xx.c

## Purpose

`spi-mpc52xx.c` drives the dedicated MPC5200 SPI controller, not PSC-SPI mode. It implements a queued message engine around a small byte-oriented controller and a finite-state machine that runs from IRQs or a polling workqueue.

## Important APIs, Types, And Functions

`struct mpc52xx_spi` stores the SPI host, MMIO registers, two IRQs, bus frequency, debug counters, pending message queue, lock/work item, current message/transfer, FSM callback, buffers, CS state, and optional GPIO CS array. FSM handlers are `mpc52xx_spi_fsmstate_idle()`, `mpc52xx_spi_fsmstate_transfer()`, and `mpc52xx_spi_fsmstate_wait()`, driven by `mpc52xx_spi_fsm_process()`, `mpc52xx_spi_irq()`, and `mpc52xx_spi_wq()`.

## Control Flow, State, And Persistence

Probe maps registers, initializes controller pins/registers, checks for mode fault, allocates the host, gets optional GPIO chip-selects, initializes the queue/work/lock, requests MODF and SPIF IRQs when available, otherwise uses polling, and registers the controller. `transfer` queues messages under lock and schedules work. The idle state dequeues a message, programs mode and baud rate, asserts CS, and starts the first byte. Transfer state handles WCOL retry, MODF failure, RX byte storage, next-byte TX, and transition to wait. Wait state honors transfer delay, advances to the next transfer, or completes the message.

State is in-memory queued messages, FSM state, GPIO CS values, and volatile controller registers. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on OF address/IRQ helpers, PowerPC timebase/bus-frequency helpers, GPIO descriptors, workqueues, spinlocks, and SPI core. It matches `fsl,mpc5200-spi`.

## Risks And Test Signals

Risks include legacy `host->transfer` queueing, no timeout for queued work, WCOL retry behavior at slow speeds, MODF when pins are misconfigured, and mixed IRQ/poll operation. Test interrupt and polled modes, slow-speed WCOL scenarios, mode-fault detection, GPIO and native CS, transfer delays, multi-transfer messages, and remove while queue/work are active.
