<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii.h

## Purpose
Private header for the US-144MKII driver, defining device protocol constants, endpoint layout, audio/MIDI buffer sizing, shared driver state, and cross-file function declarations.

## APIs, Types, and Functions
Defines USB IDs, endpoint numbers, request types, vendor requests, register selectors, URB counts, audio frame constants, MIDI buffer sizes, and capture decode geometry. Key types are `struct us144mkii_frame_pattern_observer` and `struct tascam_card`. It declares allocation, stop-work, MIDI, PCM, and control creation entry points.

## Control Flow, State, and Persistence
The header has no executable flow, but it is the authoritative schema for state shared by probe, PCM callbacks, URB completions, workqueue handlers, mixer controls, and MIDI callbacks. Persistent fields include USB/ALSA handles, URB arrays and anchors, atomic active flags, current sample rate, playback/capture counters, MIDI FIFO/in-flight bitmap, feedback pattern ring, and routing choices.

## Dependencies and Integration
Includes Linux USB, workqueue, timer, kfifo and ALSA core/control/PCM/rawmidi headers. It includes `us144mkii_pcm.h`, making the PCM declarations part of the common include boundary used by all US-144MKII source files.

## Risks and Test Signals
Risks include circular include fragility, stale comments versus actual callback behavior, buffer-size constants that must match device protocol, and unsynchronized access expectations around fields protected by `lock`, `midi_in_lock`, or `midi_out_lock`. Build coverage, sparse/lockdep, and end-to-end stream tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii.h -->
