<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-types.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-types.h

Purpose: firmware-facing packed structures and enums for SAA7164 descriptors, command metadata, DMA stream buffers, encoder/audio/tuner/VBI controls, and firmware debug/load-info messages.

Important APIs, types, and functions: key types include `tmComResHWDescr`, `tmComResInterfaceDescr`, `tmComResBusDescr`, `tmComResBusInfo`, `tmComResInfo`, `cmd`, `tmBuffer`, `tmHWStreamParameters`, `tmComResDMATermDescrHeader`, `tmComResTSFormatDescrHeader`, encoder/audio descriptor headers, bitrate/GOP/aspect structures, `tmComResVBIFormatDescrHeader`, and `tmFwInfoStruct`.

Control flow: these layouts are copied from MMIO descriptor space or serialized into command-bus payloads by API/cmd/bus code. Buffer/stream parameter structs are populated by DVB, encoder, and VBI registration/start paths and consumed by buffer configuration.

State and persistence: some structs are transient command payloads; others are cached in `saa7164_dev` or `saa7164_port`. No persistent storage. Packed layout is part of the firmware ABI.

Dependencies and integration points: SAA7164 API, bus, command, core descriptor extraction, DMA buffer setup, V4L2 controls, and DVB/encoder/VBI paths.

Risks: comments call out alignment uncertainty for `tmComResInterfaceDescr`; firmware structures depend on compiler packing and manual padding. Pointer-containing DMA structs mix CPU virtual and physical addresses, so misuse can corrupt DMA configuration. ABI regressions are difficult to catch without hardware.

Test signals: descriptor `bLength` checks, command-bus requests/responses with expected sizes, successful DMA buffer configuration, encoder control application, VBI format negotiation, and no mangled-structure logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-types.h -->
