# sources/distributed-fs/ceph-client/drivers/comedi/drivers/aio_iiro_16.c Research

Implements a legacy Comedi driver for the ACCES I/O 104-IIRO-16 isolated input/relay output board. It supports 16 relay outputs, 16 digital inputs, and optional change-of-state interrupt streaming.

`aio_iiro_16_read_inputs()` reads both input bytes. `aio_iiro_16_cos()` is the IRQ handler; it verifies IRQ enable status, reads inputs, packs status bits above the 16 input bits, writes a long sample, and handles Comedi events. `aio_iiro_enable_irq()` toggles board IRQ behavior. `aio_iiro_16_cos_cmdtest()`, `_cmd()`, and `_cancel()` implement the async COS command. `aio_iiro_16_do_insn_bits()` and `_di_insn_bits()` implement relay and input instruction access. `aio_iiro_16_attach()` configures optional IRQ and subdevices.

Attach requests an 8-byte I/O region, disables board IRQs, optionally requests a valid legacy IRQ, creates DO and DI subdevices, and reads initial relay state. If IRQ exists, the DI subdevice becomes command-capable and uses `SDF_LSAMPL` because samples include status bits. Command start enables IRQ by reading the IRQ register; cancel disables by writing zero. Relay state persists in hardware registers and Comedi `s->state`; async command state is implicit in board IRQ enable.

Dependencies are legacy Comedi APIs, Linux IRQ handling, raw I/O ports, and Comedi async buffering. The driver is experimental. Risks include legacy IRQ validation, IRQ enable/disable side effects based on read versus write operations, and packed sample interpretation. Tests should cover valid IRQ mask handling, IRQ_NONE when status lacks IRQE, relay state initialization and writes, input byte ordering, COS command trigger validation, and cancel disabling further interrupts.
