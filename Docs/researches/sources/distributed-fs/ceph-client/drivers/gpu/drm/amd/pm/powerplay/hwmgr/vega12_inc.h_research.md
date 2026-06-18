# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h

`vega12_inc.h` is a Vega12 register include aggregator. It declares no functions, types, or runtime state; its purpose is to collect generated SOC15 register offsets, defaults, masks, and shifts for THM, MP, GC, and NBIO blocks.

The included headers are `asic_reg/thm/thm_9_0_*`, `asic_reg/mp/mp_9_0_*`, `asic_reg/gc/gc_9_2_1_*`, and `asic_reg/nbio/nbio_6_1_*`. Runtime code in `vega12_hwmgr.c` and `vega12_thermal.c` uses the macros enabled here through `RREG32_SOC15`, `WREG32_SOC15`, PCIe register reads, and `REG_SET_FIELD`.

State and persistence are indirect: this file does not store data, but it exposes constants used to read and write persistent hardware register state. Dependencies are the generated ASIC register headers matching the exact Vega12/IP versions.

The main risk is incorrect IP-version binding, because wrong offsets or masks can silently misprogram hardware. Test signals include clean compilation, correct thermal interrupt programming, accurate temperature reads, and valid PCIe link-width/speed reporting on Vega12 hardware.
