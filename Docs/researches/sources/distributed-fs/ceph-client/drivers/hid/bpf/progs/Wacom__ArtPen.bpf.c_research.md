# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Wacom__ArtPen.bpf.c

## Purpose
This event quirk smooths pressure reports for the Wacom Art Pen on supported Wacom tablets. The stylus reports pressure in chunky every-other-event steps; the program interpolates odd frames by averaging current and previous pressure while delaying pressure by one event.

## Important APIs, Types, And Functions
The match is Wacom Intuos Pro 2 M PID `0x0357`, but the file is structured to support more devices through `struct wacom_params devices[]`. `wacom_params` records product ID, descriptor length, report ID, report length, and byte offsets for tip switch, pressure, and tool type. `probe()` uses `hid_bpf_allocate_context()` to inspect the actual product ID and copies matching parameters into global `params`. `artpen_pressure_interpolate()` mutates reports. Helper accessors `get_u16()` and `get_u8()` cast byte offsets.

## Control Flow
Probe rejects unsupported product/descriptor pairs and initializes `params` for matching devices. The event hook reads a 64-byte report chunk, validates report ID and offset bounds, checks tool type `0x0804` for Art Pen, and ignores other tools. If tip is up, it resets `prev_pressure` to 0 and starts the next contact on an odd frame. If tip is down and `odd` is true, it replaces pressure with the average of current pressure and `prev_pressure`; then it stores pressure and toggles `odd`.

## State And Persistence
`params` stores per-device offsets selected at probe time. `odd` tracks alternating frames, and `prev_pressure` stores the previous pressure sample. These are BPF globals, persistent while loaded.

## Dependencies And Integration Points
The program depends on HID-BPF event mutation and Wacom report layouts. It integrates after report receipt and before input delivery, leaving descriptor parsing unchanged. It depends on tool type bytes being present and little-endian-compatible with direct `__u16 *` access.

## Risks
The direct offset casts assume alignment and endianness as used by BPF/HID report data. The smoothing intentionally changes latency and may not suit all users. Only listed device descriptors are supported, so additional Wacom tablets using the Art Pen need new `devices[]` entries.

## Test Signals
Tests should use report ID 16, tool type `0x0804`, pressure offset 8, and tip offset 1 for descriptor length 949. A sample sequence 0,100,100,200,200 should become approximately 0,50,100,150,200 while non-ArtPen tool types and tip-up reports are unchanged.
