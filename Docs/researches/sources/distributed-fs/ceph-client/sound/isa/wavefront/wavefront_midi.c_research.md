# sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_midi.c

## Purpose
This file implements the low-level MIDI support for the WaveFront ICS2115 interface. It provides rawmidi callbacks for separate internal and external MIDI buses and supports Turtle Beach "Virtual MIDI" mode, where switch bytes route traffic between the synth bus and external MIDI bus.

## Important APIs, Types, and Functions
Public symbols are the rawmidi ops `snd_wavefront_midi_output` and `snd_wavefront_midi_input`, plus `snd_wavefront_midi_interrupt()`, `snd_wavefront_midi_enable_virtual()`, `snd_wavefront_midi_disable_virtual()`, and `snd_wavefront_midi_start()`. Helpers wrap MPU status/data ports: `wf_mpu_status()`, `input_avail()`, `output_ready()`, `read_data()`, `write_data()`, and `get_wavefront_midi()`. Output scheduling uses `snd_wavefront_midi_output_write()` and a timer callback.

## Control Flow
Rawmidi open records input or output substreams by `internal_mpu` or `external_mpu` ID stored in `rmidi->private_data`. Trigger callbacks toggle mode bits under the MIDI virtual lock. Output trigger starts a one-jiffy timer if needed and immediately drains bytes. The drain function first flushes the currently selected output bus, then optionally sends `WF_INTERNAL_SWITCH` or `WF_EXTERNAL_SWITCH` before writing data for the other bus. It filters switch bytes from user data while in virtual mode so users cannot accidentally alter routing.

The interrupt handler checks for incoming data. If no input is pending it treats the interrupt as an opportunity to write output. When bytes arrive, virtual mode switch bytes update the selected input substream; normal bytes are delivered through `snd_rawmidi_receive()` only when that bus has input trigger enabled. It then attempts output write again.

`snd_wavefront_midi_start()` waits for the ICS2115 MPU to be ready, marks future ICS2115 interrupts as MIDI-owned, sends UART mode command, waits for MPU ACK, enables external MIDI-to-synth routing, forces virtual MIDI off then on to resynchronize switch bytes, and updates software virtual-mode state.

## State and Persistence
State lives in `snd_wavefront_midi_t`: base ports, command/status/data ports, input and output substream arrays, mode bits, `output_mpu`, `input_mpu`, virtual-mode flag, timer count, timer object, timer card, and locks. No persistent storage exists.

## Dependencies and Integration Points
This file depends on ALSA rawmidi, WaveFront synth command helpers (`snd_wavefront_cmd()`), ICS2115 interrupt routing in `wavefront.c`, and constants from `sound/snd_wavefront.h`.

## Risks and Edge Cases
Several comments identify hard timing loops that should not exist in modern kernel code. The interrupt handler has static `substream` and `mpu` variables, which are shared across all cards and can be wrong for multi-card systems. In virtual input mode, the `WF_INTERNAL_SWITCH` case assigns `substream_output[internal_mpu]` instead of the input substream, which looks like a potential routing bug. Timer lifetime depends on `istimer` reference counting and close/trigger interactions.

## Test Signals
Verify UART mode ACK during MIDI start, internal and external rawmidi devices open independently, virtual mode emits and consumes switch bytes correctly, user-supplied switch bytes are filtered in virtual output mode, incoming bytes route to the triggered input substream, output timer drains queued bytes, and MIDI interrupt routing remains stable under simultaneous internal/external traffic.
