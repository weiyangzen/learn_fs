# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodjx_dsp.c

## Purpose

`indigodjx_dsp.c` supplies the Indigo DJx card identity and hardware initialization used with the shared Indigo Express DSP helper.

## Important APIs, Types, and Functions

`init_hw()` validates the DJx subdevice, initializes the comm page, records `device_id` and `subdevice_id`, sets `FW_INDIGO_DJX_DSP`, marks the no-ASIC hardware as loaded, enables internal-only clocking, and loads firmware. `set_mixer_defaults()` delegates to `init_line_levels()`. The file forward-declares vmixer helpers that are implemented by `indigo_express_dsp.c`.

## Control Flow

Probe enters `init_hw()`, which performs the comm-page reset and firmware load before common Echoaudio setup continues. Subsequent rate and vmixer operations are resolved to the shared Express helper included after this file.

## State and Persistence Behavior

It initializes durable fields in `struct echoaudio`: device/subdevice IDs, `bad_board`, `dsp_code_to_load`, `asic_loaded`, and internal clock capabilities. Mixer and rate state are restored by the shared code.

## Dependencies and Integration Points

It depends on `init_dsp_comm_page()` and `load_firmware()` from `echoaudio_dsp.c`, plus `indigo_express_dsp.c` for sample-rate and vmixer implementations.

## Risks and Test Signals

Risks are wrong subdevice validation or firmware index, which would fail probe or load the wrong DSP image. Test with DJx PCI ID probe, clean firmware load, internal-clock-only controls, and Express-rate playback.
