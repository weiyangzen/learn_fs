# Research: subset-b-003488

Grouped research for `subset-b-003488`. Each section preserves the source path in its title and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cyan_skillfish_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cyan_skillfish_ip_offset.h

## Purpose
This generated-style AMDGPU header provides Cyan Skillfish SOC15 register base offsets by hardware IP block, instance, and segment. It is a static address-map contract used by Cyan Skillfish register initialization and display code so common register-access macros can derive the correct per-IP base address.

## Important APIs, Types, And Data
The header defines `MAX_INSTANCE` as 6 and `MAX_SEGMENT` as 5. `struct IP_BASE_INSTANCE` contains one segment array, and `struct IP_BASE` contains the per-instance table; both are marked `__maybe_unused` to tolerate include sites that only consume flattened macros.

Static `IP_BASE` tables cover `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `DMU_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC0_BASE`, and `UVD0_BASE`. Most blocks only populate instance 0. `CLK_BASE` populates all six instances, and several blocks expose multiple segments, notably `DMU_BASE`, `NBIO_BASE`, `SMUIO_BASE`, `GC_BASE`, and `UVD0_BASE`. The bottom half mirrors the table values as `*_BASE__INSTn_SEGm` constants.

## Control Flow
There are no functions. `amdgpu/cyan_skillfish_reg_init.c` includes the table and copies selected `IP_BASE.instance` pointers into `adev->reg_offset` during ASIC register-base setup. Display DCN 2.01 code also includes it for Cyan Skillfish-specific display/clock-resource offsets.

## State And Persistence
All data is immutable compiled-in address metadata. Runtime persistence is indirect: initialized `adev->reg_offset[HWIP][instance][segment]` pointers remain the active address map for the device lifetime. This header performs no allocation, mutation, or persistent storage writes.

## Dependencies And Integration Points
The data shape is coupled to AMDGPU SOC15 register infrastructure, HWIP enum consumers, and generated register headers that expect base indices. It integrates with core AMDGPU initialization and display resource/IRQ/clock management for the Cyan Skillfish APU path.

## Risks
Incorrect offsets make register reads or writes hit the wrong hardware aperture, which can break display bring-up, SMU/MP access, memory hub programming, or GPU reset. `MAX_INSTANCE` and `MAX_SEGMENT` are local to this generated header; include sites must not assume another ASIC's dimensions. The generic `IP_BASE` type names are repeated by many offset headers, so include scope should stay narrow to avoid same-translation-unit redefinition.

## Test Signals
Build coverage of `cyan_skillfish_reg_init.c` and DCN 2.01 include sites catches symbol and type drift. Runtime signals include successful Cyan Skillfish probe, register-base initialization, display enable, SMU/clock access, MMHUB/GFX register reads, and absence of invalid-register or timeout errors during suspend/resume and reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cyan_skillfish_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/dimgrey_cavefish_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/dimgrey_cavefish_ip_offset.h

## Purpose
This generated-style header provides Dimgrey Cavefish SOC15 register base offsets by IP block, instance, and segment. It supplies the ASIC-specific address map used by AMDGPU register initialization and DCN 3.02 display code.

## Important APIs, Types, And Data
The header defines `MAX_INSTANCE` as 7 and `MAX_SEGMENT` as 6. `struct IP_BASE_INSTANCE` and `struct IP_BASE` model a rectangular table of segment base addresses. Static tables include `ATHUB_BASE`, `CLK_BASE`, `DBGU_IO0_BASE`, `DF_BASE`, `DCN_BASE`, `DPCS_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, and `VCN0_BASE`.

Dimgrey Cavefish uses a richer address map than Cyan Skillfish: most populated blocks have at least a low MMIO segment plus a high `0x024...` segment, `CLK_BASE` has seven populated instances, `DBGU_IO0_BASE` has two instances, `UMC_BASE` has four populated instances, `MP0_BASE` and `MP1_BASE` expose multiple firmware/management segments, and `NBIO_BASE` has six non-zero segments. The second half of the header exposes flattened `*_BASE__INSTn_SEGm` macros for compile-time uses.

## Control Flow
There is no executable control flow. `amdgpu/dimgrey_cavefish_reg_init.c` includes the header to populate `adev->reg_offset`. DCN 3.02 IRQ/resource/dmub code includes it to bind display and DMUB logic to Dimgrey Cavefish register apertures.

## State And Persistence
The header is immutable data only. After device initialization, pointers or copied offsets derived from it persist in the AMDGPU device's register-offset tables for the lifetime of the device. The header itself owns no runtime state.

## Dependencies And Integration Points
It is coupled to SOC15 HWIP indexing, generated register accessors, Dimgrey Cavefish ASIC init, DCN 3.02 resource construction, IRQ service setup, and DMUB support. The names `DCN_BASE`, `DPCS_BASE`, and `VCN0_BASE` are important integration points for display and media IP setup.

## Risks
Address-map drift is high impact: a wrong segment can silently program the wrong IP block, especially for high MMIO segments, UMC instances, or NBIO/MP management apertures. Consumers must honor this header's 7x6 dimensions and cannot reuse assumptions from ASICs with 6x5, 8x6, or other generated shapes. Reusing the generic `IP_BASE` names in broad include scopes risks type-name collisions with other offset headers.

## Test Signals
Build `dimgrey_cavefish_reg_init.c`, DCN 3.02 resource/IRQ paths, and DMUB support. Runtime checks should cover probe, display mode-set, HPD/AUX interrupts, VCN register access, UMC status reads, NBIO/PCIe access, clock/SMU access, suspend/resume, and GPU reset without register timeout or invalid aperture diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/dimgrey_cavefish_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/discovery.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/discovery.h

## Purpose
This header defines AMDGPU's packed firmware discovery-table ABI. It describes PSP discovery binaries, per-die IP discovery records, harvested-IP metadata, graphics-core capability tables, VCN feature fuses, MALL information, and NPS memory-partition ranges.

## Important APIs, Types, And Data
Top-level constants identify binary and table signatures: `BINARY_SIGNATURE`, `DISCOVERY_TABLE_SIGNATURE`, `GC_TABLE_ID`, `HARVEST_TABLE_SIGNATURE`, `VCN_INFO_TABLE_ID`, `MALL_INFO_TABLE_ID`, and `NPS_INFO_TABLE_ID`. `enum table` indexes the legacy fixed table list.

`struct table_info`, `struct binary_header`, and `struct binary_header_v2` describe discovery binary layout. V2 adds `num_tables` and a counted flexible `table_list`. `struct ip_discovery_header` describes the IP table, including per-die offsets and a version-4 flag that tells consumers whether IP base addresses are 64-bit. `struct ip`, `struct ip_v3`, and `struct ip_v4` represent versioned IP entries with flexible base-address arrays and endian-sensitive bitfields for harvest/variant/sub-revision.

`struct gc_info_v1_0` through `gc_info_v2_1` record graphics topology and cache parameters. `harvest_table` records disabled IP instances. `mall_info_v1_0` and `mall_info_v2_0` report MALL capacity/configuration. `vcn_info_v1_0` reports per-instance codec-disable fuse bits. `nps_info_v1_0` reports NPS type and up to twelve base/limit address ranges.

## Control Flow
This file has no functions, but its layout drives `amdgpu_discovery.c`. That code validates the binary, locates table offsets, walks dies and IP entries, interprets 32-bit versus 64-bit base arrays, applies harvest data, and imports GC/MALL/VCN/NPS records into `adev` capability structures.

## State And Persistence
The structures are views over firmware-provided binary data. Parsed values persist in `adev->discovery`, IP-version tables, harvest masks, graphics topology, video capabilities, MALL properties, and NPS ranges. The header itself has no mutable state, but its packed field layout is persistent ABI with PSP/discovery firmware.

## Dependencies And Integration Points
It relies on fixed-width integer types, `DECLARE_FLEX_ARRAY`, `__counted_by`, `#pragma pack(1)`, and endian macros. Integration is centered on `amdgpu/amdgpu_discovery.c`, which consumes these records during probe and uses the result to select IP block implementations, register bases, feature masks, and topology-dependent resource limits.

## Risks
Packing, flexible-array sizing, and endian-sensitive bitfields are critical. A wrong field size or version branch can mis-parse firmware data, causing missing IP blocks, wrong register bases, incorrect harvest masks, or unsafe feature enablement. `binary_header_v2` has a variable table count, so validation must bound offsets and sizes before dereferencing. `ip_v4` can hold either 32-bit or 64-bit base addresses depending on the discovery header flag; treating it as the wrong width corrupts iteration.

## Test Signals
Test with discovery binaries across legacy header, V2 header, IP table versions, single-die and multi-die devices, 32-bit and 64-bit base-address modes, harvested configurations, and GC/MALL/VCN/NPS table variants. Probe logs, `amdgpu_discovery` debug output, IP block versions, harvested instance masks, register-base setup, VCN codec exposure, and memory-partition reporting are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/discovery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/displayobject.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/displayobject.h

## Purpose
This SoC15 display-object header defines BIOS-shared numeric object IDs for GPUs, encoders, and connectors. These values encode object type, enum instance, and object kind into a compact integer used by AtomBIOS/display topology records.

## Important APIs, Types, And Data
`enum display_object_type` distinguishes none, GPU, encoder, and connector objects. `enum encoder_object_type` identifies internal UNIPHY encoder variants. `enum connector_object_type` covers single-link DVI-D, dual-link DVI-D, HDMI type A, LVDS, DisplayPort, eDP, and OPM. `enum object_enum_id` provides enum IDs 1 through 6.

`enum object_id_bit` defines masks and shifts: low 8 bits for object ID, bits 8-11 for enum ID, and bits 12-15 for object type. `GPU_ENUM_ID1`, the `ENCODER_INTERNAL_UNIPHY*` entries, and connector definitions such as `CONNECTOR_DISPLAYPORT_ENUM_ID1` through `CONNECTOR_DISPLAYPORT_ENUM_ID4` are composed with these shifts. OPM connector IDs map enum IDs to MXM DP/LVDS paths in comments.

## Control Flow
There are no functions. Consumers compare or decompose object IDs while parsing BIOS display path records, encoder records, connector records, and board-specific routing data.

## State And Persistence
The header is a constants-only ABI. The values persist in firmware tables and in parsed display topology state, but this file owns no runtime state or storage.

## Dependencies And Integration Points
It conditionally applies `#pragma pack(1)` for `_X86_`, matching BIOS-shared structure conventions. It overlaps conceptually with `amdgpu/ObjectID.h`, but this file is the SoC15-specific display-object definition. Integration points are AtomBIOS display parsing, connector enumeration, encoder mapping, and board topology handling.

## Risks
Changing any numeric value breaks compatibility with firmware object tables. The bit layout is small and rigid; adding new object IDs or enum IDs requires preserving mask/shift semantics. The header has legacy typos in enum names such as `objet`, so external code should use existing spellings rather than "correcting" them without a tree-wide migration.

## Test Signals
Build display BIOS parser paths and test systems with DVI, HDMI, LVDS/eDP, DisplayPort, and MXM/OPM mappings. Runtime signals include correct connector naming, HPD routing, encoder selection, link training, and absence of unknown-object diagnostics while parsing AtomBIOS tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/displayobject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/dm_pp_interface.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/dm_pp_interface.h

## Purpose
This header defines the display-manager to PowerPlay/SMU interface for display configuration and clock requirements. It is the shared contract by which display code reports active displays, timing constraints, and requested clocks to AMDGPU power-management implementations.

## Important APIs, Types, And Data
`PP_MAX_CLOCK_LEVELS` and `MAX_NUM_CLOCKS` are both 16; `MAX_NUM_DISPLAY` is 32. `enum amd_pp_display_config_type` classifies link/display modes such as DP link rates, HDMI rates, LVDS, DVI, wireless, and VGA.

`struct single_display_configuration` records one display path: controller IDs, signal type, display state, primary and secondary transmitter PHY/lane maps, flags, display type, resolution, refresh, and pixel clock. `struct amd_pp_display_configuration` aggregates policy flags and derived limits such as NB pstate disable, CPU C-state/P-state constraints, display counts, minimum memory/core/bus clocks, vblank/line timing, multi-monitor sync state, DCEF/DC clock requirements, and up to 32 display records.

Clock query/request structures include `amd_pp_simple_clock_info`, `amd_pp_clock_info`, `amd_pp_clocks`, `pp_clock_levels_with_latency`, `pp_clock_levels_with_voltage`, and `pp_display_clock_request`. `enum PP_DAL_POWERLEVEL` and `enum amd_pp_clock_type` define power-level and clock-domain selectors; `amd_pp_f_clock` aliases `amd_pp_dcef_clock`.

## Control Flow
This header has no code. Display code fills configuration and clock-request structures, then DPM/PowerPlay/SMU functions consume them to set display clocks, memory clock constraints, stutter/deep-sleep policy, DCEF/DCF/DPP/SOC clocks, and latency-aware power states.

## State And Persistence
The primary persistent state is `adev->pm.pm_display_cfg` and SMU/PowerPlay display configuration copies. Values persist across display updates until replaced by a new configuration. Clock level arrays are bounded fixed-size buffers, avoiding dynamic allocation in this ABI.

## Dependencies And Integration Points
It includes `dm_services_types.h` for common display-manager types. Integration points include `amdgpu_dpm_internal.c`, legacy DPM, PowerPlay hardware managers, SW SMU, `kgd_pp_interface.h`, `amdgpu_dm_pp_smu.c`, and display mode-set paths that request clock changes.

## Risks
Units are mixed and must be preserved: pixel/display clocks are in kHz, some bandwidth/core-clock fields are in 10 kHz-derived units, and latencies are in microseconds. `MAX_NUM_DISPLAY`, `PP_MAX_CLOCK_LEVELS`, and `MAX_NUM_CLOCKS` require caller-side bounds checks. Incorrect `multi_monitor_in_sync`, vblank, or line-time data can choose unsafe memory-clock switching behavior and cause display underflow or hangs.

## Test Signals
Exercise single-monitor, multi-monitor synchronized and unsynchronized, HDMI, DP, eDP/LVDS, high refresh, deep-sleep, stutter, and memory-clock switching cases. Validate DPM/SMU logs, clock requests, underflow counters, suspend/resume behavior, and mode-set stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/dm_pp_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h

## Purpose
This header defines DCN 1.0 display interrupt source IDs and context IDs for AMDGPU's interrupt handler and display IRQ services. It maps a broad set of DCN display events to the numeric `src_id`/`context_id` values emitted through the SOC15 IH path.

## Important APIs, Types, And Data
The file is constants-only and contains `DCN_1_0__SRCID__*` and matching `DCN_1_0__CTXID__*` macros. Groups include DC I2C software/hardware completion and DDC read requests, DCCG/DMU/DIO/WB/DPP/HUBP/HUBBUB/MPC/OPP/OPTC/MMHUBBUB/AZ performance counters, RBBMIF and DMCU internal events, ABM histogram/luma/backlight events, DPCS TX/RX errors, HPD and HPD RX events, audio endpoint format/enable/disable events, AUX software/LS/GTC events, DIG stream-disable and fast-training events, MCIF writeback and scaler conflicts, DCPG power up/down events, OTG timing/snapshot/trigger/vertical/ext-sync/DRR events, vblank/vline and HUBP VM context errors, MPCC stalls, vstartup/vready/vsync, HUBP flip/flip-away, no-lock vupdate events, and DMCUB outbox readiness.

Repeated source IDs use context IDs to distinguish channels or subevents. For example HPD and HPD RX share source 9 with context IDs, OTG snapshot/control groups use per-OTG source IDs with context selectors, and DMCUB outbox high/low priority uses source `0x68` with distinct contexts.

## Control Flow
There are no functions. Display code registers these IDs with `amdgpu_irq_add_id()` and DC IRQ service code maps incoming `amdgpu_iv_entry` records to display IRQ sources. Several paths register contiguous ranges using the first macro plus the number of CRTCs or OTGs.

## State And Persistence
The constants are immutable. Runtime state is the interrupt registration tables, enabled IRQ masks, and DC interrupt-source mapping built from these numbers. Correct mappings persist for the device lifetime and across mode-set operations.

## Dependencies And Integration Points
The header is included by `amdgpu_dm.c` and many DC IRQ service implementations from DCN 1.0 through newer DCN generations that reuse these source IDs. It integrates with SOC15 IH client `DCE`, HPD/AUX handling, page-flip/vblank delivery, timing events, DMUB message processing, and display error diagnostics.

## Risks
Many source IDs are overloaded by context ID; registering or decoding only the source can deliver the wrong event. Range assumptions depend on contiguous hardware numbering for OTGs, HUBPs, and CRTC-related events. The table contains historical naming mismatches and comments for later DCN users, so renaming macros can break broad display IRQ code even if values stay the same.

## Test Signals
Compile all DC IRQ service variants. Runtime validation should cover HPD plug/unplug and HPD RX, AUX/I2C transactions, vblank/page-flip interrupts, vstartup/vready/vupdate events, DMCUB outbox interrupts, display power-domain changes, link training, underflow/error reporting, and multi-CRTC systems where range-based registration is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_10_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_10_1.h

## Purpose
This header defines GFX 10.1 graphics interrupt source IDs for command-processor, RLC, GRBM, and SQ events. It is used by the GFX 10 AMDGPU interrupt setup and decode paths.

## Important APIs, Types, And Data
The file defines `GFX_10_1__SRCID__*` macros from the `0xB0` to `0xEF` source range. Important IDs include ring-buffer/IB interrupt packets, `CP_GENERIC_INT`, PM4 reserved-bit errors, EOP, bad opcode, privileged register/instruction faults, wait-memory-semaphore faults, context empty/busy, wait-reg-mem timeout, signal incomplete, preempt ack, GPF, GDS allocation error, ECC/FUE errors, compute query status, unattached VM doorbell, RLC streaming performance monitor, GRBM read timeout, GUI idle, and SQ interrupt.

`CP_GENERIC_INT` and `CP_IB1_INTERRUPT_PKT` both use source ID 177, so consumers must understand the generation's aliasing behavior.

## Control Flow
There is no executable code. `amdgpu/gfx_v10_0.c` registers selected source IDs with `amdgpu_irq_add_id()` for EOP and fault interrupts, then uses the same constants while processing IH entries.

## State And Persistence
The constants are immutable. Runtime state consists of registered IRQ handlers and per-source enablement in AMDGPU's interrupt framework.

## Dependencies And Integration Points
The header integrates with SOC15 IH client `GRBM_CP`, GFX 10 ring/fence handling, CP fault handling, RLC/performance events, and GPU reset/error recovery paths.

## Risks
Numeric source IDs are hardware ABI. An incorrect value can route CP faults to the wrong handler or leave fault interrupts unregistered. Alias source 177 requires careful decode semantics. Newer GFX generations have related but not identical tables, so sharing constants across generations is unsafe unless explicitly verified.

## Test Signals
Build GFX 10. Runtime tests include ring interrupt/fence completion, EOP delivery, bad PM4/opcode fault injection where possible, privileged register fault handling, preemption, GPU reset after CP faults, and SQ/RLC diagnostic interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_10_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_11_0_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_11_0_0.h

## Purpose
This header defines GFX 11.0.0 interrupt source IDs for graphics, SDMA-as-reported-through-GFX client paths, memory access, poisoning, command processor, RLC, GRBM, and SQ events.

## Important APIs, Types, And Data
It introduces low source IDs for `UTCL2_FAULT`, `UTCL2_DATA_POISONING`, and `MEM_ACCES_MON`. SDMA-related IDs occupy `0x30` through `0x43`, including atomic return, trap, SRBM write protection, context empty, preempt, IB preempt, invalid doorbell, queue hang, atomic timeout, poll timeout, page timeout/null/fault, VM hole, ECC, frozen, SRAM ECC, semaphore timeouts, and user fence.

Graphics-side IDs include `RLC_GC_FED_INTERRUPT` at `0x80`, CP generic/fault/EOP/preempt/query/doorbell/ECC sources around `0xB1`-`0xCA`, GRBM read timeout and GUI idle, and SQ interrupt `0xEF`.

## Control Flow
There are no functions. `amdgpu/gfx_v11_0.c`, `gfx_v11_0_3.c`, and `sdma_v6_0.c` use these macros while registering IRQ IDs and identifying poison/fault/SDMA events in IH entries.

## State And Persistence
The header is immutable. Runtime state is built in AMDGPU's IRQ registration tables and per-IP fault handling logic.

## Dependencies And Integration Points
It integrates with SOC15 IH clients for GFX/SDMA reporting, GFX 11 CP setup, RLC poison/FED handling, SDMA v6 IRQ setup, VM fault reporting, and reset/RAS paths.

## Risks
GFX 11 extends the table beyond older CP-only IDs, so using GFX 9/10 constants would miss SDMA and UTCL2 events. `RLC_GC_FED_INTERRUPT` has poisoning semantics in some paths; handling it as a generic perf event can hide data-poisoning conditions.

## Test Signals
Build GFX 11 and SDMA v6 paths. Runtime signals include EOP/fence completion, CP fault interrupts, SDMA trap/fence/page-fault interrupts, UTCL2 fault reporting, poisoning/RAS interrupt handling, and recovery after queue hang or GPU reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_11_0_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_12_0_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_12_0_0.h

## Purpose
This header defines GFX 12.0.0 interrupt source IDs. It continues the GFX 11-style contract for UTCL2, SDMA, RLC, CP, GRBM, and SQ events while adjusting selected source IDs for the GFX 12 generation.

## Important APIs, Types, And Data
The table contains `UTCL2_FAULT`, `UTCL2_DATA_POISONING`, `MEM_ACCES_MON`, SDMA IDs `0x30` through `0x46`, `RLC_GC_FED_INTERRUPT`, CP generic/fault/EOP/preempt/query/doorbell/ECC/FUE events, `RLC_STRM_PERF_MONITOR_INTERRUPT`, `GRBM_RD_TIMEOUT_ERROR`, `GRBM_REG_GUI_IDLE`, and `SQ_INTERRUPT_ID`.

Relative to GFX 11, `SDMA_FENCE` is defined at `0x46` rather than `0x43`, so consumers must use the generation-specific header rather than assuming the previous value.

## Control Flow
No functions are present. `amdgpu/gfx_v12_0.c` registers CP/fault interrupts with these IDs, and `amdgpu/sdma_v7_0.c` uses the SDMA subset for SDMA v7 interrupt registration and processing.

## State And Persistence
The constants are immutable. They determine persistent IRQ registration and runtime dispatch behavior for GFX 12 devices.

## Dependencies And Integration Points
The header integrates with GFX 12 command processor handling, SDMA v7, SOC15 IH dispatch, VM fault handling, data-poisoning/RAS paths, and reset diagnostics.

## Risks
The `SDMA_FENCE` value change is a compatibility risk for shared SDMA code. CP and RLC IDs overlap conceptually with earlier generations but should not be deduplicated without a generation audit. Wrong IDs can manifest as missing fence completion, unhandled page faults, or failure to reset after CP faults.

## Test Signals
Build GFX 12 and SDMA v7. Runtime validation should cover CP EOP/fence completion, SDMA user fence/trap/page-fault handling, VM fault reporting, poisoning/FED events, queue hang recovery, and GRBM/SQ diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_12_0_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_12_1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_12_1_0.h

## Purpose
This header defines GFX 12.1.0 interrupt source IDs for newer graphics and SDMA handling. It refines UTCL2 fault/retry/poison separation and adds newer CP/RLC/PMR-related source aliases.

## Important APIs, Types, And Data
`UTCL2_FAULT`, `UTCL2_RETRY`, and `UTCL2_DATA_POISONING` occupy IDs 0, 1, and 2. SDMA IDs include the GFX 12 SDMA range plus renamed or expanded error cases: `SDMA_INVALID_ADDR` at `0x3D`, `SDMA_INVALID_RB_PTR` at `0x43`, `SDMA_BE_EXCEPTION` at `0x44`, and `SDMA_FENCE` at `0x46`.

CP IDs include ring-buffer, IB1, IB2, DMA watch, PM4 reserved-bit, EOP, bad opcode, privileged fault, context, timeout, preempt, GPF, GDS, ECC, VM doorbell, FUE, suspend completion, and resume completion events. `RLC_STRM_PERF_MONITOR_INTERRUPT` and `CP_SUSPEAND_REQ_INTERRUPT` both use `0xCA`, while `RLC_POISON_INTERRUPT` and `CP_RESUME_REQ_INTERRUPT` both use `0xCB`, reflecting source aliasing that must be decoded with client/context semantics. `PMR_EA_ERROR_INTERRUPT`, GRBM, and SQ IDs complete the table.

## Control Flow
There are no functions. `amdgpu/gfx_v12_1.c` uses these IDs for CP/RLC poison interrupt registration and handling, and `amdgpu/sdma_v7_1.c` uses the SDMA subset for SDMA v7.1 interrupts.

## State And Persistence
The file is immutable hardware ABI. Runtime persistence is the per-device IRQ registration and decode tables created from these constants.

## Dependencies And Integration Points
It integrates with GFX 12.1 CP, RLC poisoning/RAS, SDMA v7.1 queue/fence handling, SOC15 IH dispatch, VM fault handling, and error-recovery code.

## Risks
Several source IDs are aliases with different semantic names. Consumers must account for IH client and context information when deciding whether `0xCA` or `0xCB` is CP suspend/resume or RLC poison/perf. The macro `CP_SUSPEAND_REQ_INTERRUPT` preserves a typo in the public name; changing it would require all users to migrate.

## Test Signals
Build GFX 12.1 and SDMA v7.1. Runtime validation should cover SDMA fence, trap, invalid address, invalid ring pointer, BE exception, CP EOP and fault interrupts, suspend/resume completion interrupts, RLC poison handling, PMR EA error reporting, and GPU reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_12_1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_9_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_9_0.h

## Purpose
This header defines GFX 9.0 graphics interrupt source IDs for command processor, RLC, GRBM, and SQ events. It is the GFX9 SOC15 interrupt-source contract used by AMDGPU GFX initialization and fault handling.

## Important APIs, Types, And Data
The table defines CP ring-buffer and IB interrupt packet IDs, PM4 reserved-bit error, EOP, bad opcode, privileged register/instruction faults, wait-memory-semaphore fault, context empty/busy, wait-reg-mem timeout, signal incomplete, preempt ack, GPF, GDS allocation error, ECC/FUE, compute query status, VM doorbell, RLC streaming performance monitor, GRBM read timeout, GUI idle, and SQ interrupt. IDs occupy the `0xB0` through `0xEF` range.

## Control Flow
There is no executable code. `amdgpu/gfx_v9_0.c` and `gfx_v9_4_3.c` register selected IDs via `amdgpu_irq_add_id()` and process incoming IH entries using the same constants.

## State And Persistence
The constants are immutable. They persist indirectly in AMDGPU's IRQ registration tables and determine runtime dispatch of GFX9 interrupts.

## Dependencies And Integration Points
The header integrates with SOC15 IH client `GRBM_CP`, GFX ring/fence handling, CP fault processing, RLC diagnostics, SQ error handling, and GPU reset/RAS paths on GFX9-class devices.

## Risks
The table is similar to GFX 10 but lacks the `CP_GENERIC_INT` alias. Reusing a newer-generation source table can create off-by-one or alias mistakes. Missing or wrong EOP IDs can stall fences; wrong fault IDs can hide CP errors and delay recovery.

## Test Signals
Build GFX9 and GFX9.4.3. Runtime tests include ring submission and fence completion, EOP IRQ delivery, bad packet/fault handling, privileged access faults, preemption, GRBM timeout diagnostics, SQ interrupt reporting, and reset after CP failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_9_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/isp/irqsrcs_isp_4_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/isp/irqsrcs_isp_4_1.h

## Purpose
This header defines ISP 4.1 interrupt source IDs for AMDGPU image-signal-processor support. It maps semaphore timeout, ringbuffer, MIPI, I2C, flash, and debug events to numeric source IDs.

## Important APIs, Types, And Data
The file defines `ISP_4_1__SRCID__*` constants. Semaphore-related IDs include wait fail, wait incomplete, and signal incomplete timeouts. Ringbuffer event IDs cover base-address changes and write-pointer changes for ringbuffers 5 through 16. Notably ringbuffer 9 through 16 wrap into IDs `0x00` through `0x0F`, while ringbuffers 5 through 8 use `0x15` through `0x1C`. Peripheral IDs include `ISP_MIPI0`, `ISP_MIPI1`, `ISP_I2C0`, `ISP_I2C1`, `ISP_FLASH0`, `ISP_FLASH1`, and `ISP_DEBUG`.

## Control Flow
There are no functions. `amdgpu/isp_v4_1_0.c` and `isp_v4_1_1.c` include this header and use the ringbuffer write-pointer IDs to set up ISP interrupt handling for firmware/queue notifications.

## State And Persistence
The constants are immutable. Runtime state consists of IRQ registration and ISP queue/ring state that reacts to these source IDs.

## Dependencies And Integration Points
The header integrates with the ISP v4.1 AMDGPU IP implementation, SOC15 IH dispatch, ringbuffer notification handling, MIPI sensor paths, I2C pad interrupts, flash control, and debug reporting.

## Risks
The non-monotonic ringbuffer numbering is easy to misread: base/write-pointer IDs for ringbuffers 9-16 start at zero. Assuming source IDs increase with ring number across the whole range will misroute notifications. Missing semaphore timeout handling can hide firmware deadlocks.

## Test Signals
Build ISP v4.1.0 and v4.1.1. Runtime validation should cover ISP firmware queue/ringbuffer write-pointer interrupts for rings 9-16, MIPI input events, I2C pad events, flash interrupts, semaphore timeout diagnostics, and debug interrupt logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/isp/irqsrcs_isp_4_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/ivsrcid_vislands30.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/ivsrcid_vislands30.h

## Purpose
This legacy Volcanic Islands interrupt-vector source ID header defines display, graphics, memory, media, SDMA, thermal, SMU, BIF, and virtual-memory source IDs plus extended IDs. It is shared by older AMDGPU display, GFX, GMC, UVD, VCE, SDMA, and PowerPlay paths.

## Important APIs, Types, And Data
Display IDs cover D1-D6 vupdate, graphics page flip, vertical interrupts, external timing sync events, HPD A-F, and HPD RX A-F. System and memory IDs include SRBM read timeout/context switch/register access errors, system/SEM/GFX page-invalid and memory-protection faults, and synthetic `VM_CONTEXT_ALL` IDs. Media IDs include UVD encoder/general/system messages and VCE trap with extended IDs for general-purpose, low-latency, and real-time queues.

GFX/CP IDs cover ring/IB interrupts, PM4 errors, EOP, bad opcode, privileged faults, wait-mem-semaphore fault, GUI idle/busy, compute query status, wait-reg-mem timeout, semaphore incomplete, preempt ack, GPF, GDS allocation, ECC, RLC streaming performance monitor, GRBM timeout/idle, and SQ interrupt. SDMA IDs cover atomic, ECC, trap, semaphore, preempt, VM hole, context empty, invalid doorbell, frozen, poll timeout, and SRBM write. Thermal/SMU IDs include TSS low/high transitions, thermal trigger, display timer triggers, GPIO 19, and BIF PF/VF mailbox events. `VISLANDS30_IV_EXTID_NONE` and `VISLANDS30_IV_EXTID_INVALID` define extended-ID sentinels.

## Control Flow
There is no code. Legacy and DCE display paths register these IDs with `amdgpu_irq_add_id()` and decode source/extended IDs in IRQ service implementations. Older GFX/GMC/UVD/VCE/SDMA/PowerPlay code uses the same constants for fault, media, and thermal interrupt registration.

## State And Persistence
The constants are immutable legacy hardware ABI. Runtime state is the IRQ registration, enabled masks, and handler dispatch based on source and extended IDs.

## Dependencies And Integration Points
Integration spans `dce_v10_0.c`, `amdgpu_dm.c`, DCE IRQ services, `gfx_v8_0.c`, `gmc_v7_0.c`, `gmc_v8_0.c`, UVD/VCE implementations, SDMA v2/v3, SMU7 hardware manager, SMU helper, and VKMS compatibility code.

## Risks
Several events share a source ID and are distinguished by extended ID, especially vertical interrupt groups and HPD/HPD RX. The file also defines synthetic IDs that are not direct hardware source IDs. Treating all constants as raw hardware values or ignoring ext IDs can misroute display or VM fault events. Because this header is used by many older code paths, even small value changes have broad regression risk.

## Test Signals
Build legacy DCE, GFX8, GMC7/8, UVD, VCE, SDMA v2/v3, and SMU7 paths. Runtime checks include HPD and page flip/vblank delivery, VM fault interrupts, CP EOP/fault handling, UVD/VCE interrupts, SDMA trap/SRBM write interrupts, thermal events, and PF/VF mailbox interrupts where virtualization is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/ivsrcid_vislands30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/nbio/irqsrcs_nbif_7_4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/nbio/irqsrcs_nbif_7_4.h

## Purpose
This header defines NBIF 7.4/NBIO interrupt source IDs for chip error, doorbell, RAS, ATHUB error, PF/VF mailbox, slot/power, and PCIe atomic error events.

## Important APIs, Types, And Data
The constants include `CHIP_ERR_INT_EVENT`, `DOORBELL_INTERRUPT`, `RAS_CONTROLLER_INTERRUPT`, `ERREVENT_ATHUB_INTERRUPT`, PF-to-VF and VF-to-PF mailbox valid/ack IDs, `CHIP_DPA_INT_EVENT`, `CHIP_SLOT_POWER_CHG_INT_EVENT`, `ATOMIC_UR_OPCODE`, and `ATOMIC_REQESTEREN_LOW`. Values span `0x5E` through `0xCF`.

## Control Flow
There are no functions. NBIO implementations register selected IDs with `amdgpu_irq_add_id()` and RAS code uses the RAS/ATHUB error IDs to route NBIO-related interrupt events.

## State And Persistence
The constants are immutable. Runtime state is the NBIO/RAS/mailbox IRQ registration and any error counters or recovery state updated by handlers.

## Dependencies And Integration Points
The header is included by `nbif_v6_3_1.c`, `nbio_v4_3.c`, `nbio_v7_4.c`, `nbio_v7_9.c`, `amdgpu_ras.c`, and NBIO RAS manager code. It integrates with PCIe, doorbell handling during power states, SR-IOV PF/VF mailbox signaling, ATHUB error reporting, and RAS controller interrupts.

## Risks
PF/VF mailbox direction is encoded in separate source IDs; swapping valid and ack or PF-to-VF and VF-to-PF breaks virtualization communication. The macro `ATOMIC_REQESTEREN_LOW` preserves a spelling typo; renaming it without updating users would break builds. Wrong RAS IDs can hide fatal hardware error notifications.

## Test Signals
Build all NBIO users. Runtime validation should cover NBIO RAS interrupt registration, ATHUB error injection/reporting, SR-IOV PF/VF mailbox valid and ack flows, doorbell events around VDDGFX-off states, PCIe atomic error reporting, and slot power-change interrupt handling where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/nbio/irqsrcs_nbif_7_4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma0/irqsrcs_sdma0_4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma0/irqsrcs_sdma0_4_0.h

## Purpose
This header defines SDMA0 4.0 interrupt source IDs for SDMA queue, memory, semaphore, ECC, preemption, and fault events.

## Important APIs, Types, And Data
The `SDMA0_4_0__SRCID__*` constants include atomic return done, atomic timeout, IB preempt, ECC, page fault/null/XNACK, trap, semaphore incomplete and wait-fail timeouts, SRAM ECC, preempt, VM hole, context empty, invalid doorbell, frozen, poll timeout, and SRBM write protection. Values occupy the `0xD9` through `0xF7` range with gaps.

## Control Flow
There are no functions. `amdgpu/sdma_v4_0.c` and `sdma_v4_4_2.c` use these constants when registering SDMA0 interrupt IDs and when dispatching SDMA fault/trap/status events.

## State And Persistence
The file is immutable hardware ABI. Runtime persistence is AMDGPU's SDMA IRQ registration and per-ring state changes driven by received interrupts.

## Dependencies And Integration Points
It integrates with SOC15 IH SDMA client handling, SDMA v4 ring/fence code, VM fault reporting, SRBM write protection handling, ECC/RAS handling, queue preemption, and GPU reset recovery.

## Risks
The SDMA0 4.0 and SDMA1 4.0 tables have the same numeric values but different macro namespaces; code must use the right namespace for clarity and per-engine registration. Misrouting XNACK/page fault/null events can produce poor VM fault diagnostics or fail to recover a ring hang.

## Test Signals
Build SDMA v4.0 and v4.4.2. Runtime tests include SDMA trap and fence events, preemption, page fault/XNACK reporting, invalid doorbell, poll timeout, SRBM write protection, ECC/SRAM ECC, context empty, and reset after SDMA hang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma0/irqsrcs_sdma0_4_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma0/irqsrcs_sdma0_5_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma0/irqsrcs_sdma0_5_0.h

## Purpose
This header defines SDMA0 5.0 interrupt source IDs. It provides the SDMA v5 source-number contract for trap, fault, semaphore, ECC, preempt, context, doorbell, poll, and SRBM write events.

## Important APIs, Types, And Data
The constants mirror the SDMA0 4.0 numeric set: atomic return done `0xD9`, atomic timeout `0xDA`, IB preempt `0xDB`, ECC `0xDC`, page fault/null/XNACK `0xDD`-`0xDF`, trap `0xE0`, semaphore incomplete/wait-fail `0xE1`-`0xE2`, SRAM ECC `0xE4`, preempt `0xF0`, VM hole `0xF2`, context empty `0xF3`, invalid doorbell `0xF4`, frozen `0xF5`, poll timeout `0xF6`, and SRBM write protection `0xF7`.

## Control Flow
There are no functions. `amdgpu/sdma_v5_0.c` and `sdma_v5_2.c` include this header and use the constants for IRQ registration and source-ID return helpers.

## State And Persistence
The header is immutable. Runtime state is SDMA v5 interrupt registration, ring/fence state, error counters, and recovery paths that respond to these IDs.

## Dependencies And Integration Points
It integrates with SDMA v5/v5.2 ring management, SOC15 IH dispatch, VM fault handling, RAS/ECC reporting, queue preemption, and reset/recovery handling.

## Risks
Although the values match SDMA0 4.0, the generation-specific namespace matters for maintainability and avoiding accidental cross-generation edits. Missing `SDMA_TRAP` or `SDMA_POLL_TIMEOUT` registration can stall user queues or hide ring hangs. Page fault/null/XNACK distinctions are important for accurate VM diagnostics.

## Test Signals
Build SDMA v5.0 and v5.2. Runtime validation should cover SDMA ring submissions and fences, trap interrupts, VM faults and XNACK/page-null handling, semaphore timeout diagnostics, invalid doorbell events, ECC/SRAM ECC handling, preemption, and reset after queue hang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma0/irqsrcs_sdma0_5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma1/irqsrcs_sdma1_4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma1/irqsrcs_sdma1_4_0.h

## Purpose
This header defines SDMA1 4.0 interrupt source IDs. It is the engine-1 namespace counterpart to the SDMA0 4.0 table for AMDGPU SDMA v4 devices.

## Important APIs, Types, And Data
The `SDMA1_4_0__SRCID__*` constants cover atomic return done, atomic timeout, IB preempt, ECC, page fault/null/XNACK, trap, semaphore incomplete and wait-fail timeouts, SRAM ECC, preempt, VM hole, context empty, invalid doorbell, frozen, poll timeout, and SRBM write protection. The numeric values match the SDMA0 4.0 table and occupy the same `0xD9`-`0xF7` ranges.

## Control Flow
There is no executable code. `amdgpu/sdma_v4_0.c` and `sdma_v4_4_2.c` include this header together with SDMA0's table to register and handle interrupts for multiple SDMA engines.

## State And Persistence
The constants are immutable. Runtime persistence is the per-engine SDMA IRQ registration, ring state, and fault/recovery bookkeeping that use these IDs.

## Dependencies And Integration Points
It integrates with SOC15 IH SDMA handling, SDMA v4 multi-engine setup, ring/fence completion, VM fault diagnostics, semaphore timeout handling, ECC/RAS, and reset recovery.

## Risks
Because SDMA0 and SDMA1 source values are identical, engine identity must come from the IH client/instance or registration context, not the numeric source alone. Using only `src_id` can conflate engines and update the wrong ring state. As with SDMA0, page fault/null/XNACK and SRBM write protection need distinct handling for useful diagnostics.

## Test Signals
Build multi-SDMA v4 paths. Runtime tests should exercise both SDMA engines independently: submissions, fences, traps, preemption, page faults, invalid doorbells, poll timeouts, SRBM write protection, ECC/SRAM ECC, and recovery after one-engine hangs without corrupting the other engine's state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma1/irqsrcs_sdma1_4_0.h -->
