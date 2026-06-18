# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_mchbar_regs.h

Purpose: centralizes MCHBAR mirror register offsets and bit fields used by i915 for memory controller, power, frequency, DRAM, and legacy chipset information.

Important APIs/macros: defines mirror bases `MCHBAR_MIRROR_BASE` and `_SNB`, stolen memory and DRAM configuration registers, clock/thermal/frequency registers, package power SKU fields, memory self-refresh watermark masks, reset-domain fields, Broxton/DG1/SKL/ICL DIMM layout masks, and display compensation register bits.

Control flow: no executable control flow; consumers use `_MMIO(...)` definitions with uncore read/write helpers. Comments note that Haswell and later mirror access has write restrictions for some registers.

State and persistence: no software state. The macros describe hardware state stored in chipset/MCHBAR registers.

Dependencies and integration: includes `i915_reg_defs.h`. Used by clock gating, GVT MMIO table, memory bandwidth/watermark, RPS/power, and chipset detection code.

Risks: bitfield definitions vary by generation; reusing a mask on the wrong platform can misinterpret DRAM layout or power data. The mirror is not accessible from command parser register reads, and Haswell write behavior is special.

Test signals: build coverage from users, platform boot on affected generations, memory bandwidth/watermark correctness, GVT snapshot coverage, and debug logs that read MCH_SSKPD or package power registers.
