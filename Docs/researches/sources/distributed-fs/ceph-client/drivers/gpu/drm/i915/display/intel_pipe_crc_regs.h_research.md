# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc_regs.h

Purpose: defines pipe CRC control, expected-value, and result registers across Intel display generations.

Important definitions: `PIPE_CRC_CTL()` and `PIPE_CRC_ENABLE`; source-selection masks and values for SKL+, IVB+, ILK+, VLV, i9xx/G4X, and gen2 border inclusion; pre-IVB expected/result channel registers; IVB expected/result registers; HSW expected/result registers.

Control flow/state: no logic. The macros encode MMIO offsets and bitfields used by CRC setup and IRQ handlers.

Dependencies/integration: depends on `intel_display_reg_defs.h` and is consumed by `intel_pipe_crc.c` plus display IRQ CRC handlers that read result registers.

Risks/test signals: register aliasing mistakes can produce bad CRC values. Notably `PIPE_CRC_EXP_4_IVB()` and `PIPE_CRC_EXP_5_IVB()` use `_PIPE_CRC_EXP_2_*` in the macro body despite defining separate offsets nearby; this deserves compile/source review against hardware specs. Test CRC capture on IVB/HSW/SKL and compare expected result register reads.
