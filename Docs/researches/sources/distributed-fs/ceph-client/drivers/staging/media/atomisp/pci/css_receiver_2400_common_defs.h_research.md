# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_receiver_2400_common_defs.h

Purpose: provides legacy/common CSS receiver 2400 MIPI data-format, format-type, repeat-pattern, compression, packet, and custom-decoding definitions.

Important APIs/types/functions: macros define short packet field widths, MIPI data IDs for YUV/RGB/RAW/user-defined/embedded and frame/line events, format type IDs, repeat patterns, compression modes, RAW16/RAW18 configuration fields, packet header/payload bit positions, and custom decoder fields.

Control flow: no executable flow. Receiver and backend code use these constants for packet decoding and register packing.

State and persistence: constants only; hardware state is controlled elsewhere.

Dependencies and integration: this header uses the same guard name as `mipi_backend_common_defs.h` and contains nearly overlapping definitions, which can affect include ordering. It represents the CSS receiver 2400 side of MIPI packet interpretation.

Risks and test signals: duplicate guard/definition overlap is a significant integration risk if both headers are included in one translation unit. Some format comments appear inconsistent with macro values. Tests should verify include-order builds, sensor format mapping, packet decode fields, and custom decoder register packing.
