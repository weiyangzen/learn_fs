# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpe_regs.h

Purpose: register map and bitfield definitions for the TI VPE/VIP top-level blocks used by the VPE mem2mem and VIP capture drivers. It names PID, interrupt, clock/reset, datapath format/select, upsampler, DEI, EDI, and film-mode-detection registers.

Important APIs/types: this header exports macros only. Key groups include `VPE_PID_*` extraction fields, `VPE_INT0_*` list/client/error interrupt bits, `VPE_CLK_ENABLE`/`VPE_CLK_RESET` and clock bits, `VPE_CLK_FORMAT_SELECT` datapath fields (`VPE_RGB_OUT_SELECT`, `VPE_DS_SRC_DEI_SCALER`, `VPE_CSC_SRC_DEI_SCALER`, `VPE_DS_BYPASS`, `VPE_COLOR_SEPARATE_422`), chroma upsampler register offsets/fields, DEI frame-size/bypass/flush/progressive bits, EDI configuration/LUT fields, and FMD window/control/status fields.

Control flow: `vpe.c` composes shadow MMR ADB payloads using these offsets and fields, then uploads them through VPDMA. `vip.c` also uses VIP/VPE top-level clock/reset/datapath constants while configuring slice paths and interrupts. The values determine which hardware subblocks are clocked, reset, routed, and interrupted.

State and persistence: no software state is stored here. The macros describe persistent MMIO state in the hardware until reset or reprogrammed by VPE/VIP.

Dependencies and integration: depends on `BIT()` being available from included kernel headers in users. It is integrated with `vpe.c`, `vip.c`, and scaler/CSC register offsets used in ADB construction.

Risks: duplicated macro names in the upsampler/EDI blocks can hide accidental redefinition drift. A typo-like `VPE_INTC_EOI` versus the VIP code’s `VIP_INTC_E0I` usage should be watched in compile coverage. Register-field changes are not type-checked, so wrong masks/shifts would produce valid builds but invalid hardware programming.

Test signals: compile coverage for VPE and VIP users; register dump comparison against the DRA7 TRM; successful VPE scaling/deinterlacing and VIP capture datapath routing; interrupts firing and clearing on expected list/error bits; and reset/clock sequencing across runtime PM cycles.
