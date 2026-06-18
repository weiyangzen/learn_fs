<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.c

Purpose: Implements the cx18 internal A/V decoder V4L2 subdevice: register access helpers, firmware/initialization, video standard setup, input routing, tuner/audio status, video controls, scaling, stream enable, log-status, debug register access, and subdevice registration.

Important APIs/functions: Register helpers `cx18_av_read/write`, `write_expect`, 32-bit variants, and `and_or` operate on the CXADEC register window. `cx18_av_initialize()` loads firmware, stops the 8051, initializes PLLs/DLLs/AFE/output/VBI/default controls, and sets up default volume. `cx18_av_std_setup()` computes timing, blanking, filters, burst gate, chroma subcarrier, and VBI line offsets for 525/625-line and PAL/NTSC/SECAM variants. `set_input()` validates composite/S-video/component/audio input encodings, configures AFE mux/ADC/AFE registers, updates state, calls audio path setup, and restarts detection. V4L2 ops cover firmware load/reset, tuner get/set, standard/radio/frequency, audio/video routing, stream enable, pad format scaling, VBI operations, controls, and log-status. `cx18_av_probe()` initializes `cx18_av_state`, controls, subdev ops, and registers the subdevice.

Control flow: Probe initializes defaults and registers the subdevice, then does base PLL init. First `load_fw` or reset performs full firmware and decoder initialization. Standard or frequency changes recompute video timing and restart audio/video detection. Routing changes run through `set_input()`, which programs muxes and audio path together. Format set validates requested scaling against source active size and writes horizontal/vertical scaler registers. Stream enable toggles output registers.

State/persistence: `cx18_av_state` stores revision, selected video/audio input, audio clock, audio mode, radio flag, standard, VBI slicer offsets, initialization flag, controls, and subdevice object. Hardware registers persist while the decoder is configured.

Dependencies/integration: Depends on cx18 core IO helpers, card input enums/tables, firmware loader (`cx18_av_loadfw`), VBI helpers, audio helper ops from `cx18-av-audio.c`, and V4L2 subdev/control frameworks.

Risks: Large amounts of analog-video timing and register programming are magic-number based and standard-specific. Input encodings are bit-packed; invalid combinations must be rejected to avoid bad AFE programming. `cx18_av_set_fmt()` has strict scaling limits and returns `-ERANGE`. Initialization sequencing around firmware, sleep, DLLs, and AFE reset is hardware-sensitive. Control default volume clamps hardware values to avoid V4L2 range errors.

Test signals: Subdevice probe, firmware load once, reset, standard switching across NTSC/PAL/SECAM variants, composite/S-video/component/audio routing, tuner audio mode detection, V4L2 controls, scaling limits, stream enable/disable, VBI format ops, log-status output, and advanced debug register access when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.c -->
