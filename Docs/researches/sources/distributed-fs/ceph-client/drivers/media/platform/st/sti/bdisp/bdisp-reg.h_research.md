# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-reg.h

Purpose: defines the hardware-facing BDisp descriptor layout, MMIO register offsets, bit fields, filter table geometry, and hardware color format codes used by `bdisp-hw.c`.

Important APIs and types: `struct bdisp_node` mirrors the BDisp node register groups, including general node chaining, target, color fill, three sources, clipping, filters, matrix conversion, deinterlace, pace, and gradient fields. Register constants cover global control/status, AQ1 command queue, plug registers, node register windows, coefficient table bases, and static filter dimensions. Bit definitions include reset, interrupt, idle, instruction source selectors, scaling/color-conversion flags, target/source type flags, and BDisp color encodings.

Control flow: no executable flow exists in this header. Its structure and constants are consumed by the hardware builder and reset/interrupt paths, where descriptor fields are filled in memory and then referenced through AQ1 register writes.

State and persistence: the header has no runtime state. It defines the ABI between the driver and hardware, so changes affect every submitted node and register access.

Dependencies and integration points: requires standard kernel integer and `BIT()` definitions from including compilation units. It is included by `bdisp-hw.c` and indirectly tied to debugfs node dumps in the BDisp driver.

Risks: field order in `struct bdisp_node` must remain exactly aligned with hardware expectations. Several names/comments show typo-like artifacts (`BTL_S1TY_SUBBYTE`, `BTL_S2TY_SUBBYTE`, "firect fill"), which are harmless if unused but can confuse maintenance. Constants are largely raw hardware values, so incorrect edits can silently corrupt DMA programming.

Test signals: compile coverage is necessary but insufficient. Real validation comes from node dump comparison against the hardware manual, successful color format conversions, AQ1 interrupt delivery, and regression tests around scaling/filter programming.
