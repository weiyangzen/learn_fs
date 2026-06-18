# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dmm32at.c

## Purpose

This driver supports the Diamond Systems Diamond-MM-32-AT board. It provides 32-channel 16-bit analog input, timer/interrupt-driven AI commands, four-channel 12-bit analog output, and a paged 8255 digital I/O subdevice.

## Important APIs, Types, and Functions

Important routines include `dmm32at_reset()`, `dmm32at_ai_set_chanspec()`, `dmm32at_ai_insn_read()`, `dmm32at_ai_cmdtest()`, `dmm32at_setaitimer()`, `dmm32at_ai_cmd()`, `dmm32at_isr()`, `dmm32at_ao_insn_write()`, `dmm32at_8255_io()`, and `dmm32at_attach()`. Range data is in `dmm32at_airanges`, `dmm32at_rangebits[]`, and `dmm32at_aoranges`.

## Control Flow, State, and Persistence

Attach accepts only specific ISA base addresses, claims 0x10 ports, resets and probes readback/status values, optionally requests an IRQ, and creates AI/AO/8255 subdevices. AI setup resets FIFO, optionally enables scan mode, writes low/high channels and range bits, then waits for settling. Command mode validates timer-only scan/convert timing, programs the onboard counters through paged registers under `dev->spinlock`, enables AI interrupts and clock, and the ISR drains one scan into the Comedi buffer. AO writes LSB then MSB/channel, waits for DAC not busy, does a dummy read to update the DAC, and stores readback.

## Dependencies and Integration Points

Dependencies include Linux delay/IRQ, Comedi core, and `comedi_8255`. The 8255 integration uses `subdev_8255_cb_init()` because the DIO registers are behind the board's page register.

## Risks and Test Signals

`dmm32at_reset()` only succeeds when hardware readback indicates all A/D channels are configured single-ended, so jumper settings can block attach. Other risks are page-register races, unsupported external AI triggers despite flags in hardware, coarse conversion timing buckets, and FIFO/status handling. Test supported base addresses, reset probe under jumper variants, AI single and command scans, AO busy timeout/update, 8255 port directions through the callback, and interrupt reset behavior.
