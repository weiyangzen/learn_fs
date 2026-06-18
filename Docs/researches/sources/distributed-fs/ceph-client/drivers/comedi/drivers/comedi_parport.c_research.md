# sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_parport.c

Purpose: Implements a legacy manually configured Comedi driver for standard PC parallel ports. It exposes data pins as bidirectional DIO, status pins as DI, control pins as DO, and optionally an interrupt-backed DI command subdevice using ACK/pin 10.

Important APIs/types/functions: Register offsets are `PARPORT_DATA_REG`, `PARPORT_STATUS_REG`, and `PARPORT_CTRL_REG`; control bits include IRQ enable and bidirectional enable. Important functions are `parport_attach()`, `parport_data_reg_insn_bits()`, `parport_data_reg_insn_config()`, `parport_status_reg_insn_bits()`, `parport_ctrl_reg_insn_bits()`, `parport_intr_cmdtest()`, `parport_intr_cmd()`, `parport_intr_cancel()`, and `parport_interrupt()`.

Control flow: Attach requests an I/O region from user-supplied option 0 and optionally requests an IRQ from option 1. It allocates three subdevices without IRQ, or four with IRQ. Subdevice 0 maps the 8-bit data register as DIO; its config handler toggles the parallel-port bidirectional control bit depending on `s->io_bits`. Subdevice 1 reads five status bits shifted down from the status register. Subdevice 2 writes four control output bits while preserving IRQ/bidir control bits. Optional subdevice 3 supports a narrow command interface with `TRIG_NOW` start and `TRIG_EXT` scan begin; command start enables IRQ, cancel disables it, and the interrupt handler writes a dummy zero sample then calls `comedi_handle_events()`.

State and persistence: State is the requested I/O base, optional IRQ, DIO `s->state`/`s->io_bits`, and hardware data/control registers. Attach initializes data and control registers to zero. No durable state exists beyond hardware latch values and Comedi runtime state.

Dependencies and integration points: Depends on Comedi legacy attach/detach, I/O-port access, and Linux IRQ APIs. Users must supply I/O base and optional IRQ through Comedi configuration. It integrates with Comedi async buffers only for the optional interrupt subdevice.

Risks: Parallel-port electrical behavior and inverted status/control lines are hardware-specific; the driver exposes raw register bits with limited normalization. Optional IRQ request failure is non-fatal and silently results in no command subdevice. Command samples are dummy wakeups, not captured status values. Test signals include I/O region rejection, data DIO input/output mode switching, status/control bit reads/writes, IRQ command start/cancel, and interrupt-generated Comedi events.
