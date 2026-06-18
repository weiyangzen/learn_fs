# subset-b-003494 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_ip_offset.h

## Purpose

`navi10_ip_offset.h` is a generated AMDGPU ASIC address-map header for Navi 10/DCN 2.0 class hardware. It does not implement behavior; it publishes immutable base offsets for hardware IP blocks so display and SOC15 register-access code can translate block-relative register offsets into concrete MMIO addresses.

The file is guarded by `_navi10_ip_offset_HEADER`, defines `MAX_INSTANCE` as 6 and `MAX_SEGMENT` as 6, then provides both structured `IP_BASE` tables and flattened `*_BASE__INSTn_SEGm` macros. The source is data-only but high impact because these constants decide which hardware block a register read or write reaches.

## Important APIs, Types, And Data

The public C data model is:

- `struct IP_BASE_INSTANCE`, containing `unsigned int segment[MAX_SEGMENT]`.
- `struct IP_BASE`, containing `struct IP_BASE_INSTANCE instance[MAX_INSTANCE]`, marked `__maybe_unused` so generated constants can be included by multiple consumers without warnings.

The static `IP_BASE` tables describe Navi 10 block bases for `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `DCN_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `RSMU_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, and `VCN_BASE`. The data is mostly instance 0 with zero-filled unused instances. Notable populated segment groups include `CLK_BASE` with six segment offsets, `DCN_BASE` with four display offsets, `GC_BASE` with two graphics/SDMA-facing offsets, `NBIO_BASE` with four NBIO segments, `SMUIO_BASE` with two segments, and `VCN_BASE` with two codec segments.

Every table is mirrored by macro constants like `DCN_BASE__INST0_SEG0`, `CLK_BASE__INST0_SEG5`, or `VCN_BASE__INST0_SEG1`. These macros are useful for register list initializers or preprocessor-style access patterns where the structured table is not used directly.

## Control Flow

There is no runtime control flow in this header. The effective flow is inclusion-time:

1. A Navi 10 display component includes the header.
2. Code chooses an IP table or flattened macro for the relevant hardware block.
3. Register access helpers combine a base segment with a block-local register offset.
4. The resulting MMIO address is read, written, polled, or added to a register list.

Direct includes in this tree include DCN 2.0 resource, GPIO, IRQ, and clock manager code: `display/dc/resource/dcn20/dcn20_resource.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`.

## State And Persistence Behavior

The header stores immutable compile-time data. It owns no runtime state, no locks, no allocation, and no persistence path. The stateful effect occurs in consumers: once these constants are compiled into the driver, display and power-management code use them to access persistent hardware registers until reset, suspend/resume reinitialization, or module unload.

Because the constants become part of the kernel image, a wrong base address persists as a driver-hardware ABI error for every Navi 10 device using that code path.

## Dependencies

The file depends on kernel/compiler definitions for `__maybe_unused` and on AMDGPU/SOC15 register access conventions that interpret IP block bases and segment indices. It is intended to be included with generation-specific register offset and mask headers under `include/asic_reg/`, plus display code that knows the Navi 10/DCN 2.0 hardware layout.

It shares generic names such as `struct IP_BASE` and `ATHUB_BASE` with other ASIC offset headers. Consumers normally include one ASIC offset header per translation unit to avoid symbol/name collisions.

## Integration Points

Primary integration is with the DCN 2.0 display stack: resource construction, GPIO factory setup, IRQ service registration, and clock manager SMU/register access. The `DCN_BASE`, `CLK_BASE`, `MP0_BASE`, `MP1_BASE`, `SMUIO_BASE`, `THM_BASE`, and `VCN_BASE` entries are especially relevant to display bring-up, clock/thermal programming, and multimedia/display block access.

The header also aligns with sibling ASIC offset headers such as `navi12_ip_offset.h`, `navi14_ip_offset.h`, and `renoir_ip_offset.h`. Shared display code assumes the table/macro naming scheme is stable while each ASIC-specific file supplies the correct address map.

## Risks

The main risk is silent MMIO misaddressing. A single incorrect populated segment can make a valid register macro access the wrong hardware aperture, causing display bring-up failures, clock programming errors, interrupt issues, or hard-to-debug hangs while polling status bits.

Zero-filled entries are ambiguous unless the caller knows the hardware map. Zero can mean an absent instance/segment, but some blocks legitimately start near low offsets. Code must rely on the known table shape rather than scanning for nonzero values without context.

The generic symbol names create compile-time collision risk if more than one `*_ip_offset.h` file is included into the same C file. Changes to `MAX_INSTANCE` or `MAX_SEGMENT` are also risky because consumers and generated macro sets assume the exact instance/segment cardinality.

## Test Signals

Strong signals are successful build coverage of all DCN 2.0 consumers, followed by hardware probe on Navi 10 with display enabled. Runtime validation should include DCN resource creation, display modeset, GPIO/DDC detection, IRQ delivery, clock manager initialization, suspend/resume, and register dumps that confirm known DCN, CLK, SMUIO, THM, VCN, and NBIO addresses resolve as expected.

Failures commonly surface as MMIO read/write faults, timeouts while polling display or SMU registers, missing hotplug/IRQ events, bad clock reporting, or display modeset failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi12_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi12_ip_offset.h

## Purpose

`navi12_ip_offset.h` is a generated AMDGPU IP base-offset table for Navi 12 hardware. It gives the driver a compile-time map from hardware IP block, instance, and segment to MMIO base addresses. Like the other `*_ip_offset.h` files, it contains no executable logic; its purpose is to make register offset composition deterministic for ASIC-specific display and SOC15 code.

The file uses `_navi12_ip_offset_HEADER`, `MAX_INSTANCE` 7, and `MAX_SEGMENT` 5. The larger instance count and different segment count distinguish it from Navi 10 and reflect Navi 12's generated address map.

## Important APIs, Types, And Data

The exported types are the same generated pair used by sibling files:

- `struct IP_BASE_INSTANCE { unsigned int segment[MAX_SEGMENT]; }`
- `struct IP_BASE { struct IP_BASE_INSTANCE instance[MAX_INSTANCE]; } __maybe_unused`

The static base tables cover `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `DIO_BASE`, `DMU_BASE`, `DPCS_BASE`, `FUSE_BASE`, `GC_BASE`, `HDA_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIF0_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `USB0_BASE`, and `UVD0_BASE`.

The flattened macro API follows `BLOCK_BASE__INSTn_SEGm`. Navi 12 has several nontrivial mappings: `CLK_BASE` has populated offsets across instances 0 through 5, `MP0_BASE` and `MP1_BASE` use distinct firmware/management apertures, `NBIF0_BASE` and `PCIE0_BASE` are separate tables, `SDMA_BASE` has populated values for instance 0 and instance 1, and `UMC_BASE` has four populated memory-controller instances. Display-related `DMU_BASE` and `DPCS_BASE` share the same populated segment list.

## Control Flow

There are no functions, branches, callbacks, or initialization routines in this file. Consumers include the header and use the constants during register-address calculation. The operational flow is:

1. ASIC-specific code selects the Navi 12 address-map header.
2. Register helper macros or register-list initializers reference `*_BASE` tables or `*_BASE__INSTn_SEGm` macros.
3. The selected segment base is added to a register-local offset.
4. The computed MMIO address is used for hardware programming, polling, or diagnostics.

Unlike `navi10_ip_offset.h` and `renoir_ip_offset.h`, a direct include of `navi12_ip_offset.h` was not found under `drivers/gpu/drm/amd` in this snapshot. That suggests it is either retained as generated ASIC data for conditional/out-of-tree users, included through build variants not present in the searched files, or available for future/partial Navi 12 enablement.

## State And Persistence Behavior

The file contributes immutable constants compiled into any consumer. It has no mutable software state and no persistence. The hardware state affected by consumers is persistent MMIO state: display, clock, PCIe/NBIF, firmware-management, SDMA, UVD, USB/HDA, and memory-controller registers remain programmed until reset, power gating, suspend/resume, or driver teardown.

If a consumer starts using this header, the constants become part of the runtime hardware ABI for Navi 12.

## Dependencies

The only syntactic dependency is the kernel's `__maybe_unused` annotation. Practical dependencies are AMDGPU SOC15/MMIO register helper conventions, matching register offset/mask headers for the hardware blocks being addressed, and ASIC selection logic that ensures this Navi 12 map is not used on a different GPU.

The file shares global names such as `CLK_BASE`, `GC_BASE`, and `struct IP_BASE` with other ASIC headers, so it should not be mixed with sibling `*_ip_offset.h` headers in one translation unit.

## Integration Points

Potential integration points are Navi-family display resource code, GPIO/IRQ setup, SMU/clock code, SDMA and memory-controller setup, and register dump tooling. The table contents line up with the broader AMDGPU generated-register scheme: `NBIF0_BASE`/`PCIE0_BASE` for bus registers, `DMU_BASE`/`DPCS_BASE`/`DIO_BASE` for display, `MP0_BASE`/`MP1_BASE` for management processors, and `UVD0_BASE`/`SDMA_BASE` for media and DMA engines.

The lack of direct in-tree includes is itself an integration signal: changes here may not be compile-tested unless a specific Navi 12 path includes it or broader generated-header validation is run.

## Risks

Address-map errors can compile cleanly and fail only on hardware. Incorrect `MP0_BASE` or `MP1_BASE` values can break firmware mailbox or SMU interactions; bad `PCIE0_BASE` or `NBIF0_BASE` values can corrupt bus configuration; wrong `DMU_BASE`/`DPCS_BASE` values can break display timing or link programming; incorrect `UMC_BASE` instances can affect memory-controller diagnostics or RAS flows.

Because no direct consumer was found, drift risk is higher: the file may not receive normal compile or boot coverage. The generated table must remain synchronized with hardware documentation and with any code that eventually selects it.

## Test Signals

Best signals are a build target that includes this header, static checks for duplicate `struct IP_BASE` inclusion conflicts, and Navi 12 hardware smoke tests. Runtime signals should include successful GPU probe, register readback sanity for each populated block, display modeset, clock/SMU initialization, SDMA ring tests, UVD/media ring tests, PCIe/NBIF diagnostics, suspend/resume, and memory-controller/RAS readouts where applicable.

For a currently unused header, a useful guard is generated-data comparison against the authoritative register database plus a compile-only consumer that verifies the table and macro names remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi12_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi14_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi14_ip_offset.h

## Purpose

`navi14_ip_offset.h` is the generated MMIO base-offset map for Navi 14 hardware. It publishes IP block base addresses as fixed C tables and preprocessor macros so AMDGPU register helpers can address the correct ASIC-specific aperture.

The header has the same overall format as `navi12_ip_offset.h`: include guard `_navi14_ip_offset_HEADER`, `MAX_INSTANCE` 7, `MAX_SEGMENT` 5, `IP_BASE` structures, static base tables, and flattened `BLOCK_BASE__INSTn_SEGm` constants. Its value is the Navi 14-specific address map, not executable logic.

## Important APIs, Types, And Data

The public types are:

- `struct IP_BASE_INSTANCE`, an array of five segment offsets.
- `struct IP_BASE`, an array of seven instances, marked `__maybe_unused`.

The header defines static tables for `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `DIO_BASE`, `DMU_BASE`, `DPCS_BASE`, `FUSE_BASE`, `GC_BASE`, `HDA_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIF0_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `USB0_BASE`, and `UVD0_BASE`.

Important Navi 14-specific details include populated display tables for `DMU_BASE` and `DPCS_BASE`, multiple clock table instances, two populated `SDMA_BASE` instances, and memory-controller entries under `UMC_BASE`. Compared with Navi 12, this file maps `MP1_BASE` the same way as `MP0_BASE`, and `PCIE0_BASE` mirrors the `NBIF0_BASE` segment set instead of the separate PCIe aperture used by Navi 12. Those differences are exactly the kind of ASIC-specific variation this header preserves.

## Control Flow

The file has no runtime control flow. It participates in compile-time address selection:

1. A Navi 14 consumer includes the header.
2. The consumer references an `IP_BASE` table or flattened macro for a hardware block.
3. SOC15/display register helpers combine that base with register-local offsets and base indices.
4. Hardware accesses use the resulting address for initialization, reset, clocking, display, media, bus, or diagnostics.

No direct in-tree include of `navi14_ip_offset.h` was found in the searched AMDGPU sources. The header therefore appears to be generated support data that may be used by build configurations, future code, or out-of-tree/platform-specific paths not visible in this source snapshot.

## State And Persistence Behavior

The constants are immutable and compiled into any object that includes the header. The file itself does not allocate memory, mutate driver state, read firmware, or persist settings. Its state impact is indirect: every register programmed through these constants changes hardware state that may last until reset, power-gating transitions, suspend/resume, or driver teardown.

## Dependencies

The file relies on kernel/compiler support for `__maybe_unused` and on AMDGPU register-access conventions that know how to use the base arrays. Correct operation also depends on matching ASIC selection, matching offset/mask headers, and avoiding inclusion of multiple ASIC offset headers with conflicting generic names in one translation unit.

## Integration Points

Potential consumers are the same AMDGPU layers that consume sibling Navi headers: display resource and GPIO code, IRQ services, clock/SMU code, SDMA/media setup, PCIe/NBIF code, RAS or diagnostics, and register dump tooling. Even without a direct include in this tree, its shape matches the generated interface used by DCN and SOC15 code.

The file integrates conceptually with `navi12_ip_offset.h`: both share many block names and segment patterns, but key MP1 and PCIe/NBIF differences mean substituting one for the other would be unsafe.

## Risks

The dominant risk is hardware misprogramming from a wrong base value or accidentally using the Navi 14 table for a different ASIC. Because register helpers hide address arithmetic, many errors would not be caught by the compiler. Display blocks (`DMU_BASE`, `DPCS_BASE`, `DIO_BASE`), management blocks (`MP0_BASE`, `MP1_BASE`), bus blocks (`NBIF0_BASE`, `PCIE0_BASE`), and memory-controller blocks (`UMC_BASE`) are especially sensitive.

The absence of direct includes in this snapshot means normal builds may not catch syntax drift, renamed tables, or generated-data mistakes. The generic symbol names also make multi-ASIC inclusion in a single C file risky.

## Test Signals

Useful test signals include compile coverage from a Navi 14-specific consumer, generated-data comparison against the authoritative hardware database, and real Navi 14 probe tests. Runtime validation should exercise display modeset and hotplug, clock/SMU register access, SDMA ring tests, UVD/media ring tests, PCIe/NBIF readback, memory-controller diagnostics, and suspend/resume.

Any timeout while polling display, SMU, SDMA, UVD, or bus status registers after selecting this map is a strong signal to inspect the affected base table and segment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi14_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/pptable.h

## Purpose

`pptable.h` defines the packed ATOMBIOS PowerPlay table ABI used by AMDGPU legacy power-management code. It is not an algorithmic implementation; it is a binary layout contract for parsing firmware-provided performance, voltage, thermal, fan, PCIe, multimedia, and platform power data.

The file uses `_PPTABLE_H` and wraps all definitions in `#pragma pack(1)`, then restores packing with `#pragma pack()`. That packing is central: most structures map directly onto byte streams read from BIOS tables.

## Important APIs, Types, And Data

Major exported structure families:

- Thermal and fan metadata: `ATOM_PPLIB_THERMALCONTROLLER`, `ATOM_PPLIB_FANTABLE` through `ATOM_PPLIB_FANTABLE5`, and controller constants such as `ATOM_PP_THERMALCONTROLLER_*` plus fan parameter flags.
- Main PowerPlay table revisions: `ATOM_PPLIB_POWERPLAYTABLE`, `ATOM_PPLIB_POWERPLAYTABLE2`, `ATOM_PPLIB_POWERPLAYTABLE3`, `ATOM_PPLIB_POWERPLAYTABLE4`, and `ATOM_PPLIB_POWERPLAYTABLE5`. Later versions extend earlier versions by embedding the previous version as `basicTable*` and adding offsets or power fields.
- Extended offsets: `ATOM_PPLIB_EXTENDEDHEADER` points to VCE, UVD, SAMU, PPM, ACP, PowerTune, SCLK/VDDGFX dependency, and VQ budgeting subtables.
- State and non-clock descriptors: `ATOM_PPLIB_STATE`, `ATOM_PPLIB_STATE_V2`, `StateArray`, `ClockInfoArray`, `NonClockInfoArray`, `ATOM_PPLIB_NONCLOCK_INFO`, and `ATOM_PPLIB_THERMAL_STATE`.
- ASIC clock formats: `ATOM_PPLIB_R600_CLOCK_INFO`, `ATOM_PPLIB_RS780_CLOCK_INFO`, `ATOM_PPLIB_EVERGREEN_CLOCK_INFO`, `ATOM_PPLIB_SI_CLOCK_INFO`, `ATOM_PPLIB_CI_CLOCK_INFO`, `ATOM_PPLIB_SUMO_CLOCK_INFO`, `ATOM_PPLIB_KV_CLOCK_INFO`, and `ATOM_PPLIB_CZ_CLOCK_INFO`.
- Dependency and limit tables: `ATOM_PPLIB_Clock_Voltage_Dependency_*`, `ATOM_PPLIB_Clock_Voltage_Limit_*`, `ATOM_PPLIB_CAC_Leakage_*`, and `ATOM_PPLIB_PhaseSheddingLimits_*`.
- Multimedia and power subtables: VCE, UVD, SAMU, ACP, PowerTune, PPM, and VQ budgeting record/table structures.

Important macro groups include platform capabilities in `ulPlatformCaps`, non-clock classification flags, `ulCapsAndSettings` PCIe/display/video flags, R600 clock flags, RS780 voltage/sideport/HT constants, PPM design constants, and VQ display config constants.

Several structures use flexible arrays annotated with `__counted_by`, such as `ucClockStateIndices[]`, `clockInfoIndex[]`, `entries[]`, and `nonClockInfo[]`. Consumers must combine the count fields with table offsets and entry sizes rather than using `sizeof` as a complete allocation size.

## Control Flow

There is no function-level control flow in this header. The runtime flow happens in parsers:

1. AMDGPU locates an ATOMBIOS PowerPlay table and casts or copies the bytes into one of the packed `ATOM_PPLIB_POWERPLAYTABLE*` layouts.
2. The parser checks `usTableSize`, data revision, and structure size before accessing fields added by later revisions.
3. Offset fields such as `usStateArrayOffset`, `usClockInfoArrayOffset`, `usNonClockInfoArrayOffset`, `usFanTableOffset`, dependency-table offsets, and extended-header offsets are added to the base table pointer.
4. Counted arrays and entry-size fields determine how many records to walk.
5. Parsed data is translated into DPM states, voltage dependencies, fan policy, PCIe link policy, multimedia clock limits, PowerTune limits, and platform capability flags.

Direct integration found in this tree includes `include/atombios.h`, `pm/powerplay/hwmgr/processpptables.c`, and legacy DPM files such as `pm/legacy-dpm/legacy_dpm.c`, `si_dpm.c`, and `kv_dpm.c`. `legacy_dpm.c` walks clock-voltage dependency records, table revision extensions, CAC leakage, phase shedding, and other offsets defined here.

## State And Persistence Behavior

The header itself stores no mutable state. It defines how persistent firmware data is interpreted. The underlying data comes from ATOMBIOS/VBIOS and remains the platform's power-management policy source for the booted device. Driver consumers derive runtime state from it: available performance states, clock/voltage dependencies, fan curves, thermal-controller behavior, platform capability bits, PowerTune budgets, and multimedia clock constraints.

Because structures are packed ABI definitions, changing field order, width, packing, or offset semantics would change how persistent BIOS bytes are decoded and can break existing firmware tables.

## Dependencies

This header depends on ATOMBIOS scalar aliases and common table types such as `UCHAR`, `USHORT`, `ULONG`, and `ATOM_COMMON_TABLE_HEADER`, supplied through surrounding AMDGPU ATOMBIOS headers. It also depends on compiler support for packed pragmas, flexible arrays, and the kernel's `__counted_by` annotation in newer hardened builds.

Practical dependencies include all legacy PowerPlay/DPM parsers that trust these definitions, firmware/BIOS table producers that populate the same binary layouts, and any diagnostics that dump or validate PowerPlay table contents.

## Integration Points

`pptable.h` is included from `atombios.h`, making its ABI visible to broader AMDGPU ATOMBIOS consumers. It is directly used by legacy PowerPlay and DPM parser code to build runtime power states. `processpptables.c` is a central integration point for parsing PowerPlay tables, while `legacy_dpm.c`, `si_dpm.c`, and `kv_dpm.c` consume specific revisions and dependency tables.

The table contents feed clock selection, voltage control, fan and thermal handling, PCIe link choices, multimedia engine limits, PowerTune enforcement, and OverDrive-style maximum clock reporting. Bugs here therefore cross module boundaries between firmware parsing, power management, thermal control, display/video capabilities, and hardware bring-up.

## Risks

The highest risk is ABI drift. `#pragma pack(1)` is required; removing or changing it would alter offsets and corrupt parsing. Extending structures without updating size checks, offsets, and revision handling can make old BIOS tables appear to contain fields that are not present. Flexible arrays and offset-based subtables require strict bounds checking because the data source is firmware-provided bytes.

Integer unit mistakes are also risky. The file mixes units such as 10 kHz-style split clock fields, MHz comments for older tables, milliwatts, centigrade hundredths, PWM hundredths of a percent, and milliohm scaled values. Misinterpreting a field can cause unstable clocks, unsafe voltage decisions, bad fan response, or incorrect power caps.

The use of nested versioned structures (`POWERPLAYTABLE2` through `5`) creates compatibility risk: consumers must check `usTableSize` before touching later fields such as dependency offsets, CAC leakage, TDP limits, and load-line slope. Count fields and entry-size fields must be trusted only after validating that the computed range stays inside the table.

## Test Signals

Compile tests should cover legacy DPM and PowerPlay parsers with packed layout warnings enabled. Runtime signals include successful parsing of known VBIOS PowerPlay tables across R600, RS780, Evergreen, SI, CI, Sumo, Kaveri, and Carrizo-era devices; correct DPM state enumeration; valid fan table loading; sane voltage dependency tables; and stable PowerTune limits.

Negative tests should feed truncated or malformed tables and verify that parsers reject out-of-bounds offsets and impossible counts. Hardware signals include stable boot clocks, DPM transitions, suspend/resume, thermal response, PCIe link changes, UVD/VCE/ACP/SAMU clock constraints, and absence of overclock/OverDrive limit regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/renoir_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/renoir_ip_offset.h

## Purpose

`renoir_ip_offset.h` is the generated AMDGPU IP base-offset map for Renoir APU/DCN 2.1 hardware. It supplies compile-time MMIO base addresses for display, multimedia, management, bus, audio, USB, memory-controller, and related blocks. Consumers use these constants to compose correct register addresses for Renoir-specific driver paths.

The header uses `_renoir_ip_offset_HEADER`, `MAX_INSTANCE` 7, and `MAX_SEGMENT` 5. It follows the same `IP_BASE` table plus flattened macro pattern used by other AMDGPU ASIC offset headers, but its block list is broader than Navi 10 because Renoir is an APU-oriented map.

## Important APIs, Types, And Data

The exported generated types are:

- `struct IP_BASE_INSTANCE`, containing five segment entries.
- `struct IP_BASE`, containing seven instances and marked `__maybe_unused`.

Static base tables include `ACP_BASE`, `ATHUB_BASE`, `CLK_BASE`, `DBGU_IO0_BASE`, `DF_BASE`, `DIO_BASE`, `DMU_BASE`, `DPCS_BASE`, `FUSE_BASE`, `GC_BASE`, `HDA_BASE`, `HDP_BASE`, `IOHC0_BASE`, `ISP_BASE`, `L2IMU0_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIF0_BASE`, `DCN_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA0_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `USB0_BASE`, and `UVD0_BASE`.

The flattened macro set follows `BLOCK_BASE__INSTn_SEGm` through the declared seven-by-five matrix. Notable populated areas include APU peripherals (`ACP_BASE`, `HDA_BASE`, `USB0_BASE`, `ISP_BASE`), display blocks (`DIO_BASE`, `DMU_BASE`, `DPCS_BASE`, `DCN_BASE`), management processor windows (`MP0_BASE`, `MP1_BASE`), IO fabric (`IOHC0_BASE`, `L2IMU0_BASE`, `NBIF0_BASE`, `PCIE0_BASE`), and two populated `UMC_BASE` instances.

## Control Flow

This file has no functions or runtime branches. Its operational flow is:

1. Renoir-specific display or DMUB code includes the header.
2. The code references base tables or flattened macros while building register addresses.
3. Register helpers add the base to block-relative offsets from matching register headers.
4. The driver programs display clocks, GPIO, IRQs, DMUB/DCN resources, VBIOS SMU access, or other hardware state.

Direct includes found in this tree include `display/dmub/src/dmub_dcn21.c`, `display/dc/resource/dcn21/dcn21_resource.c`, `display/dc/gpio/dcn21/hw_factory_dcn21.c`, `display/dc/gpio/dcn21/hw_translate_dcn21.c`, `display/dc/irq/dcn21/irq_service_dcn21.c`, `display/dc/clk_mgr/dcn21/rn_clk_mgr.c`, and `display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c`.

## State And Persistence Behavior

The header contributes immutable constants only. It owns no dynamic state and performs no persistence. The stateful consequences occur through consumers that program hardware registers using these bases: display resources, GPIO/DDC lines, IRQ routing, clock manager state, DMUB interactions, SMU/VBIOS mailbox access, audio/USB/ACP/ISP-related registers, and memory/bus diagnostics can all depend on correct offsets.

The compiled constants persist for the lifetime of the loaded driver and define the Renoir hardware address contract for those consumers.

## Dependencies

The syntactic dependency is `__maybe_unused`. Operational dependencies are AMDGPU DCN 2.1 and DMUB code, SOC15-style register helpers, generation-matched register offset/mask headers, and ASIC detection that selects Renoir paths only for compatible devices.

Because this header defines generic symbols such as `CLK_BASE`, `MP0_BASE`, and `struct IP_BASE`, translation units should avoid including multiple ASIC IP-offset headers together unless names are isolated.

## Integration Points

The strongest integration points are DCN 2.1 resource construction, GPIO factory/translation, IRQ service setup, Renoir clock manager code, VBIOS SMU access, and DMUB support. `DCN_BASE`, `DMU_BASE`, `DPCS_BASE`, `DIO_BASE`, `CLK_BASE`, `MP0_BASE`, `MP1_BASE`, `SMUIO_BASE`, and `THM_BASE` are directly relevant to display bring-up and power/clock control. APU-specific tables such as `ACP_BASE`, `HDA_BASE`, `USB0_BASE`, and `ISP_BASE` reflect integration with non-discrete GPU peripherals.

The file also aligns with sibling generated maps such as `navi12_ip_offset.h` and `navi14_ip_offset.h`, but Renoir has distinct low and high fabric/peripheral segments that should not be substituted across ASICs.

## Risks

Incorrect Renoir base offsets can break core user-visible display behavior. Bad display bases can cause modeset, GPIO/DDC, hotplug, IRQ, or DMUB failures. Bad `MP0_BASE`/`MP1_BASE` values can break SMU or firmware mailbox access. Bad APU peripheral bases can affect audio, USB, ACP, or ISP-related paths if consumers use those entries.

The file includes both `DCN_BASE` and display-adjacent `DMU_BASE`/`DPCS_BASE` tables with overlapping-looking segment values. Consumers must choose the intended block constant; using a similarly named table from another generation can compile but target the wrong address. Zero placeholders remain a risk for code that treats nonzero as the only validity criterion without understanding the table.

## Test Signals

Useful validation starts with compile coverage of DCN 2.1, Renoir clock manager, DMUB, GPIO, and IRQ consumers. Hardware signals include Renoir probe, display modeset on internal and external connectors, HPD/DDC behavior, DMUB initialization, clock manager and VBIOS SMU operations, suspend/resume, audio-over-display behavior, and no timeouts while polling display, SMU, or interrupt status registers.

Register dump comparison against expected Renoir addresses for `DCN_BASE`, `CLK_BASE`, `MP0_BASE`, `MP1_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, and bus/peripheral tables is the most direct check that the map matches hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/renoir_ip_offset.h -->
