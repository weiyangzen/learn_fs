# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoiox_dsp.c

## Purpose

`indigoiox_dsp.c` supplies the Indigo IOx identity and initialization layer used with the shared Indigo Express DSP implementation.

## Important APIs, Types, and Functions

`init_hw()` validates the IOx subdevice, initializes the comm page, stores IDs, sets `FW_INDIGO_IOX_DSP`, marks the no-ASIC card as loaded, enables internal clock only, and loads firmware. `set_mixer_defaults()` initializes line levels. Vmixer function prototypes are resolved by `indigo_express_dsp.c`.

## Control Flow

Probe calls this `init_hw()` before common setup. Once firmware is loaded, common restore calls into the Express helper for sample-rate and vmixer operations.

## State and Persistence Behavior

It initializes the durable card identity, firmware selection, `bad_board`, `asic_loaded`, and clock capability fields. Mixer, monitor, and sample-rate values are held by common Echoaudio state.

## Dependencies and Integration Points

It depends on `echoaudio_dsp.c` for comm-page and firmware loading and on `indigo_express_dsp.c` for operational DSP controls.

## Risks and Test Signals

Risks are wrong firmware index or subdevice mask. Test with IOx PCI ID probe, clean firmware load, internal-only clock detection, stereo capture, and Express-rate playback.
