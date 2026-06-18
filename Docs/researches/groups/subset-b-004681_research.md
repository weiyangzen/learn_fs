# Research: subset-b-004681

Grouped source research for IPA table, microcontroller, register-description, and ipvlan header/build files. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_table.c

Purpose: Implements IPA filter and route table allocation, validation, hardware initialization, reset, and hash/cache flush logic. It translates the driver-owned endpoint/route model into IPA-resident table regions whose entries point at a coherent DMA "zero rule" until AP or modem owners install real rules.

Important APIs and functions: Public entry points are `ipa_filtered_valid()`, `ipa_table_hash_support()`, `ipa_table_reset()`, `ipa_table_hash_flush()`, `ipa_table_setup()`, `ipa_table_config()`, `ipa_table_init()`, `ipa_table_exit()`, and `ipa_table_mem_valid()`. Key helpers include `ipa_table_mem()` for selecting IPv4/IPv6 filter/route memory regions, `ipa_table_addr()` for deriving DMA addresses inside the coherent backing allocation, `ipa_table_reset_add()` for DMA-shared-memory reset commands, `ipa_table_init_add()` for `TABLE_INIT` commands, and tuple-zeroing helpers for endpoint filter and route hash/cache configuration registers.

Control flow: Early validation records `ipa->filter_count` and `ipa->route_count` from IPA memory-region sizes. `ipa_table_init()` allocates coherent memory containing the zero rule, filter bitmap, and repeated zero-rule DMA addresses. `ipa_table_setup()` submits one transaction that initializes IPv4/IPv6 route and filter tables, including hashed table addresses when supported, and zeroes unused filter slots. Later `ipa_table_reset()` resets AP or modem-owned filter entries one endpoint at a time and resets contiguous route ranges for the selected execution environment. `ipa_table_hash_flush()` writes either the legacy `FILT_ROUT_HASH_FLUSH` bits or the IPA v5.0+ unified `FILT_ROUT_CACHE_FLUSH` bits.

State and persistence: The file mutates `ipa->filter_count`, `ipa->route_count`, `ipa->table_virt`, and `ipa->table_addr`; it reads `ipa->filtered`, `ipa->modem_route_count`, endpoint ownership, and version-specific register maps. Hardware-visible table contents persist in IPA local memory until reset, reinitialized, or overwritten by AP/modem owners. The coherent zero-rule backing allocation persists from `ipa_table_init()` until `ipa_table_exit()`.

Dependencies and integration points: Depends on GSI transactions, IPA immediate commands, IPA local-memory descriptors, endpoint metadata, version selection, and register descriptors from `ipa_reg()`. It integrates with probe-time memory validation, modem/AP bring-up reset paths, IPA command submission, and hardware route/filter cache programming.

Risks: Version distinctions are subtle: IPA v4.2 lacks hashed tables, pre-v5.0 filter bitmaps reserve bit 0 for global filtering, and v5.0+ separates filter/router cache registers. Table size validation must remain in lockstep with `TABLE_INIT` command field limits and memory-region definitions. A wrong DMA address, count, or bitmap shift can make hardware route/filter through stale or invalid rules. Reset transactions intentionally report allocation failures but continue with route/filter attempts, so partial reset states are possible after command allocation pressure.

Test signals: Validate probe on IPA versions with and without hash support; check memory-region mismatch, undersized table, and overlarge command-field rejection paths; exercise AP and modem table resets; confirm IPv4/IPv6 hashed and non-hashed tables point at the zero rule after setup; verify pre-v5.0 bitmap left-shift behavior and v5.0+ unshifted behavior; confirm hash/cache flush register writes after rule updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_table.h

Purpose: Declares the IPA filter and route table lifecycle API used by probe, configuration, modem/AP reset, and rule synchronization code.

Important APIs and types: The header forward-declares `struct ipa` and exposes `ipa_filtered_valid()`, `ipa_table_hash_support()`, `ipa_table_reset()`, `ipa_table_hash_flush()`, `ipa_table_setup()`, `ipa_table_config()`, `ipa_table_init()`, `ipa_table_exit()`, and `ipa_table_mem_valid()`. The API is intentionally table-centric and hides DMA allocation, IPA memory-region lookup, and command construction inside `ipa_table.c`.

Control flow and integration: Callers validate table memory and filtering endpoint masks before table initialization, call `ipa_table_init()` to allocate coherent backing memory, call `ipa_table_setup()` and `ipa_table_config()` during hardware setup, call `ipa_table_reset()` when resetting AP or modem-owned entries, and call `ipa_table_hash_flush()` after hashed rule updates. There is no matching deconfig/teardown for setup/config because hardware state is overwritten or lost as part of broader IPA teardown.

State and persistence: The header owns no state, but its functions allocate and release `ipa->table_virt`/`ipa->table_addr` and program persistent hardware table/cache state.

Dependencies: Requires Linux integer types and the full IPA core definition at implementation call sites. It is coupled to `ipa_mem`, `ipa_cmd`, endpoint, version, and register code through the implementation.

Risks: Prototype drift can break setup/reset ordering across the IPA driver. The boolean parameters (`modem`, `filter`) are compact but easy to misuse, so call sites should be checked for ownership semantics. Hash support is version-derived rather than platform-data-derived, so new hardware versions must update version logic.

Test signals: Build coverage across IPA probe/remove and reset paths; runtime coverage of table setup, hash flush, and modem/AP reset paths on hash-capable and non-hash-capable versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_uc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_uc.c

Purpose: Handles the minimal AP-side interface to the IPA-resident microcontroller: shared-memory layout, microcontroller interrupt dispatch, proxy power retention during firmware start, and panic notification.

Important APIs and functions: Public functions are `ipa_uc_interrupt_handler()`, `ipa_uc_config()`, `ipa_uc_deconfig()`, `ipa_uc_power()`, and `ipa_uc_panic_notifier()`. Internal pieces include `struct ipa_uc_mem_area`, command/response/event enums, `ipa_uc_shared()` for locating the `IPA_MEM_UC_SHARED` block, event/response interrupt handlers, and `send_uc_command()` for writing a command then raising the `IPA_IRQ_UC` register bit.

Control flow: Configuration clears `ipa->uc_powered`/`ipa->uc_loaded` and enables the two microcontroller IRQs. `ipa_uc_power()` takes a one-time runtime-PM proxy reference before the modem first boots the microcontroller. On `IPA_IRQ_UC_1`, `ipa_uc_response_hdlr()` accepts `INIT_COMPLETED`, marks the microcontroller loaded, enables IPA power retention, drops the autosuspend reference, and clears `uc_powered`; other responses are warnings. On `IPA_IRQ_UC_0`, event handling logs errors and ignores LOG_INFO. During panic, the AP sends `ERR_FATAL` and delays briefly to allow microcontroller state save.

State and persistence: Runtime state is held in `ipa->uc_powered`, `ipa->uc_loaded`, IPA power-retention state, and a function-static `already` flag that ensures only the first modem boot takes a proxy reference. The shared memory block is hardware-visible IPA SRAM; reserved bytes must not be touched. No durable storage is used.

Dependencies and integration points: Depends on IPA memory descriptors, IPA interrupt enable/disable routing, runtime PM, IPA power retention, register descriptors, MMIO accessors, and panic-notifier integration. It assumes the shared memory interface version is compatible with hardware interface `0x2000`.

Risks: The static `already` flag is process-wide, so reset/reprobe behavior depends on driver lifetime assumptions. Reserved shared-memory fields must remain untouched. Unexpected INIT responses can leave power references unchanged. Panic notification only runs when `uc_loaded` is true, so early crashes do not notify the microcontroller. Command writes need little-endian conversion and correct IRQ register bits.

Test signals: Confirm first modem boot keeps runtime PM active until `INIT_COMPLETED`; verify autosuspend reference is dropped exactly once; inject unsupported event/response values; test config/deconfig ordering with and without loaded firmware; validate panic notifier writes `ERR_FATAL` and delays; check suspend/resume or reset paths for stale `uc_powered`/`uc_loaded`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_uc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_uc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_uc.h

Purpose: Declares the IPA microcontroller control and interrupt API used by IPA core setup, interrupt dispatch, power sequencing, and panic handling.

Important APIs and types: The header forward-declares `struct ipa` and declares `ipa_uc_interrupt_handler()`, `ipa_uc_config()`, `ipa_uc_deconfig()`, `ipa_uc_power()`, and `ipa_uc_panic_notifier()`. The public API intentionally exposes only lifecycle and notification hooks, not the shared-memory layout or command enums.

Control flow and integration: IPA core code calls config/deconfig around device setup and teardown, dispatches IPA microcontroller interrupt IDs through `ipa_uc_interrupt_handler()`, calls `ipa_uc_power()` when modem boot requires a proxy IPA power reference, and uses `ipa_uc_panic_notifier()` from crash-notifier handling.

State and persistence: The header has no state, but its functions mutate `ipa->uc_powered`, `ipa->uc_loaded`, runtime-PM references, interrupt enablement, and IPA retention state.

Dependencies: Requires the IPA core type and the `enum ipa_irq_id` definition to be visible before use. The implementation depends on IPA memory, interrupt, power, PM runtime, and register layers.

Risks: Misordered config/power/deconfig calls can leak or prematurely drop a runtime-PM reference. Missing enum visibility would break compilation. The API does not return status for config/deconfig/panic operations, so failures are logged internally.

Test signals: Compile coverage for interrupt dispatch and panic notifier users; runtime coverage for first-boot proxy power, IRQ enable/disable, and deconfig cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_uc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_version.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_version.h

Purpose: Defines the enumerated IPA hardware versions, their paired GSI version comments, and execution-environment IDs shared across IPA/GSI register maps and driver logic.

Important APIs and types: `enum ipa_version` lists IPA versions from `IPA_VERSION_3_0` through `IPA_VERSION_5_5`, ending with `IPA_VERSION_COUNT`. `enum gsi_ee_id` defines AP, modem, microcontroller, and TrustZone execution environments as `GSI_EE_AP`, `GSI_EE_MODEM`, `GSI_EE_UC`, and `GSI_EE_TZ`.

Control flow and integration: Version values select IPA and GSI register maps, hardware data tables, feature branches such as table hash support and cache/register layout, and endpoint/route ownership behavior. Execution-environment IDs are embedded in register offsets and ownership comparisons throughout IPA/GSI code.

State and persistence: The header owns no runtime state. The enum ordering is a persistent internal ABI because comparisons such as `version < IPA_VERSION_5_0` encode feature boundaries.

Dependencies: Only depends on Linux types, but many IPA and GSI translation units depend on these definitions.

Risks: Adding a version requires updating string conversion, register-map selection, hardware data, feature gates, and any range comparisons. Incorrect enum ordering can silently break feature tests. GSI version comments are documentation only and must be kept aligned with platform data.

Test signals: Build all register-map references for each version; probe supported platforms; exercise version boundary logic around IPA v4.2 hash absence and IPA v5.0 cache/register changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg.h

Purpose: Provides the common descriptor format and helper macros/functions for versioned IPA and GSI register maps.

Important APIs and types: `struct reg` describes a register offset, instance stride, field-mask array, and name. `struct regs` wraps a version-specific array of register descriptors. Macros `REG`, `REG_STRIDE`, `REG_FIELDS`, and `REG_STRIDE_FIELDS` define static register descriptors. Inline helpers `reg()`, `reg_fmask()`, `reg_bit()`, `reg_field_max()`, `reg_encode()`, `reg_decode()`, `reg_offset()`, and `reg_n_offset()` implement validated access to offsets and bitfields.

Control flow: Callers select a `struct reg` by register ID, optionally encode/decode fields using mask arrays, and compute either a simple offset or an indexed offset using stride. Error cases warn and return zero or NULL-like fallbacks, allowing caller paths to avoid immediate crashes while surfacing invalid register IDs or field IDs.

State and persistence: No mutable state exists. The descriptors are static constants, and their values encode the hardware ABI for all register accesses.

Dependencies and integration points: Used by `ipa_reg()` and `gsi_reg()` wrappers and every versioned file in `drivers/net/ipa/reg/`. It depends on Linux `ARRAY_SIZE`, bit, bug, log2, and type helpers.

Risks: `reg_bit()` assumes the field mask is a single bit; using it for multi-bit fields warns and returns zero. `reg_encode()` silently returns zero on invalid values after warning, which can accidentally program a zero field if callers ignore validation. Offset zero is both a possible fallback and a legitimate value in some v5 IPA maps, so callers should not treat zero offset alone as success.

Test signals: Compile all versioned register maps; unit-like checks for encode/decode boundaries; runtime probe on each supported hardware version; fault-injection or debug coverage for out-of-range register/field IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v3.1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v3.1.c

Purpose: Defines the GSI register descriptor table for GSI v1.0 as paired with IPA v3.1.

Important APIs and data: Exports `const struct regs gsi_regs_v3_1`. The file defines channel context, event context, doorbell, status, command, interrupt, error-log, and scratch registers using `REG*` macros. Field masks cover channel protocol/direction/EE/channel ID/event ring index/state/element size, channel ring length, QoS weight/prefetch/doorbell engine, event ring parameters, command opcodes, interrupt selection, error fields, and scratch fields.

Control flow and integration: There is no executable control flow. Runtime GSI code indexes `gsi_regs_v3_1.reg` through common helpers to program channels, event rings, doorbells, IRQ masks, and error handling for AP execution-environment offsets.

State and persistence: Static constant descriptors encode hardware offsets under the older `0x4000 * GSI_EE_AP` execution-environment window and `0x80` channel/event strides. Register values persist in hardware, not in this file.

Dependencies: Includes `gsi_reg.h`, `ipa_version.h`, and `reg.h`. It depends on enum register IDs and field IDs matching the array layout.

Risks: v3.1 lacks later hardware parameter descriptors such as `HW_PARAM_2`; code must gate feature discovery accordingly. Incorrect AP EE base offsets or field widths can break channel setup, event delivery, or interrupt clearing.

Test signals: Probe an IPA v3.1 platform, allocate channels/events, ring doorbells, receive IRQs, and decode error logs using the v3.1 map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v3.1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v3.5.1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v3.5.1.c

Purpose: Defines the GSI register descriptor table for GSI v1.3 / IPA v3.5.1-era hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v3_5_1`. It is structurally close to the v3.1 table but adds `HW_PARAM_2` field masks for channel pending translation, full-channel logic, and status-related hardware capability discovery. It retains legacy channel context, event context, QoS, doorbell, command, interrupt, error-log, and scratch descriptors.

Control flow and integration: Common GSI code selects this table for IPA v3.5.1 platforms and uses it for MMIO offsets and bitfield packing/unpacking. `HW_PARAM_2` lets setup code discover capabilities rather than relying only on fixed data.

State and persistence: The file contains only static descriptor state. It uses the same older AP EE window pattern and per-channel/per-event stride model as v3.1.

Dependencies: Depends on shared GSI register ID enums, field ID enums, execution-environment IDs, and the generic `reg` helpers.

Risks: This map is near-identical to adjacent versions, so copy/paste drift in a single field mask or offset is hard to spot. Consumers must not assume later SDMA or RD/WR-engine fields exist just because `HW_PARAM_2` is present.

Test signals: Hardware probe on IPA v3.5.1, capability reads from `HW_PARAM_2`, channel/event setup, command completion, IRQ mask/clear, and error-log decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v3.5.1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.0.c

Purpose: Defines the GSI register descriptor table for GSI v2.0 / IPA v4.0 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v4_0`. It keeps the legacy register-window layout while expanding `HW_PARAM_2` to include SDMA capability fields such as `GSI_USE_SDMA`, SDMA interrupt count, maximum burst, and IOVEC count in addition to pending/full-channel flags.

Control flow and integration: GSI setup and command code use this table to program channel contexts, event contexts, QoS, scratch, doorbell, command, status, and interrupt registers. Capability discovery uses the v4.0 `HW_PARAM_2` mask to conditionally configure SDMA-related behavior.

State and persistence: All state is static constant register metadata. Hardware state programmed through the descriptors persists in GSI MMIO registers until reset or reprogramming.

Dependencies: Depends on `gsi_reg.h` ID definitions, `ipa_version.h` execution-environment values, and `reg.h` descriptor helpers.

Risks: v4.0 is a boundary where capability fields broaden but offsets still look like v3.x; treating it as a later v4.5+ map would use wrong base offsets for some blocks. Incorrect SDMA field masks can make capability detection unreliable.

Test signals: Probe IPA v4.0, read and interpret `HW_PARAM_2`, open/close channels and event rings, generate doorbells, and verify IRQ status/mask/clear handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.11.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.11.c

Purpose: Defines the GSI register descriptor table for IPA v4.11 / GSI v2.11 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v4_11`. Compared with older v4.0-style maps, channel/event blocks move to the `0x0000f000`/`0x00012000` layout, QoS gains prefetch and byte-doorbell fields, `GENERIC_CMD` includes parameter bits, and `HW_PARAM_2` exposes RD/WR-engine and inter-EE capability bits.

Control flow and integration: Common GSI channel, event, interrupt, generic command, and capability code consumes this table through register helper lookups. The descriptors determine how channel state and event ring state are packed into MMIO writes.

State and persistence: Static register descriptors only. Values programmed using them persist in hardware register state and are tied to AP execution-environment offsets.

Dependencies: Uses common field IDs from `gsi_reg.h`; correctness depends on those IDs matching every `fmask` array index and `reg_array` entry.

Risks: v4.11 is close to v4.5/v4.9 but not identical; `GENERIC_PARAMS` exists here while some earlier v4 maps do not. QoS field differences can alter prefetch and doorbell semantics. Wrong base offset will prevent interrupts and commands from reaching the AP EE block.

Test signals: Probe v4.11 hardware, exercise generic commands with parameters, verify `HW_PARAM_2` capability decode, open channels, run traffic, and confirm IRQ clear/mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.5.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.5.c

Purpose: Defines the GSI register descriptor table for IPA v4.5 / GSI v2.5 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v4_5`. The map uses the newer v4 AP EE base offsets and retains channel context, event context, command, doorbell, interrupt, error, and scratch descriptors. QoS includes `PREFETCH_MODE` and `EMPTY_LVL_THRSHOLD`; `HW_PARAM_2` exposes SDMA, RD/WR-engine, inter-EE, pending-translate, and full-logic capabilities.

Control flow and integration: Selected by version-specific GSI register selection, then used by the shared GSI code for all MMIO offset and field operations.

State and persistence: Static metadata only. The hardware state written via this map includes channel/event ring configuration, interrupt state, doorbells, and error logs.

Dependencies: Depends on shared register/field IDs and the `REG_STRIDE_FIELDS` macros from `reg.h`.

Risks: Field availability differs from v4.9 and v4.11; code that assumes `DB_IN_BYTES` or `GENERIC_PARAMS` on v4.5 would encode nonexistent bits. Offsets must align with the shifted v4.5 register aperture.

Test signals: IPA v4.5 probe, capability reads, channel/event allocation, interrupt generation/clear, doorbell writes, and traffic over GSI channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.9.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.9.c

Purpose: Defines the GSI register descriptor table for IPA v4.9 / GSI v2.9 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v4_9`. It follows the v4.5-style base layout and adds QoS support for `DB_IN_BYTES` along with weighted round-robin, max prefetch, prefetch mode, and empty-level threshold fields. `HW_PARAM_2` includes SDMA and RD/WR/inter-EE capability fields.

Control flow and integration: Shared GSI setup uses this descriptor set for channel context programming, event ring setup, doorbells, commands, IRQ handling, and hardware capability discovery.

State and persistence: Only static descriptors live in the file. Hardware register values programmed through them remain active until reset or channel teardown.

Dependencies: Coupled to `gsi_reg.h` enum ordering and `reg.h` helper behavior.

Risks: This map is almost identical to v4.5/v4.11, so version-table selection must be precise. Enabling byte-based doorbell logic on versions that lack `DB_IN_BYTES`, or omitting it on v4.9 when required, can break ring updates.

Test signals: Probe v4.9 hardware, validate QoS programming including byte doorbells, exercise channel and event command paths, and confirm interrupts and error logs decode correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v5.0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v5.0.c

Purpose: Defines the GSI register descriptor table for IPA v5.0 / GSI v3.0 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v5_0`. The map shifts to the v5 `0x12000 * GSI_EE_AP` execution-environment aperture, widens channel protocol/channel ID/ring length fields, moves event EE bits, adds `CH_ERINDEX`, `LOW_LATENCY_EN`, `GENERIC_PARAMS`, and `HW_PARAM_4`, and keeps the core channel/event/doorbell/interrupt/error descriptors.

Control flow and integration: GSI core code uses this map to program v5 channel contexts, event contexts, QoS, commands, generic commands, interrupt blocks, and capability discovery. `HW_PARAM_4` exposes event-per-EE and IRAM protocol-count style data not present in older maps.

State and persistence: Static ABI metadata only. Programmed GSI channel and event state persists in hardware while channels are active.

Dependencies: Depends on the same shared `gsi_reg.h` IDs as older maps, but field masks differ substantially; version dispatch must select this table for v5-style hardware.

Risks: The v5 field layout is not backward compatible with v3/v4 layouts. Using older encode/decode assumptions truncates channel IDs or ring lengths. The larger EE aperture and reordered IRQ offsets make copy/paste from v4 maps dangerous.

Test signals: Probe IPA v5.0, validate channel/event setup with widened fields, read `HW_PARAM_2` and `HW_PARAM_4`, exercise low-latency/QoS configuration, command paths, doorbells, IRQ clear/mask, and sustained traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v5.0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v3.1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v3.1.c

Purpose: Defines IPA core register descriptors for IPA v3.1 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v3_1`. The map covers compatibility/configuration, clock-on status, default routing, shared memory size, QSB read/write limits, legacy filter/route hash flush, aggregation state/force-close, IPA_BCR, local packet processor context, counter configuration, source/destination resource groups 0-7, endpoint init/status/hash configuration, IPA IRQ registers, microcontroller IRQ, and suspend IRQ registers.

Control flow and integration: Runtime IPA code selects this descriptor table by hardware version, then uses `ipa_reg()` and generic register helpers to encode fields and compute MMIO offsets for setup, endpoint configuration, table hash flushing, interrupts, and resource programming.

State and persistence: Static constant descriptors only. Hardware state programmed through these offsets persists until reset or reconfiguration.

Dependencies: Depends on `ipa_reg.h` register and field IDs plus `ipa_version.h`. The file uses legacy pre-v5 endpoint stride and hash-combined register layout.

Risks: v3.1 has older bit positions for routing, clocks, resource limits, and endpoint hash fields. Global-filter bitmap behavior in table code also applies to this generation. Misusing later v4/v5 maps would program wrong offsets or fields.

Test signals: IPA v3.1 probe, endpoint configuration, resource limit programming, table hash flush, IRQ handling, microcontroller interrupt delivery, and aggregation force-close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v3.1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v3.5.1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v3.5.1.c

Purpose: Defines IPA core register descriptors for IPA v3.5.1 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v3_5_1`. It extends the v3.1-style map with `IPA_TX_CFG`, `FLAVOR_0`, and idle indication descriptors while retaining legacy hash flush, IPA_BCR, counter config, endpoint control/config/NAT/header/mode/aggregation/deaggregation/resource/status, combined endpoint filter/router hash config, IRQ, UC IRQ, and suspend registers.

Control flow and integration: Selected for v3.5.1 platforms and consumed through common register helpers during probe, endpoint setup, resource setup, table hash flush, and interrupt configuration.

State and persistence: Static register metadata only. Values written through the map remain in IPA hardware until changed or reset.

Dependencies: Coupled to `ipa_reg.h` field IDs and endpoint/resource code that expects v3.x offset/stride layout.

Risks: It looks close to v3.1 but has additional TX/flavor/idle registers and fewer resource groups than some later maps. Feature code must test register presence through the versioned table rather than assuming all later fields exist.

Test signals: Probe IPA v3.5.1, read flavor information, configure TX settings, run endpoint traffic, flush hash tables, and exercise IRQ/microcontroller paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v3.5.1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.11.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.11.c

Purpose: Defines IPA core register descriptors for IPA v4.11 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_11`. The table includes expanded `COMP_CFG` clock/configuration masks, legacy `FILT_ROUT_HASH_FLUSH`, moved aggregation and IRQ offsets, TX configuration, flavor, idle indication, Qtime timestamp and timer granularity registers, resource groups, endpoint config/status, combined endpoint filter/router hash config, and UC/suspend IRQ descriptors.

Control flow and integration: IPA setup and endpoint code uses this table to program v4.11-specific offsets and fields. Table code still uses pre-v5 combined hash registers and legacy hash flush bits for this version.

State and persistence: Static metadata only; programmed IPA registers persist in hardware.

Dependencies: Relies on shared IPA register IDs and field enums. It integrates with endpoint, resource, interrupt, table, and timing configuration code.

Risks: v4.11 shares many structures with v4.5/v4.9 but has some field-mask differences and a different IRQ base than earlier v4.2-style maps. Treating it as v5 would incorrectly use cache-flush and split cache config registers.

Test signals: Probe v4.11, configure endpoints and resources, verify qtime/timer setup, flush legacy hash tables, handle IPA/UC/suspend IRQs, and run traffic through aggregation/deaggregation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.2.c

Purpose: Defines IPA core register descriptors for IPA v4.2 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_2`. It includes `FILT_ROUT_HASH_EN` and `FILT_ROUT_HASH_FLUSH` descriptors even though higher-level table logic treats IPA v4.2 as not supporting hashed tables. The map covers compatibility, clocks, route, shared memory, QSB, aggregation, IPA_BCR, counter/TX/flavor/idle, resource groups, endpoint setup/status, IRQ, UC IRQ, and suspend registers.

Control flow and integration: Common IPA code uses the map for MMIO access on v4.2 platforms. `ipa_table_hash_support()` special-cases this version, so table memory validation expects absent or zero-sized hashed table regions despite register descriptors existing.

State and persistence: Static register descriptors only. Hardware state persists in MMIO registers after programming.

Dependencies: Depends on `ipa_reg.h` ID definitions and version selection code. Endpoint and resource paths expect the v4.2 offsets and field widths.

Risks: The presence of hash enable/flush descriptors can mislead callers; feature policy must follow `ipa_table_hash_support()`. v4.2 differs from v4.5+ in timer/qtime availability and some endpoint/hash handling.

Test signals: Probe v4.2 with hashed table regions absent or zero-sized; verify table setup skips hashes; configure endpoints and resources; exercise IRQ/UC paths and traffic without hash-table use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.5.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.5.c

Purpose: Defines IPA core register descriptors for IPA v4.5 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_5`. The map covers expanded compatibility and clock fields, route/default pipe fields, shared memory and QSB limits, legacy hash flush, aggregation active/force-close, packet processor context, TX configuration, flavor, idle indication, Qtime timestamp, XO/timer pulse granularity, source/destination resource groups, endpoint configuration/status, combined endpoint filter/router hash config, and IRQ/UC/suspend blocks.

Control flow and integration: IPA v4.5 runtime code uses this table through `ipa_reg()` for endpoint bring-up, resource configuration, table hash flush, interrupt handling, and timestamp/timer setup.

State and persistence: Static descriptors only; hardware register values are persistent until reset or reprogramming.

Dependencies: Depends on `ipa_reg.h` enum IDs and `reg.h` helper semantics. Table code relies on the legacy `FILT_ROUT_HASH_FLUSH` and `ENDP_FILTER_ROUTER_HSH_CFG` descriptors present here.

Risks: v4.5 is a feature-rich pre-v5 map; using v5 cache descriptors would be wrong, but using older v4.2 assumptions would miss timer/qtime fields. Field-mask changes in `COMP_CFG` and endpoint aggregation can affect performance or correctness.

Test signals: Probe v4.5, configure timers and timestamps, initialize endpoints/resources, flush legacy hash tables, exercise IPA and UC interrupts, and validate traffic with aggregation/deaggregation settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.7.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.7.c

Purpose: Defines IPA core register descriptors for IPA v4.7 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_7`. It follows the v4.5-family layout with compatibility, clock, route, shared memory, QSB, legacy hash flush, aggregation, local packet context, TX, flavor, idle, qtime/timer, resource group, endpoint, combined endpoint filter/router hash, and IRQ/UC/suspend descriptors.

Control flow and integration: Selected by hardware data for v4.7 platforms and used by common IPA setup, endpoint, resource, table, and interrupt code.

State and persistence: Contains only static descriptor state. Register values programmed through these descriptors persist in hardware.

Dependencies: Coupled to `ipa_reg.h` IDs and to feature paths that expect pre-v5 hash/cache layout.

Risks: The v4.7 file is close to v4.5/v4.9 and can be easy to interchange accidentally. Small field-mask differences in endpoint header extension, aggregation, or compatibility fields may only show up under specific offload/aggregation traffic.

Test signals: Probe v4.7, initialize endpoints, run TX/RX traffic with checksum/header/aggregation settings, flush hash tables, and verify IPA/UC/suspend IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.9.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.9.c

Purpose: Defines IPA core register descriptors for IPA v4.9 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_9`. The map is in the v4.5/v4.7 family and includes expanded compatibility fields, route/shared memory/QSB, legacy hash flush, aggregation, local packet context, TX configuration, flavor, idle/qtime/timer registers, resource groups, endpoint setup/status, combined endpoint filter/router hash config, and IRQ/UC/suspend descriptors.

Control flow and integration: Common IPA code uses this descriptor set for all v4.9 MMIO accesses. Table code uses its legacy hash flush and combined endpoint hash register fields.

State and persistence: Static register metadata only. Hardware state written via these descriptors remains active until reset or explicit reconfiguration.

Dependencies: Depends on `ipa_reg.h` ID/field ordering and `ipa_version.h` version dispatch.

Risks: v4.9 is pre-v5 despite being close to the v5 boundary; cache flush remains `FILT_ROUT_HASH_FLUSH`, and filter/router hash tuple configuration remains combined. Version-boundary mistakes will affect table cache coherency and endpoint hash programming.

Test signals: Probe v4.9, validate hash flush after table changes, configure endpoints/resources/timers, exercise interrupts, and run traffic through aggregation and checksum/header offload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v5.0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v5.0.c

Purpose: Defines IPA core register descriptors for IPA v5.0 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v5_0`. The map moves many core offsets, starts with `FLAVOR_0`, uses v5-style route and shared-memory fields, replaces legacy hash flush with `FILT_ROUT_CACHE_FLUSH`, uses wider/newer resource limit masks, changes endpoint stride to `0x80`, and splits endpoint filter and router cache configuration into `ENDP_FILTER_CACHE_CFG` and `ENDP_ROUTER_CACHE_CFG`.

Control flow and integration: Selected for IPA v5.0 platforms. Table code writes unified filter/router cache flush bits and zeroes split cache config registers. Endpoint/resource/interrupt setup uses the v5 offsets and field masks through `ipa_reg()`.

State and persistence: Static descriptor state only; hardware register state persists outside this file.

Dependencies: Depends on common IPA register IDs and field IDs being broad enough to represent both pre-v5 hash and v5 cache layouts.

Risks: This is a major layout boundary. Pre-v5 code assumptions about filter bitmap shifting, combined hash tuple registers, and legacy hash flush are wrong for v5. Incorrect offset zero handling is important because `FLAVOR_0` is at offset 0.

Test signals: Probe v5.0, read flavor/max-pipe data, initialize endpoints with `0x80` stride, flush route/filter caches after table changes, verify split cache tuple zeroing, exercise interrupts and traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v5.0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v5.5.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v5.5.c

Purpose: Defines IPA core register descriptors for IPA v5.5 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v5_5`. It follows the v5 cache-oriented layout while moving several top-level offsets relative to v5.0. It defines flavor, compatibility, clocks, route, shared memory, QSB, aggregation, cache flush, local packet context, TX, idle/qtime/timer, resource groups, endpoint config/status, split filter/router cache config, IPA IRQ, UC IRQ, and suspend descriptors.

Control flow and integration: IPA v5.5 hardware data selects this map, and common code uses it for endpoint/resource setup, cache flushes, interrupt control, and timer/TX configuration.

State and persistence: Static descriptor metadata only. Programmed register state persists in IPA hardware.

Dependencies: Coupled to v5-capable `ipa_reg.h` field IDs and version-selection logic. Table logic relies on its `FILT_ROUT_CACHE_FLUSH`, `ENDP_FILTER_CACHE_CFG`, and `ENDP_ROUTER_CACHE_CFG` descriptors.

Risks: v5.5 is close to v5.0 but has top-level offset shifts and some mask differences, such as compatibility and qtime fields. Reusing v5.0 offsets can silently program the wrong register. Offset-zero fallback handling from `reg_offset()` must not obscure real offset-zero registers in the v5 family.

Test signals: Probe v5.5, validate flavor/pipe limits, configure endpoints/resources/timers, flush caches, verify split cache tuple zeroing, handle IPA/UC/suspend IRQs, and run data traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v5.5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ipvlan/Makefile

Purpose: Defines the build objects for the ipvlan and ipvtap network drivers.

Important APIs and data: `obj-$(CONFIG_IPVLAN) += ipvlan.o` builds the ipvlan composite object when ipvlan is enabled. `obj-$(CONFIG_IPVTAP) += ipvtap.o` builds ipvtap separately. `ipvlan-objs-$(CONFIG_IPVLAN_L3S) += ipvlan_l3s.o` conditionally adds L3S support, and `ipvlan-objs := ipvlan_core.o ipvlan_main.o $(ipvlan-objs-y)` defines the base ipvlan object composition.

Control flow and integration: Kbuild evaluates the config symbols and links `ipvlan_core.o`, `ipvlan_main.o`, and optionally `ipvlan_l3s.o` into `ipvlan.o`. The built objects register rtnetlink/link operations and packet handlers elsewhere in the ipvlan subsystem.

State and persistence: No runtime state. Build outputs persist as kernel objects/modules according to Kconfig and build mode.

Dependencies: Depends on Kconfig symbols `CONFIG_IPVLAN`, `CONFIG_IPVTAP`, and `CONFIG_IPVLAN_L3S`, plus source files named in the object lists.

Risks: Missing conditional object linkage would compile out L3S hooks while headers still expose stubs or declarations. Object ordering is simple but should keep core/main linked into the composite ipvlan object.

Test signals: Build with ipvlan disabled, ipvlan enabled, ipvtap enabled, and `CONFIG_IPVLAN_L3S` toggled; verify module/object symbols and L3S registration availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan.h

Purpose: Defines shared data structures, constants, inline helpers, and cross-file function declarations for the ipvlan driver.

Important APIs and types: Constants define driver name/version, address hash sizes, MAC filter bitmap size, and multicast backlog limit. `ipvl_hdr_type` classifies IPv4, IPv6, ICMPv6, and ARP headers. `struct ipvl_pcpu_stats` stores per-CPU RX/TX counters with sync protection. `struct ipvl_dev` represents an ipvlan netdev, `struct ipvl_addr` tracks per-device L3 addresses in hash/list form, `struct ipvl_port` represents the lower-device port and address hash tables, and `struct ipvl_skb_cb` stores skb control metadata. Inline helpers retrieve `ipvl_port` under RCU/BH/RTNL and manipulate PRIVATE/VEPA flags.

Control flow and integration: The header connects `ipvlan_core`, `ipvlan_main`, optional `ipvlan_l3s`, and ipvtap-facing code. RX handlers use `ipvlan_handle_frame()`, address lookup uses the port hash table helpers, TX uses `ipvlan_queue_xmit()`, multicast backlog processing uses workqueue state in `ipvl_port`, and rtnetlink setup uses link creation/deletion/register declarations. Optional L3S functions compile to real declarations or harmless stubs depending on `CONFIG_IPVLAN_L3S`.

State and persistence: Runtime state is in `ipvl_port` lower-device attachment, RCU-protected address tables, per-device address lists, per-CPU statistics, MAC filter bitmaps, backlog queues, IDA allocation, and netdevice tracking. No durable persistence exists; state follows netdev lifecycle and network namespace movement.

Dependencies and integration points: Includes core networking, RCU, notifier, netdevice, VLAN, IPv4/IPv6 route/address, netfilter, rtnetlink, l3mdev, and namespace headers. It integrates with Linux rx_handler attachment, rtnl link operations, per-CPU stats, workqueues, and optional L3S netfilter hook behavior.

Risks: RCU/RTNL accessor choice matters; using the wrong helper can race port teardown. Address hash/list mutation is guarded by `addrs_lock` and must coordinate with RCU freeing. `skb->cb` overlay must not conflict with other users along the path. Backlog limit and multicast processing affect memory pressure and delivery ordering. Optional L3S stubs return success for init/cleanup but `ipvlan_l3s_register()` returns `-ENOTSUPP`, so callers must tolerate feature absence.

Test signals: Build with and without `CONFIG_IPVLAN_L3S`; create/delete ipvlan links in L2/L3/L3S modes; add/remove IPv4 and IPv6 addresses; exercise RX demux, TX queueing, multicast backlog, PRIVATE/VEPA flags, namespace migration, statistics accounting, and lower-device teardown under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan.h -->
