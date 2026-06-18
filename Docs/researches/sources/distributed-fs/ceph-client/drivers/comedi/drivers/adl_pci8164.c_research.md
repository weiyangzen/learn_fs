# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci8164.c

## Purpose

This experimental driver supports the ADLINK PCI-8164 four-axis motion-control board by exposing axis register windows as generic COMEDI procedure subdevices.

## Important APIs, types, and functions

Register macros define per-axis offsets and four register groups: command/status, output/status, buffer 0, and buffer 1. The shared callbacks are `adl_pci8164_insn_read()` and `adl_pci8164_insn_write()`. `adl_pci8164_auto_attach()` creates four `COMEDI_SUBD_PROC` subdevices, each with four channels, using `s->private` to store the register offset.

## Control Flow

PCI probe calls COMEDI PCI auto-config. Auto-attach enables PCI, stores BAR 2 as `dev->iobase`, allocates four subdevices, and assigns each subdevice to one register group. Reads and writes compute `dev->iobase + PCI8164_AXIS(chan) + offset` for the channel and perform 16-bit port I/O for each requested sample. Detach uses generic PCI cleanup.

## State and Persistence

The driver keeps no private state beyond each subdevice's register offset pointer. Hardware command, status, and buffer registers hold runtime motion-controller state. There is no persistent storage and no explicit reset.

## Dependencies and Integration Points

The file depends on COMEDI PCI helpers and port I/O accessors. It presents low-level register access rather than a higher-level motion-control API, so user space must understand the PCI-8164 register protocol.

## Risks

Because the driver exposes raw procedure registers, incorrect user writes can directly affect motion hardware. There is no validation beyond channel count, no interrupt support, no reset, and no semantic decoding of command/status registers. The use of integer offsets stored in `void *` is a common older COMEDI pattern but should not be expanded without care.

## Test Signals

Validation includes probe, correct four subdevices with four channels each, 16-bit reads and writes to each axis/register group, expected hardware status changes after commands, bounds behavior for channel selection through COMEDI core, and clean detach.
