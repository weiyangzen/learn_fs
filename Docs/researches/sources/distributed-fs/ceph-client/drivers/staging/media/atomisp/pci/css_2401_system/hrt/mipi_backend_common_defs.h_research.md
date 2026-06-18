# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/mipi_backend_common_defs.h

Purpose: defines common MIPI/CSS receiver data-format IDs, format type mappings, repeat patterns, packet bit fields, compression fields, and custom decoding bit layout used by the MIPI backend.

Important APIs/types/functions: macros map MIPI data IDs for YUV/RGB/RAW/user-defined/short packets, CSS receiver format type IDs, repeat-pattern lengths, compression schemes, RAW16/RAW18 fields, packet SOP/channel/format/payload fields, and custom decoder state/pixel extractor/valid-EOP fields. It also defines `_HRT_MIPI_BACKEND_FMT_TYPE_CUSTOM`.

Control flow: no direct logic. These macros are consumed by backend LUT/configuration code and generated register packing.

State and persistence: no software state; constants describe packet and register bit layout.

Dependencies and integration: shared by `mipi_backend_defs.h` and legacy/common receiver code. Comments note the definitions must stay aligned with hardware design files.

Risks and test signals: many constants are hardware ABI and comments show historical design-time variants. Tests should verify data-type mapping for all supported sensor formats, compression configuration, packet header extraction, and custom decoder setup.
