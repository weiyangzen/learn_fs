# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec.c

## Purpose
Parent MFD and transport driver for NVIDIA/Compal NVEC embedded controllers. It runs a Tegra I2C slave state machine, queues sync/async EC commands, dispatches EC events to notifier subscribers, and creates child devices for keyboard, mouse, power, and OEM LED functions.

## Important APIs, Types, And Functions
Exports `nvec_write_async()`, `nvec_write_sync()`, `nvec_register_notifier()`, `nvec_unregister_notifier()`, and `nvec_msg_free()`. Internals include `nvec_msg_alloc()`, `nvec_request_master()`, `nvec_dispatch()`, `nvec_interrupt()`, `nvec_rx_completed()`, `nvec_tx_completed()`, `tegra_init_i2c_slave()`, `tegra_nvec_probe()`, remove and PM callbacks, and the `nvec_devices[]` MFD cells.

## Control Flow
Probe reads `slave-addr`, maps the I2C-slave controller, gets IRQ/clock/reset/request GPIO, initializes lists, completions, work items, and the message pool, requests an IRQ with `IRQF_NO_AUTOEN`, enables the slave controller, turns on EC global events, installs a catch-all status notifier, optionally fetches firmware version synchronously, adds MFD children, unmutes speakers, and enables lid/power-button events. Async writes allocate TX messages and schedule `tx_work`, which pulls the request GPIO low and waits for the EC transfer completion. The IRQ handler reads/writes bytes through a finite-state machine, queues complete RX messages, and completes TX/sync waiters. `rx_work` matches sync responses or calls the notifier chain for unsolicited events.

## State And Persistence
`struct nvec_chip` owns MMIO, clock/reset/GPIO, notifier list, RX/TX queues, message pool, current RX/TX pointers, completions, locks, sync-write bookkeeping, and state-machine integer. `nvec_power_handle` and `pm_power_off` are global side effects. No durable storage exists.

## Dependencies And Integration Points
Depends on platform/OF, Tegra I2C registers, clk/reset/GPIO, IRQs, workqueues, MFD core, atomic notifiers, and PM sleep. Child drivers use the exported write/notifier APIs through their parent platform device.

## Risks
The interrupt state machine is sensitive to status flag combinations and manually recovers from partial RX/TX. Message pool exhaustion can break RX or TX; TX buffers deliberately start at one quarter of the pool to reserve RX capacity. `nvec_write_sync()` has a fixed 2s timeout and global pending tuple. `pm_power_off` is overwritten and unconditionally cleared on remove with a FIXME. Suspend depends on synchronous EC commands.

## Test Signals
OF probe with valid/invalid `slave-addr`, IRQ byte-sequence tests for RX event, sync response, EC read request, premature END_TRANS, pool exhaustion, TX timeout, child MFD creation, notifier dispatch, firmware request, suspend/resume, global event toggling, and `pm_power_off` behavior.
