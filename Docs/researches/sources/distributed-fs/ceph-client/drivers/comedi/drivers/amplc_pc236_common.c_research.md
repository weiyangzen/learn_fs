# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236_common.c Research

Implements common support for Amplicon PC236-family drivers: a primary 8255 DIO subdevice and an optional interrupt-driven pseudo-DI subdevice.

`pc236_intr_update()` toggles software interrupt enable and invokes an optional board callback. `pc236_intr_check()` verifies enabled state and optionally delegates hardware check/clear. `pc236_intr_cmdtest()`, `_cmd()`, and `_cancel()` implement the Comedi async interrupt command. `pc236_interrupt()` writes a zero sample and handles events when the board interrupt is valid. Exported `amplc_pc236_common_attach()` creates subdevices, initializes 8255, and requests IRQ.

Common attach sets `dev->iobase`, allocates two subdevices, initializes subdevice 0 through `subdev_8255_io_init()`, marks subdevice 1 unused, disables interrupts, and turns subdevice 1 into command-capable DI only if IRQ request succeeds. Commands accept `TRIG_NOW`, `TRIG_EXT`, `TRIG_FOLLOW`, `TRIG_COUNT`, and `TRIG_NONE` in a fixed pattern, then simply enable board interrupts until cancel. State persists in `pc236_private.enable_irq` under `dev->spinlock`.

Dependencies are Comedi 8255 helper, Linux IRQ APIs, Comedi async event buffering, and exported symbol linkage for front-end modules. Risks include generating only zero-valued samples, optional callbacks changing ISR validity, and subdevice 1 being unused when IRQ unavailable. Tests should cover cmdtest trigger validation, start/cancel toggling, IRQ_NONE when disabled, callback invocation under lock, successful sample/event on valid IRQ, and attach behavior with failed IRQ request.
