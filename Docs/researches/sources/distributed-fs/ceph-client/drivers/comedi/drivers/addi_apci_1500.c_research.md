# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1500.c

## Purpose

This driver supports the ADDI-DATA APCI-1500 16-channel DI / 16-channel DO PCI board with Zilog Z8536-based pattern interrupts and three counter/timer channels. It exposes DI, DO, and timer subdevices, with optional async DI interrupt support.

## Important APIs, types, and functions

`struct apci1500_private` stores AMCC and add-on BAR bases, clock source, and AND/OR trigger pattern masks. Z8536 access is serialized by `z8536_read()`, `z8536_write()`, and `z8536_reset()`. Other important functions include `apci1500_ack_irq()`, `apci1500_interrupt()`, `apci1500_di_cfg_trig()`, `apci1500_di_inttrig_start()`, `apci1500_di_cmdtest()`, `apci1500_di_cmd()`, `apci1500_di_cancel()`, `apci1500_timer_insn_config()`, `apci1500_timer_insn_read()`, `apci1500_timer_insn_write()`, and `apci1500_auto_attach()`.

## Control Flow

Auto-attach enables the PCI device, records BAR 0 AMCC, BAR 1 Z8536, and BAR 2 add-on bases, resets the Z8536, requests an IRQ, allocates three subdevices, initializes DI and DO, clears DO state, and sets up a three-channel timer subdevice. DI async commands are two-stage: users first configure AND or OR trigger patterns with `INSN_CONFIG_DIGITAL_TRIG`, then `do_cmd` installs an internal trigger callback. When the internal trigger fires, the driver writes Z8536 pattern masks, enables matching port interrupts, enables ports, and authorizes the main interrupt. The ISR acknowledges port A/B interrupt status, distinguishes port B diagnostic errors from input events, writes a status sample, and handles events.

## State and Persistence

Cached state includes trigger pattern mask/transition/polarity arrays, selected clock source, DO state in the subdevice, and Z8536 mode/counter registers. Hardware state is reset at attach and interrupt disable on detach. No disk persistence exists.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, AMCC S5933 definitions, Z8536 register definitions, COMEDI command validation helpers, DIO state helpers, and counter/timer instruction conventions including 8254 mode constants.

## Risks

Z8536 indexed control access is sensitive and protected by `dev->spinlock`; missing serialization would corrupt register selection. Pattern configuration is complex: AND trigger edge mode allows only one edge-detect channel per port, and invalid shifts must be rejected. `INSN_CONFIG_SET_GATE_SRC` appears to preserve only the gate-enable bit when updating mode, so mode-bit handling is a change-sensitive area. Timer clock-source mapping stores hardware value 3 for user source 2, which must remain documented by tests.

## Test Signals

Signals include DI reads, DO writes, OR/AND pattern interrupt samples for both ports, voltage and short-circuit diagnostic status bits, timer arm/disarm/read/write, all supported 8254-mode translations, clock-source get/set round trips, IRQ disable on cancel/detach, and no shared-IRQ handling when AMCC does not assert.
