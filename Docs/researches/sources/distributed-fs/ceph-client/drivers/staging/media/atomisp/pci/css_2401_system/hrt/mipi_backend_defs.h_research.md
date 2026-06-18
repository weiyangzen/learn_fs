# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/mipi_backend_defs.h

Purpose: defines the MIPI backend register map, register widths, streaming bus field macros, LUT field macros, and custom decoder bit layout for CSS 2401.

Important APIs/types/functions: macros enumerate enable/status/compression/raw/IRQ/custom/LUT/stall register indices, register widths, SP/LP LUT entry counts, channel/format widths, streaming pixel/value/SOP/EOP bit positions parameterized by SID width, PPC, and pixel width, and LUT packet-disregard/SID/channel/format bit fields.

Control flow: no executable flow. Host code uses these indices and bit positions for MIPI backend programming and state capture.

State and persistence: none in software; register writes by consumers persist in hardware.

Dependencies and integration: includes `mipi_backend_common_defs.h` and is consumed by CSI RX private backend helpers and stream2mmio definitions.

Risks and test signals: several macros lack parentheses around additive expressions, which can surprise composed expressions. Custom decoder comments show changed bit positions versus older definitions. Tests should validate packed LUT values, streaming bus widths for each backend SID width, and raw/custom mode register programming.
