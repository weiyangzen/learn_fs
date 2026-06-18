# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo_express_dsp.c

## Purpose

`indigo_express_dsp.c` is the shared DSP helper for Indigo Express-derived DJx and IOx cards. It supplies sample-rate programming, vmixer operations, internal clock detection, and no-ASIC behavior, while the small DJx/IOx files supply hardware identity.

## Important APIs, Types, and Functions

`set_sample_rate()` maps 32, 44.1, 48, 64, 88.2, and 96 kHz to `INDIGO_EXPRESS_*` control-register bits, including double-speed encodings. `set_vmixer_gain()` and `update_vmixer_level()` mirror the original Indigo vmixer table update path. `detect_input_clocks()` returns internal only, and `load_asic()` is a no-op.

## Control Flow

DJx/IOx initialization includes this file after defining the card-specific `init_hw()`. Rate changes wait for DSP handshake, mask out `INDIGO_EXPRESS_CLOCK_MASK`, update `comm_page->control_register` when needed, and send `DSP_VC_UPDATE_CLOCKS`. Vmixer changes update one matrix cell and send `DSP_VC_SET_VMIXER_GAIN`.

## State and Persistence Behavior

Persistent state is limited to `sample_rate`, the comm-page control register, and vmixer gain arrays. No external clock or ASIC state is maintained.

## Dependencies and Integration Points

It depends on shared DSP helpers and Indigo Express constants in `echoaudio_dsp.h`. It is included by `indigodjx.c` and `indigoiox.c` after their card-specific DSP identity files.

## Risks and Test Signals

Risks are incorrect double-speed masking, omitting 64 kHz support, and vmixer indexing mistakes. Test signals are successful rate switching including 64/88.2/96 kHz, internal-only clock controls, and working vmixer routing on both DJx and IOx modules.
