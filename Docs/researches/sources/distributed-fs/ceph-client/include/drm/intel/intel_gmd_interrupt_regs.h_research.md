# sources/distributed-fs/ceph-client/include/drm/intel/intel_gmd_interrupt_regs.h

Purpose: centralizes Intel graphics/display interrupt MMIO register offsets and bit definitions for legacy i915 interrupt sources, Gen8 master IRQ, Gen11 GU/GFX master IRQ, and selected Valleyview/Cherryview registers.

Important APIs/types/functions: defines interrupt source bits for PM, ISP, LPE pipes, MIPI, port, pipe vblank/event/hblank/DPBM, overlay/plane flips, errors, sync, debug, user, ASLE, and BSD. MMIO macros cover `GEN8_MASTER_IRQ`, `GEN11_GU_MISC_ISR/IMR/IIR/IER`, `GEN11_GFX_MSTR_IRQ`, `SCPD0`, `VLV_IIR_RW`, `VLV_IER/IIR/IMR/ISR`, and `VLV_PCBR`.

Control flow: interrupt setup code programs masks/enables, reads ISR/IIR, routes master bits to display/GT/PCU/GU handlers, and acknowledges sources. Macros such as `GEN8_DE_PIPE_IRQ(pipe)` generate per-pipe bits.

State and persistence: hardware interrupt enable/mask/status registers are mutable device state. This header defines addresses and bits but no software state.

Dependencies and integration: expects `_MMIO`, `I915_IRQ_REGS`, and platform display base macros from Intel register infrastructure. Integrated by i915/xe interrupt code.

Risks and test signals: overlapping bit aliases across generations must be applied only to correct hardware. Tests should cover interrupt storms, vblank delivery per pipe, hotplug/port IRQs, GU miscellaneous IRQs, suspend/resume register restore, and platform-specific mask programming.
