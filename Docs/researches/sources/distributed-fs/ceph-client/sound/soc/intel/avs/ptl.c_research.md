# sources/distributed-fs/ceph-client/sound/soc/intel/avs/ptl.c

Purpose: Supplies Panther Lake DSP operation table and power-domain handling, reusing most MTL/LNL/ICL helpers while switching to PTL-specific power-gating registers.

Important APIs/functions: Internal `avs_ptl_core_power_on()`, `avs_ptl_core_power_off()`, `avs_ptl_core_power()`, and exported `const struct avs_dsp_ops avs_ptl_dsp_ops`.

Control flow: Power-on sets DSP domain SPA, waits for CPA, prevents power gating through `MTL_REG_HfPWRCTL2`, waits for `MTL_REG_HfPWRSTS2`, and assigns host ownership. Power-off allows power gating through the PWRCTL2 path, clears SPA, and waits for CPA clear. The ops table delegates reset/interrupt/load/log/coredump/D0ix behavior to platform-compatible helpers.

State and persistence: State is hardware register state only.

Dependencies and integration: Uses MTL register definitions and helpers from `registers.h`, tracepoints, `avs_mtl_*` IPC interrupt controls, `avs_lnl_core_stall`, HDA firmware loading, ICL logging/D0ix helpers, and AVS ops dispatch in the parent device.

Risks: PTL shares MTL names for registers but uses PWRCTL2/PWRSTS2 for DSP HP power gating; incorrect register selection would break power transitions. Main-core masking means additional cores are ignored by this path.

Test signals: PTL boot and runtime PM transitions, firmware loading through HDA path, IPC interrupt handling via reused MTL code, and D0ix entry/exit on active/inactive streams.
