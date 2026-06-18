# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-scs1x.c

## Purpose

This file implements Stanton SCS.1x custom MIDI transport over unique HSS1394 asynchronous FireWire transactions, instead of standard AM824 MIDI channels.

## Important APIs, types, and functions

`struct fw_scs1x` stores address-handler state, input/output RawMIDI substreams, output transaction state, escaping state, and workqueue data. `snd_oxfw_scs1x_add()` registers the async handler, announces its address to the device, and creates a RawMIDI device. `handle_hss()` receives device writes. `scs_output_work()` packetizes RawMIDI bytes into device-specific HSS packets and sends block-write requests.

## Control flow

Incoming packets are converted either directly from user-data packets or escaped into vendor SysEx sequences. Outgoing data is pulled from RawMIDI, normalizes running status into full commands, handles escaped SysEx payloads, sends one FireWire block transaction at a time, and reschedules work from the transaction callback. Playback drain waits until `output_idle`.

## State and persistence behavior

The driver persists the local handler address in the device via a change-address packet. Output state includes current MIDI status, pending transaction bytes, error flag, and idle wait state. Bus reset calls `snd_oxfw_scs1x_update()` to re-register the address.

## Dependencies and integration points

It is enabled by OXFW quirks in `oxfw.c` and stores private state in `oxfw->spec`. It uses FireWire address handlers, raw transactions, workqueues, wait queues, and ALSA RawMIDI.

## Risks and test signals

Risks include MIDI parser edge cases, transaction error recovery, address stale after bus reset, and waiting forever in drain if idle is not signaled. Tests should cover SysEx escape round trips, running status, invalid real-time statuses, bus reset, permanent transaction errors, and capture/playback trigger toggles.
