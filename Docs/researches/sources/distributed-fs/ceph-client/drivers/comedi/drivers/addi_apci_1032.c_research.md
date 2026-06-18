# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1032.c

## Purpose

This driver supports the ADDI-DATA APCI-1032 32-channel digital input PCI board. It exposes a normal 32-bit DI subdevice and, when an IRQ is available, an asynchronous change-of-state interrupt subdevice for channels 0-15.

## Important APIs, types, and functions

Key register definitions cover DI, interrupt mode, status, and control registers. `struct apci1032_private` stores AMCC interrupt-controller I/O base plus cached mode/control masks. Important functions are `apci1032_reset()`, `apci1032_cos_insn_config()`, `apci1032_cos_cmdtest()`, `apci1032_cos_cmd()`, `apci1032_cos_cancel()`, `apci1032_interrupt()`, `apci1032_di_insn_bits()`, `apci1032_auto_attach()`, and `apci1032_detach()`.

## Control Flow

PCI probe calls COMEDI PCI auto-config. Auto-attach allocates private data, enables the PCI device, records AMCC BAR 0 and board BAR 1 bases, resets interrupt hardware, requests a shared IRQ if present, and allocates two subdevices. The first subdevice reads all 32 digital inputs. The second is a command-capable DI subdevice only if IRQ setup succeeded. Users configure COS mode with `INSN_CONFIG_DIGITAL_TRIG`; command start writes mode masks and enables the selected OR-edge or AND-level interrupt mode. The ISR verifies AMCC interrupt assertion, disables the board interrupt, reads the status, writes one sample, handles COMEDI events, and reenables the interrupt.

## State and Persistence

State includes cached `mode1`, `mode2`, and `ctrl` in `dev->private`, `s->state` for the last COS status sample, `dev->iobase`, `dev->irq`, and AMCC I/O base. Hardware interrupt configuration persists until reset, cancel, or detach; no nonvolatile state is touched.

## Dependencies and Integration Points

The file depends on COMEDI PCI helpers, Linux IRQ APIs, and `amcc_s5933.h` for interrupt assertion checks. It integrates with COMEDI async buffers through `comedi_buf_write_samples()` and `comedi_handle_events()`.

## Risks

COS configuration uses bit shifts from user data; out-of-range shifts deliberately clear new masks but preserve behavior should be tested. AND and OR modes are mutually exclusive and switching modes wipes old channel masks. IRQ handling assumes `dev->read_subdev` exists and that the AMCC interrupt bit correctly identifies the board on shared IRQ lines. The driver is marked untested, so register semantics are a hardware risk.

## Test Signals

Validation should include probe, 32-channel DI reads, no-IRQ fallback with the COS subdevice unused, OR edge and AND level interrupt commands, cancel disabling interrupts, shared IRQ rejection when AMCC does not assert, and detach resetting mode/control registers.
