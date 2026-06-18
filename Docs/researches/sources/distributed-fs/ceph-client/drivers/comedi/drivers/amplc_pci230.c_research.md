# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci230.c

## Purpose
This Comedi PCI driver supports Amplicon PCI230/PCI230+ and PCI260/PCI260+ multifunction boards. It provides AI streaming and instruction reads, optional AO streaming and writes on PCI230-class boards, optional 8255 DIO on PCI230-class boards, 82C54 timer-based pacing, external trigger routing, and hardware-version-specific workarounds for original and plus boards.

## Important APIs, Types, and Functions
`struct pci230_board` captures PCI ID, AI/AO resolution, minimum plus-board hardware version, and DIO presence. `struct pci230_private` stores spinlocks for ISR/resource/AI/AO stop paths, BAR3 DAQ base, hardware version, ADC/DAC control shadows, ADC gain and FIFO threshold shadows, interrupt-enable shadow, resource ownership, and AI/AO running flags. Central functions include `pci230_ai_insn_read()`, `pci230_ao_insn_write()`, `pci230_ai_cmdtest()`, `pci230_ai_cmd()`, `pci230_ai_start()`, `pci230_handle_ai()`, `pci230_ai_stop()`, `pci230_ao_cmdtest()`, `pci230_ao_cmd()`, `pci230_ao_start()`, `pci230_handle_ao_nofifo()`, `pci230_handle_ao_fifo()`, `pci230_ao_stop()`, `pci230_interrupt()`, and `pci230_auto_attach()`.

## Control Flow
Attach detects plus models by PCI region size and hardware version, enables PCI, stores BAR2/BAR3, configures extended functions for PCI260+ external gates and PCI230+ v2 DAC FIFO, resets ADC/DAC FIFOs, requests IRQ, allocates an 82C54 pacer, and creates AI, AO, and DIO subdevices according to board capabilities. AI instruction reads program one channel, gain, unipolar/bipolar and single-ended/differential mode, then use counter Z2-CT2 rather than the built-in software trigger to avoid differential-trigger bugs.

AI command validation enforces trigger compatibility, scan/convert timing limits, all-same reference and polarity, valid repeated ascending channel subsequences, pairwise range restrictions for single-ended channels, and the PCI230+/260+ hardware-version bug requiring multi-channel sequences to start at channel 0. `pci230_ai_cmd()` claims needed counters, programs channel enables/gains, resets FIFO twice with a settling delay, sets CT2 as an initially high conversion source, optionally configures CT0/CT1/CT2 for scans and conversions, and starts immediately or via `inttrig`. `pci230_ai_start()` enables ADC interrupts, switches to the real conversion source, updates FIFO interrupt threshold, and opens timer gates or installs software trigger callbacks. `pci230_handle_ai()` drains FIFO data into the Comedi buffer, detects FIFO overrun, updates trigger level, and raises EOA.

AO supports direct no-FIFO writes and command output. Older boards use CT1 interrupts and immediate DAC writes; hardware version 2+ uses the DAC FIFO. `pci230_ao_cmd()` claims CT1 for timer pacing, programs range and FIFO/channel enable state, gates CT1 until start, and installs an internal start trigger. `pci230_ao_start()` preloads FIFO when available, selects timer/external/software scan trigger, gates timers, and enables the relevant interrupt source. `pci230_interrupt()` masks active sources, dispatches CT1, DAC FIFO, and ADC handlers, reenables the shadow mask, then calls Comedi event handling.

## State and Persistence Behavior
State is held in private shadows for ADC/DAC control, interrupt enables, gains, FIFO threshold, resource owner masks, and running flags. Shared 82C54 counters are protected by `res_spinlock` so AI and AO commands do not simultaneously use the same timer. Hardware register state persists across commands until cancel/reset paths restore FIFOs, trigger sources, timers, and interrupt enables. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on Comedi PCI, Comedi async buffers/events, `comedi_8254`, `comedi_8255`, Linux IRQs, and port I/O. It integrates with the PCI bus through Amplicon IDs 0x0000 and 0x0006, and with Comedi through AI read, AI command, AO write, AO command, DIO 8255, and read/write subdevice registration.

## Risks
The command matrix is complex, and bugs can appear in timer resource ownership, trigger-source combinations, or hardware-version detection. The code has several hardware workarounds: double ADC FIFO reset, settling delay, CT2 software trigger substitution, plus-board channel-0 sequence requirement, and optional v2 DAC FIFO support. Interrupt stop paths spin until another CPU's ISR exits. Some capabilities depend on detected `hwver`, making behavior differ across cards with identical PCI IDs. Buffer underruns/overruns are surfaced as Comedi errors but can also leave hardware FIFOs needing reset.

## Test Signals
Test PCI230, PCI230+, PCI260, and PCI260+ detection; AI insn reads in single-ended and differential modes; AI commands for timer, external, internal, finite, and continuous cases; channel-list rejection cases; simultaneous AI/AO resource conflicts; AO commands on old no-FIFO and v2 FIFO hardware; cancellation from process and interrupt context; 8255 DIO availability only on PCI230-class boards; and error paths for FIFO overrun/underrun and unavailable IRQ.
