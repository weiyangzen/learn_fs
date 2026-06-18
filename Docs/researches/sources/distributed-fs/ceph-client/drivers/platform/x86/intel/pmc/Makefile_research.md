<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Makefile

## Purpose
Builds the Intel PMC core, platform driver, and SSRAM telemetry helper.

## Important Build Rules
`intel_pmc_core-y` links common core plus platform maps `spt.o`, `cnp.o`, `icl.o`, `tgl.o`, `adl.o`, `mtl.o`, `arl.o`, `lnl.o`, `ptl.o`, and `wcl.o`. `intel_pmc_core_pltdrv-y := pltdrv.o` builds the platform driver. `intel_pmc_ssram_telemetry-y += ssram_telemetry.o` builds telemetry support.

## Control Flow And State
Kbuild links all platform map tables into the core module so runtime ID matching can select the appropriate register map.

## Dependencies, Risks, And Test Signals
Risks are missing object additions for new SoCs or stale object names. Test targeted builds and ensure `adl_reg_map` and other map symbols resolve from `core.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Makefile -->
