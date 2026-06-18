# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.h

## Purpose
`ppatomctrl.h` is the public type and function contract for the legacy ATOM BIOS PowerPlay adapter. It defines normalized hwmgr-facing structures that hide the raw ATOM table layouts used in `ppatomctrl.c`.

## Important APIs and types
The header defines clock divider structures for older ASIC families, memory PLL structures, spread-spectrum structures/enums, voltage tables, MC register/timing tables, GPIO pin assignment, AVFS parameters, SCLK range tables, and EDC leakage table shapes. Constants such as `PP_ATOMCTRL_MAX_VOLTAGE_ENTRIES`, `VBIOS_MC_REGISTER_ARRAY_SIZE`, `VBIOS_MAX_AC_TIMING_ENTRIES`, and `MAX_SCLK_RANGE` bound fixed-size output arrays.

Function declarations cover BIOS GPIO/voltage lookups, EVV voltage calculation, reference clocks, spread spectrum, MC timing table initialization, DRAM timing programming, memory/engine PLL divider calculation, eFuse reads, AVFS/profiling reads, leakage table reads, and shared rail lookup.

## Control flow and state
There is no executable code. The header establishes caller-owned output buffer contracts. The `.c` implementation fills these buffers from ATOM data/command tables and usually returns `0` on success with nonzero/negative values on failure.

## Dependencies and integration points
The header includes `hwmgr.h`, so it is part of the internal AMDGPU powerplay hwmgr interface rather than a generic BIOS parser. ASIC-specific hwmgr implementations include it to acquire voltage tables, PLL dividers, AVFS data, and memory timings from legacy ATOM BIOS.

## Risks and test signals
Fixed-size arrays must stay aligned with implementation bounds. If firmware exposes more voltage entries, MC registers, timing entries, or SCLK ranges than the constants allow, the implementation must reject or clamp safely. Several exported structs mirror hardware/firmware units such as 10 kHz clocks, millivolts, 0.25 mV units, GPIO masks, and FCW fields; tests should verify unit conversions at the `.c` boundary.
