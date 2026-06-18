# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds_regs.h

Purpose: defines LVDS port control registers and bitfields for integrated and PCH LVDS.

Important APIs/types/functions: `LVDS` and `PCH_LVDS` MMIO addresses; `LVDS_PORT_EN`; pipe select fields for old and CPT/PCH platforms; dither, sync polarity, border, A0-A3/CLKB/B0-B3 power fields; and `LVDS_DETECTED`.

Control flow: LVDS code reads these fields for discovery/readout and writes them during pre-enable and disable.

State and persistence behavior: definitions only; state is in hardware LVDS registers.

Dependencies and integration points: depends on i915 register macros and is consumed by LVDS encoder code and related display readout.

Risks: LVDS port enable must be set before DPLL enable because DPLL semantics change when LVDS is assigned to a pipe. Pipe select masks differ between CPT and older platforms.

Test signals: readout of pipe selection and enable bits, pre-enable programming for single/dual link and sync polarity, and PCH detect bit handling.
