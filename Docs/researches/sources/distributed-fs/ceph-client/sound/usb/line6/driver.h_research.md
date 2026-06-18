# sources/distributed-fs/ceph-client/sound/usb/line6/driver.h

## Purpose
Defines the shared Line 6 driver data model, constants, capability bits, and exported core APIs.

## Important Types and APIs
`struct line6_properties` describes device identity, capabilities, altsetting, control endpoints, and audio endpoints. Capability bits distinguish control, PCM, hardware monitoring, capture requiring output, MIDI-over-control, low-level info, and monitoring controls. `struct usb_line6` is the shared per-card state: USB device, properties, packet timing, ALSA card, PCM/MIDI objects, listen URB/buffers, message FIFO, startup work, and callback hooks. The header declares raw message, sysex, read/write, serial number, probe/disconnect, and PM APIs.

## State and Integration
Device-specific modules embed `struct usb_line6` as the leading portion of larger private structs by passing a `data_size` to `line6_probe()`. PCM and MIDI modules hang their state off `line6pcm` and `line6midi`. The FIFO and delayed work provide optional control/event plumbing.

## Risks and Test Signals
Risks include capability combinations that require matching endpoints and initialized submodules, size/layout assumptions for embedding, and fallback packet properties hiding endpoint descriptor bugs. Tests should instantiate each device-specific property set and verify probe, control, PCM, and MIDI combinations.
