# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoio_dsp.c

## Purpose

`indigoio_dsp.c` implements DSP initialization, fixed clocking, sample-rate programming, and vmixer handling for Indigo IO.

## Important APIs, Types, and Functions

`init_hw()` validates `INDIGO_IO`, sets `FW_INDIGO_IO_DSP`, marks no ASIC, enables internal clock only, and loads firmware. `set_mixer_defaults()` restores default levels. `detect_input_clocks()` reports internal only. `load_asic()` is a no-op. `set_sample_rate()` programs the same MIA-style fixed clock encodings as the original Indigo. `set_vmixer_gain()` and `update_vmixer_level()` manage virtual mixer cells.

## Control Flow

After probe and firmware load, common code initializes line, monitor, and vmixer levels. Rate changes wait for a DSP handshake before changing `control_register`, then send `DSP_VC_UPDATE_CLOCKS`.

## State and Persistence Behavior

State includes sample rate, control-register value, vmixer gains, monitor gains from common code, and internal-only clock capabilities. No ASIC or external clock state exists.

## Dependencies and Integration Points

It depends on shared Echoaudio DSP helpers and is selected by the `indigoio.c` wrapper. ALSA monitor and vmixer controls exercise its comm-page writes.

## Risks and Test Signals

Risks are assuming external clock support on a card that reports internal only, and incorrect vmixer dimensions with analog input present. Test stereo capture/playback, monitor loopback, vmixer persistence, and all supported rates.
