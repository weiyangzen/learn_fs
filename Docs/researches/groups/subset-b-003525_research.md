# Research: subset-b-003525

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/hwmgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/hwmgr.h

## Purpose

`hwmgr.h` is the central PowerPlay hardware-manager interface for the AMDGPU power-management stack. It defines the long-lived `struct pp_hwmgr` device state object, backend callback tables, SMU manager callbacks, power-play table callbacks, clock/voltage dependency records, fan and thermal policy structures, and entry points used by the generic PowerPlay lifecycle code.

## Important APIs, Types, And Functions

The file exports voltage scaling constants, display-gap and BACO state enums, DPM level/table helpers, many clock-voltage dependency table layouts, CAC/TDP/PPM tables, fan and thermal-controller descriptors, `enum SMU_ASIC_RESET_MODE`, and `enum PP_TABLE_VERSION`. Its major API surfaces are `struct pp_smumgr_func`, `struct pp_hwmgr_func`, and `struct pp_table_func`.

`struct pp_smumgr_func` abstracts firmware operations such as SMU init/fini/start, firmware loading, SMC message sends, PPTable upload/download, SMC table management, AVFS/fan setup, DPM population, and SMC stop. `struct pp_hwmgr_func` abstracts ASIC-specific policy operations: backend init, state selection, DPM forcing, display notifications, power gating, fan control, sensor reads, overdrive, power limits, BACO, feature masks, MP1 state, I2C bus ownership, XGMI/DF C-state control, GPU metrics, and gfx state changes. `struct pp_hwmgr` stores chip identifiers, PP table pointers, current/request/boot power states, function tables, display configuration, fan and thermal state, forced DPM levels, workload settings, power limits, and delayed SW CTF work.

The declared lifecycle entry points are `hwmgr_early_init`, `hwmgr_sw_init`, `hwmgr_sw_fini`, `hwmgr_hw_init`, `hwmgr_hw_fini`, `hwmgr_suspend`, `hwmgr_resume`, and `hwmgr_handle_task`, plus ASIC init hooks for SMU7, SMU8, Vega12, and Vega20.

## Control Flow And Data Flow

This header contains no function bodies. Runtime control flows through the callback tables: generic PowerPlay code initializes `pp_hwmgr`, installs ASIC-specific `hwmgr_func`, `smumgr_funcs`, and `pptable_func` tables, then delegates policy requests through these function pointers. Power-state changes flow from user/display/thermal requests into `pp_power_state` and `pp_hw_power_state`, through adjustment callbacks, into SMC table updates and firmware messages.

## State And Persistence Behavior

`struct pp_hwmgr` is the persistent in-kernel state holder for a GPU power-management instance. It keeps PP table memory, backend-private pointers, current/requested power-state pointers, fan defaults, thermal controller information, DPM forced levels, feature masks, overdrive and workload settings, power limits, display config, and delayed work. Hardware persistence is indirect through callbacks that program SMC firmware, clocks, voltages, fan policy, and power-gating states.

## Dependencies And Integration Points

The header depends on Linux `seq_file`, mutex/delayed-work types through included headers, and AMD PowerPlay headers `amd_powerplay.h`, `hardwaremanager.h`, `hwmgr_ppt.h`, `ppatomctrl.h`, `power_state.h`, and `smu_helper.h`. It integrates with ASIC hwmgr implementations under `pm/powerplay/hwmgr`, SMU manager code, AtomBIOS PP table parsing, display-manager clock requests, thermal/interrupt code, sysfs/debugfs reporting, suspend/resume, reset, and metrics paths.

## Risks And Edge Cases

Callback-table ABI drift is the main risk: a missing or mismatched ASIC callback can break only one generation at runtime. Flexible arrays require correct allocation sizing. Many units differ across fields, including kHz/MHz, millivolts, VID encoding, centigrade scales, PWM percent, and RPM. `workload_prority` is misspelled but part of the structure layout. `msg_lock` must serialize SMC messages. State pointers must not outlive PP table or backend allocations, especially across suspend/resume and teardown.

## Test Signals

Useful signals are AMDGPU builds with PowerPlay enabled, probe on SMU7/SMU8/Raven/Vega hardware, power-state transitions, forced DPM sysfs operations, display hotplug and watermark changes, fan PWM/RPM control, thermal throttling and SW CTF, BACO entry/exit, suspend/resume, GPU reset, SMU firmware reload, overdrive edits, power-limit updates, and GPU metrics reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/hwmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/polaris10_pwrvirus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/polaris10_pwrvirus.h

## Purpose

`polaris10_pwrvirus.h` embeds a Polaris10-specific synthetic power-virus workload setup as static register-write and DFY data tables. It is not normal power-management policy code; it is a hardware bring-up/validation payload used by consumers that understand the command table format and can write the listed CP, RLC, TCC, TCP, MEC, HQD, MQD, and SRBM registers.

## Important APIs, Types, And Data

The exported structures are `PWR_Command_Table`, a `{ data, reg }` register write tuple, and `PWR_DFY_Section`, a packed descriptor containing DFY control, high/low target address, data size, and a flexible `dfy_data[]` payload. The file defines hypervisor MEC microcode register offsets `mmCP_HYP_MEC1_UCODE_ADDR/DATA` and `mmCP_HYP_MEC2_UCODE_ADDR/DATA`.

The main data exports are `pwr_virus_table_pre`, six `pwr_virus_sectionN` DFY sections, and `pwr_virus_table_post`. The pre table disables or programs RLC/CP/MEC/TCC/TCP state, writes repeated MEC1/MEC2 microcode words, and ends with `{0, 0xFFFFFFFF}`. The DFY sections carry command/data payloads at addresses such as `0x540fe800`, `0x540fef00`, `0x540ff000`, `0x54106500`, `0x54106900`, and `0x54116f00`; their declared sizes are 416, 16, 7440, 240, 384, and 1024 dwords. The post table programs MQD/HQD queue bases, PQ controls, active bits, write/read pointers, SRBM instances, and polling control, then terminates with the same sentinel.

## Control Flow And Data Flow

There is no C control flow. Consumers must impose the sequence: apply `pwr_virus_table_pre`, copy each DFY section to the requested GPU memory/register window according to `dfy_cntl` and address fields, then apply `pwr_virus_table_post` to activate queues. The data flow is direct from static arrays to MMIO/register-indexed writes and queue memory consumed by CP/MEC hardware.

## State And Persistence Behavior

All state lives in GPU hardware after the tables are applied. The payload changes microcode address/data ports, queue descriptors, active HQDs, polling addresses, command processor controls, and memory-backed payload areas. Those effects persist until explicit teardown, queue reset, CP reset, GPU reset, or power-cycle. The header itself stores only read-only static constants in the kernel image.

## Dependencies And Integration Points

The file relies on many `mm*` register macros supplied by ASIC register headers included by the consuming C file. It integrates with Polaris10 hwmgr/power-containment test logic, CP/MEC queue setup, SRBM instance selection, and low-level register-write helpers.

## Risks And Edge Cases

This is high-risk hardware programming data. Running it on the wrong ASIC, firmware revision, queue topology, memory address map, or register header can corrupt command-processor state or hang the GPU. The sentinel must be honored exactly. DFY sizes must match payload lengths. Pre/post ordering matters. The hard-coded addresses and queue selectors assume a specific Polaris10 environment and should not be generalized without hardware documentation.

## Test Signals

Validation needs Polaris10-only compile coverage, a register macro resolution build, controlled lab execution of the workload, GPU hang/reset recovery checks, thermal and power telemetry correlation, queue activity observation, CP/MEC status polling, and confirmation that normal graphics/compute submission recovers after teardown or reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/polaris10_pwrvirus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/power_state.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/power_state.h

## Purpose

`power_state.h` defines the generic PowerPlay power-state model shared by hardware managers. It describes user-visible state labels, classification flags, validation constraints, display/memory/software policy blocks, thermal ranges, UVD clocks, and clock-engine requests that higher-level code translates into ASIC-specific hardware states.

## Important APIs, Types, And Functions

`struct pp_hw_power_state` is the hardware-specific tail, currently represented by a `magic` field in the generic header and embedded in `struct pp_power_state`. `struct pp_power_state` combines an id, list links, classification, validation, PCIe, display, memory, temperature, software, UVD clock, and hardware blocks.

Important enums include `PP_StateUILabel`, `PP_StateClassificationFlag`, `PP_RefreshrateSource`, and `PP_MMProfilingState`. `PP_StateClassificationFlag` contains boot, thermal, forced, user 2D/3D/DC, UVD, ACPI, BACO, limited power, ULV, and overdrive template flags. `struct PP_TemperatureRange` holds edge, hotspot, memory, emergency, critical, and software CTF thresholds in `PP_TEMPERATURE_UNITS_PER_CENTIGRADES` units. `struct pp_clock_engine_request` carries client/context identifiers plus requested SCLK, MCLK, ICLK, VCE/UVD clocks, hard minimums, overdrive, ceilings, CUs, flags, and multimedia profiling state.

## Control Flow And Data Flow

The file has no executable code. Power-state data usually flows from BIOS/PP table parsing into `pp_power_state` arrays, then through hwmgr selection and adjustment callbacks, and finally into ASIC-specific `pp_hw_power_state` programming. Clock requests flow from multimedia/display clients into `pp_clock_engine_request`, where hwmgr code interprets requested clock ceilings, hard minimums, and profiling state.

## State And Persistence Behavior

Instances are persistent software state owned by the hardware manager. List links allow ordered and all-state traversal. Flags and validation fields determine whether a state can be selected under DC, display, thermal, or user conditions. Hardware persistence is indirect through the embedded hardware state and later SMC/register programming.

## Dependencies And Integration Points

The header assumes kernel integer and bool types from includers. It is included by `hwmgr.h`, thermal policy headers, PP table parsing, display-clock request code, UVD/VCE power-state selection, and user-facing power profile paths.

## Risks And Edge Cases

The misspelled `PP_StateMemroyBlock` is part of the ABI spelling in source. Classification flags exceed 16 bits, so truncating to `uint16_t` would drop BACO, limited-power-2, ULV, and UVD MVC state. Temperature units must not be confused with the 0.01 C units used by some fan tables. List links need correct initialization and lifetime management.

## Test Signals

Tests should cover PP table state parsing, boot/current/request state selection, UVD and display-specific state requests, DC disallow rules, thermal state transitions, BACO and ULV flags, multimedia profiling requests, and state equality checks in ASIC hwmgr callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/power_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_debug.h

## Purpose

`pp_debug.h` provides local debug and assertion helpers for AMD PowerPlay code. It standardizes the kernel log prefix to `amdgpu: [powerplay]`, wraps rate-limited warnings, exposes debug logging, and provides a helper for addressing flexible array entries.

## Important APIs, Types, And Functions

The main macros are `PP_ASSERT_WITH_CODE(cond, msg, code)`, `PP_ASSERT(cond, msg)`, `PP_DBG_LOG(fmt, ...)`, and `GET_FLEXIBLE_ARRAY_MEMBER_ADDR(type, member, ptr, n)`. The assertion macros warn through `pr_warn_ratelimited`; the `WITH_CODE` variant also executes caller-provided recovery or return code. `PP_DBG_LOG` maps to `pr_debug`. The flexible-array helper computes an address by taking the member address inside `ptr` and adding `n * sizeof(type)`.

## Control Flow And Data Flow

The assertion macros introduce conditional control flow at call sites but do not stop execution unless the caller-supplied `code` does so. Logging data flows into kernel printk infrastructure. Flexible array access is pure pointer arithmetic and relies on the caller's allocation layout.

## State And Persistence Behavior

The header stores no state. Its persistent effects are log records and whatever side effects the caller places in `PP_ASSERT_WITH_CODE`.

## Dependencies And Integration Points

It includes Linux `types.h`, `kernel.h`, and `slab.h`. It integrates broadly with PowerPlay hwmgr, SMU, PP table parsing, thermal, and helper code wherever warning/logging and flexible array addressing are needed.

## Risks And Edge Cases

Assertions are diagnostic, not hard invariants. Code after `PP_ASSERT` still runs. `PP_ASSERT_WITH_CODE` can hide control-flow complexity because arbitrary code is passed as a macro argument. The flexible-array macro does no bounds checking and depends on correct element type, member name, and allocation size.

## Test Signals

Signals include build coverage for all macro users, dynamic-debug output from `PP_DBG_LOG`, rate-limited warning behavior under bad PP table inputs, and sanitizer/KASAN coverage for flexible-array users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_endian.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_endian.h

## Purpose

`pp_endian.h` centralizes endian conversion between host CPU representation and SMC firmware table representation. The SMC side is treated as big-endian for 16-bit and 32-bit fields.

## Important APIs, Types, And Functions

The exported macros are `PP_HOST_TO_SMC_UL`, `PP_SMC_TO_HOST_UL`, `PP_HOST_TO_SMC_US`, `PP_SMC_TO_HOST_US`, and in-place conversion helpers `CONVERT_FROM_HOST_TO_SMC_UL`, `CONVERT_FROM_SMC_TO_HOST_UL`, and `CONVERT_FROM_HOST_TO_SMC_US`. They wrap Linux `cpu_to_be32`, `be32_to_cpu`, `cpu_to_be16`, and `be16_to_cpu`.

## Control Flow And Data Flow

There is no control flow. Data moves through these macros before tables or scalar values are copied to SMC memory or after values are read back from SMC memory. The in-place helpers assign the converted value back to the passed lvalue.

## State And Persistence Behavior

The header has no state. The persistent effect is the byte order of data stored in SMC tables, firmware mailboxes, or local host copies after conversion.

## Dependencies And Integration Points

It depends on Linux endian helper macros supplied by includers or kernel headers. It integrates with SMU table upload/download paths, PP table transformations, firmware interface structures, and any code exchanging 16-bit or 32-bit fields with SMC firmware.

## Risks And Edge Cases

Double conversion silently corrupts values. Missing conversion may only fail on big-endian or little-endian host combinations that differ from test hardware. The header has no 64-bit helper, so multiword fields need explicit high/low handling. The in-place macros evaluate the lvalue more than once syntactically through assignment and conversion, so callers should avoid expressions with side effects.

## Test Signals

Useful signals are table round-trip tests, SMC message/table upload on little-endian hosts, static review of conversion boundaries, and firmware version/clock/voltage values matching expected numeric ranges after readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_thermal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_thermal.h

## Purpose

`pp_thermal.h` provides shared thermal policy constants for PowerPlay, especially SMU7-era temperature ranges and critical-temperature-fault offsets. It is a small data header used by thermal controller setup code.

## Important APIs, Types, And Functions

The file includes `power_state.h` and defines two static `struct PP_TemperatureRange` arrays: `SMU7ThermalWithDelayPolicy` and `SMU7ThermalPolicy`. Each contains a low/normal row with minimums around `-273150` and maximums around `99000`, and a high/emergency row around `120000`. It also defines `CTF_OFFSET_EDGE`, `CTF_OFFSET_HOTSPOT`, and `CTF_OFFSET_HBM`, each set to 5.

## Control Flow And Data Flow

There is no executable control flow. Consumers select one of the static policies and copy or reference threshold values when initializing thermal management. The CTF offsets are used as adjustment constants when deriving firmware critical temperature thresholds.

## State And Persistence Behavior

The arrays are static read-only data in each translation unit that includes the header. Programmed thermal thresholds persist in SMC firmware or hardware thermal controllers after consumers apply them.

## Dependencies And Integration Points

The header depends on `struct PP_TemperatureRange` from `power_state.h` and on `__maybe_unused` from kernel compiler attributes. It integrates with SMU7 hwmgr thermal setup, fan policy, software CTF handling, and thermal interrupt or polling paths.

## Risks And Edge Cases

Because the arrays are defined in a header as `static const`, each includer gets its own copy. The initializer omits the final `sw_ctf_threshold` field, relying on zero initialization. Temperature units must match `PP_TEMPERATURE_UNITS_PER_CENTIGRADES`. The difference between delayed and non-delayed policies is not encoded in the values shown here, so consumers must provide behavior elsewhere.

## Test Signals

Validation should include thermal controller init on SMU7 ASICs, fan response around 99 C and 120 C thresholds, software CTF tests, suspend/resume threshold restoration, and build coverage with warnings enabled for struct initializer changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/ppinterrupt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/ppinterrupt.h

## Purpose

`ppinterrupt.h` defines the minimal interrupt callback contract used by PowerPlay. It identifies thermal IRQ edge types and the registration record used to bind an interrupt source to a callback and context.

## Important APIs, Types, And Functions

`enum amd_thermal_irq` defines `AMD_THERMAL_IRQ_LOW_TO_HIGH`, `AMD_THERMAL_IRQ_HIGH_TO_LOW`, and `AMD_THERMAL_IRQ_LAST`. `irq_handler_func_t` is a callback taking private data, a source id, and an interrupt-vector entry pointer, returning an int status. `struct pp_interrupt_registration_info` stores the callback, callback context, source id, and IV entry pointer.

## Control Flow And Data Flow

The header has no implementation. Runtime flow is event-driven: an ASIC interrupt handler decodes an IV entry, finds a PowerPlay registration, and invokes `call_back(context, src_id, iv_entry)`. Thermal transitions are represented by the enum values when registering or dispatching thermal interrupt handling.

## State And Persistence Behavior

Registration structures are software state owned by interrupt setup code. The header itself stores no state. Hardware interrupt configuration and registered callback lifetimes persist until unregister, device teardown, or reset.

## Dependencies And Integration Points

It depends on `uint32_t` from kernel integer typedefs supplied by includers. It integrates with hwmgr `register_irq_handlers`, AMDGPU interrupt handling, thermal threshold events, and ASIC-specific PowerPlay interrupt glue.

## Risks And Edge Cases

Callback context lifetime must cover every possible interrupt until unregister completes. `iv_entry` is a raw pointer and must be interpreted with the correct ASIC interrupt format. Source id mismatches can route thermal events to the wrong handler. IRQ handlers must avoid sleeping unless dispatch context permits it.

## Test Signals

Useful signals are thermal low-to-high and high-to-low interrupt tests, handler registration/unregistration during suspend/resume and teardown, synthetic IV entry dispatch, and lockdep coverage for callback context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/ppinterrupt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/rv_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/rv_ppsmc.h

## Purpose

`rv_ppsmc.h` defines the Raven PowerPlay-to-SMC message and result ABI. It gives driver code numeric command IDs for MP1/SMU firmware operations such as clock limits, power gating, table transfers, display notifications, GFXOFF, reset, and power-limit queries.

## Important APIs, Types, And Functions

The file exports result codes `PPSMC_Result_OK`, `Failed`, `UnknownCmd`, `CmdRejectedPrereq`, and `CmdRejectedBusy`. Message constants include version queries, GFX power up/down and GFXOFF control, ISP/VCN/SDMA power gating, hard-min clocks for ISP/VCN/FCLK/DCEFCLK/SOCCLK/GFXCLK, display count, video FPS, table transfer address setup, table transfer directions, driver reset, GFX overdrive, soft reset, MMHUB power gating, RCC/PFC/PME restore, GPU state changes, and GFX busy query. It typedefs `PPSMC_Result` as `uint16_t` and `PPSMC_Msg` as `int`.

## Control Flow And Data Flow

There is no code. Consumers pass a `PPSMC_MSG_*` value, usually with an optional parameter, to hwmgr/SMU message functions. Firmware returns a `PPSMC_Result` that controls retries, prerequisite handling, or error propagation. Table-transfer messages pair with DRAM address setup messages before moving tables between driver and SMU memory.

## State And Persistence Behavior

Messages can mutate persistent firmware and hardware state: power-gated blocks, DPM hard minimums, clock ceilings, display count, table content, GFXOFF state, and reset state. The header itself is stateless and packed for ABI consistency.

## Dependencies And Integration Points

It depends on fixed-width integer types and `#pragma pack`. It integrates with Raven hwmgr, SMU message send helpers, clock and power-gating APIs, display-manager notifications, VCN/ISP/SDMA paths, table upload/download, and reset handling.

## Risks And Edge Cases

Numeric message IDs are firmware ABI values; renumbering breaks communication. `PPSMC_Message_Count` is `0x42`, while not every value in the range is defined. Busy or prerequisite rejection needs caller-specific retry or ordering. Some messages require parameters in specific units not encoded here.

## Test Signals

Validation should include Raven firmware version query, table transfer round trips, GFXOFF enable/disable, VCN/ISP/SDMA power gating, display count changes, hard-min clock requests, reset messages, and handling of busy/prerequisite rejection results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/rv_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu10.h

## Purpose

`smu10.h` defines SMU10 firmware feature bits, workload bits, firmware status scratch layout, and SMU table IDs. It is a compact driver/firmware ABI header used by Raven/Picasso-era PowerPlay code to reason about enabled features and firmware-visible DPM levels.

## Important APIs, Types, And Functions

The file declares 64 feature bit positions for controllers and power features such as CCLK, fan, PPT/TDC/thermal/FIT/EDC, PLL power down, ULV, VDDOFF, VCN/ACP/ISP/FCLK/SOCCLK/MP0/LCLK/SHUB/DCEF/GFX DPM, deep sleep clocks, S0i2, whisper mode, MGCG, GFX CKS, PSI0, PROCHOT, CPUOFF, STAPM, and core C-states. It also defines masks for many of those bits and workload bit positions for fullscreen 3D, video, VR, compute, and custom policy.

`FwStatus_t` is a packed bitfield view of MP1 external scratch registers. It tracks current and target DPM levels for ACP, ISP, VCN, LCLK, MP0CLK, FCLK, SOCCLK, DCEFCLK, and SHUBCLK, plus ULV/S0i2/whisper status and a two-dword feature status bitmap. Table IDs include BIOS IF, watermarks, custom DPM, PM status log, DPM clocks, and momentary PM.

## Control Flow And Data Flow

No executable code is present. Driver code reads scratch registers into `FwStatus_t` or interprets equivalent words, checks feature masks, selects workload bits, and requests table transfers using table IDs. Firmware updates status fields asynchronously as DPM levels and low-power states change.

## State And Persistence Behavior

`FwStatus_t` represents firmware-maintained persistent status in MP1 scratch registers. Feature masks and table IDs are compile-time constants. Programmed SMU tables persist in firmware memory until replaced, reset, or firmware reload.

## Dependencies And Integration Points

The header depends on fixed-width types and packed layout. It integrates with `smu10_driver_if.h`, SMU10 hwmgr code, firmware status polling, feature enable/disable controls, workload policy selection, watermarks, custom DPM, PM logging, and DPM clock table transfers.

## Risks And Edge Cases

Several masks use plain `1 << bit`; bits above 31 would overflow a 32-bit int if masks were added for high features without `1ULL`. Bitfield layout is compiler-sensitive, although this is normally used in kernel/firmware-matched builds. Feature-status arrays span two dwords, so callers must handle 64-bit masks carefully.

## Test Signals

Useful tests are SMU10 build coverage, firmware feature-status reads, DPM level readback during clock changes, S0i2/ULV/GFX DPM transitions, workload switching, table transfer of watermarks/custom DPM/DPM clocks, and high feature bit mask handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu10_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu10_driver_if.h

## Purpose

`smu10_driver_if.h` defines the SMU10 driver table interface version and the packed table layouts exchanged between AMDGPU and SMU10 firmware for display clocks, watermarks, custom DPM activity coefficients, and DPM clock reporting.

## Important APIs, Types, And Functions

The interface version is `SMU10_DRIVER_IF_VERSION 0x6`. `NUM_DSPCLK_LEVELS` and the DPM level constants size fixed arrays. `FloatInIntFormat_t` stores fixed-point values. `DSPCLK_e` identifies DCEFCLK, DISPCLK, PIXCLK, and PHYCLK. `DisplayClockTable_t` maps a frequency to VID. `WatermarkRowGeneric_t` stores min/max clock and memory clock ranges plus watermark setting/type, while `Watermarks_t` contains rows for SOCCLK and DCFCLK over four ranges.

`CUSTOM_DPM_SETTING_e` enumerates GFXCLK, CCLK, FCLK CCX/GFX/stalls, and LCLK activity monitor slots. `DpmActivityMonitorCoeffExt_t` carries hysteresis, FPS, minimum active frequency type, fixed-point minimum active frequency, proportional-derivative limits, time constants, and coefficients. `CustomDpmSettings_t` groups those per setting. `DpmClock_t` and `DpmClocks_t` report DCEF, SOC, FCLK, and memory clock/voltage pairs.

## Control Flow And Data Flow

There is no implementation. Driver code fills these structures in host memory, sends table-transfer messages to firmware, or reads firmware-populated DPM clock tables back. Display and memory watermark data flows from display mode decisions into `Watermarks_t`. Custom DPM coefficients flow from policy code into firmware activity monitors.

## State And Persistence Behavior

These structures become persistent SMU table state after transfer. Firmware can use them until the next table update, reset, or reload. The header itself has no mutable state.

## Dependencies And Integration Points

It depends on fixed-width integer types. It integrates with SMU10 message/table transfer code, display watermark programming, custom DPM tuning, DPM clock query paths, and hwmgr clock reporting APIs.

## Risks And Edge Cases

Changing any structure requires an interface-version bump and matching firmware support. Fixed array sizes are ABI, not suggestions. Units differ by field: some frequencies are MHz, voltages are millivolts with two fractional bits, and coefficients are fixed-point. Padding fields must remain initialized to deterministic values for firmware compatibility.

## Test Signals

Validation should include structure size checks against firmware expectations, SMU10 table transfer smoke tests, display mode/watermark changes, custom DPM profile updates, DPM clock readback sanity, and version mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu10_driver_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu11_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu11_driver_if.h

## Purpose

`smu11_driver_if.h` is the large SMU11 driver/firmware ABI header for PPTable v2.0-era discrete GPUs. It defines clock-level counts, feature and throttler bits, workload bits, I2C/VR telemetry descriptors, DPM descriptors, the packed `PPTable_t`, metrics and watermark tables, AVFS debug/override tables, overdrive settings, activity monitor coefficients, table IDs, and ECC/debug bit fields.

## Important APIs, Types, And Functions

Important constants include DPM level counts for GFXCLK, VCLK, DCLK, ECLK, MP0CLK, SOCCLK, UCLK, FCLK, DCEFCLK, DISPCLK, PIXCLK, PHYCLK, PCIe link, and XGMI. Feature bits cover DPM, ULV, PPT/TDC/thermal, deep sleep, AC/DC, VR hot, firmware CTF, LED, fan, GFX EDC, GFXOFF, clock gating, XGMI, and ECC. The file also defines DPM override flags, VR mapping/PSI bits, throttler status bits, workload bits, table transfer status values, XGMI states, and margin-removal bits.

Core types include I2C controller enums/configuration, `QuadraticInt_t`, `LinearInt_t`, `DroopInt_t`, `PPCLK_e`, `POWER_SOURCE_e`, `VOLTAGE_MODE_e`, `AVFS_VOLTAGE_TYPE_e`, `DpmDescriptor_t`, packed `PPTable_t`, `DriverSmuConfig_t`, `OverDriveTable_t`, `SmuMetrics_t`, `Watermarks_t`, `AvfsDebugTable_t`, `AvfsFuseOverride_t`, and `DpmActivityMonitorCoeffInt_t`. `PPTable_t` is the main board and policy table: limits, thermal thresholds, voltage ranges, load lines, clock frequency tables, DC max clocks, PCIe/XGMI settings, TDPM, fan policy, AVFS curves, BTC/aging data, debug overrides, VR mappings, telemetry calibration, GPIOs, LED pins, spread spectrum, I2C controllers, and reserved/padding areas.

## Control Flow And Data Flow

There is no executable code. The driver parses or constructs PPTable data, uploads it through SMU table-transfer messages, reads `SmuMetrics_t` for telemetry, updates watermarks from display requirements, applies overdrive edits, and optionally transfers AVFS/debug/activity-monitor tables. Firmware consumes the table fields to make DPM, voltage, fan, thermal, XGMI, and throttling decisions, then reports current state through metrics and status bits.

## State And Persistence Behavior

The structures define persistent firmware table state. `PPTable_t` configures long-lived board policy until replaced or firmware reset. `SmuMetrics_t` is a firmware-updated snapshot table. `OverDriveTable_t`, watermarks, AVFS overrides, and activity coefficients persist in SMU memory once transferred. Padding and reserved fields are part of the ABI and affect size/alignment.

## Dependencies And Integration Points

The header depends on fixed-width types and packed layout. It integrates with SMU v11 hwmgr/smu code, PPTable parsing, fan control, thermal and throttling handling, overdrive sysfs, XGMI, ECC reporting, display watermarks, I2C telemetry sensors, AVFS/BTC calibration, metrics reporting, and table-transfer code.

## Risks And Edge Cases

The commented version note says structure changes require an interface-version update elsewhere, so silent ABI edits are dangerous. Some masks correctly use `1ULL` for bits above 31, while many lower masks use `1`; callers should use 64-bit feature containers. Packed layout, floats in `AvfsDebugTable_t`, and reserved padding make cross-compiler and firmware compatibility sensitive. Units vary widely: MHz, millivolts, current, temperature, RPM, PWM, GPIO polarity, and fixed-point coefficients.

## Test Signals

Validation needs compile-time size/offset checks, SMU11 firmware version compatibility, PPTable upload and readback, metrics sanity under load, fan and thermal throttling tests, overdrive edits, watermark updates during display changes, XGMI state transitions, ECC mask handling, I2C telemetry reads, and AVFS override/debug table transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu11_driver_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7.h

## Purpose

`smu7.h` defines shared SMU7 firmware constants and compact structures for older discrete GPU PowerPlay support. It describes DPM level limits, scratch-register bit fields, VR configuration encoding, PID control parameters, feature masks, firmware header layout, and display configuration enum values.

## Important APIs, Types, And Functions

The file defines SMU and VBIOS context IDs, maximum levels for VDDC, VDDCI, MVDD, VDDNB, graphics, memory, GIO, PCIe link, UVD, VCE, ACP, SAMU, and SMIO. It exports DPM action constants (`DPM_NO_LIMIT`, `DPM_NO_UP`, `DPM_GO_DOWN`, `DPM_GO_UP`), GPIO clamp modes, scratch B target/current index masks for PCIe/UVD/VCE/ACP/SAMU, VR configuration masks and shifts, VR source values, `SMU7_PIDController`, feature-enable masks, handshake-disable masks, `SMU7_Firmware_Header`, `SMU7_FIRMWARE_HEADER_LOCATION`, and `enum DisplayConfig`.

`SMU7_Firmware_Header` maps firmware image metadata and table offsets: digest, version, sizes, entry point, RTOS, soft registers, DPM table, fan table, CAC tables, MC register/timing tables, PM fuse table, globals, reserved space, and signature.

## Control Flow And Data Flow

No code is present. Driver code uses constants to parse firmware headers, locate SMC tables, configure DPM limits, interpret scratch register indexes, and encode voltage-controller configuration. Display configuration values feed SMC policy for display PHY/link conditions.

## State And Persistence Behavior

The header defines layouts for persistent firmware image data and runtime SMC table/register state. Scratch fields reflect current/target DPM levels maintained by firmware. VR and handshake settings persist after table or soft-register programming.

## Dependencies And Integration Points

It depends on `SMU__NUM_*` macros from generation-specific headers such as `smu71.h` or sibling ASIC headers, plus fixed-width types. It integrates with SMU7 hwmgr, firmware loading, PP table conversion, MC table setup, voltage controller setup, display configuration policy, UVD/VCE/ACP/SAMU DPM, and PCIe DPM.

## Risks And Edge Cases

`SMU7_CONTEXT_ID_SMC` and `SMU7_CONTEXT_ID_VBIOS` are duplicated. The file uses `//` comments in macros intended for kernel C. Macro dependencies mean include order matters. Scratch masks assume three-bit level indexes. Firmware header layout is packed ABI and must match the firmware image exactly.

## Test Signals

Useful checks are SMU7 firmware header parsing, DPM table offset validation, scratch register decode during clock changes, voltage-controller configuration tests, UVD/VCE/PCIe DPM transitions, display config changes, and firmware signature/version sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu71.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu71.h

## Purpose

`smu71.h` is an SMU7.1/Iceland firmware ABI header. It specializes SMU7 constants and structures for a dGPU-only variant, defining DPM dimensions, scoreboards, soft registers, firmware header offsets, CAC table structures, and display configuration values used by the PowerPlay hwmgr and SMC firmware.

## Important APIs, Types, And Functions

The header defines `SMU__NUM_PCIE_DPM_LEVELS`, `SMU__NUM_SCLK_DPM_STATE`, `SMU__NUM_MCLK_DPM_LEVELS`, Iceland/dGPU feature macros, `SID_OPTION`, `data_64_t`, `data_128_t`, SMU7 context IDs, SMU71 maximum level counts, DPM action constants, GPIO clamp modes, scratch B bit masks, DTE dimensions, `SMU71_PIDController`, `SMU7_LocalDpmScoreboard`, `SMU7_VoltageScoreboard`, `SMU7_PCIeLinkSpeedScoreboard`, `SMU7_PowerScoreboard`, `SMU7_ThermalScoreboard`, feature masks, handshake disables, `SMU71_SoftRegisters`, `SMU71_Firmware_Header`, `SMU7_HystController_Data`, `enum DisplayConfig`, and local CAC table structures.

The scoreboards expose firmware runtime state for DPM PID control, voltage requests across clients, PCIe DPM, power calculation, and thermal control. `SMU71_SoftRegisters` carries reference clocks, timer period, feature enables, display PHY configs, activity averages, enabled DPM levels, DRAM log addresses, ULV counters, microcode status, freeze/forced flags, and activity weight. `SMU71_Firmware_Header` extends the SMU7 header with UVD, ACP, VCE, SAMU DPM table pointers and ULV settings.

## Control Flow And Data Flow

There is no C implementation. Driver code reads firmware headers and soft-register offsets, writes feature enables and enabled-level masks, interprets scoreboards for diagnostics or policy, and transfers SMC tables. Firmware updates scoreboards as PID loops, voltage arbitration, PCIe DPM, power, and thermal controllers run.

## State And Persistence Behavior

Most structures are layouts for persistent firmware memory. Soft registers and scoreboards retain runtime state until firmware reset. Function pointers inside `SMU7_LocalDpmScoreboard` are meaningful to SMC firmware builds, not host driver execution. CAC tables and firmware table offsets persist as part of firmware/SMC memory.

## Dependencies And Integration Points

The header conditionally packs structures when not building SMC microcode. It integrates with SMU7/SMU71 hwmgr code, firmware parsing, DPM/voltage/PCIe/thermal/power diagnostics, MC/CAC setup, display configuration policy, ULV handling, and local CAC programming.

## Risks And Edge Cases

Host code must not call firmware function pointers embedded in scoreboards. Conditional fields under `SMU__DGPU_ONLY` change structure layout and must match firmware. `SMU71_MAX_LEVELS_GIO` references `SMU__NUM_LCLK_DPM_LEVELS`, which must be defined by the build context. Packed ABI changes can break firmware table offsets. Several names retain SMU7 prefixes even in SMU71-specific structures.

## Test Signals

Validation should include structure size/offset checks, Iceland firmware header parsing, soft-register read/write, DPM and voltage scoreboard sanity during load changes, PCIe DPM transitions, thermal and power scoreboard updates, local CAC table programming, ULV counters, and suspend/resume firmware state restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu71.h -->
