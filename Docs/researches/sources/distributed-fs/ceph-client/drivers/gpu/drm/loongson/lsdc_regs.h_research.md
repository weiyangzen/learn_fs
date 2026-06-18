# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_regs.h

Purpose: central register and bitfield map for the Loongson display controller, pixel/GFX PLLs, CRTC timing/config, DVO, cursor, interrupts, GPIO I2C, HDMI, AVI infoframes, vblank counters, and audio PLL registers.

Important APIs/types/functions: `LSDC_PLL_REF_CLK_KHZ`, chip config bases and PLL offsets, pixel format and DMA-step enums, CRTC CFG/timing/address registers, cursor format/size/location enums, interrupt masks/enables, GPIO registers, HDMI PHY/interface/PLL bits, HPD flags, AVI packet bits, and vblank counter registers.

Control flow: no code flow. CRTC, plane, IRQ, I2C, output, and PLL modules use these definitions for MMIO accesses.

State and persistence: describes persistent hardware register state. Comments document chip-specific oddities such as mixed CRTC register offsets, one-cursor LS7A1000 behavior, and different interrupt clear semantics.

Dependencies and integration points: includes Linux bitops/types. Integrated across all `lsdc_*` modules.

Risks and test signals: incorrect offsets affect display timing, scanout addresses, cursor, HDMI, or interrupts. The `LSDC_HDMI1_AVI_CONTENT0` value overlaps `LSDC_HDMI1_PHY_CAL_REG`; verify against hardware docs. Test register dumps, HDMI modes, vblank IRQs, cursor ops, GPIO DDC, and both LS7A1000/LS7A2000 paths.
