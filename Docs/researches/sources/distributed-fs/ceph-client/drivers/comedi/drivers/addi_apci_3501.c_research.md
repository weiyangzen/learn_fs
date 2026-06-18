# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3501.c

## Purpose

This driver supports the ADDI-DATA APCI-3501 analog output board variants with 4 or 8 AO channels, 2 digital inputs, 2 digital outputs, and an EEPROM memory subdevice. The timer/watchdog hardware is recognized in comments but not supported as a COMEDI subdevice.

## Important APIs, types, and functions

`struct apci3501_private` stores the AMCC base. Important functions are `apci3501_wait_for_dac()`, `apci3501_ao_insn_write()`, DIO handlers, `apci3501_eeprom_wait()`, `apci3501_eeprom_readw()`, `apci3501_eeprom_get_ao_n_chan()`, `apci3501_eeprom_insn_read()`, `apci3501_reset()`, `apci3501_auto_attach()`, and `apci3501_detach()`.

## Control Flow

Auto-attach enables PCI, records AMCC BAR 0 and board BAR 1, reads AMCC NVRAM user data to determine analog-output channel count, allocates five subdevices, initializes AO if the EEPROM reports channels, initializes 2-bit DI and DO, leaves timer/watchdog unused, adds a 256-word internal memory subdevice for EEPROM reads, and resets outputs. AO writes set board-wide range mode, wait until the DAC ready bit is set, write channel/value data, and update readback. Reset clears DO and drives all eight possible AO channels to 0 V bipolar.

## State and Persistence

Runtime state is AO readback, DO state, board-wide AO range mode, and AMCC EEPROM read state. The driver reads EEPROM but does not write it. Reset writes current analog/digital outputs but no nonvolatile data.

## Dependencies and Integration Points

The file depends on COMEDI PCI, AMCC S5933 NVRAM register definitions, COMEDI readback helpers, and range tables. It integrates with PCI ID `0x3001`, whose variants share IDs and require EEPROM feature discovery.

## Risks

`apci3501_wait_for_dac()` spins without an explicit timeout, unlike most COMEDI wait paths, so broken hardware can hang the caller. AO range is board-wide although exposed per-channel through chanspec; writing one channel can change all channels' output range. EEPROM parsing must match ADDI function descriptors or AO may be disabled. Reset loops over eight channels even when only four exist, relying on harmless writes.

## Test Signals

Signals include EEPROM-reported 4- and 8-channel variants, AO bipolar/unipolar writes with readback, rejection of >13-bit unipolar values, DI/DO bits, EEPROM memory reads, reset setting outputs to zero, and behavior when DAC ready never appears.
