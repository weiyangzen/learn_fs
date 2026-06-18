# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/hardwaremanager.h

## Purpose
`hardwaremanager.h` defines common PowerPlay hardware-manager abstractions used by ASIC-specific backends such as Vega20. It provides platform capability bits, performance/clock descriptor types, fan-speed capability metadata, capability helpers, and generic `phm_*` function declarations that dispatch through `struct pp_hwmgr`.

## Important APIs, Types, and Functions
Important types include `struct phm_fan_speed_info`, `enum phm_platform_caps`, `struct pp_hw_descriptor`, `enum PHM_PerformanceLevelDesignation`, `struct PHM_PerformanceLevel`, `enum PP_PCIEGen`, `struct PP_Clocks`, `struct pp_clock_info`, `struct phm_platform_descriptor`, `struct phm_clocks`, `struct phm_odn_performance_level`, and `struct phm_odn_clock_levels`. Inline helpers `phm_cap_set()`, `phm_cap_unset()`, `phm_cap_enabled()`, and macro `PP_CAP(c)` are heavily used by ASIC backends to gate features.

The declared `phm_*` functions cover ASIC setup, dynamic state management, power-state application, clock adjustment, DPM forcing, display configuration changes, thermal start/stop, DAL clock queries, clock-by-type queries, display clock voltage requests, max high clocks, and SMC firmware CTF disable.

## Control Flow
The header defines dispatch-layer contracts but not implementations. ASIC code fills callback tables, while generic PHM functions call through those callbacks to execute backend-specific logic. Capability bits set during PPTable and backend init determine later branches such as microcode fan control, PowerControl, OD8 AC/DC support, UMD pstate, BACO, and display-clock behavior.

## State and Persistence
`struct phm_platform_descriptor` is the main generic state container described here. It stores platform caps, VBIOS interrupt ID, overdrive and clock step information, hardware performance counts, TDP and voltage adjustment fields, and related limits. ASIC backends populate it during init; it persists for the lifetime of the `pp_hwmgr`.

## Dependencies and Integration Points
This header sits between generic PowerPlay code and ASIC hwmgr implementations. Vega20 uses its caps helpers throughout initialization, PowerTune, fan control, display handling, and OD setup. It also depends on shared enums/types from DM and KGD PP interfaces through includers.

## Risks
Capability enum order is ABI-like within the driver because caps are stored as bit positions in an integer array. Adding or reordering entries can break persisted assumptions inside a build. `PP_CAP(c)` assumes a local variable named `hwmgr`, which is convenient but can obscure dependencies and fail in contexts without that name. Duplicate DPM update macros also exist in Vega20 headers, creating possible maintenance drift.

## Test Signals
Compile coverage plus runtime feature gating is key: platform caps printed or inferred from behavior should match VBIOS/driver policy, generic PHM calls should dispatch to Vega20 callbacks, and fan/thermal/DPM/OD/display features should appear only when the corresponding caps are set.
