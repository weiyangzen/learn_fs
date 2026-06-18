<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cirrus.h -->
# sources/distributed-fs/ceph-client/include/video/cirrus.h

Purpose: defines Cirrus Logic VGA/framebuffer chipset register indexes for sequencer, CRT controller, graphics controller, attribute controller, sleep, clock, cursor, and blitter extensions.

Important APIs and types: macro constants name POS/sleep ports, sequencer extension registers, CRT extension/status registers, graphics controller extension and BLT registers, and attribute controller extension registers for CL-GD542x/543x-style chips.

Control flow: the Cirrus framebuffer driver unlocks extension registers, programs clocks/timing/cursor, configures memory/performance, and drives the blitter using these register indexes.

State and persistence: live state is in VGA/Cirrus indexed registers and framebuffer memory. The header is macro-only.

Dependencies and integration points: integrates with `clgenfb`/Cirrus fbdev code and legacy VGA register access helpers.

Risks and test signals: risks include accessing scratch registers marked do-not-access, chipset revision differences, blitter register sequencing, and VGA index/data port races. Test mode set, cursor, acceleration, suspend/resume, and multiple CL-GD chip variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cirrus.h -->
