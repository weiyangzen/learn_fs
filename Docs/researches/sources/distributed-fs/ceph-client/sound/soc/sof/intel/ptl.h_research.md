<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.h

## Purpose
Small Panther Lake internal header for mic privacy capability bit definitions and the PTL ops setup entry point.

## Important APIs, Types, and Functions
Defines `PTL_MICPVCP_DDZE_FORCED`, `PTL_MICPVCP_DDZE_ENABLED`, `PTL_MICPVCP_DDZLS_SDW`, and `PTL_MICPVCP_GET_SDW_MASK(x)`. Declares `sof_ptl_set_ops(struct snd_sof_dev *sdev, struct snd_sof_dsp_ops *dsp_ops)`.

## Control Flow, State, and Persistence
The header has no state or runtime control flow. Its macros encode the firmware capability word interpretation used by `ptl.c`: whether DDZE is enabled, forced, and which SoundWire link mask should be programmed.

## Dependencies and Integration
Relies on generic kernel bit macros such as `BIT()` and `GENMASK()` from included translation units. It is included by PTL platform setup code and is part of the internal Intel SOF HDA integration boundary.

## Risks and Test Signals
The main risk is bitfield drift with firmware/HDA capability definitions; a wrong shift or mask would program the wrong SoundWire links for mic privacy. Build coverage of `ptl.c` and runtime capability dumps or privacy IRQ tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.h -->
