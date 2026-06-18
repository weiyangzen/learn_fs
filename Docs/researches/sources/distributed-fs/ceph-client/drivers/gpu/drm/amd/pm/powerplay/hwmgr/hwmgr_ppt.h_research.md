# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hwmgr_ppt.h

## Purpose
`hwmgr_ppt.h` defines PowerPlay table v1 data structures consumed by hwmgr table-processing code. It models clock/voltage dependency records, multimedia clock dependencies, voltage lookup rows, PCIe entries, and GPIO-related PowerPlay table data.

## Important Types
`phm_ppt_v1_clock_voltage_dependency_record` stores a clock with voltage indices and concrete voltage values for VDDC, VDDGFX, VDDCI, MVDD, phase count, CKS flags, voltage offsets, and SCLK offset. The dependency table wrappers use flexible arrays with `count`. Multimedia records capture UVD, VCE, ACP, and SAMU clocks with related voltage data. Voltage lookup records hold calculated/base/CAC-low/mid/high voltages. PCIe records include generation speed, lane width, and associated SCLK. `phm_ppt_v1_gpio_table` exposes the VRHot-triggered SCLK DPM index.

## State, Dependencies, And Integration
This header has no executable state. It depends on `hardwaremanager.h`, `smumgr.h`, and AtomBIOS types. Runtime table parsers allocate and fill these structures from VBIOS/PowerPlay tables; ASIC hwmgr code then uses them to build dynamic states, DPM levels, voltage tables, and PCIe policy.

## Risks And Test Signals
Risks are flexible-array allocation mistakes, count overflow, unit mismatch between BIOS tables and hwmgr consumers, and version confusion between PowerPlay table formats. Test signals include successful pptable parsing, correct DPM level counts and voltages, valid PCIe lane/gen policy, VRHot behavior, and no out-of-bounds access under malformed VBIOS tables.
