# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/power_state.h

## Purpose

`power_state.h` defines the generic PowerPlay power-state model shared by hardware managers. It describes user-visible state labels, classification flags, validation constraints, display/memory/software policy blocks, thermal ranges, UVD clocks, and clock-engine requests translated into ASIC-specific hardware states.

## Important APIs, Types, And Functions

`struct pp_power_state` combines an id, list links, classification, validation, PCIe, display, memory, temperature, software, UVD clock, and hardware blocks. `struct pp_hw_power_state` is the embedded hardware-specific tail. Important enums include `PP_StateUILabel`, `PP_StateClassificationFlag`, `PP_RefreshrateSource`, and `PP_MMProfilingState`. `struct PP_TemperatureRange` holds edge, hotspot, memory, emergency, critical, and software CTF thresholds. `struct pp_clock_engine_request` carries client/context identifiers and requested SCLK, MCLK, ICLK, VCE/UVD clocks, hard minimums, overdrive, ceilings, CU counts, flags, and multimedia profiling state.

## Control Flow And Data Flow

The file has no executable code. Power-state data flows from BIOS/PP table parsing into `pp_power_state` arrays, then through hwmgr selection and adjustment callbacks into ASIC-specific `pp_hw_power_state` programming. Clock requests flow from multimedia/display clients into `pp_clock_engine_request`.

## State And Persistence Behavior

Instances are persistent software state owned by the hardware manager. List links allow ordered and all-state traversal. Flags and validation fields determine whether a state can be selected under DC, display, thermal, or user conditions. Hardware persistence is indirect through embedded hardware state and later SMC/register programming.

## Dependencies And Integration Points

The header assumes kernel integer and bool types from includers. It is included by `hwmgr.h`, thermal policy headers, PP table parsing, display-clock request code, UVD/VCE power-state selection, and user-facing power profile paths.

## Risks And Edge Cases

The misspelled `PP_StateMemroyBlock` is part of the source ABI spelling. Classification flags exceed 16 bits, so truncating them drops BACO, limited-power-2, ULV, and UVD MVC state. Temperature units must not be confused with fan-table units. List links require correct initialization and lifetime management.

## Test Signals

Tests should cover PP table state parsing, boot/current/request state selection, UVD and display-specific requests, DC disallow rules, thermal transitions, BACO and ULV flags, multimedia profiling requests, and state equality checks in ASIC hwmgr callbacks.
