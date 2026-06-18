# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-input.c

Purpose: implements the DCMIPP input bridge subdevice. It accepts an external parallel, BT.656, or CSI-2 source on its sink pad, maps incoming mbus codes to DCMIPP internal formats on its source pad, programs input interface registers, and forwards stream enable/disable to the upstream source.

Important APIs and functions: format lookup helpers are `dcmipp_inp_pix_map_by_index` and `dcmipp_inp_pix_map_by_code`. Subdevice operations include init state, enum mbus code, enum frame size, set/get format, enable/disable streams, and s_stream helper integration. Hardware paths are `dcmipp_inp_configure_parallel` and `dcmipp_inp_configure_csi`. Entity lifecycle is `dcmipp_inp_ent_init`, internal release, and `dcmipp_inp_ent_release`.

Control flow: init registers a two-pad video-interface bridge subdevice. Format setting clamps dimensions and colorimetry, rejects unsupported mbus codes, excludes JPEG on BT.656, and when the sink format changes mirrors an adjusted source format. Stream enable locates the upstream subdev linked to the sink pad, configures parallel/BT.656 bus polarity, embedded sync, PRCR format and byte swap, or configures CSI data-type filtering through P0FSCR and CMCR, then enables the upstream stream. Disable stops the upstream stream and disables the parallel interface when applicable.

State and persistence: state is V4L2 subdev pad format state plus bus flags/type stored by the core in `dcmipp_ent_device`. Hardware register state is programmed only for active streams. There is no persistent storage.

Dependencies and integration points: depends on DCMIPP common helpers/register macros, media/V4L2 subdev APIs, MIPI CSI-2 data type constants, and endpoint bus settings parsed by `dcmipp-core.c`. It feeds byteproc through an immutable internal link.

Risks and test signals: risks include many mbus mapping aliases, sink/source code pair validation, JPEG/all-data CSI behavior, BT.656 exclusion rules, byte swap configuration for 2x8 formats, no local IRQ handling, and disabling only the parallel interface while CSI input selection remains register state. Test with all supported mbus codes, parallel polarity variants, BT.656 sync, CSI RAW/YUV/RGB/JPEG data-type filtering, media-ctl format propagation, stream enable failure unwinding, and upstream subdev missing/unbound cases.
