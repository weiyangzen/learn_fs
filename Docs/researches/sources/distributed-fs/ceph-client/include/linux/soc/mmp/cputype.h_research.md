# sources/distributed-fs/ceph-client/include/linux/soc/mmp/cputype.h

Purpose: This header provides Marvell MMP/PXA-family CPU type detection helpers.

Important APIs/types/functions: It defines ID masks and inline/macros that classify MMP and related Marvell application processors by CPU ID or SoC revision.

Control flow: Platform and peripheral drivers use the helpers during initialization to choose variant-specific register offsets, clocks, or quirks.

State and persistence: The header interprets architecture CPU ID state; it stores no mutable data.

Dependencies and integration: Integrates with ARM platform support for MMP/PXA, board files, clocks, pinctrl, and legacy drivers.

Risks and test signals: Bad masks or disabled config paths can misclassify SoCs. Test compile-time coverage for each enabled CPU family and boot/probe on representative MMP variants.
