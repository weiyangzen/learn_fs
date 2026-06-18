# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe-fmts.h

Purpose: central format table for RP1 CFE CSI-2 capture and PiSP FE output negotiation.

Important APIs/types/functions: `formats[]` maps V4L2 FourCC to media bus code, bit depth, CSI-2 data type, optional remap FourCCs, and flags (`META_OUT`, `META_CAP`, `FE_OUT`). Entries cover YUV, RGB, Bayer packed RAW8/10/12/14, 16-bit Bayer/mono, PiSP compressed outputs, greyscale, generic CSI-2 metadata, and FE config/stats metadata.

Control flow: no functions; lookup helpers in `cfe.c` iterate this table for ioctl validation, CSI-2 data type selection, source-pad remap/compressed code checks, and FE format filtering.

State and persistence: immutable compile-time data.

Dependencies and integration: depends on `cfe.h`, V4L2 pixel/meta formats, media bus formats, and `media/mipi-csi2.h` data type constants.

Risks: incorrect `csi_dt` will make CSI-2 channel filtering capture the wrong packets. Incorrect `remap` entries break 16-bit unpacked or PiSP compressed output modes. FE output flags restrict which formats can traverse the PiSP FE path.

Test signals: enumerate video and metadata formats on CSI2/FE nodes, route sink formats to source pads with normal/remap/compressed codes, validate FE outputs only expose `FE_OUT` formats, and capture RAW metadata data types.
