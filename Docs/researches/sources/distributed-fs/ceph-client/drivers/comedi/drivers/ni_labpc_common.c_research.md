# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_common.c

## Purpose
`ni_labpc_common.c` contains the shared Lab-PC implementation for ISA `ni_labpc`, PCI `ni_labpc_pci`, and PCMCIA `ni_labpc_cs`. It implements AI instruction reads, AI command validation/execution, interrupt handling, AO writes, 8255 DIO setup, calibration DAC access, EEPROM access, and common resource initialization.

## Important APIs, Types, And Functions
`enum scan_mode` classifies single-channel, interval single-channel, multi-channel up, and multi-channel down scans. Range tables define Lab-PC+ AI, Lab-PC-1200 AI, and AO ranges. Access adapters `labpc_inb()`/`labpc_outb()` and `labpc_readb()`/`labpc_writeb()` let common code target I/O ports or MMIO.

AI helpers include `labpc_cancel()`, `labpc_ai_set_chan_and_gain()`, `labpc_setup_cmd6_reg()`, `labpc_read_adc_fifo()`, `labpc_clear_adc_fifo()`, `labpc_ai_insn_read()`, timing helpers around `labpc_adc_timing()`, `labpc_ai_scan_mode()`, `labpc_ai_check_chanlist()`, `labpc_ai_cmdtest()`, and `labpc_ai_cmd()`. Data movement is handled by `labpc_drain_fifo()`, `labpc_drain_dregs()`, and `labpc_interrupt()`, with ISA DMA delegated to `labpc_setup_dma()`, `labpc_drain_dma()`, and `labpc_handle_dma_status()`. AO/calibration/EEPROM functions include `labpc_ao_write()`, `labpc_ao_insn_write()`, `labpc_serial_out()`, `labpc_serial_in()`, `labpc_eeprom_read()`, `labpc_eeprom_write()`, `write_caldac()`, `labpc_calib_insn_write()`, and `labpc_eeprom_insn_write()`.

## Control Flow
`labpc_common_attach()` allocates `labpc_private`, selects byte-access callbacks from `dev->mmio` versus `dev->iobase`, clears command registers, optionally requests the IRQ, allocates two 8254 counter blocks, and creates five subdevices: AI, AO or unused, 8255 DIO, calibration or unused, and EEPROM or unused. Lab-PC-1200 boards get calibration and EEPROM subdevices; AO-capable boards initialize outputs to midscale.

Instruction AI reads cancel any command, program channel/gain/reference, configure command registers, clear FIFO, trigger conversions one at a time, poll data availability, and read FIFO words. Command execution first validates trigger combinations and timing, classifies scan mode, chooses transfer type based on DMA availability, wake flags, board FIFO support, and count size, programs channel/gain/range/reference, interval counter, 8254 pacers, FIFO, optional DMA, interrupt enables, external trigger/pacing bits, and finally starts software or hardware trigger under spinlock.

Interrupt handling reads status registers, rejects unrelated IRQs, handles overrun/overflow errors, drains data through ISA DMA or FIFO, clears timer interrupts, detects external stop, sets EOA when `count` reaches zero, and dispatches Comedi events.

## State And Persistence
`labpc_private` command-register shadows preserve bitfields across AI/AO/DIO/calibration operations. `count` tracks remaining samples for count-limited commands and can exceed 32 bits. `current_transfer` records whether interrupts should drain FIFO or ISA DMA. `stat1`/`stat2` cache latest status reads. Calibration and EEPROM subdevices use Comedi readback arrays; EEPROM readback is populated at attach.

## Dependencies And Integration Points
The file depends on Comedi core, 8255, 8254, Linux IRQ/delay/io helpers, `ni_labpc_regs.h`, `ni_labpc.h`, and optional ISA DMA wrappers. It exports `labpc_common_attach()` and `labpc_common_detach()` for bus-specific modules.

## Risks
Command validation and hardware programming are tightly coupled to scan direction rules; Lab-PC+ cannot scan up, while Lab-PC-1200 can. External start and external stop cannot be used together. FIFO drain has a hard timeout to avoid infinite loops. EEPROM writes are restricted to addresses 16-127, but writes still affect persistent board memory. `labpc_common_detach()` only frees `devpriv->counter`; the pacer is stored in `dev->pacer` and relies on generic cleanup. IRQ detection logic combines `stat2` even for non-1200 boards after initializing it to zero; status handling must remain careful.

## Test Signals
Tests should cover I/O versus MMIO callback selection, command-trigger validation matrix, timing rounding for convert/scan timer combinations, scan-mode chanlist validation, transfer-mode selection for DMA/FIFO/CMDF flags, FIFO drain count decrement and timeout, external stop drain path, overrun/overflow event generation, AO range bit updates and readback, calibration DAC serial writes, EEPROM readback population and user-area write restriction, attach subdevice layout for Lab-PC+ versus 1200 variants, and IRQ/no-IRQ command availability.
