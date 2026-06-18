# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_at_ao.c

## Purpose
`ni_at_ao.c` is the legacy ISA Comedi driver for NI AT-AO-6 and AT-AO-10 analog output boards. It provides direct AO writes, 8-bit DIO, and internal calibration DAC access. IRQ and DMA configuration options are documented but unused.

## Important APIs, Types, And Functions
`struct atao_board` defines board name and AO channel count. `struct atao_private` shadows command registers `cfg1` and `cfg3` and has a `caldac` array for calibration readback intent. `atao_select_reg_group()` toggles the alternate register group bit. `atao_ao_insn_write()` writes AO samples after Comedi offset munging. `atao_dio_insn_bits()` and `atao_dio_insn_config()` implement 8-bit DIO with nibble-granular direction. `atao_calib_insn_write()` serializes channel/value data into three DAC8800 TrimDACs. `atao_reset()` applies the documented board reset sequence. `atao_attach()` creates all subdevices.

## Control Flow
Legacy attach requests a 0x20-byte I/O region, allocates private data, allocates an 8254 pacer, and creates four subdevices: AO, DIO, calibration, and an unused EEPROM placeholder. AO channel 0 requires register group 2 access, so writes to channel 0 temporarily select group 2 and restore group 1 afterward. DIO config maps channel 0-3 and 4-7 to separate output-enable bits in `CFG3`. Calibration writes clock an 11-bit channel/value bitstring MSB first, then strobe the target caldac.

Reset clears command registers, configures counter outputs high, puts caldac control into NOP, clears the FIFO, selects group 2 to clear interrupt/DMA flags, and returns to group 1.

## State And Persistence
Persistent runtime state is the command-register shadows in `atao_private`, AO and calibration readback arrays, and DIO subdevice state/io bits. Hardware outputs remain programmed until reset or subsequent writes. No streaming state is present.

## Dependencies And Integration Points
The driver uses legacy Comedi attachment, ISA port I/O, Comedi 8254 helper allocation, Comedi DIO helpers, and `module_comedi_driver()`. It is selected by board name through the `comedi_driver` board table rather than PCI/PCMCIA auto discovery.

## Risks
The EEPROM subdevice is unused despite calibration values being factory-stored there; calibration persistence must be handled by user tooling or external mechanisms. DIO direction is configured per nibble, not per channel. AO range is selected solely from user option `[3]`, reflecting hardware jumpers; incorrect configuration misrepresents output voltage. Register group switching around channel 0 is a fragile hardware quirk.

## Test Signals
Tests should verify board-name selection for 6/10 AO channels, I/O region validation, AO offset-munged writes and channel 0 group switching, AO readback, DIO nibble direction mapping to `CFG3`, caldac serial bit order and strobe, reset register sequence, pacer allocation failure, and detach through `comedi_legacy_detach()`.
