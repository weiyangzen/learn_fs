# subset-b-004679 research

Grouped research for IPA/GSI driver files under `sources/distributed-fs/ceph-client/drivers/net/ipa`. Each section is source-tree aligned and intended to be split into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v3.5.1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v3.5.1.c

Purpose: Supplies the static `ipa_data_v3_5_1` platform descriptor consumed by the IPA probe/match path. It binds IPA v3.5.1 hardware to QSB bus tuning, endpoint-to-GSI-channel mappings, resource group limits, IPA-local memory layout, deprecated IMEM/SMEM fallback addresses, and power/interconnect votes. The file has no runtime functions; its behavior is expressed through immutable tables.

Important data: `ipa_qsb_data` defines DDR/PCIE outstanding read/write limits, without `max_reads_beats` because this version predates that field. `ipa_gsi_endpoint_data` maps AP command TX, AP LAN RX, AP modem TX/RX, and modem-owned endpoints to concrete EE IDs, GSI channel IDs, IPA endpoint IDs, directions, TRE/event counts, TLV FIFO depths, and endpoint config. AP modem TX and modem TX paths mark `filter_support`. The exported `ipa_data_v3_5_1` sets `version = IPA_VERSION_3_5_1`, a nonzero `backward_compat` mask for legacy BCR quirks, `modem_route_count = 8`, and pointers to all local tables.

Control flow and integration: `ipa_main` selects this descriptor from Device Tree compatible data, then `gsi_init()` consumes `endpoint_count`/`endpoint_data` to allocate AP GSI rings and validate TRE/event/TLV constraints. IPA memory setup uses the memory descriptors for filter, route, header, proc context, modem, and microcontroller event-ring regions. Command setup validates table/header regions against the immediate-command field widths.

State and persistence: The file contributes no mutable state. Its constants become boot-time configuration for in-memory `struct ipa`, `struct gsi_channel`, endpoint bitmaps, DMA ring allocation sizes, and IPA-local memory programming. Persistence is hardware state after setup, not file-local storage.

Dependencies: Includes Linux bit helpers plus IPA headers for endpoint, memory, power, register, resource, and version constants. It depends on `ipa_data.h` struct layouts and on enum values in endpoint/memory headers remaining stable.

Risks: Channel IDs, endpoint IDs, and memory offsets are silicon-contract values; a single wrong number can silently route traffic to the wrong endpoint or corrupt IPA-local tables. `backward_compat` bits are version-specific and must not be copied to newer descriptors. IMEM/SMEM values are deprecated fallback data and should match older DT consumers only.

Test signals: Probe should accept the v3.5.1 compatible, GSI setup should not reject power-of-two rings or TLV limits, IPA memory validation should pass canary layout checks, and modem data path smoke tests should exercise AP modem TX/RX plus AP LAN RX. Regression logs to watch include GSI bad channel state, table-region size/offset errors, and BCR programming failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v3.5.1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.11.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.11.c

Purpose: Defines `ipa_data_v4_11`, the complete boot-time descriptor for IPA v4.11 platforms. It captures the IPA/GSI topology expected by the common driver: QSB parameters, AP and modem endpoint mappings, resource groups, local memory regions, legacy IMEM/SMEM fallback values, and power/interconnect requirements.

Important data: The endpoint array maps AP command TX to channel 5 endpoint 7, AP LAN RX to channel 14 endpoint 9, AP modem TX to channel 2 endpoint 2, and AP modem RX to channel 7 endpoint 16, with modem AP and DL NLO entries present for filter/routing setup. AP rings generally use 256 entries, while AP modem TX uses a 512-entry ring and TLV count 16. The memory table includes hashed/non-hashed IPv4/IPv6 filter and route regions, modem/AP header regions, proc contexts, NAT table, PDN config, stats regions, modem memory, and an end marker. `ipa_data_v4_11` sets `modem_route_count = 8` and a 60 MHz core clock.

Control flow and integration: The descriptor is selected by Device Tree match data and passed through IPA initialization. `gsi_init()` uses AP endpoint entries to allocate rings, command DMA pools, and NAPI contexts. `gsi_setup()` later validates hardware channel/event counts and programs GSI context registers. IPA table and command initialization validate the memory regions supplied here before issuing immediate commands.

State and persistence: All objects here are `static const` or exported `const`, so the file has no mutable state. Runtime state appears after consumers copy or reference these constants into `struct ipa` and program registers and IPA SRAM.

Dependencies: Depends on `ipa_data.h`, endpoint/memory enums, resource constants, and interconnect names matching platform DT. It also interacts indirectly with `gsi_reg.c`, because IPA v4.11 selects the v4.11 GSI register definition set and uses generic-command parameters for flow-control behavior.

Risks: v4.11 has version-sensitive register behavior: GSI generic commands include `GENERIC_PARAMS`, and channel/event register fields differ from v5.0. Incorrectly reusing v5.x endpoint IDs or memory offsets would break table initialization. The local memory table contains canary-protected regions, so offset/size drift can surface as memory validation failures or modem crashes.

Test signals: Probe on v4.11 DT should complete without GSI channel-not-supported errors. IPA command init should validate header and register-write offsets. Runtime tests should include modem channel flow-control toggles, AP command TX immediate commands, NAT/stats memory access, and suspend/resume channel stop/start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.2.c

Purpose: Provides `ipa_data_v4_2`, the descriptor for IPA v4.2 hardware. It is an early v4 descriptor with the AP/modem endpoint topology, local memory layout, resource group programming, power data, and legacy IMEM/SMEM fallback addresses.

Important data: AP command TX uses channel 1 endpoint 6 and AP LAN RX uses channel 2 endpoint 8. AP modem TX/RX use channels 0/3 and endpoints 1/9. Modem command/LAN/AP endpoints are also represented so filtering and routing tables account for non-AP endpoints. Several hashed route/filter memory regions have size 0, indicating hash support is absent or disabled for this target. `ipa_data_v4_2` sets `version = IPA_VERSION_4_2`, `modem_route_count = 8`, 100 MHz core clock, 0x2000 IMEM, and 0x2000 SMEM.

Control flow and integration: The most important integration detail is in `gsi.c`: IPA v4.2 requires the AP to allocate modem channels with GSI generic commands, so modem endpoint entries in this descriptor feed `modem_channel_bitmap` during `gsi_channel_init()`. AP endpoints are initialized into GSI channels and command pools; modem endpoints are skipped for AP ring allocation but retained for IPA endpoint/filter bookkeeping.

State and persistence: The descriptor is immutable. Runtime state is created by consumers: endpoint bitmaps, channel maps, resource programming, and IPA-local memory table initialization. The AP modem-channel allocation quirk affects GSI hardware state during setup/teardown.

Dependencies: Requires v4.2-compatible endpoint names, IPA memory IDs, resource group IDs, GSI EE constants, and the v4.0 GSI register layout selected by `gsi_reg.c` for IPA v4.2.

Risks: Because v4.2 has the modem-channel allocation workaround, wrong modem channel IDs can cause generic command failures or leave modem channels unallocated. Zero-sized hashed memory regions must remain consistent with hash-support detection. TLV counts are lower than later platforms, so command channel validation must still satisfy `IPA_COMMAND_TRANS_TRE_MAX`.

Test signals: Logs should not show generic allocate/halt command failures for modem channels. Table initialization must tolerate zero hash sizes. Data path smoke should cover AP modem TX/RX, AP LAN RX, and modem restart/teardown to validate generic halt unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.5.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.5.c

Purpose: Defines `ipa_data_v4_5`, a v4.5 platform descriptor containing endpoint topology, resource limits, IPA-local memory map, QSB settings, and power/interconnect data.

Important data: AP command TX is channel 9 endpoint 7, AP LAN RX channel 10 endpoint 16, AP modem TX channel 7 endpoint 2, and AP modem RX channel 1 endpoint 14. Modem AP and DL NLO endpoint entries are included for table setup. AP modem TX uses 512 TRE/event entries and TLV count 16; command TX uses TLV count 20. Memory layout includes hash and non-hash filter/route regions, header areas, larger modem proc context, NAT and stats regions, modem memory, UC event ring, and PDN config. `ipa_data_v4_5` uses a 150 MHz core clock comment-marked as uncertain in source.

Control flow and integration: Consumers treat this file as authoritative configuration. `gsi_channel_init_one()` validates the AP endpoint ring sizes and allocates rings based on these values. IPA memory setup and immediate-command validation use the offsets and sizes for filter/route/header initialization. Resource data is programmed into IPA resource-management registers during config.

State and persistence: No file-local mutable state exists. These constants shape runtime `struct ipa` memory descriptors, endpoint maps, and GSI channel state, and they persist only as programmed hardware state during the driver lifetime.

Dependencies: Uses `ipa_data.h`, `ipa_endpoint.h`, `ipa_mem.h`, `ipa_power.h`, and resource definitions. IPA v4.5 selects the v4.5 GSI register descriptions, including split channel protocol encoding and prefetch-mode fields.

Risks: v4.5 differs from v4.2 in endpoint numbering, nonzero hash table regions, larger SMEM, and GSI register fields. Copying values across versions can break endpoint routing or memory canaries. The core clock uncertainty comment is a signal that power/performance regressions should be checked on hardware.

Test signals: Successful probe, no GSI validation errors, table init with hashed route/filter regions, modem data path throughput, and power/interconnect vote sanity. Watch for DMA command failures to the NAT/stats areas and for unexpected endpoint status after modem SSR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.7.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.7.c

Purpose: Exports `ipa_data_v4_7`, the IPA v4.7 static configuration. The file defines the endpoint map, resource groups, memory regions, QSB data, and power/interconnect votes used by common IPA/GSI initialization.

Important data: AP command TX is channel 5 endpoint 7, AP LAN RX channel 14 endpoint 9, AP modem TX channel 2 endpoint 2, and AP modem RX channel 7 endpoint 16. The modem AP and DL NLO entries are present and mark filter support where required. Memory layout resembles v4.11 more than v4.5: 0x3000 local memory end marker, hash and route regions, modem/AP headers, NAT table, PDN config, stats, modem memory, and canary-protected regions. Core clock is 100 MHz with source comments noting uncertainty.

Control flow and integration: `gsi_init()` initializes only AP-owned channels, while modem entries remain available to IPA endpoint and filtering logic. `gsi_channel_program()` uses this version to select v4.5-style GSI register encodings. IPA command code uses the memory descriptors for header and table immediate commands.

State and persistence: The file contributes immutable descriptor data. State is generated by consumers through endpoint bitmaps, channel maps, DMA rings, and programmed SRAM/register content.

Dependencies: Relies on stable endpoint indices, memory IDs, resource group constants, and interconnect names. The selected GSI register set is `gsi_regs_v4_5`, so field availability must match v4.7 hardware.

Risks: v4.7 endpoint IDs overlap with v4.11 patterns but are not identical to v4.9/v5.x. Any mismatch can be hard to diagnose because traffic may complete on the wrong IPA endpoint. The local memory map has zero-size end markers and canaries that must remain aligned with firmware expectations.

Test signals: Probe should pass GSI channel/event count checks. AP command, LAN RX, and modem TX/RX paths should pass basic traffic. Suspend/resume should stop/start GSI channels using v4+ semantics. Canary and IPA memory validation should report no overlap or out-of-range errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.9.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.9.c

Purpose: Provides `ipa_data_v4_9`, a v4.9 hardware descriptor with GSI endpoint topology, IPA memory layout, resource allocation limits, QSB parameters, and power/interconnect votes.

Important data: AP command TX uses channel 6 endpoint 7, AP LAN RX channel 7 endpoint 11, AP modem TX channel 2 endpoint 2, and AP modem RX channel 12 endpoint 20. Modem AP RX shares channel 7 but is modem-owned and not initialized as an AP channel. Memory includes the full hashed/non-hashed table set, modem/AP headers, large modem proc context, NAT table, quota/tethering/filter-route/drop stats, modem memory, UC event ring, and PDN config. The descriptor sets `version = IPA_VERSION_4_9`, `modem_route_count = 8`, SMEM 0x9000, and 60 MHz core clock.

Control flow and integration: IPA v4.9 selects `gsi_regs_v4_9`. GSI channel programming enables `DB_IN_BYTES` for v4.9+, so this descriptor's channels are paired with byte-addressed doorbell behavior in `gsi_channel_program()`. IPA command code validates table and header regions and allocates command payloads from the AP command channel defined here.

State and persistence: All tables are immutable. Runtime state appears in GSI rings, NAPI contexts, endpoint maps, IPA memory, and modem route/filter tables configured from these constants.

Dependencies: Depends on endpoint/memory/resource enum stability and on DT interconnect names matching `memory`, `imem`, and `config` style entries used by the power layer. Also depends on v4.9 register descriptors for DB-in-bytes fields.

Risks: v4.9 channel IDs differ from v4.7/v4.11 even where endpoint names are similar. The DB-in-bytes register behavior makes GSI ring programming version-sensitive. Mistyped stats or NAT offsets can corrupt modem-visible memory while probe still succeeds.

Test signals: Hardware probe without unsupported-channel messages, successful route/filter table initialization, BQL accounting on TX completions, and modem SSR recovery. Watch for GSI event-with-no-transaction warnings, table command failures, and unexpected general interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.0.c

Purpose: Defines `ipa_data_v5_0`, the first v5.x descriptor in this set. It describes the v5.0 endpoint topology, resource limits, reordered local memory layout, QSB parameters, and power/interconnect requirements.

Important data: AP command TX is channel 12 endpoint 14, AP LAN RX channel 13 endpoint 16, AP modem TX channel 11 endpoint 2, and AP modem RX channel 1 endpoint 23. AP modem TX has TLV count 25, higher than older versions. Modem route count rises to 11. Local memory starts with `IPA_MEM_UC_EVENT_RING` at offset 0, then UC shared/info, table regions, headers, proc contexts, stats, AP filter regions, modem memory, NAT table, and PDN config. The descriptor provides legacy IMEM fallback 0x14688000/0x3000 and SMEM 0x9000, with 120 MHz core clock.

Control flow and integration: IPA v5.0 selects `gsi_regs_v5_0`. In `gsi_channel_program()`, v5.0 moves event ring index from `CH_C_CNTXT_0` to `CH_C_CNTXT_1`, uses v5 hardware event count discovery, keeps `DB_IN_BYTES`, and supports wider endpoint IDs in immediate commands. `ipa_cmd_ip_packet_init_add()` writes the full endpoint byte on v5+.

State and persistence: Static descriptor only. Runtime state is built by GSI ring allocation, IPA memory setup, resource programming, and table initialization.

Dependencies: Depends on v5.0 register descriptions, endpoint IDs up to 23, memory IDs including AP-specific filter regions, and resource limits matching hardware/firmware. Interconnect names must match DT for power setup.

Risks: v5.0 has major layout changes from v4.x: endpoint IDs are wider, memory starts with UC event ring, route entries are larger, and GSI event count discovery uses `HW_PARAM_4`. Backporting v4 assumptions can break command payload encoding or channel programming.

Test signals: Probe should report correct hardware channel/event counts via `HW_PARAM_2`/`HW_PARAM_4`; AP command pipeline clear should route through full 8-bit endpoint IDs; modem route count 11 should size route tables correctly; data path should exercise larger AP modem TX TLV depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.2.c

Purpose: Exports `ipa_data_v5_2`, the static IPA v5.2 configuration for endpoint, resource, memory, QSB, and power setup.

Important data: AP command TX uses channel 6 endpoint 9, AP LAN RX channel 7 endpoint 11, AP modem TX channel 5 endpoint 2, and AP modem RX channel 9 endpoint 18. AP modem TX uses 512 TRE/event entries and TLV count 25. Modem route count is 11. Unlike v5.0/v5.5, this descriptor no longer supplies deprecated IMEM address/size fallback values, but it does specify SMEM 0xb000. Memory includes v5-sized route tables, modem/AP headers, large modem proc context, quota/tethering/filter-route/drop stats, modem memory, NAT, and PDN config.

Control flow and integration: The descriptor is consumed by the same v5 register and command paths as v5.0. The absence of IMEM fallback means DT-provided IMEM is expected. GSI setup uses v5 event-count discovery and v5 channel context fields. IPA command code uses full-byte endpoint encoding and validates the v5 memory offsets.

State and persistence: Immutable source tables. Runtime state is allocated and programmed by IPA/GSI setup and torn down through the common driver.

Dependencies: Requires DT to provide memory resources that older descriptors could fall back to in this file. Depends on v5.0 GSI register definitions, endpoint/memory enum stability, and power/interconnect bindings.

Risks: v5.2 mixes v5 GSI behavior with endpoint/channel IDs that differ from v5.0/v5.5. Missing IMEM fallback can expose DT regressions. Route/filter region sizes and offsets are close together and canary-protected, so manual edits need overlap checks.

Test signals: Probe with v5.2 DT should not require descriptor IMEM fallback. IPA memory validation, command pipeline clear, AP modem traffic, and modem SSR should pass. Watch for DT memory resource errors, GSI command timeouts, and table init region overflow logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.5.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.5.c

Purpose: Defines `ipa_data_v5_5`, the descriptor for IPA v5.5. It describes endpoint/channel mappings, resource groups, expanded memory layout, QSB settings, and power/interconnect votes.

Important data: Endpoint topology matches v5.0 for the main AP channels: command TX channel 12 endpoint 14, LAN RX channel 13 endpoint 16, modem TX channel 11 endpoint 2, and modem RX channel 1 endpoint 23. AP modem TX uses TLV count 25. Modem route count is 11. Memory is v5-style with UC event ring at offset 0, UC shared/info, expanded route table sizes, headers, large modem proc context, quota/tethering/filter-route/drop stats, AP v4/v6 filter regions, modem memory, NAT table, and PDN config. The descriptor has IMEM fallback 0x14688000/0x2000, SMEM 0xb000, and 120 MHz core clock.

Control flow and integration: Common IPA/GSI init uses these constants to allocate channel rings, command pools, endpoint maps, and IPA-local memory. v5.5 uses the same `gsi_regs_v5_0` register layout as v5.0/v5.2 in this driver. Immediate commands encode endpoint IDs with full 8-bit width.

State and persistence: The file is immutable descriptor data only. Programmed GSI channels, event rings, route/filter tables, and IPA memory are the resulting runtime state.

Dependencies: Depends on v5 register layouts, endpoint/memory/resource enums, DT interconnect and memory bindings, and firmware expectations for IPA-local memory offsets.

Risks: Similarity with v5.0 can hide subtle differences: IMEM size is smaller, SMEM is larger, route table sizes differ, and memory stats/AP filter regions differ. Copying v5.0 assumptions into v5.5 can corrupt modem-visible local memory or under-size fallback memory.

Test signals: v5.5 probe should pass GSI channel/event discovery, command-channel setup, and memory validation. Traffic tests should cover AP modem TX/RX and LAN RX; command tests should cover table init, pipeline clear, and DMA shared-memory commands. Modem SSR should not leave stale channel state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi.c

Purpose: Implements the IPA Generic Software Interface runtime: register programming, channel/event-ring allocation, command issue/wait, interrupt handling, NAPI polling, modem-channel workarounds, setup/teardown, suspend/resume, and the public GSI lifecycle API. It is the bridge between static `ipa_data` endpoint descriptors and live GSI hardware state.

Important APIs/functions: Public entry points are `gsi_init()`, `gsi_exit()`, `gsi_setup()`, `gsi_teardown()`, `gsi_channel_start()`, `gsi_channel_stop()`, `gsi_channel_reset()`, `gsi_suspend()`, `gsi_resume()`, `gsi_channel_suspend()`, `gsi_channel_resume()`, `gsi_channel_tre_max()`, and `gsi_modem_channel_flow_control()`. Internal clusters handle IRQ masks (`gsi_irq_*`), hardware commands (`gsi_command()`, channel/event command helpers, generic commands), ring utilities, event processing, channel programming, and channel setup/init/exit.

Control flow: `gsi_init()` sets device/version, allocates a dummy netdev for NAPI, maps GSI registers, records IRQ, and initializes AP-owned channels from endpoint data. `gsi_setup()` first verifies GSI firmware enabled hardware, requests IRQ, discovers hardware channel/event counts, initializes the error log, enables interrupts, allocates/programs event rings and channels, and allocates modem channels for IPA v4.2. Channel start enables NAPI and IEOB completion interrupts before issuing `GSI_CH_START`; stop waits for transaction quiescence, stops hardware, then disables completion IRQ/NAPI. Completion interrupts disable IEOB for affected event rings and schedule NAPI, where events are translated back to transactions and retired.

State and persistence: `struct gsi` owns register mappings, cached IRQ masks, completion/result state, mutex, channel/event arrays, event allocation bitmap, modem channel bitmap, and a dummy netdev. `struct gsi_channel` owns ring indices, stats counters, NAPI, and transaction state. Persistent effects are programmed GSI registers and DMA-coherent rings.

Dependencies/integration: Depends on `gsi_reg` register descriptions, `gsi_trans` transaction helpers, `ipa_gsi` callbacks for TX accounting and completion release, static endpoint data from `ipa_data.h`, Linux IRQ/NAPI/DMA APIs, and version constants. It integrates upward with IPA setup and downward with GSI hardware.

Risks: Hardware command timeouts are short and state-sensitive; wrong endpoint data produces channel validation or unsupported-channel failures. Ring index math assumes power-of-two rings and 32-bit low DMA addresses in event pointers. Interrupt flood handling only reports after repeated loops. Modem generic commands ignore some channel-state errors by design, so real modem-channel mistakes can be subtle.

Test signals: Unit-level signals are scarce because this is hardware code. Useful runtime checks include successful probe/setup/teardown, no GSI command timeout logs, correct NAPI completion behavior, no event-with-no-transaction warnings, TX BQL accounting callbacks firing, suspend/resume channel stop/start passing, and modem SSR/flow-control tests on v4.2+.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi.h

Purpose: Declares the public GSI subsystem data structures and API used by the IPA driver. It defines ring, transaction-pool, channel, event-ring, and top-level GSI state structures plus lifecycle/channel-control entry points.

Important APIs/types: `GSI_CHANNEL_COUNT_MAX`, `GSI_EVT_RING_COUNT_MAX`, and `GSI_TLV_MAX` bound driver-supported hardware. `struct gsi_ring` tracks DMA-coherent ring virtual/DMA addresses, count, and software index. `struct gsi_trans_pool` and `struct gsi_trans_info` describe fixed pools and transaction state cursors. `enum gsi_channel_state` and `enum gsi_evt_ring_state` mirror hardware states. `struct gsi_channel` combines topology, ring pointers, TX accounting, transaction info, and NAPI. `struct gsi` stores device, version, register mapping, IRQ masks, completions, mutex, channel/event arrays, and dummy netdev.

Control flow and integration: Public functions declared here are implemented by `gsi.c` and called by IPA core and endpoint code. `gsi_init()` runs before hardware readiness; `gsi_setup()` runs after firmware/early GSI enablement; `gsi_teardown()`/`gsi_exit()` undo those phases. Channel start/stop/reset/suspend/resume are called by endpoint and power paths. `gsi_channel_tre_max()` informs transaction and command-pool sizing.

State and persistence: This header defines the in-memory state model. Ring indices are volatile software cursors; transaction cursors model free/allocated/committed/pending/completed/polled lifetimes; IRQ bitmaps cache programmed masks. No persistent storage is declared.

Dependencies: Includes Linux completion, mutex, netdevice, and type headers plus `ipa_version.h`. It forward-declares platform, endpoint, and transaction types to avoid broad include coupling.

Risks: Consumers must respect phase ordering: `gsi_init()` before setup, setup before channel start, stop before reset/teardown, and exit after teardown. Cursor fields in `gsi_trans_info` are tightly coupled to modulo ring sizes; changing ring sizing rules requires reviewing transaction code. `GSI_CHANNEL_COUNT_MAX`/event max are driver caps, not necessarily hardware caps.

Test signals: Compile-time checks validate type visibility. Runtime test signals are successful init/setup/exit pairing, channel lifecycle tests, and transaction allocation pressure tests that do not corrupt cursor state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_private.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_private.h

Purpose: Provides the private GSI interface shared only between `gsi.c` and `gsi_trans.c`. It exposes transaction state transitions, ring helpers, doorbell/update helpers, and TX accounting hooks without making them public to the wider IPA driver.

Important APIs/types: Defines `GSI_RING_ELEMENT_SIZE` as 16 bytes, used for both channel TREs and event entries. Declares transaction transitions `gsi_trans_move_complete()`, `gsi_trans_move_polled()`, `gsi_trans_complete()`, mapping/lookup helpers, pending cancellation, transaction init/exit, `gsi_channel_doorbell()`, `gsi_channel_update()`, `gsi_ring_virt()`, and TX accounting hooks `gsi_trans_tx_committed()`/`gsi_trans_tx_queued()`.

Control flow and integration: `gsi_trans.c` uses the doorbell and update hooks implemented in `gsi.c` when committing or querying transactions. `gsi.c` uses transaction lookup and state transition helpers when handling events and NAPI polling. The header is the contract that keeps transaction mechanics and hardware event processing coordinated.

State and persistence: No state is defined here beyond the shared element-size constant. The declared functions mutate `struct gsi_channel` transaction cursors, ring indices, mapped transaction pointers, and TX accounting counters.

Dependencies: Includes only Linux types and forward declarations for GSI structs. It intentionally limits include spread and documents that only `gsi.c` and `gsi_trans.c` should include it.

Risks: This file’s boundary is fragile: exposing these helpers beyond the two implementation files would let callers bypass transaction invariants. `GSI_RING_ELEMENT_SIZE` must match hardware event/TRE struct sizes; mismatch is guarded by build-time checks in implementation files.

Test signals: Build should fail if event/TRE sizes diverge. Runtime signals include correct mapping from completion events to transactions, clean cancellation on channel reset, and TX queue/complete accounting matching network stack expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_reg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_reg.c

Purpose: Implements GSI register description selection, register-ID validation for each IPA/GSI version, and I/O mapping of the `gsi` memory resource.

Important APIs/functions: `gsi_reg()` validates a requested `enum gsi_reg_id` against the current version and returns its `struct reg` descriptor. `gsi_reg_init()` obtains the named platform memory resource `gsi`, checks it fits in 32-bit address math, selects the version-specific `struct regs`, and maps it with `ioremap()`. `gsi_reg_exit()` unmaps and clears pointers.

Control flow: During `gsi_init()`, `gsi_reg_init()` runs before any GSI register access. The version switch maps IPA v3.1 to `gsi_regs_v3_1`, v3.5.1 to `gsi_regs_v3_5_1`, v4.2 to `gsi_regs_v4_0`, v4.5/v4.7 to `gsi_regs_v4_5`, v4.9 to `gsi_regs_v4_9`, v4.11 to `gsi_regs_v4_11`, and v5.x to `gsi_regs_v5_0`. Later GSI code calls `gsi_reg()` for every register access.

State and persistence: Mutates `gsi->regs` and `gsi->virt`; both are cleared on exit. No persistent storage is used.

Dependencies: Depends on platform resources, Linux I/O mapping, `gsi.h`, `gsi_reg.h`, and generic `reg.h` helpers. It also depends on version-specific register tables defined elsewhere under the IPA register data.

Risks: Invalid version mapping or register validity rules can make later code read/write wrong offsets. The `WARN()` in `gsi_reg()` returns NULL for invalid IDs, so callers must not request gated registers on unsupported versions. Resource address range validation assumes 32-bit GSI offsets.

Test signals: Probe should fail clearly on missing `gsi` DT resource, unsupported IPA version, or failed remap. Version smoke tests should exercise IPA 3.5.1, 4.2, 4.9, 4.11, and 5.x paths so gated registers such as `HW_PARAM_4` are used only when valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_reg.h

Purpose: Defines the GSI register ID namespace, register field IDs, hardware enum values, IRQ bit definitions, error codes, and register API declarations used by `gsi.c` and `gsi_reg.c`.

Important APIs/types: `enum gsi_reg_id` enumerates all GSI registers used by the driver. Field ID enums describe per-register fields such as channel context, event context, QOS, command opcodes, hardware parameters, interrupt masks/status, error logs, and scratch results. Hardware enums cover channel/event states, channel protocol types, prefetch modes, command opcodes, generic command results, interrupt types, global/general IRQ bits, and error types/codes. Extern `gsi_regs_v*` declarations provide version-specific register tables.

Control flow and integration: Implementation code never hard-codes most bit positions; it requests a `struct reg` and uses `reg_encode()`, `reg_decode()`, `reg_bit()`, and offsets. Version-specific register tables plug into this common ID/field contract. `gsi_reg_init()` and `gsi_reg()` are the public register helpers for the GSI implementation.

State and persistence: Header-only constants and declarations. Runtime state is in `struct regs` selected by `gsi_reg.c` and in hardware registers written by `gsi.c`.

Dependencies: Includes Linux bit helpers and forward-declares platform/GSI structs. Depends on generic register abstraction in `reg.h` and on version table definitions in the IPA register data files.

Risks: Field ID mismatches against version-specific `struct reg` definitions can encode wrong bits with no type-system protection. Comments mark version-gated fields such as `GENERIC_PARAMS`, `HW_PARAM_4`, `CH_ERINDEX`, `DB_IN_BYTES`, and `LOW_LATENCY_EN`; changes must be cross-checked with `gsi_reg_id_valid()` and channel programming.

Test signals: Build coverage across all version register tables, runtime probe on each supported IPA version, and logs free of invalid-register WARNs. Hardware tests should include command start/stop/reset, event processing, flow control, and error interrupt decode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_trans.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_trans.c

Purpose: Implements the GSI transaction abstraction used for IPA data transfers and immediate commands. It reserves TREs, owns scatterlist/command-payload resources, formats TREs, rings channel doorbells, tracks transaction lifetimes, handles DMA mapping/unmapping, and coordinates completion/cancellation.

Important APIs/functions: Pool APIs are `gsi_trans_pool_init()`, `gsi_trans_pool_alloc()`, `gsi_trans_pool_exit()`, plus DMA variants. Transaction APIs include `gsi_channel_trans_alloc()`, `gsi_trans_free()`, `gsi_trans_cmd_add()`, `gsi_trans_page_add()`, `gsi_trans_skb_add()`, `gsi_trans_commit()`, `gsi_trans_commit_wait()`, `gsi_trans_complete()`, `gsi_trans_read_byte()`, and channel transaction init/exit. Private state helpers move transactions between allocated, committed, pending, completed, polled, and free cursors.

Control flow: Allocation atomically reserves TRE capacity before returning a zeroed `struct gsi_trans` and scatterlist space. Add functions populate command, page, or SKB scatterlist entries and perform DMA mapping for data paths. Commit writes one TRE per scatterlist element, sets chain/IEOT/BEI/type flags, maps the final TRE to the transaction, advances ring index, updates TX accounting, moves state to committed/pending, and rings the doorbell when requested or when the ring is full. Completion unmaps DMA, calls IPA completion callback, completes waiters, and frees resources. Reset cancellation marks pending transactions cancelled and schedules NAPI.

State and persistence: `struct gsi_trans_info` holds atomic TRE availability, cursor IDs, transaction array, TRE-to-transaction map, scatterlist pool, and command payload DMA pool. Pools are fixed-size and circular; allocations are implicitly freed when TRE reservations are released. No persistent storage exists.

Dependencies: Depends on Linux DMA/scatterlist/SKB APIs, `gsi_private` for doorbells/update, `ipa_gsi` callbacks for transaction release/complete and TX accounting, and `ipa_cmd` opcodes for immediate commands.

Risks: Cursor arithmetic is modulo ring count and assumes power-of-two validated ring sizes. Pool allocation intentionally over-allocates to avoid wrap straddles; changing max allocation can double memory use. Failure to free unused or failed transactions leaks TRE reservations. Command transactions use DMA-coherent payloads and `DMA_NONE`; mixing data and command assumptions would corrupt mapping/unmapping behavior.

Test signals: Allocation pressure should return NULL rather than overrun TREs. SKB/page mapping failures should be recoverable by freeing the transaction. Completion events should map to the final TRE. Cancel/reset tests should complete cancelled RX transactions. TX tests should verify BQL queued/completed byte and transaction counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_trans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_trans.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_trans.h

Purpose: Declares the GSI transaction public interface and `struct gsi_trans`, the unit used by IPA endpoint and command code to describe transfers and immediate commands.

Important APIs/types: `IPA_COMMAND_TRANS_TRE_MAX` caps command transactions at 8 TREs. `struct gsi_trans` records GSI pointer, channel ID, cancellation state, reserved/used TRE counts, transfer length, caller data or command opcodes, scatterlist pointer, DMA direction, refcount, completion, and TX accounting snapshots. Public APIs cover pool init/alloc/free, DMA pool management, idle checks, transaction allocation/free, command/page/SKB add, commit/wait, and single-byte read helpers.

Control flow and integration: Callers allocate a transaction for a channel, add one or more operations, and commit it. Command code uses `gsi_trans_cmd_add()` and `gsi_trans_commit_wait()`; endpoint code uses page/SKB add and asynchronous commit. Completion is signaled through the embedded completion and IPA callbacks, while `gsi.c` consults transaction state during NAPI polling.

State and persistence: The header defines per-transaction mutable state but no global storage. Refcounting allows synchronous waiters and the polling path to coordinate destruction. `cancelled` carries reset/cancel state to IPA completion handlers.

Dependencies: Includes Linux completion, DMA direction, refcount, types, and `ipa_cmd.h` for command opcodes. Forward-declares device, page, scatterlist, SKB, GSI, and pools.

Risks: `used_count` can be less than `rsvd_count`, so users must not assume all reserved TREs are emitted. Command opcode storage is fixed to `IPA_COMMAND_TRANS_TRE_MAX`; command-channel TLV depth must be validated against that. Callers must free transactions after add failures.

Test signals: Compile integration with endpoint and command users, transaction wait completion, cancellation path behavior, and DMA map/unmap correctness for SKB/page transfers. Boundary tests should include max command TRE count and full-ring pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_trans.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa.h

Purpose: Defines the top-level `struct ipa` driver state and declares `ipa_setup()`, the setup-stage entry point. This header is the central ownership model for IPA core, GSI, power, memory, endpoints, interrupts, modem state, and QMI integration.

Important APIs/types: `struct ipa` embeds `struct gsi`, records hardware version, device, completions, remoteproc notifier, SMP2P/power pointers, route/filter table DMA allocation, interrupt state, microcontroller flags, register mapping, IPA-local memory mapping and descriptor array, IMEM/SMEM IOVAs, zero buffer, endpoint bitmaps, endpoint arrays/maps, setup completion, modem state, netdev, and QMI state. `ipa_setup()` performs setup after GSI firmware readiness.

Control flow and integration: IPA initialization is staged: init without hardware, config with IPA power/register access, and setup after GSI readiness. `ipa_setup()` is called either after TrustZone firmware load or after modem SMP2P readiness. GSI and immediate-command layers use `container_of(trans->gsi, struct ipa, gsi)` to reach this object.

State and persistence: This is the primary mutable state for the IPA driver. It persists for the lifetime of the platform device. Hardware-programmed state is mirrored by bitmaps for endpoint defined/available/set_up/enabled, microcontroller readiness flags, modem state, and memory/register mappings.

Dependencies: Includes GSI, endpoint, memory, QMI, and version headers plus Linux notifier/types. It forward-declares interrupt, power, SMP2P, and netdev types to reduce include coupling.

Risks: Because many subsystems share `struct ipa`, lifecycle ordering is critical. `setup_complete`, modem state, endpoint bitmaps, and GSI channel state must stay consistent through modem SSR and suspend/resume. Table and memory pointers must be valid before immediate commands run.

Test signals: Probe/remove lifecycle, firmware readiness paths, SMP2P-triggered setup, modem SSR notifier behavior, endpoint enable/disable bitmap consistency, and QMI/netdev integration. Failures often show as command timeout, endpoint not found, or table/memory validation logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_cmd.c

Purpose: Implements IPA immediate-command construction and validation. Immediate commands use the AP command TX GSI endpoint to initialize tables/headers, write registers, DMA to/from IPA memory, clear the pipeline, and tag status.

Important APIs/functions: Public functions include `ipa_cmd_table_init_valid()`, command pool init/exit, `ipa_cmd_table_init_add()`, `ipa_cmd_hdr_init_local_add()`, `ipa_cmd_register_write_add()`, `ipa_cmd_dma_shared_mem_add()`, `ipa_cmd_pipeline_clear_add()`, `ipa_cmd_pipeline_clear_count()`, `ipa_cmd_pipeline_clear_wait()`, `ipa_cmd_trans_alloc()`, and `ipa_cmd_init()`. Internal helpers validate header/register-write fields, allocate DMA-coherent command payloads, encode IP packet init and tag status, and add a small transfer for pipeline clear.

Control flow: `ipa_cmd_init()` performs build-time and runtime validation of header memory and register-write offsets. `ipa_cmd_pool_init()` creates a DMA-coherent payload pool on the command channel. Command add functions allocate a payload, fill little-endian hardware structs, and call `gsi_trans_cmd_add()` with the opcode. Pipeline clear builds a four-command sequence: no-op register write with full clear, packet-init to exception/LAN RX endpoint, tag-status command, and a zero-filled transfer, then waits for IPA completion.

State and persistence: Command payload memory is pooled in the command channel transaction info. The file itself has no globals. Runtime effects include IPA-local table/header content, register writes, DMA memory updates, and pipeline-clear completion state in `ipa->completion`.

Dependencies: Depends on GSI transactions, IPA core state, endpoint maps, memory descriptors, IPA register metadata, and IPA table hash support. It uses Linux bitfield helpers and DMA address types. Version branches handle v4+ pipeline-clear opcode fields and v5+ full-byte endpoint IDs.

Risks: Immediate-command payload encodings are hardware ABI. Offset/size fields are narrow and version-sensitive; validation must run before issuing commands. Command pool exhaustion should not occur if TRE reservations succeeded, so pool sizing must match `gsi_channel_tre_max()`. Pipeline clear depends on AP LAN RX endpoint being configured.

Test signals: Command init should reject oversized table/header/register offsets. Table init should work with and without hash regions. Pipeline clear should complete after modem/endpoint operations. DMA shared memory commands should read/write expected IPA-local regions. Watch for GSI command timeout and IPA completion stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_cmd.h

Purpose: Declares IPA immediate-command opcodes and the command-building API used by IPA setup, table, memory, and endpoint code.

Important APIs/types: `enum ipa_cmd_opcode` defines hardware opcodes for IPv4/IPv6 filter and route table init, header init, register write, IP packet init, DMA shared memory, packet tag status, and `IPA_CMD_NONE` for non-command transfer TREs. Function declarations cover validation, command-channel pool lifecycle, table/header/register/DMA command append, pipeline clear, command transaction allocation, and command subsystem init.

Control flow and integration: Callers allocate a command transaction with `ipa_cmd_trans_alloc()`, append one or more commands using the add helpers, and commit synchronously through GSI transaction APIs. Setup uses validation helpers before programming memory-backed tables. Pipeline clear is used when hardware state must drain before continuing.

State and persistence: Header declares no state. The implementation mutates command-channel DMA pools and IPA/GSI hardware state.

Dependencies: Forward-declares GSI channel/transaction, IPA, and IPA memory structs. Includes Linux types. `gsi_trans.h` includes this header for opcode values, so include cycles are deliberately minimized.

Risks: Opcode numeric values are hardware ABI and must not change without matching hardware documentation. `IPA_CMD_NONE` is a sentinel used by GSI transaction formatting to emit a normal transfer TRE; treating it as a real immediate command would be incorrect. Callers must respect `IPA_COMMAND_TRANS_TRE_MAX` from `gsi_trans.h`.

Test signals: Compile coverage for all command users, immediate-command smoke during setup, route/filter table init, pipeline clear completion, and DMA shared-memory read/write checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_data.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_data.h

Purpose: Defines the schema for IPA/GSI platform configuration data and declares all supported `struct ipa_data` descriptors. It is the common contract between Device Tree match data and the runtime IPA/GSI initialization code.

Important APIs/types: `IPA_RESOURCE_GROUP_MAX` bounds resource group arrays. `struct ipa_qsb_data` describes QSB outstanding request limits. `struct gsi_channel_data` defines TRE/event ring sizes and TLV FIFO depth. `struct ipa_endpoint_data` carries filtering support and endpoint config. `struct ipa_gsi_endpoint_data` binds EE ID, GSI channel ID, IPA endpoint ID, direction, channel data, and endpoint data. Resource, memory, interconnect, power, and top-level `struct ipa_data` aggregate those tables. Externs declare descriptors from v3.1 through v5.5.

Control flow and integration: Platform match code selects one `struct ipa_data`. IPA init consumes `endpoint_data` for endpoint maps and `gsi_init()`, `resource_data` for IPA resource programming, `mem_data` for local/IMEM/SMEM setup, `power_data` for clock/interconnect votes, QSB data for bus register programming, and `modem_route_count` for route table sizing.

State and persistence: This header defines immutable configuration structures. Runtime consumers keep pointers to static descriptors and program mutable hardware/driver state from them.

Dependencies: Includes Linux types and IPA endpoint, memory, and version headers. It is included by data files, GSI init, command code, and IPA core users.

Risks: Struct layout changes affect every version data file. Comments document deprecated IMEM fallback fields and version-specific fields such as `max_reads_beats` absence on v3.5.1 and `backward_compat` only before v4.5. Incorrect resource or endpoint schema interpretation can break all platforms.

Test signals: Build all data descriptors after schema changes. Probe each supported compatible to ensure tables validate. Static checks should confirm ring counts are powers of two, TLV counts fit, memory descriptors are non-overlapping, and final descriptors point at all required sub-tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_data.h -->
