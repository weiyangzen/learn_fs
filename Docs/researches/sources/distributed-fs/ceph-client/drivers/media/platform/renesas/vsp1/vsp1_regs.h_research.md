# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_regs.h

Purpose: provides the VI6/VSP1 register address and bitfield macro contract used by the Renesas VSP1 driver. It is a pure header with no runtime state; correctness is determined by matching the hardware register map.

Important definitions: general control macros cover `VI6_CMD`, reset/status, WPF interrupts, display interrupts, and line counters. Display-list control definitions cover DL enable, headers, swap, extended command control, AUTOFLD interrupt flags, and body sizes. RPF macros describe source size, input format, byte swaps, location, alpha, masks/color-keying, strides, DMA addresses, multiplier alpha, Gen4 extended input formats, and dithering. WPF macros describe source selection, clipping, output format, rotation, destination stride/address, and writeback. UIF, DPR routing, SRU, UDS, LUT/CLU/HST/HSI, BRU/BRS blending, HGO/HGT statistics, LIF, security, version, CLUT/LUT/CLU tables, and hardware format IDs are also covered.

Control flow/state: there is no control flow, but macro composition drives all display-list bodies and direct MMIO writes in sibling files. Offset macros such as `VI6_RPF_OFFSET`, `VI6_WPF_OFFSET`, `VI6_UIF_OFFSET`, and `VI6_UDS_OFFSET` are used to address indexed hardware instances.

Dependencies/integration: consumed by `vsp1_pipe.c` format tables, RPF/WPF/UDS/SRU/UIF programming, display-list management, route setup, and interrupt/status handling. It relies on kernel `BIT()` and standard integer arithmetic in callers.

Risks and test signals: bitfield shifts and masks are high blast-radius: a single bad value can corrupt image layout, routes, interrupts, DMA addresses, or CSC. Particular risk areas are Gen4 extended RPF formats, WPF writeback, indexed offsets, and DPR node IDs. Test signals include register trace comparison against known-good kernels, streaming across every supported block, color/plane swap validation, and hardware version detection on Gen2/Gen3/Gen4/RZ-G2L variants.
