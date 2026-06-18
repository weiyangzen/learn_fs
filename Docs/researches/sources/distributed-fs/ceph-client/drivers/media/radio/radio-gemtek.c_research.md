# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-gemtek.c

Purpose: ISA/optional PnP V4L2 driver for GemTek radio cards and compatibles, using the shared `radio-isa` framework but implementing its own BU2614/BU2614FS serial protocol.

Important types/APIs: `struct gemtek` extends `radio_isa_card` with muted state and cached 32-bit BU2614 data word. It implements callbacks for allocation, optional I/O probing, mute/volume, frequency, and rxsubchans. Module parameters control automatic probing, `hardmute`, fixed I/O ports, and radio node numbers. Valid ports include `0x20c`, `0x30c`, `0x24c`, `0x34c`, `0x248`, and `0x28c`.

Control flow: probe may automatically test candidate ports by toggling CE/CK/DA and checking echoed bus bits. Frequency calculation adds IF offset and reference divisor scaling, fills BU2614 fields, and serializes 32 bits over I/O pins. Mute either toggles line mute or, with `hardmute`, shuts down the PLL and skips retuning while muted. Module exit sets `hardmute = true` before unregistering to force PLL off.

State and persistence: cached BU2614 data and mute state are runtime memory; `radio-isa` stores current frequency. Hardware PLL/mute state persists until changed or module exit.

Dependencies and integration: ISA I/O, optional PnP ID `ADS7183`, `radio-isa`, V4L2 controls. Risks include reverse-engineered timing/probing, hardmute changing frequency behavior, and stereo status inferred from the no-signal bit. Test signals include port autodetection, hardmute on/off retuning, PnP registration, unload PLL-off behavior, and V4L2 tuner/mute compliance.
