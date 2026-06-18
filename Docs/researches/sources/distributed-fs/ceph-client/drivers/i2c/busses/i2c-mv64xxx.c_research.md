# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mv64xxx.c

Purpose: Marvell mv64xxx/Orion and compatible Allwinner I2C controller driver. It supports interrupt-driven and atomic polling transfers, 10-bit addressing, runtime PM, bus recovery, clock/reset control, register-layout variants, and an optional Marvell transaction-generator offload path.

Important APIs/types: `struct mv64xxx_i2c_data` owns message state, FSM state/action, control bits, register offsets, clock factors, waitqueue, spinlock, adapter, offload flags, errata flags, runtime PM resources, and recovery info. `struct mv64xxx_i2c_regs` describes register layout variants. Key functions are `mv64xxx_i2c_xfer()`, `mv64xxx_i2c_xfer_atomic()`, `mv64xxx_i2c_execute_msg()`, `mv64xxx_i2c_fsm()`, `mv64xxx_i2c_do_action()`, `mv64xxx_i2c_intr()`, `mv64xxx_i2c_offload_xfer()`, `mv64xxx_of_config()`, and runtime PM callbacks.

Control flow: probe maps registers, gets optional clocks and reset, configures baud factors from platform data or OF, initializes optional pinctrl recovery, enables runtime PM, requests IRQ, and registers a numbered adapter. Normal transfer resumes the device, stores the message array, chooses offload for one-message or write-read transactions of 1-8 bytes when allowed, otherwise starts the FSM. The FSM interprets controller status values, chooses actions for address bytes, data bytes, restarts, receive ACK control, STOP, and error recovery. Completion wakes a waitqueue or is polled in atomic mode.

State and persistence: active message pointers and counters exist only during transfer. Runtime PM suspend asserts reset and disables clocks; resume enables clocks, resets hardware, and initializes registers. Persistent configuration includes baud factors, register layout, offload enablement, errata delay, inverted clear semantics, and bus recovery pinctrl.

Dependencies and integration: integrates with OF compatibles for Allwinner sun4i/sun6i and Marvell mv64xxx/mv78230 variants, legacy `mv643xx_i2c` platform data, clocks, resets, pinctrl-based bus recovery, runtime PM, IRQs, and the I2C core including `.xfer_atomic`.

Risks: the FSM is broad and status-code dependent; unexpected status triggers hardware reinit and bus recovery. Timeout abort attempts can still leave `block` set and require full hardware reinit. Offload handles only up to 8 bytes and has separate interrupt/status semantics from the normal FSM. Some cleanup paths manually call runtime suspend based on PM state. Atomic polling re-enters the IRQ handler and relies on a small delay for status-register update ordering.

Test signals: cover normal and atomic transfers, 7-bit and 10-bit addressing, repeated starts, read/write NACKs, arbitration loss, timeout abort and recovery, offloaded single read/write and write-read paths, runtime suspend/resume, Allwinner inverted IFLG clearing, mv78230 errata delay, and probe via OF and legacy platform data.
