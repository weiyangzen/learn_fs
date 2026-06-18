# subset-b-003527 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu9_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu9_driver_if.h

## Purpose

`smu9_driver_if.h` is the packed driver-to-SMU ABI for early SMU9/Vega power management. It defines the binary table layouts, table IDs, feature limits, and command arguments used when the Linux AMDGPU PowerPlay driver exchanges power, clock, voltage, fan, watermark, AVFS, and debug data with SMU firmware. The file has no executable functions; its primary responsibility is keeping the host-side C layout identical to the firmware layout.

The interface version is `SMU9_DRIVER_IF_VERSION 0xE`, with an explicit warning that any structure change must increment the version. That is a strong signal that compatibility is versioned at the byte-layout level rather than by named fields.

## Important APIs, types, and constants

The DPM limit macros define fixed array sizes for graphics, UVD, VCE, MP0, memory, SOC, DCEF, PCIe link, EVV voltage, and PSP level maps. These constants size the arrays embedded in `PPTable_t` and therefore define how much data the firmware expects for each clock domain.

`PllSetting_t` describes a PLL level with feedback multipliers, spread-spectrum state, and divider ID. It is used for graphics and memory clock levels. `GbVdroopTable_t` and `QuadraticInt_t` encode fixed-point droop/guardband equations. `DisplayClockTable_t` pairs display clock frequencies with voltage IDs. `DSPCLK_e` identifies DCEF, DISP, PIX, and PHY clock classes.

`PPTable_t` is the central packed table. It contains PowerTune limits, external I2C component addresses, Gemini board aperture data, ULV settings, SOC voltage IDs, graphics/SOC/UVD/VCE/MP0/memory DPM tables, display clock tables, voltage mode selectors, averaging alpha values, PCIe link settings, fan control parameters, GPIO assignments, LED pins, AVFS/guardband equations, ageing guardband parameters, boost/ACG settings, and firmware padding.

`Watermarks_t` contains four watermark ranges for SOC/DCEF clock classes. `AvfsTable_t`, `AvfsDebugTable_t`, and `AvfsFuseOverride_t` describe AVFS runtime tables, debug samples, and fuse/equation overrides. The `TABLE_*` constants map the table-transfer SMU messages to specific shared-memory table IDs.

The file also defines `UCLK_SWITCH_SLOW`/`FAST`, GFX DIDT bit masks and shifts for SQ/TCP/TD/DB blocks, and margin-removal bit indices.

## Control flow

There is no local runtime control flow. The effective flow is imposed by PowerPlay managers: allocate or fill a `PPTable_t`/related table in driver memory, program the driver DRAM address through SMU messages, and use `SMC_MSG_TransferTableDram2Smu` or `SMC_MSG_TransferTableSmu2Dram` with the `TABLE_*` IDs. Firmware then consumes the packed layout directly.

Call sites must populate dependent fields consistently. For example, voltage modes determine whether indexed voltage tables, AVFS interpolation, worst-case values, or static offsets are meaningful; link DPM fields must match PCIe capabilities; and fan fields only matter when firmware fan control is enabled.

## State and persistence behavior

The structures model firmware-owned runtime state and driver-provided policy, not persistent kernel state. Values persist in SMU RAM or DRAM-backed transfer buffers until the driver uploads a replacement table, the firmware overwrites a status/debug table, or the GPU resets. GPIO, fan, I2C, voltage, and DPM fields can affect live hardware behavior after transfer.

Because `PPTable_t` is packed, padding fields are also ABI state. The `MmHubPadding` arrays are reserved for firmware/internal use and must remain present to preserve offsets.

## Dependencies and integration points

The header includes `smu9.h` and depends on Linux fixed-width integer types being available through the include chain. It integrates with the PowerPlay SMU manager abstraction in `smumgr.h`, generation-specific SMC message headers such as `vega10_ppsmc.h`, and SMU9 manager implementations that transfer `TABLE_PPTABLE`, `TABLE_WATERMARKS`, `TABLE_AVFS`, and related IDs.

It also depends on VBIOS/PowerPlay table parsing code for actual values: thermal limits, fan parameters, DPM clocks, voltages, I2C addresses, and board-specific capabilities are typically derived from VBIOS tables before being encoded here.

## Risks

The main risk is ABI drift. Any field insertion, type-size change, array-size change, or packing change can cause firmware to interpret the wrong bytes as clocks, voltages, thermal limits, or fan settings. The file uses fixed-width types and `#pragma pack(push, 1)` to reduce that risk, but consumers still need version checks against firmware.

Unit mismatches are another risk: fields mix MHz, 10 KHz units, Celsius, watts, amps, SVI2 VID, mOhms, and fixed-point equation formats. Incorrect scaling can silently produce unstable DPM or thermal behavior. The AVFS and ageing-guardband equations are especially sensitive because they encode fixed-point coefficients and shifts.

## Test signals

Useful validation includes build coverage for SMU9 PowerPlay, firmware interface-version checks, table-size/offset assertions against firmware specifications, and runtime testing on Vega hardware. Runtime signals include successful PP table upload/download, correct DPM level enumeration, stable fan behavior, valid temperature/power telemetry, successful watermark updates, and no SMU table-transfer failures in kernel logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu9_driver_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu_ucode_xfer_cz.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu_ucode_xfer_cz.h

## Purpose

`smu_ucode_xfer_cz.h` defines Carrizo-era SMU microcode transfer metadata. It provides the task/job table format used by firmware and driver code to describe save, restore, load, register access, and initialization work. The file is a binary contract for constructing a table of contents and associated task list in memory.

## Important APIs, types, and constants

The job/task constants define a small bytecode. `TASK_TYPE_*` identifies no-op, microcode load/save, register load/save, and initialization tasks. `TASK_ARG_REG_*` selects register spaces such as SMC indirect, MMIO, FCH, and UNB. `TASK_ARG_INIT_*` names initialization targets like the multimedia power log and clock table.

`JOB_*` constants enumerate save/restore jobs for GFX, FCH, UNB, GMC, and GNB. `IGNORE_JOB` and `END_OF_TASK_LIST` provide sentinels for job and task traversal. `SMU_DRAM_REQ_MM_PWR_LOG` gives the firmware-requested DRAM region size for the multimedia power log.

The `UCODE_ID_*`, `UCODE_ID_*_MASK`, and `UCODE_ID_*_SIZE_BYTE` macros enumerate the firmware components available to the transfer logic: SDMA, CP CE/PFP/ME/MEC jump tables, GMCON RENG, RLC segments, and DMCU ERAM/IRAM. `NUM_UCODES` fixes the component count at 14.

`data_64_t` splits a 64-bit address into high/low 32-bit words. `SMU_Task` stores a task type, argument, next-task index, address, and size. `struct TOC` contains a 32-entry job list followed by a flexible task array.

The `METADATA_CMD_*` constants describe embedded metadata operations for register programming, delay, register-space changes, and whether the operation applies on save or load. `SMU_MetaData_Mode0` through `Mode3` describe register address/data/mask payload formats.

## Control flow

No functions are defined here. Runtime code interprets `struct TOC`: select a job index from `JobList`, walk linked `SMU_Task.next` entries until `END_OF_TASK_LIST`, and execute each task according to its type and argument. Metadata commands are interpreted as another compact command stream for register writes, masked writes, polling, delay, or register-space selection.

## State and persistence behavior

The header describes transient transfer state in DRAM plus hardware state modified by tasks. Microcode load/save tasks move firmware blobs to or from addresses identified by `data_64_t`; register tasks save and restore MMIO-like register contents; initialization tasks provision firmware-visible DRAM regions. Persisted effects are whatever the SMU loads into hardware or saves for later restore during power transitions.

## Dependencies and integration points

The file depends only on fixed-width integer types available to the including compilation unit. It integrates with Carrizo SMU boot/resume code, firmware image layout code, and any logic that constructs the TOC from component masks and firmware blob addresses.

It also integrates with the microcode IDs used elsewhere in AMDGPU. The masks must match firmware expectations so the right blobs are loaded, and the size constants must match the packaged firmware image sizes.

## Risks

Task-list corruption can produce firmware loads from the wrong physical address, overrun a firmware image, or execute an unintended register-space operation. `struct TOC` uses a flexible array with no local bounds enforcement, so callers must allocate enough space and validate task indices.

The hard-coded microcode sizes are brittle. If firmware blobs change size without updating the constants or without independent runtime size validation, transfer code can truncate or overrun payloads. Metadata command values are also magic constants; a mismatch with firmware command decoding can cause silent no-ops or destructive register writes.

## Test signals

Test signals include successful Carrizo SMU boot, suspend/resume save/restore, graphics and multimedia firmware component load success, and absence of SMC/firmware load errors. Focused validation should exercise each job type, metadata register modes, and firmware images whose sizes match every `UCODE_ID_*_SIZE_BYTE` constant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu_ucode_xfer_cz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu_ucode_xfer_vi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu_ucode_xfer_vi.h

## Purpose

`smu_ucode_xfer_vi.h` defines the Volcanic Islands SMU DRAM table of contents used for firmware component transfer. It describes a fixed-size TOC containing entries for SMU, SDMA, CP, GMCON, RLC, VBIOS, metadata, and related payloads. It is a layout header rather than an implementation.

## Important APIs, types, and constants

`SMU_DRAMData_TOC_VERSION` identifies the TOC format. `SMU_DIGEST_SIZE_BYTES`, `SMU_FB_SIZE_BYTES`, and `SMU_MAX_ENTRIES` set digest, firmware buffer, and entry-count limits. `MAX_IH_REGISTER_COUNT` bounds interrupt-handler register restore metadata.

The `UCODE_ID_*` constants enumerate supported firmware components. IDs 0 through 14 cover major firmware blobs and metadata; IDs 32 through 36 cover RLC scratch/SRM, MEC storage, and VBIOS parameters; `UCODE_META_DATA 0xFF` identifies metadata payloads. The low `UCODE_ID_*_MASK` macros map the first 13 entries to a bitmask used by callers to select components.

`UCODE_FLAG_UNHALT_MASK` marks entries whose firmware should be unhalted after load. `struct SMU_Entry` is the per-component descriptor: ID, version, image address, metadata address, data size, flags, and register-entry count. The structure has explicit `__BIG_ENDIAN` member ordering for the paired 16-bit fields. `struct SMU_DRAMData_TOC` stores version, number of entries, and a 12-entry array.

## Control flow

There is no executable control flow in the header. Runtime transfer code builds a `SMU_DRAMData_TOC`, populates each `SMU_Entry`, points the SMU at the DRAM buffer, and issues firmware load messages. Firmware then walks the entries and performs the selected component loads or register restore operations.

## State and persistence behavior

The TOC is transient DRAM state used during firmware loading or restore. The persistent effects are loaded firmware images, restored interrupt-handler registers, VBIOS parameter availability, and any firmware unhalt operations triggered by entry flags. The structure itself is replaced whenever the driver prepares a new transfer.

## Dependencies and integration points

The header depends on the including driver path for integer definitions and endian macros. It integrates with VI SMU firmware loading, CGS firmware lookup, PSP/SMU boot sequencing, and register restore metadata generation. Consumers must provide valid GPU-visible addresses split into high/low words.

The endianness branch is important because the SMU consumes a specific memory representation. Host and firmware byte order must agree after any CPU-to-firmware conversions performed by the caller.

## Risks

`SMU_MAX_ENTRIES` is 12 even though more than 12 IDs are defined. Callers must decide which IDs are represented in a given TOC and avoid overflowing the array. The 16-bit field ordering under `__BIG_ENDIAN` is easy to miss during refactoring.

Address and size fields are trusted by firmware. A bad address split, stale metadata address, incorrect register count, or missing `UNHALT` flag can fail boot, leave engines halted, or restore wrong hardware state. Bitmask constants do not cover every defined ID, so code that assumes mask coverage for all IDs can skip high-numbered payloads.

## Test signals

Useful validation includes VI ASIC boot, firmware reload after suspend/resume, successful SDMA/CP/RLC bring-up, and no SMU load error responses. Table-generation tests should verify entry count, endian layout, address alignment, data sizes, register metadata counts, and behavior when optional payload IDs are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu_ucode_xfer_vi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smumgr.h

## Purpose

`smumgr.h` is the public PowerPlay SMU manager façade. It defines generic table/member IDs and declares wrapper functions that higher-level hardware managers use without binding directly to a generation-specific SMU implementation. The actual work is delegated through `pp_smumgr_func` implementations such as `ci_smu_funcs`.

## Important APIs, types, and constants

`enum SMU_TABLE` names update targets for UVD, VCE, and BIF tables. `enum SMU_TYPE` and `enum SMU_MEMBER` describe logical offset queries into soft-register and discrete DPM table structures. `enum SMU_MAC_DEFINITION` provides logical maximums such as graphics, memory, link, SMIO, VDDC, VDDGFX, VDDCI, MVDD, and UVD handshake definitions.

`enum SMU9_TABLE_ID` and `enum SMU10_TABLE_ID` enumerate generation-specific table IDs used by transfer-manager paths. SMU9 has PP, watermark, AVFS, tools, and AVFS fuse tables; SMU10 has watermark and clock tables.

The declared functions cover PP table download/upload, SMC message send with or without a parameter, SCLK threshold update, SMC table update, firmware-header parsing, thermal AVFS and fan setup, SMC table initialization, graphics/memory level population, MC register table initialization, logical offset/max queries, DPM-running and hardware-AVFS presence checks, DPM-profile updates, generic SMU table manager transfer, and stopping the SMC.

## Control flow

Callers invoke `smum_*` wrappers with a `struct pp_hwmgr *`. The wrapper layer looks up the generation-specific function table installed in the hardware manager and calls the implementation if present. That lets SMU7, SMU8, SMU9, SMU10, and ASIC-specific managers provide different register sequences under a common interface.

Typical initialization flow is: initialize the SMU backend, process firmware headers to discover firmware-owned table offsets, initialize MC and DPM tables, upload the SMC table, configure thermal/fan behavior, and then service runtime updates through message sends and table updates.

## State and persistence behavior

`smumgr.h` itself stores no state. State lives in `pp_hwmgr`, its `backend`, and its `smu_backend`. The functions declared here may mutate firmware SRAM, GPU registers, DPM enable masks, software table copies, thermal/fan tables, and PowerPlay runtime profile settings.

Because the interface uses logical IDs for offsets and table updates, state persistence depends on the implementation: some updates write SMC SRAM directly; others send messages that make firmware update internal state; others populate host-side cache structures first.

## Dependencies and integration points

The header includes Linux types plus `amd_powerplay.h` and `hwmgr.h`. It integrates with every PowerPlay hardware manager that needs firmware-mediated power management. Generation-specific headers supply the message IDs and table layouts used below this abstraction.

This file is also an integration contract between policy code and firmware transport code. Policy code should use these wrappers instead of reaching into implementation-private SMU tables unless no generic operation exists.

## Risks

The abstraction returns generic `int`/`bool` values but hides generation-specific semantics. A wrapper may be implemented as a no-op or may return success even if firmware logged an error, depending on the backend. Logical member IDs can also map to different offsets across generations, so a missing `get_offsetof` case can return zero, which may look like a valid offset.

Because many APIs accept `void *` or raw table pointers, type safety is limited. Callers must know which generation and table ID they are targeting.

## Test signals

Build signals include successful compilation of all PowerPlay SMU manager implementations against this interface. Runtime signals include successful firmware-header processing, SMC message exchange, DPM table initialization, UVD/VCE table updates, fan table upload, and clean SMU stop/unload paths across supported ASIC families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/tonga_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/tonga_ppsmc.h

## Purpose

`tonga_ppsmc.h` is a Tonga/SMU7-era SMC message and flag dictionary. It defines firmware response codes, system/state flags, thermal/fan constants, DPM flags, event bits, and a large set of `PPSMC_MSG_*` command IDs used by PowerPlay managers when controlling SMC firmware.

## Important APIs, types, and constants

The file uses `#pragma pack(push, 1)` but defines no structs. `PPSMC_Result` and `PPSMC_Msg` are `uint16_t` typedefs. `PPSMC_Result_OK`, `NoMore`, `NotNow`, `Failed`, `UnknownCmd`, and `UnknownVT` encode firmware responses; `PPSMC_isERROR(x)` treats bit 7 as the error marker.

System and state flags describe DC/AC, UVD, VCE, PCIe x1, GPIO DC detection, step VDDC, GDDR5, baby-step disable, regulator-hot signals, 12-channel memory, PowerTune/DPM2 features, watermark levels, deep sleep, power boost, and power shift.

The message list spans core SMC control (`Halt`, `Resume`, forced levels), power features (CAC, TDP clamping, PowerShift, OCP), multimedia power (`UVDPowerON/OFF`, `VCEPowerON/OFF`, ACP/SAMU/SDMA/IOMMU), DPM masks and forced levels, AC/DC and VR-hot interrupts, status logging, package power limits, overdrive, fan targets, BACO, microcode load addresses/status, VBIOS load, metadata loading, telemetry calibration, and display power messages.

Event status bits identify thermal, regulator-hot, DC, and GPIO17 events.

## Control flow

The header defines command IDs only. Runtime control flow is in callers such as SMU7/Tonga/CI managers: write an optional argument, write a message ID to the SMC message register, poll the response register, then interpret the result. Higher-level flows combine messages, for example freezing DPM levels before direct table edits and unfreezing them afterward.

## State and persistence behavior

Messages change firmware and hardware state: DPM enable masks, forced levels, power-gated IP state, clock sources, fan targets, voltage overrides, logging buffers, microcode load state, and BACO monitoring state. The flags are embedded in SMC DPM tables or interpreted as status/event bits.

The header itself persists no state, but the numeric command IDs are persistent ABI. Firmware and driver must agree on these values for every boot.

## Dependencies and integration points

The header depends on integer typedefs from the including environment. It integrates with SMU7 table structures, manager implementations in `smumgr/`, and hardware managers that translate user/profile/power events into SMC commands.

It is specifically relevant to Tonga-like SMU7 firmware, but many command names are shared with other SMU7-family chips. The values must not be mixed blindly with Vega SMU9 headers, where command numbering and result widths differ.

## Risks

This header contains a dense, hand-maintained command namespace with repeated or overlapping legacy IDs in the Trinity-specific section. Sending a command ID intended for a different firmware branch can be ignored, rejected, or interpreted as a different operation.

Several commands directly affect voltage, power limits, thermal throttling, microcode loading, and power-gated blocks. A wrong argument or command sequence can hang engines or destabilize power management. Since the header does not encode argument semantics, all validation must live in callers and firmware.

## Test signals

Validation requires runtime SMC message tests on supported ASICs: DPM enable/disable, UVD/VCE power transitions, forced clock levels, fan target updates, package power limit updates, PM status logging, BACO monitor paths, and microcode load status. Kernel logs should show no `UnknownCmd`, rejected-prerequisite, or failed message responses for supported flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/tonga_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega10_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega10_ppsmc.h

## Purpose

`vega10_ppsmc.h` defines the SMU message ABI for Vega10 PowerPlay. It maps driver-visible `PPSMC_MSG_*` names to firmware command IDs, defines response codes, and records the expected SMU microcode version `0x001c0800`.

## Important APIs, types, and constants

`PPSMC_Result` is `uint16_t`; `PPSMC_Msg` is `int`. Response codes include OK, failed, unknown command, rejected prerequisite, and rejected busy. Message IDs cover SMU version/interface queries, feature enable/disable, workload and PPT limits, driver/tools DRAM address programming, table transfers, default/backup PP table selection, BTC, I2C bus arbitration, telemetry, ULV masks, VID offsets, floor SOC voltage, soft reset, BACO, low-GFX interrupt thresholds, soft min/max DPM indices, current DPM indices, average frequencies/activity, temperature sensors, overdrive, deep-sleep DCEF, AC switching, UCLK fast switch, fan targets, MP1 unload, display clock requests, DRAM logging, DIDT configuration, serial number reads, virtual DRAM addresses, ACG, current package power, PCC throttle, and package power PID alpha.

`PPSMC_Message_Count` is `0x69`, making it a useful upper bound for sanity checks in consumers.

## Control flow

No functions are present. Callers use the IDs through the SMU message transport: set argument if needed, write the message, wait for a nonzero response, and handle the response. Table-related messages pair with table IDs from `smu9_driver_if.h`.

## State and persistence behavior

The messages alter SMU firmware state such as feature masks, workload policy, power limits, PP table contents, voltage offsets, DPM bounds, fan thresholds, logging buffers, ACG state, and BACO monitoring. Some messages are queries that return values through the firmware response/argument registers rather than modifying persistent state.

## Dependencies and integration points

This header integrates with Vega10 SMU manager code, `smu9_driver_if.h` table definitions, PowerPlay profile and thermal code, and firmware that implements the listed command IDs. It must match the Vega10 firmware branch; Vega12/Vega20 headers have similar names but different numbering, extra split feature-mask commands, and sometimes different typedef widths.

## Risks

The central risk is command-number drift across SMU9 ASICs. Reusing a Vega10 ID on Vega12/Vega20 can call the wrong firmware operation. Another risk is result-width assumptions: this header uses a 16-bit result while Vega20 uses 32-bit result/message typedefs.

The header does not declare argument units. Callers must know when parameters are DPM indices, MHz, RPM, percentages, VID offsets, table IDs, or DRAM address halves. Incorrect units can be accepted by firmware but produce wrong policy.

## Test signals

Test signals include `GetSmuVersion` and `GetDriverIfVersion` success, PP table transfer success, feature-mask transitions, clock bound updates, temperature/fan queries, DRAM logging setup, display clock requests, and BACO monitor behavior on Vega10 hardware. Firmware-response logging should not show unknown or busy/rejected messages in valid sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega10_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega12/smu9_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega12/smu9_driver_if.h

## Purpose

`vega12/smu9_driver_if.h` is the Vega12-specific SMU9 driver interface. It supersedes the base SMU9 layout with interface version `0x10`, larger graphics DPM capacity, explicit feature masks, new DPM descriptor/equation formats, metrics and overdrive tables, driver configuration, and activity monitor coefficients.

## Important APIs, types, and constants

The file defines DPM array sizes for GFX, VCLK, DCLK, ECLK, MP0, UCLK, SOCCLK, DCEFCLK, DISPCLK, PIXCLK, PHYCLK, and PCIe link. Graphics DPM has 16 levels, while several display/video domains have eight levels.

`FEATURE_*_BIT` and `FEATURE_*_MASK` enumerate 32 firmware features including DPM domains, ULV, deep sleep, PPT/TDC/thermal, regulator hot, fan control, GFX EDC, GFXOFF, CG, and ACG. `DPM_OVERRIDE_*` masks describe policy links between voltage/frequency domains and GFXOFF clock switching. VR mapping, PSI selection, throttler status, workload bits, and table-transfer status constants define additional firmware ABI fields.

`PPCLK_e` names clock domains. `QuadraticInt_t`, `LinearInt_t`, and `DroopInt_t` encode firmware equations. `DpmDescriptor_t` describes voltage mode, discrete-level snapping, conversion to AVFS clock, and static-spread/AVFS curves per clock domain.

`PPTable_t` is the central packed Vega12 power table. It includes AC/DC socket power limits, TDC limits, thermal limits, FIT/PPM limits, ULV offsets, min/max voltages, DPM descriptors, frequency tables for all clock domains, DC-mode maximums, MP0 levels, graphics CKS/ACG settings, UCLK/PCIe link settings, TDPM settings, fan controls, AVFS/BTC/ageing equations, I2C sensor addresses, voltage step limits, VR mappings, telemetry calibration, GPIO/LED pins, spread-spectrum settings, VR2 address, board reserved words, and firmware padding.

Additional tables include `DriverSmuConfig_t` for LPF taus, `OverDriveTable_t` for overdrive clocks/fan/temperature limits, `SmuMetrics_t` for current clocks, averages, activity, voltage offsets, power, temperatures, throttler status, and link level, `Watermarks_t`, `AvfsDebugTable_t`, `AvfsFuseOverride_t`, and `DpmActivityMonitorCoeffInt_t`.

`TABLE_*` IDs cover PP table, watermarks, AVFS, AVFS debug, AVFS fuse override, PM status log, SMU metrics, driver config, activity monitor coefficients, and overdrive.

## Control flow

The header provides no code. Runtime flow is table-oriented: the driver builds a specific table, writes the driver DRAM address to firmware, and transfers the selected table ID. Query paths transfer SMU-owned metrics or debug tables back to DRAM. Feature enable/disable messages use the feature masks and Vega12 message IDs from `vega12_ppsmc.h`.

## State and persistence behavior

Most structures describe SMU-resident policy or telemetry. `PPTable_t`, `DriverSmuConfig_t`, `Watermarks_t`, `OverDriveTable_t`, and activity coefficients are driver-authored policy tables. `SmuMetrics_t` and AVFS debug tables are firmware-authored runtime telemetry. Data persists in firmware memory until reuploaded, overwritten by firmware, or reset.

The packed layout and reserved fields are persistent ABI. `FeaturesToRun[2]` and table IDs also persist as the firmware interpretation boundary between host policy and SMU behavior.

## Dependencies and integration points

The file integrates with Vega12 SMU manager code, `vega12_ppsmc.h` messages, PowerPlay profile/overdrive/thermal paths, display watermark programming, AVFS tooling, and metrics queries. It depends on fixed-width integer definitions from the including environment and the firmware's exact interpretation of packed structures.

## Risks

Compared with the base SMU9 interface, this file has more clock domains and more cross-domain policy. Array-size, table-ID, or feature-mask mistakes can produce wrong clock bounds, broken video/display DPM, incorrect GFXOFF behavior, or missing thermal throttling. `FeaturesToRun[2]` suggests 64-bit feature plumbing, but only 32 feature bits are defined here, so high-word behavior must match firmware expectations.

Equation and voltage fields use compact integer formats without local validation. Mis-scaled AVFS/BTC/ageing coefficients or telemetry offsets can cause unstable voltage selection. Because metrics and policy tables share transfer infrastructure, callers must not confuse read-only telemetry IDs with driver-authored upload IDs.

## Test signals

Validation should cover Vega12 interface-version negotiation, PP table upload, feature enable/disable masks, metrics table transfer, watermarks, overdrive table upload, activity monitor coefficient transfer, fan and thermal behavior, GFXOFF/ACG behavior, and all display/video clock domains. Offset/size checks against firmware headers are especially important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega12/smu9_driver_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega12_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega12_ppsmc.h

## Purpose

`vega12_ppsmc.h` defines Vega12 SMU message IDs and response codes. It is the command-number companion to `vega12/smu9_driver_if.h`, covering feature masks, table transfers, DPM frequency bounds, fan/thermal settings, GFXOFF/ACG controls, Gemini settings, BACO, and debug queries.

## Important APIs, types, and constants

`SMU_UCODE_VERSION` is `0x00270a00`. `PPSMC_Result` is `uint16_t`; `PPSMC_Msg` is `int`. Response codes include OK, failed, unknown command, rejected prerequisite, and busy.

Vega12 splits feature control into low/high allowed masks, enable masks, disable masks, and enabled-feature queries. Table-related messages include driver/tools DRAM address programming and SMU-to-DRAM/DRAM-to-SMU transfers. DPM control uses frequency-oriented commands such as `SetSoftMinByFreq`, `SetSoftMaxByFreq`, `SetHardMinByFreq`, `SetHardMaxByFreq`, `GetMinDpmFreq`, `GetMaxDpmFreq`, `GetDpmFreqByIndex`, and `GetDpmClockFreq`.

Other messages cover memory channel configuration, Gemini mode/aperture, PCIe parameters, overdrive, deep-sleep DCEF, AC/DC interrupt/power-source notification, UCLK fast switch, reset, RPM/video/fan/temperature settings, MP1 unload, DRAM logging, DIDT, display count, margin removal, serial numbers, virtual DRAM address, ACG/BTC, GFXOFF allow/disallow, PPT-limit query, and DC-mode max DPM frequency.

## Control flow

No functions are defined. The runtime pattern is the SMU message transport. Vega12 managers use these IDs with optional parameters and then poll firmware response. Table-transfer messages pair with table IDs from `vega12/smu9_driver_if.h`.

## State and persistence behavior

Messages update firmware feature state, DPM bounds, table buffers, fan/thermal targets, power limits, PCIe policy, Gemini mode, ACG/GFXOFF state, logging state, and reset/unload state. Query messages return firmware state through the message response/argument registers.

## Dependencies and integration points

The header must be used with Vega12 firmware and Vega12 table layouts. It integrates with SMU9 manager code, PowerPlay feature-mask configuration, display and thermal subsystems, overdrive paths, and BACO/reset handling.

## Risks

Many names overlap with Vega10 and Vega20 but numeric values and available messages differ. Cross-generation reuse is unsafe. Feature-control splitting into low/high words requires callers to update both halves when features exceed 32 bits; otherwise firmware state can be partially configured.

Frequency-oriented DPM commands require correct clock-domain encoding in parameters, which this header does not define. Callers must pair the message with the correct Vega12 parameter convention.

## Test signals

Test signals include successful `GetDriverIfVersion`, feature-mask programming, PP/watermark/metrics/overdrive table transfers, DPM min/max frequency queries and updates, fan/RPM messages, GFXOFF allow/disallow, ACG initialization, BACO transitions, and DC-mode max frequency queries on Vega12 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega12_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega20_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega20_ppsmc.h

## Purpose

`vega20_ppsmc.h` defines the Vega20 SMU message ABI. It is closely related to the Vega12 command set but uses 32-bit result/message typedefs and adds Vega20-specific commands for WAFL, FCLK/GFX clock ratio, debug data, XGMI mode, AFLL BTC, shutdown/reset preparation, multi-GPU fan boost, AVFS voltage query, BACO workaround, and DFC state control.

## Important APIs, types, and constants

Response codes are OK, failed, unknown command, rejected prerequisite, and busy. Both `PPSMC_Result` and `PPSMC_Msg` are `uint32_t`, which differs from Vega10/Vega12.

The command list includes version/interface queries, low/high feature masks, workload/PPT limits, DRAM address programming, table transfers, PP table selection, BTC, I2C bus arbitration, floor SOC voltage, reset/BACO, frequency min/max/hard/soft bound operations, DPM frequency queries, SS voltage by DPM, memory channel and Gemini settings, PCIe override, overdrive, AC/DC notification, UCLK switching, fan/thermal controls, MP1 unload/reset/shutdown preparation, DRAM logging, DIDT, display count, margin removal, serial reads, virtual DRAM address programming, GFXOFF allow/disallow, PPT-limit/debug/DC-frequency queries, XGMI mode, AFLL BTC, BACO workaround, and DFC state control.

`PPSMC_MSG_GfxDeviceDriverReset` is commented out at `0x3B`, documenting a reserved/removed command slot.

## Control flow

The file is a constant map only. Runtime code sends messages through the SMU transport and interprets 32-bit responses. Table-transfer commands pair with Vega20 table IDs from the corresponding SMU driver-interface header, not with the older Vega10/Vega12 definitions by assumption.

## State and persistence behavior

Messages mutate firmware-managed feature masks, clock limits, power limits, table contents, fan policy, logging, BACO/XGMI/GFXOFF state, MP1 reset/shutdown readiness, and debug/telemetry state. Some commands are query-only and return values through firmware argument registers.

## Dependencies and integration points

This header integrates with Vega20 PowerPlay/SMU manager code, high-level DPM policy, multi-GPU/XGMI handling, BACO/reset/shutdown flows, AVFS tooling, and fan/thermal management. Its 32-bit typedefs imply call sites must not assume 16-bit command/result widths.

## Risks

Cross-generation message reuse is the major risk. Vega20 removes or reserves some Vega12 commands and adds new IDs, so shared code must select the correct header through the ASIC-specific manager. The wider result/message types can also expose truncation bugs in helper functions typed for `uint16_t`.

Commands for reset/shutdown, XGMI, BACO workaround, and clock ratios are high-impact. Bad sequencing can affect multi-GPU links, low-power transitions, or firmware survivability during driver unload/reset.

## Test signals

Validation should cover version/interface queries, feature masks, PP table transfers, DPM frequency operations, debug data retrieval, XGMI mode changes, AFLL BTC, BACO entry/exit and workaround, MP1 reset/shutdown preparation, multi-GPU fan boost, AVFS voltage query, and DFC state control on Vega20 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega20_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/Makefile

## Purpose

This Makefile collects all PowerPlay SMU manager object files and appends them to `AMD_POWERPLAY_FILES`. It is the build glue that ensures the common manager plus ASIC-specific implementations are compiled into the AMDGPU PowerPlay component.

## Important APIs, types, and variables

`SMU_MGR` lists object files: `smumgr.o`, SMU8, Tonga, Fiji, Polaris10, Iceland, SMU7, Vega10, SMU10, CI, Vega12, VegaM, SMU9, and Vega20 managers. `AMD_PP_SMUMGR` prefixes each object with `$(AMD_PP_PATH)/smumgr/`. `AMD_POWERPLAY_FILES += $(AMD_PP_SMUMGR)` exports the objects to the parent build.

## Control flow

Kbuild evaluates the variable assignments during AMDGPU build setup. There is no runtime control flow. The order in `SMU_MGR` controls link input ordering but the actual runtime implementation is selected by ASIC-specific function tables and initialization code.

## State and persistence behavior

The file stores build configuration only. Its effect persists in generated object lists for the current build. It does not create runtime state.

## Dependencies and integration points

It depends on `AMD_PP_PATH` and `AMD_POWERPLAY_FILES` being defined by the surrounding PowerPlay build system. Every object named here must have a corresponding source file in `smumgr/` and must compile under the selected kernel/AMDGPU configuration.

## Risks

Missing an object silently removes a generation-specific SMU backend from the build, causing runtime ASIC initialization failures or unresolved function selection. Adding an object without the source or with unmet dependencies breaks the build. Because all managers are collected here, merge conflicts or stale entries can affect multiple ASIC families.

## Test signals

The primary test is an AMDGPU build that compiles and links PowerPlay successfully. Additional signals include module symbol availability for each manager function table and runtime probe success on ASICs represented by the listed object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c

## Purpose

`ci_smumgr.c` implements the CI/Sea Islands SMU manager backend for AMDGPU PowerPlay. It loads SMU firmware, discovers firmware table offsets, constructs SMU7 discrete DPM, voltage, fan, memory-controller, memory-timing, and power-tune tables, uploads those tables into SMC SRAM, sends SMC messages, updates runtime DPM settings, and stops/resets the SMC.

The exported integration point is `ci_smu_funcs`, a `pp_smumgr_func` table wired into the generic `smumgr.h` façade.

## Important APIs, functions, and data

The file defines device-specific `ci_pt_defaults` for Hawaii XT/PRO, Bonaire XT, and Saturn XT. These defaults seed SVI load-line, TDC, DTE, BAPM gradient, and thermal RC table fields.

Low-level SMC access helpers include `ci_set_smc_sram_address`, `ci_copy_bytes_to_smc`, `ci_read_smc_sram_dword`, `ci_program_jump_on_start`, `ci_is_smc_ram_running`, `ci_send_msg_to_smc`, and `ci_send_msg_to_smc_with_parameter`. They access SMC indirect registers, copy big-endian words into SRAM, poll responses, and manage SMC start state.

Clock/DPM population functions include `ci_calculate_sclk_params`, `ci_populate_single_graphic_level`, `ci_populate_all_graphic_levels`, `ci_calculate_mclk_params`, `ci_populate_single_memory_level`, `ci_populate_all_memory_levels`, `ci_populate_smc_link_level`, `ci_populate_smc_acpi_level`, `ci_populate_smc_uvd_level`, `ci_populate_smc_vce_level`, and `ci_populate_smc_acp_level`.

Voltage and PowerTune functions include `ci_get_dependency_volt_by_clk`, `ci_populate_smc_voltage_table`, VDDC/VDDCI/MVDD table population, ULV population, PM fuse population, BAPM parameter setup, leakage/SIDD helpers, SVI2/VR config, and PowerTune default selection.

Memory-controller support includes `ci_program_memory_timing_parameters`, `ci_initialize_mc_reg_table`, VBIOS MC table copy/translation, LP register initialization, valid-flag detection, and update/upload paths for overdrive MCLK changes.

Runtime update functions include `ci_update_sclk_threshold`, `ci_update_dpm_settings`, `ci_update_uvd_smc_table`, `ci_update_vce_smc_table`, `ci_update_smc_table`, `ci_thermal_setup_fan_table`, and offset/max query helpers.

Lifecycle functions include `ci_upload_firmware`, `ci_process_firmware_header`, `ci_init_smc_table`, `ci_smu_init`, `ci_smu_fini`, `ci_is_dpm_running`, `ci_reset_smc`, `ci_stop_smc_clock`, and `ci_stop_smc`.

## Control flow

Initialization allocates a `struct ci_smumgr` in `ci_smu_init`. Firmware processing then calls `ci_upload_firmware` if the SMC is not already running, resets/disables the SMC clock as needed, loads the firmware image into SRAM, and reads firmware header offsets for the DPM table, soft registers, MC register table, fan table, ARB timing table, and version.

`ci_init_smc_table` is the main table-construction flow. It selects PowerTune defaults, clears the cached DPM table, populates voltage tables, sets platform flags, builds ULV state, uploads graphics and memory levels, fills PCIe link, ACPI, VCE, ACP, UVD, memory timing, boot levels, initial state, BAPM, intervals, thermal limits, PCIe boot level, VR/SVI2 config, GPIOs, endian-converts scalar fields, uploads the DPM table to SRAM, initializes MC registers, uploads PM fuses, and finally starts the SMC.

Runtime profile updates freeze SCLK or MCLK DPM if enabled, patch activity/hysteresis fields directly in SMC SRAM at field offsets, and then unfreeze the DPM level. UVD/VCE table updates recalculate enable masks based on AC/DC voltage ceilings and forced-profile modes, then send SMC mask messages.

## State and persistence behavior

State is split between `hwmgr->backend` (`smu7_hwmgr` policy and DPM data), `hwmgr->smu_backend` (`ci_smumgr` cached SMU tables and firmware offsets), SMC SRAM, hardware registers, VBIOS-derived tables, and firmware runtime state. Cached tables persist until `ci_smu_fini` frees `smu_backend`, but firmware SRAM state persists independently until reset, stop, or reupload.

Many fields are endian-converted before upload because SMC firmware expects big-endian table encoding. The memory-controller table is derived from VBIOS timing data and current hardware LP registers, with only registers whose values vary across memory timing entries marked valid.

## Dependencies and integration points

The implementation depends on Linux kernel allocation/delay/types, CGS register access, AMDGPU device and PCI IDs, SMU7 table definitions, PowerPlay hardware manager state, VBIOS/ATOM control helpers, generated register headers, PCIe lane encoding, and firmware lookup through `cgs_get_firmware_info`.

It integrates upward through `ci_smu_funcs` and generic `smumgr` wrappers. It integrates downward with SMC indirect registers, SMC firmware headers, memory controller registers, clock PLL divider queries, thermal controller parameters, platform capability flags, and SMC messages from `ppsmc.h`.

## Risks

Several helpers trust table counts and firmware offsets after limited validation. Bad VBIOS dependency tables, zero clock entries, oversized MC tables, or stale firmware offsets can fail initialization or write invalid SRAM contents. The code uses many direct unit conversions and endian conversions; missing one can corrupt firmware policy.

`ci_send_msg_to_smc` logs a non-OK response but still returns `0`, so callers may treat rejected or failed firmware commands as success. Some update paths ignore return values from `smum_send_msg_to_smc*`. Direct SMC SRAM patching in `ci_update_dpm_settings` depends on exact structure offsets and field widths.

The firmware copy path rejects images larger than SMC RAM and requires a 4-byte-multiple size, but address-plus-size validation is otherwise simple. Partial-byte copy logic in `ci_copy_bytes_to_smc` preserves low bytes from the existing word, so callers must understand the byte ordering.

## Test signals

Build tests should compile the CI manager and all referenced SMU7 structures/registers. Runtime tests need CI-family hardware boot, firmware header parsing, DPM table upload, SMC start, DPM-running detection, graphics/memory level enumeration, UVD/VCE/ACP transitions, fan table upload, thermal throttling, AC/DC and PCIe behavior, suspend/resume, and driver unload/reset.

Good debug signals include no invalid SMC address messages, no firmware load size errors, no failed ATOM divider queries, no PM fuse/MC table upload failures, stable DPM masks, correct fan response, and absence of SMC unknown/failed message logs during supported flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.h

## Purpose

`ci_smumgr.h` defines the private data structures used by `ci_smumgr.c`. It captures CI-specific PowerTune defaults, memory-controller register table data, and the per-device SMU manager backend stored in `hwmgr->smu_backend`.

## Important APIs, types, and constants

The `SMU__NUM_*` macros record CI-era maximum DPM state counts for SCLK, MCLK, LCLK, and PCIe. The header includes `smu7_discrete.h`, `pp_endian.h`, and `ppatomctrl.h`, tying the private structures to SMU7 firmware layouts and VBIOS table parsing.

`struct ci_pt_defaults` stores SVI load-line defaults, TDC defaults, DTE ambient temperature base, display CAC, BAPM thermal gradient, and BAPM RC arrays sized by `SMU7_DTE_ITERATIONS * SMU7_DTE_SOURCES * SMU7_DTE_SINKS`.

`struct ci_mc_reg_entry` stores one memory-clock ceiling and the corresponding memory-controller register values. `struct ci_mc_reg_table` stores the register-address list, entry count, valid-register bitmask, and all timing entries copied and normalized from VBIOS.

`struct ci_smumgr` stores firmware-discovered offsets for soft registers, DPM table, MC register table, fan table, ARB timing table, and ULV settings; cached SMU7 DPM and PM fuse tables; selected PowerTune defaults; cached converted MC registers; and the CI MC register table.

## Control flow

This header has no runtime logic. `ci_smumgr.c` allocates `struct ci_smumgr` during SMU init, fills offsets after firmware-header parsing, populates the cached tables during SMC table initialization, and frees the structure during SMU finalization.

## State and persistence behavior

`struct ci_smumgr` is the persistent per-device software cache for the CI SMU backend. It persists for the lifetime of the hardware manager and mirrors or stages state that is also uploaded into SMC SRAM. Firmware offsets remain valid only for the loaded firmware image; cached DPM/MC/PM-fuse tables must be rebuilt or reuploaded when policy inputs change.

## Dependencies and integration points

The structures are tightly coupled to `SMU7_Discrete_DpmTable`, `SMU7_Discrete_PmFuses`, `SMU7_Discrete_MCRegisters`, ATOM MC register tables, and endian conversion helpers. They are private to the CI SMU manager but indirectly support generic `smumgr` operations through `ci_smu_funcs`.

## Risks

The `validflag` field is `uint16_t`, while `SMU7_DISCRETE_MC_REGISTER_ARRAY_SIZE` may require careful bounds discipline. If more than 16 MC registers vary, high bits cannot be represented here unless the firmware layout also limits the valid set. Firmware offsets are raw `uint32_t` values with no type distinction, so accidental use of the wrong offset field can write valid-looking data to the wrong SMC SRAM region.

Because cached tables mirror packed firmware structures, any upstream SMU7 layout change requires corresponding review of this private state.

## Test signals

Useful validation includes successful allocation/free of `smu_backend`, firmware-header offset discovery, MC table initialization from VBIOS, DPM table upload from cached `smc_state_table`, PM fuse upload from `power_tune_table`, and memory timing updates after MCLK overdrive changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.h -->
