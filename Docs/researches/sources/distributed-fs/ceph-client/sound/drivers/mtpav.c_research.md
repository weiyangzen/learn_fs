# sources/distributed-fs/ceph-client/sound/drivers/mtpav.c

## Purpose
Implements the ALSA raw-MIDI driver for the MOTU MidiTimePiece AV on a legacy PC parallel port. The driver exposes hardware, remote, computer, ADAT, and broadcast MIDI substreams while translating ALSA rawmidi traffic into the MTPAV parallel-port byte protocol.

## Important APIs, Types, And Functions
`struct mtpav` owns the ALSA card, I/O resource, IRQ, rawmidi device, timer, spinlock, selected input/output port state, and `struct mtpav_port` array. `translate_subdevice_to_hwport()` and `translate_hwport_to_subdevice()` map ALSA substream numbers to MTP hardware port selectors. `snd_mtpav_getreg()`, `snd_mtpav_mputreg()`, `snd_mtpav_wait_rfdhi()`, and `snd_mtpav_send_byte()` are the low-level parallel register helpers. Rawmidi callbacks are provided through `snd_mtpav_input` and `snd_mtpav_output`.

## Control Flow
Module init registers a platform driver and synthetic platform device. Probe creates a managed ALSA card, initializes locks and timers, creates rawmidi substreams, requests the fixed I/O region and IRQ, scans ports into smart routing mode, then registers the card. Output trigger writes immediately and uses `timer_list` polling to continue draining rawmidi output buffers. Input open enables parallel-port interrupts; the IRQ handler reads nibble-encoded bytes, recognizes `0xf5` port-change messages, and delivers data to the currently selected rawmidi input substream.

## State And Persistence
State is runtime-only: open/trigger bits per port, running status per output port, IRQ/timer reference counts, current MTP input/output selectors, and ALSA rawmidi buffers. Module parameters persist only as load-time configuration (`index`, `id`, `port`, `irq`, `hwports`).

## Dependencies And Integration
Depends on ISA-style I/O (`inb`/`outb`), Linux timers/IRQs, platform devices, and ALSA core/rawmidi. It integrates with user space through ALSA rawmidi subdevices and card naming.

## Risks And Test Signals
The driver touches legacy hardware directly and has busy-wait loops without hard failure reporting if the device is absent or slow. The output trigger path appears suspicious because it increments the timer reference only when `MTPAV_MODE_OUTPUT_TRIGGERED` is already set, which can prevent timer startup on the first trigger. Useful tests are hardware probe/load, rawmidi substream enumeration, interrupt-driven input, multi-port output routing, close/unload timer cleanup, and invalid `hwports` clamping.
