# Research: subset-b-001447

This grouped report covers the AMD DC interrupt service variants for DCN 2.x through DCN 4.x plus the shared IRQ abstractions and DisplayPort link accessory helpers. Each section is source-path aligned and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c

Purpose: implements the DCN 2.0 ASIC interrupt service factory. It maps hardware interrupt `src_id`/`ext_id` values into the stable `enum dc_irq_source` namespace and provides the MMIO register table used by the shared `dal_irq_service_set()` and `dal_irq_service_ack()` paths.

Important APIs and functions: `dal_irq_service_dcn20_create()` allocates an `irq_service`, `dcn20_irq_construct()` installs `irq_source_info_dcn20` and `irq_service_funcs_dcn20`, and `to_dal_irq_source_dcn20()` handles vblank, vline0, page-flip, vupdate-no-lock, HPD, and HPD RX source translation. The file defines table-entry macros for HPD, HPD RX, HUBP surface flip, OTG vupdate, OTG vstartup/vblank, OTG vertical interrupt 0, plus dummy I2C/DPSINK/GPIO/underflow entries.

Control flow: the interrupt dispatcher calls `dal_irq_service_to_irq_source()`, which reaches `to_dal_irq_source_dcn20()`. Consumers then enable or acknowledge the returned source through the shared service. HPD entries use `hpd0_ack()` to acknowledge and flip polarity based on delayed sense state; most other real entries rely on generic register writes because their callback structs have NULL `set`/`ack`.

State and persistence: the service is heap allocated with `kzalloc_obj()` and owns no dynamic state beyond `ctx`, `info`, and `funcs`. The IRQ table is static const and persists for the module lifetime. Hardware state is changed through enable and ack MMIO masks in HPD, HUBPREQ, and OTG registers.

Dependencies and integration points: includes DCN 2.0 offsets/masks, `irqsrcs_dcn_1_0.h`, `dm_services.h`, and DCE110 dummy/HPD helpers. It integrates with the display manager's interrupt registration path through the exported `dal_irq_service_dcn20_create()` symbol.

Risks: table indexes must match `enum dc_irq_source`; incorrect mask polarity or clear bits can leave interrupts stuck or disabled. DCN20 has six HPD/RX, six vblank/vline/vupdate, and six pflip mappings, so reduced-pipe ASICs should not reuse this table without auditing. HPD callback reuse assumes HPD0 field names are macro-compatible for all instances.

Test signals: compile coverage catches register macro drift; runtime evidence is successful hotplug, page flip, vblank, vline, and vupdate interrupt delivery on DCN20 hardware. Negative tests should verify unsupported I2C/DPSINK/GPIO/underflow dummy entries warn/assert if enabled or acked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.h

Purpose: public factory header for the DCN 2.0 interrupt service.

Important APIs/types/functions: declares `struct irq_service *dal_irq_service_dcn20_create(struct irq_service_init_data *init_data);` and includes the shared `../irq_service.h` definitions for `irq_service`, `irq_source_info`, and initialization data.

Control flow and integration: ASIC bring-up code includes this header and calls the create function to obtain an initialized service whose callbacks and table are implemented in `irq_service_dcn20.c`.

State and persistence: this header owns no state. Its main contract is that callers must later destroy the returned heap object through the shared IRQ service lifetime path.

Dependencies, risks, and test signals: depends on the shared IRQ service ABI. Any signature change must stay synchronized with the C file and ASIC factory callers; build coverage is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c

Purpose: DCN 2.0.1 interrupt service implementation for a smaller display configuration. It follows the DCN20 pattern but narrows active translations and table entries to the supported pipes/connectors.

Important APIs and functions: `to_dal_irq_source_dcn201()` maps two vblank, two vline0, two vupdate, two HPD, and two HPD RX interrupt IDs. The static `irq_source_info_dcn201` table contains HPD/RX entries for instances 0 and 1, pflip entries for 0 through 3, active vblank/vupdate/vline entries for 0 and 1, and dummy placeholders for unsupported sources. `dal_irq_service_dcn201_create()` allocates and constructs the service.

Control flow: hardware source IDs are translated before generic enable/ack operations consume the table. The generic IRQ write path is used for pflip, vblank, vline0, and vupdate-no-lock; HPD uses `hpd0_ack()`. The constructor binds the static table and `irq_service_funcs_dcn201`.

State and persistence: no mutable per-source software state is stored. The static table persists; hardware enable and ack state is persisted in HPD, HUBPREQ, and OTG registers until changed.

Dependencies and integration points: uses DMU/DCN 2.0.1 register base macros, DCN 1.0 interrupt source IDs, and the DCE110 dummy/HPD helper interface. It plugs into ASIC initialization through `dal_irq_service_dcn201_create()`.

Risks: the file maps pflip entries for four HUBP instances but only maps interrupt source IDs for two HUBP flip interrupts, which requires hardware-specific validation. Accidentally enabling dummy entries for HPD3+ or vblank3+ indicates a caller/hardware mismatch.

Test signals: validate hotplug and HPD RX on the first two connectors, vblank/vline/vupdate interrupt delivery for the first two OTGs, and page flip behavior on supported planes. Build failures indicate register offset or mask drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.h

Purpose: exposes the DCN 2.0.1 interrupt service constructor.

Important APIs/types/functions: includes `../irq_service.h` and declares `dal_irq_service_dcn201_create()`.

Control flow and integration: display ASIC factory code calls this function when the detected IP version needs the DCN201 IRQ table and source mapper.

State and persistence: header-only declaration; no storage.

Dependencies, risks, and test signals: ABI drift with the C implementation or factory code is caught at build time. Runtime validation belongs to the DCN201 C file and shared IRQ service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c

Purpose: DCN 2.1 interrupt service, extending the DCN20 model with a DMCUB low-priority outbox interrupt source.

Important APIs and functions: `to_dal_irq_source_dcn21()` maps standard DCN display events plus `DCN_1_0__SRCID__DMCUB_OUTBOX_LOW_PRIORITY_READY_INT` to `DC_IRQ_SOURCE_DMCUB_OUTBOX`. `dmub_outbox_int_entry()` defines the DMCUB enable/ack registers using `DMCUB_OUTBOX1_READY_INT_EN` and `DMCUB_OUTBOX1_READY_INT_ACK`. `dal_irq_service_dcn21_create()` is the exported factory.

Control flow: interrupt source translation selects one of HPD/RX, vblank, vline0, pflip, vupdate, or DMCUB outbox. The shared IRQ service acknowledges/enables via table entries. DMCUB outbox uses generic ack/set because its callbacks are NULL.

State and persistence: static const IRQ table plus heap service object. Persistent effects are the programmed DMCUB interrupt enable/ack state and the normal OTG/HUBP/HPD interrupt control registers.

Dependencies and integration points: depends on DCN 2.1 offset/mask headers, DMU base offsets, DCN interrupt source IDs, DCE110 shared helpers, and the DMCUB interrupt register definitions. It integrates display firmware mailbox readiness with the same `dc_irq_source` dispatch path as display pipe events.

Risks: DMCUB outbox low-priority vs high-priority mapping differs across generations; confusing OUTBOX0 and OUTBOX1 can break firmware notifications. The table includes five HPD/RX entries and only four active pflip entries despite source translation cases for six pflip IDs, so hardware capability assumptions must be checked.

Test signals: verify DMCUB outbox IRQs wake the DMUB service, hotplug works on supported connectors, and vblank/page-flip events remain stable. Unit-level confidence is mostly compile-time macro coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.h

Purpose: declares the DCN 2.1 IRQ service factory.

Important APIs/types/functions: `dal_irq_service_dcn21_create()` returns a configured `struct irq_service` for DCN21.

Control flow and integration: included by ASIC-specific resource/factory code to select the DCN21 IRQ implementation.

State and persistence: no state in the header.

Dependencies, risks, and test signals: depends on the shared `irq_service.h` contract. Build coverage catches declaration/definition mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c

Purpose: DCN 3.0 IRQ service for full six-pipe display configurations, with DMCUB high-priority outbox support represented as `DC_IRQ_SOURCE_DMCUB_OUTBOX0`.

Important APIs and functions: `to_dal_irq_source_dcn30()` maps six vblank, six vline0, six pflip, six vupdate, HPD/RX, and `DMCUB_OUTBOX_HIGH_PRIORITY_READY_INT`. `dmub_trace_int_entry()` programs `DMCUB_OUTBOX0_READY_INT_EN/ACK`. `dal_irq_service_dcn30_create()` allocates and constructs the service.

Control flow: source IDs enter through the common dispatcher, are converted to `dc_irq_source`, and are serviced by generic enable/ack or the HPD polarity-aware ack helper. DMCUB trace/outbox is handled as another table entry.

State and persistence: the static table is immutable and the service object only holds pointers. Hardware state lives in DMCUB, OTG, HUBPREQ, and HPD registers.

Dependencies and integration points: includes DCN 3.0 offsets/masks, DCN IRQ source IDs, and DCE110 helpers. This file connects DCN30 display interrupt routing to the DRM AMD display core and DMUB trace/outbox processing.

Risks: DMCUB high-priority OUTBOX0 naming differs from DCN21 OUTBOX1. Incorrect mapping can make firmware trace/outbox events invisible. Six-pipe table entries should only be selected for hardware exposing the matching register instances.

Test signals: DMCUB outbox interrupt handling, vblank/page-flip interrupt counters, hotplug events, and link training paths that rely on DMUB notification. Compile-time register macro availability is a key regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.h

Purpose: public declaration for creating a DCN 3.0 IRQ service.

Important APIs/types/functions: declares `dal_irq_service_dcn30_create()` and imports the shared IRQ service definitions.

Control flow and integration: ASIC detection code includes this header to instantiate the DCN30-specific source mapper and register table.

State and persistence: no header state.

Dependencies, risks, and test signals: declaration must match `irq_service_dcn30.c`; build testing is the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c

Purpose: DCN 3.0.2 IRQ service variant. It resembles DCN30, including DMCUB high-priority OUTBOX0 support, but uses DCN 3.0.2 offset/mask headers.

Important APIs and functions: `to_dal_irq_source_dcn302()` maps six display timing and flip sources plus HPD/RX and high-priority DMCUB outbox. Macros build HPD, HPD RX, pflip, vupdate, vblank, vline0, and DMUB trace entries. `dal_irq_service_dcn302_create()` is the factory.

Control flow: translation and table-driven enable/ack match the shared IRQ service pattern. HPD ack uses polarity flipping; other functional entries use generic register set/ack because callbacks are NULL.

State and persistence: a static const table and heap `irq_service` wrapper. Hardware interrupt state is persistent in the selected MMIO registers until the service changes it.

Dependencies and integration points: depends on DCN 3.0.2 register headers, DCN interrupt source IDs, DCE110 helpers, and the shared IRQ framework. DMCUB OUTBOX0 integrates firmware-side notification into display interrupt routing.

Risks: register tables are hand-expanded by macros; source/index mismatches can silently route the wrong IRQ source. OUTBOX0 vs OUTBOX1 mismatch is the main firmware integration risk.

Test signals: successful creation on DCN302 hardware, DMCUB outbox delivery, page-flip/vblank/vline interrupts, and HPD/HPD RX events. Compilation validates offset/mask symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.h

Purpose: declares the DCN 3.0.2 IRQ service constructor.

Important APIs/types/functions: `dal_irq_service_dcn302_create(struct irq_service_init_data *init_data)`.

Control flow and integration: used by ASIC factory code to bind DCN302-specific interrupt source mapping.

State and persistence: header contains no storage.

Dependencies, risks, and test signals: depends on `../irq_service.h`; build coverage catches prototype drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c

Purpose: compact DCN 3.0.3 IRQ service for a two-pipe/two-HPD configuration, based on Sienna Cichlid/DCN 3.0.3 register definitions.

Important APIs and functions: `to_dal_irq_source_dcn303()` maps only two vblank, two vline0, two pflip, two vupdate, and two HPD/RX source pairs. `irq_source_info_dcn303` contains two HPD entries, two HPD RX entries, two I2C/DPSINK dummy entries, two underflow dummy entries, and functional pflip/vupdate/vblank/vline0 entries for instances 0 and 1. `dal_irq_service_dcn303_create()` allocates the service.

Control flow: the dispatcher gets a reduced source map. Valid entries use the same generic set/ack and HPD ack behavior as larger DCN tables. Unsupported sources are either absent or dummy, reducing accidental hardware access to non-existent instances.

State and persistence: static const table plus heap service object. The only persistent changes are interrupt control register writes.

Dependencies and integration points: includes Sienna Cichlid IP offsets, DCN 3.0.3 offsets/masks, DCN interrupt IDs, and DCE110 helper definitions. It is selected by DCN303 ASIC initialization.

Risks: reduced source coverage means generic code must not assume six pipes/connectors after this service is installed. Missing DMCUB outbox handling is intentional for this variant; adding firmware paths must audit whether the hardware exposes matching registers.

Test signals: two-display hotplug and page-flip/vblank validation, plus attempts to use unsupported sources should fail through dummy entries rather than touching invalid registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.h

Purpose: factory declaration for the DCN 3.0.3 interrupt service.

Important APIs/types/functions: declares `dal_irq_service_dcn303_create()`.

Control flow and integration: selected by ASIC-specific initialization when DCN303 register definitions are required.

State and persistence: no state.

Dependencies, risks, and test signals: includes the shared IRQ service contract; build tests catch C/header mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c

Purpose: DCN 3.1 IRQ service with low-priority DMCUB outbox support and a mostly four-pipe table despite source translation cases for six standard display IDs.

Important APIs and functions: `to_dal_irq_source_dcn31()` maps vblank, vline0, pflip, vupdate, HPD/RX, and `DMCUB_OUTBOX_LOW_PRIORITY_READY_INT`. `irq_source_info_dcn31` defines HPD/RX entries for instances 0 through 4, pflip entries for 0 through 3, vupdate/vblank/vline0 entries for 0 through 5 in the static table, and DMCUB OUTBOX1 support.

Control flow: source translation feeds `dal_irq_service_set/ack()`. HPD uses shared polarity-aware ack; DMCUB and display timing entries rely on generic MMIO masks.

State and persistence: immutable IRQ table and heap service. Hardware interrupt enable/ack bits persist in DMCUB, OTG, HUBPREQ, and HPD registers.

Dependencies and integration points: uses DCN31 register offsets/masks, DCE110 helpers, and the common DCN interrupt ID header. DMCUB outbox integrates firmware events with display interrupts.

Risks: hardware instance count is easy to misread because source translation lists six pipes while pflip table entries only cover four active HUBP entries. Connector count appears five HPD/RX entries in the table. Callers should respect resource caps rather than infer from enum ranges.

Test signals: hotplug on all exposed connectors, page flip on active HUBPs, DMCUB outbox interrupts, and vblank/vline events under modeset and DPMS transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.h

Purpose: public interface for constructing the DCN 3.1 IRQ service.

Important APIs/types/functions: declares `dal_irq_service_dcn31_create()`.

Control flow and integration: included by DCN31 ASIC factory/resource setup code.

State and persistence: header has no storage.

Dependencies, risks, and test signals: relies on the shared `irq_service.h` ABI; build coverage is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c

Purpose: DCN 3.1.4 IRQ service. It is structurally close to DCN31 but uses DCN 3.1.4 register offsets and a local `DCN_BASE__INST0_SEG2` override.

Important APIs and functions: `to_dal_irq_source_dcn314()` maps six standard display source IDs, HPD/RX by ext_id, and DMCUB low-priority outbox. The table defines HPD/RX for instances 0 through 4, pflip for 0 through 3, vupdate/vblank/vline0 for the supported OTG range, dummy placeholders for unsupported PFLIP5/6 and some vline1 entries, and DMCUB OUTBOX1.

Control flow: same shared path: source translation, table lookup, optional HPD-specific ack, otherwise generic register writes.

State and persistence: static const table and transient heap wrapper. Persistent state is in hardware interrupt enable/ack registers.

Dependencies and integration points: depends on DCN 3.1.4 offset/mask headers and the shared DCE110/IRQ framework. It is the binding point between DCN314 interrupt IDs and common DRM display interrupt handling.

Risks: base-segment overrides are brittle; wrong base values will compile but program incorrect registers. Instance count assumptions around HPD5/6, PFLIP5/6, and vline1 must match actual resource capabilities.

Test signals: runtime IRQ smoke tests on DCN314 hardware, especially DMCUB outbox, HPD, page flip, and vblank after modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.h

Purpose: declares the DCN 3.1.4 IRQ service factory.

Important APIs/types/functions: `dal_irq_service_dcn314_create()`.

Control flow and integration: used by ASIC setup to select the DCN314 mapper/table.

State and persistence: no state.

Dependencies, risks, and test signals: depends on shared IRQ types; compile coverage catches ABI drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c

Purpose: DCN 3.1.5 IRQ service variant, similar to DCN314 but with explicit DCN base segment definitions for segments 0 through 5.

Important APIs and functions: `to_dal_irq_source_dcn315()` maps standard six-ID display events, HPD/RX ext IDs, and DMCUB low-priority outbox. `irq_source_info_dcn315` covers HPD/RX instances 0 through 4, pflip 0 through 3, vupdate/vblank/vline0 entries, dummy unsupported sources, and DMCUB OUTBOX1. `dal_irq_service_dcn315_create()` is the factory.

Control flow: common IRQ source translation and table-driven set/ack. HPD ack uses `hpd0_ack()`, other real sources use generic register fields.

State and persistence: static const table and allocated service object. The base segment macros determine the persistent MMIO locations touched during enable/ack.

Dependencies and integration points: DCN 3.1.5 offset/mask headers, DCE110 IRQ helpers, DCN interrupt IDs, and the shared IRQ service. Integrates ASIC interrupt wiring with DC core.

Risks: hard-coded base segments are high risk when reused across steppings. Table entries for unsupported sources intentionally dummy out several enum slots; callers must not assume all six translated source IDs have active hardware entries.

Test signals: hardware IRQ tests for DMCUB outbox, HPD/RX, vblank, and page flips; build testing for register macro compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.h

Purpose: exposes the DCN 3.1.5 IRQ service constructor.

Important APIs/types/functions: declares `dal_irq_service_dcn315_create()`.

Control flow and integration: ASIC initialization includes this header to instantiate the DCN315 table.

State and persistence: no state in the header.

Dependencies, risks, and test signals: synchronized build with the C file is the key validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c

Purpose: DCN 3.2 IRQ service with support for additional OTG vertical interrupt lines (`VLINE1` and `VLINE2`) and DMCUB low-priority outbox.

Important APIs and functions: `to_dal_irq_source_dcn32()` maps standard vblank/vline0/pflip/vupdate/HPD/RX and DMCUB outbox source IDs. The table includes callback structs and macros for vline0, vline1, and vline2, although source translation only maps vertical interrupt 0 IDs directly. `dal_irq_service_dcn32_create()` is the factory.

Control flow: most callers use translation for interrupt dispatch; consumers that explicitly enable `DC_IRQ_SOURCE_DC*_VLINE1` or `DC*_VLINE2` can use table entries even though they are not returned by the current translator. Shared generic set/ack programs the OTG vertical interrupt control registers.

State and persistence: static const table and heap service object. VLINE1/2 enable state is persistent hardware state in OTG vertical interrupt 1/2 control registers.

Dependencies and integration points: DCN 3.2 register headers, DCE110 helpers, DCN IRQ source IDs, and shared IRQ service. Integration includes more precise scanline interrupt programming for timing-sensitive display operations.

Risks: mismatch between translation coverage and table coverage can confuse new call sites. Only four active pflip entries are present while enum ranges contain six. DMCUB OUTBOX1 mapping must match firmware usage.

Test signals: vline0/1/2 programming tests, vblank/page flip, DMCUB outbox notification, and HPD. Compile coverage catches missing vertical interrupt register symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.h

Purpose: factory header for DCN 3.2 IRQ service.

Important APIs/types/functions: declares `dal_irq_service_dcn32_create()`.

Control flow and integration: selected by DCN32 ASIC initialization to install the DCN32 IRQ source mapper and register table.

State and persistence: no state.

Dependencies, risks, and test signals: shared IRQ ABI dependency; build coverage validates the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c

Purpose: DCN 3.5 IRQ service using runtime register base offsets from `ctx->dcn_reg_offsets` instead of compile-time DCN base constants.

Important APIs and functions: `to_dal_irq_source_dcn35()` maps six display source IDs, HPD/RX ext IDs, and DMCUB low-priority outbox. Unlike earlier static-table files, `dcn35_irq_init_part_1/2()` populate a mutable `irq_source_info_dcn35` array at construct time through `REG_STRUCT`. `dal_irq_service_dcn35_create()` allocates and constructs the service.

Control flow: constructor obtains `struct dc_context *ctx = init_data->ctx`, then expands table-init macros against `ctx->dcn_reg_offsets`. Runtime dispatch and enable/ack then follow the shared path. HPD ack is polarity-aware; other sources use generic MMIO writes.

State and persistence: `irq_source_info_dcn35` is a static mutable table initialized at service construction. This creates global process/module state rather than per-service table storage. Hardware state is in the normal interrupt registers.

Dependencies and integration points: DCN 3.5 register headers, `dc_context` register-offset configuration, DCE110 helpers, and shared IRQ service. This design integrates with ASICs whose base addresses are supplied dynamically.

Risks: static mutable initialization is not obviously concurrency-safe if multiple services with different contexts were constructed. Reinitialization with a different `ctx->dcn_reg_offsets` would overwrite the global table. The table activates four pflip/vblank/vline/vupdate instances and HPD/RX 0 through 4, while the translator recognizes six source IDs.

Test signals: construct-time tests should verify computed register addresses, especially on platforms with non-default offsets. Runtime signals are hotplug, DMCUB outbox, vblank/vline/vupdate, and page flips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.h

Purpose: declares the DCN 3.5 IRQ service factory.

Important APIs/types/functions: `dal_irq_service_dcn35_create()`.

Control flow and integration: used by DCN35 factory code; the C file performs runtime table initialization from `dc_context`.

State and persistence: no header state.

Dependencies, risks, and test signals: shared IRQ ABI dependency. Build coverage catches signature drift; runtime validation belongs to the C implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c

Purpose: DCN 3.5.1 IRQ service. It is a runtime-offset variant like DCN35, with the same broad source categories and DMCUB low-priority outbox support.

Important APIs and functions: `to_dal_irq_source_dcn351()` maps display timing/flip IDs, HPD/RX ext IDs, and DMCUB outbox. `dcn351_irq_init_part_1/2()` populate `irq_source_info_dcn351` through `REG_STRUCT`, using `ctx->dcn_reg_offsets`. `dal_irq_service_dcn351_create()` is the exported constructor.

Control flow: construction initializes the static mutable table for the current context, then shared source translation and set/ack paths use it. HPD ack uses `hpd0_ack()`, while pflip, vblank, vupdate, vline0, and DMCUB outbox use generic register masks.

State and persistence: static mutable IRQ table initialized at construction time plus one heap service object. Hardware register state persists across enable/ack calls.

Dependencies and integration points: DCN 3.5.1 offsets/masks, dynamic `dc_context` base offsets, DCE110 helper callbacks, and the common IRQ service. It is integrated where DCN351 ASIC resources are created.

Risks: same mutable-global table risk as DCN35 and DCN36. Source translation includes six display IDs, but initialization enables only four pflip/vblank/vline/vupdate instances and HPD/RX 0 through 4. Incorrect offset initialization can target wrong registers.

Test signals: register-address sanity checks after construction, DMCUB outbox delivery, HPD/RX events, and display timing interrupts under modeset/page flip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.h

Purpose: compact factory header for DCN 3.5.1 IRQ service.

Important APIs/types/functions: declares `dal_irq_service_dcn351_create()`.

Control flow and integration: included by DCN351 ASIC setup code.

State and persistence: no storage; all state is in the C implementation and hardware registers.

Dependencies, risks, and test signals: depends on `../irq_service.h`; compile coverage validates the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c

Purpose: DCN 3.6 IRQ service. It follows the DCN351 runtime-offset construction pattern and provides low-priority DMCUB outbox plus standard display interrupt categories.

Important APIs and functions: `to_dal_irq_source_dcn36()` maps six vblank/vline0/pflip/vupdate IDs, HPD/RX ext IDs, and DMCUB outbox. `dcn36_irq_init()` populates the static mutable `irq_source_info_dcn36` table using `ctx->dcn_reg_offsets`. `dal_irq_service_dcn36_create()` allocates the service.

Control flow: constructor initializes table addresses from the current `dc_context`, then installs table and funcs. Runtime dispatch uses shared translation and table-driven generic ack/set, except HPD ack uses `hpd0_ack()`.

State and persistence: the static mutable table is process/module-wide and rewritten during construction. Hardware interrupt masks persist in registers. The heap service only stores pointers.

Dependencies and integration points: DCN 3.6 offsets/masks, DCE110 helpers, `dc_context` dynamic offsets, DCN interrupt source IDs, and shared IRQ service. It is the interrupt bridge for DCN36 display resources.

Risks: global mutable table can be corrupted by multiple contexts or unexpected repeated construction. Table initialization enables only a subset of translated instances, so resource capability checks are required. DMCUB OUTBOX1 mapping must match firmware IRQ routing.

Test signals: verify table address values after construction, HPD and DMCUB interrupts, and vblank/page flip behavior on active pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.h

Purpose: declares the DCN 3.6 IRQ service factory.

Important APIs/types/functions: `dal_irq_service_dcn36_create()`.

Control flow and integration: selected by DCN36 ASIC initialization.

State and persistence: no state.

Dependencies, risks, and test signals: depends on shared IRQ service types; build coverage catches mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c

Purpose: DCN 4.0.1 IRQ service with compile-time DCN 4.1 register offsets, DMCUB low-priority outbox, and active vline0/vline1/vline2 table entries.

Important APIs and functions: `to_dal_irq_source_dcn401()` maps six standard display source IDs, HPD/RX ext IDs, and DMCUB outbox. `irq_source_info_dcn401` has four HPD/RX entries, four pflip entries, four vblank/vupdate/vline0/vline1/vline2 entries, dummy entries for unsupported PFLIP5/6 and some vline slots, and DMCUB OUTBOX1. `dal_irq_service_dcn401_create()` constructs the service.

Control flow: source translation covers vline0 only; vline1/vline2 are exposed for explicit enable/ack by their `dc_irq_source` values. Generic set/ack writes register masks for most entries; HPD uses the shared polarity-aware ack helper.

State and persistence: static const table and heap wrapper. Hardware state is persisted in HPD, HUBPREQ, OTG, and DMCUB registers.

Dependencies and integration points: DCN 4.1.0 offset/mask headers, DCN IRQ source IDs, DCE110 helpers, and shared IRQ service. Integrates newer multi-vline timing sources with the common interrupt API.

Risks: `DCN_BASE__INST0_SEG2` override and compile-time base expansion are sensitive to register-map changes. Only four HPD/RX and pflip instances are active despite enum and translation cases for six IDs. VLINE1/2 availability should be tied to hardware resource caps.

Test signals: DCN401 hardware tests for vline0/1/2 programming, DMCUB outbox, HPD/RX, vblank, and page flips; build checks for DCN 4.1 register macro drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.h

Purpose: public DCN 4.0.1 IRQ service factory declaration.

Important APIs/types/functions: declares `dal_irq_service_dcn401_create()`.

Control flow and integration: used by DCN401 ASIC setup to select this mapper/table.

State and persistence: no state.

Dependencies, risks, and test signals: shared IRQ ABI dependency; compile coverage validates declaration consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c

Purpose: DCN 4.2 IRQ service for dal-dev, using DCN 4.2 register offsets and the same modern four-active-pipe table style as DCN401.

Important APIs and functions: `to_dal_irq_source_dcn42()` maps standard display IDs, HPD/RX ext IDs, and DMCUB low-priority outbox. `irq_source_info_dcn42` contains HPD/RX 0 through 3, pflip/vblank/vupdate/vline0/1/2 0 through 3, DMCUB OUTBOX1, and dummy placeholders for unsupported enum slots. `dal_irq_service_dcn42_create()` is the factory.

Control flow: constructor installs the static table and mapper. Runtime set/ack uses the shared service. VLINE1/2 table entries are available by explicit `dc_irq_source` use even though the translator maps only vertical interrupt 0 source IDs.

State and persistence: static const table and allocated service object. Hardware interrupt enable and clear bits persist in MMIO.

Dependencies and integration points: DCN 4.2 offsets/masks, DCE110 shared IRQ service declarations, and DCN interrupt source IDs. The header includes DCE110 service definitions instead of the local generic `irq_service.h`, which still provides the needed shared types through that path.

Risks: dal-dev comment suggests this may be branch- or development-specific. Include-path difference from other DCN headers should be kept intentional. Table/hardware resource mismatch around four active pipes and HPDs should be validated.

Test signals: compile for DCN42 register macros, then runtime HPD, DMCUB outbox, vblank, page flip, and vline0/1/2 tests on DCN4.2 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.h

Purpose: DCN4.2 IRQ service interface, marked as dal-dev only in the file comment.

Important APIs/types/functions: declares `dal_irq_service_dcn42_create()`. Unlike most sibling headers, it includes `../dce110/irq_service_dce110.h` instead of `../irq_service.h`.

Control flow and integration: factory callers include this header to instantiate the DCN42 IRQ service.

State and persistence: no state.

Dependencies, risks, and test signals: the include choice couples this header to the DCE110 service header exporting or including the shared IRQ types. Build coverage should catch include-order regressions; runtime validation belongs to the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/irq_service.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/irq_service.c

Purpose: shared implementation of the display core IRQ service. It provides construction/destruction, source lookup, generic enable/ack register programming, hardware-source translation dispatch, and special HPD ack helpers.

Important APIs and functions: `dal_irq_service_construct()` stores `dc_context`; `dal_irq_service_destroy()` frees the heap service; `dal_irq_service_set()` validates a source, acknowledges it first, then invokes a source-specific `set` callback or `dal_irq_service_set_generic()`; `dal_irq_service_ack()` invokes a source-specific `ack` callback or `dal_irq_service_ack_generic()`; `dal_irq_service_to_irq_source()` dispatches to the ASIC-specific mapper; `hpd0_ack()` and `hpd1_ack()` acknowledge HPD and update interrupt polarity from delayed sense state.

Control flow: ASIC-specific create functions allocate `struct irq_service`, call this constructor, and install table/function pointers. Runtime enable goes `set -> find table -> ack current pending state -> callback/generic write`. Runtime ack goes `ack -> find table -> callback/generic write`. Hardware interrupt decode goes through the installed `to_dal_irq_source`.

State and persistence: the object stores `ctx`, `info`, and `funcs`. Generic set/ack mutate persistent hardware register fields through `dm_read_reg()`/`dm_write_reg()`. The service does not copy the IRQ table, so table lifetime must exceed service lifetime.

Dependencies and integration points: depends on `dm_services.h`, logger interface, register helpers, DCE/DCE/DCN service headers, and `irq_service_interface.h`. It is used by all DCE/DCN ASIC interrupt service variants and by display hotplug/page-flip/vblank consumers.

Risks: `dal_irq_service_set()` always acknowledges before enabling/disabling, which can clear pending state unexpectedly if a caller only intended to mask. Dummy callbacks warn and assert, so selecting dummy entries in production indicates an invalid source/hardware mismatch. HPD polarity helpers use hard-coded HPD0/HPD1 field macros and rely on macro compatibility.

Test signals: unit-style MMIO mocks can verify mask/value writes; integration tests are hotplug polarity behavior, vblank/page-flip interrupt delivery, invalid-source logging, and destruction nulling the caller's pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/irq_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/irq_service.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/irq_service.h

Purpose: internal IRQ service ABI shared by DCE/DCN interrupt service implementations.

Important APIs/types/functions: defines `struct irq_source_info_funcs` with optional `set` and `ack`; `struct irq_source_info` with source IDs, enable/ack/status registers, masks, values, and callback pointer; `struct irq_service_funcs` with `to_dal_irq_source`; and `struct irq_service` with context, table, and function table. Declares shared construct/generic set/generic ack and HPD ack helpers.

Control flow and integration: ASIC files allocate an `irq_service`, call `dal_irq_service_construct()`, assign a `const struct irq_source_info *info` table and `irq_service_funcs`, then the public IRQ service interface uses those fields to enable, ack, and translate sources.

State and persistence: declares the layout for service state but owns no storage. The `info` pointer is not owned by the service, so table lifetime is an integration contract.

Dependencies and risks: depends on `include/irq_service_interface.h` and `irq_types.h`. Structure layout changes affect every ASIC-specific IRQ service file. Callback NULL semantics mean generic behavior; dummy callback pointers intentionally trip warnings/assertions.

Test signals: full driver build across DCE/DCN variants and focused tests for generic set/ack behavior using populated `irq_source_info` instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/irq_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq_types.h

Purpose: central IRQ type and source enumeration for AMD display core.

Important APIs/types/functions: defines `interrupt_handler`, opaque `irq_handler_idx`, `DAL_INVALID_IRQ_HANDLER_IDX`, `enum dc_irq_source`, `enum irq_type`, `DAL_VALID_IRQ_SRC_NUM`, `DAL_PFLIP_IRQ_SRC_NUM`, interrupt context and polarity enums, `DC_DECODE_INTERRUPT_POLARITY`, `struct dc_timer_interrupt_params`, and `struct dc_interrupt_params`.

Control flow and integration: ASIC mappers return `enum dc_irq_source` values from hardware IDs; consumers use these stable enum values to register, enable, and acknowledge interrupts. `enum irq_type` aliases the first source in grouped ranges so callers can derive per-pipe IRQ sources by adding instance offsets.

State and persistence: no runtime state. The enum order is persistent ABI within the driver and is explicitly required to match the base driver.

Dependencies and risks: depends on `os_types.h` and forward-declares `dc_context`. The largest risk is reordering or inserting enum values incorrectly, which would desynchronize table indexes, base-driver expectations, and range arithmetic. Range macros assume contiguous PFLIP, VUPDATE, VBLANK, VLINE, and underflow values.

Test signals: compile coverage across all IRQ table initializers, assertions for `DAL_VALID_IRQ_SRC_NUM`, and runtime checks that each hardware source maps to the intended enum. Any enum change should trigger broad ASIC IRQ regression testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/Makefile

Purpose: Kbuild fragment listing AMD display core link subcomponent object files and adding them to `AMD_DISPLAY_FILES`.

Important APIs/types/functions: defines object groups `LINK`, `LINK_ACCESSORIES`, `LINK_HWSS`, and `LINK_PROTOCOLS`; expands each through `$(addprefix $(AMDDALPATH)/dc/link/, ...)`; appends generated object paths to `AMD_DISPLAY_FILES`.

Control flow and integration: the parent AMD display build includes this Makefile so link detection, DPMS, resource, validation, accessories (`link_dp_trace.o`, `link_dp_cts.o`), hardware sequencing, and protocol modules are compiled into the driver.

State and persistence: build metadata only; no runtime state.

Dependencies and risks: depends on parent variables `AMDDALPATH` and `AMD_DISPLAY_FILES`. Missing an object here can compile out required link functionality; adding an object with missing source or unmet config guards breaks the driver build.

Test signals: kernel/driver build, link-time symbol resolution, and confirming new link module source files are represented in the correct object group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_cts.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_cts.c

Purpose: DisplayPort compliance test support for link training, automated test handling, PHY/video/audio test patterns, and preferred link/training override application.

Important APIs and functions: `dp_handle_automated_test()` reads `DP_TEST_REQUEST` and dispatches link training, link test pattern, audio test pattern, and PHY test pattern handling. `dp_set_test_pattern()` programs PHY or CRTC test patterns and DPCD receiver state. `dp_set_preferred_link_settings()` stores and optionally retrains a DP link. `dp_set_preferred_training_settings()` stores training overrides, updates MST branch bandwidth when relevant, and optionally retrains. Internal helpers include `get_link_rate_from_test_link_rate()`, `dp_retrain_link_dp_test()`, `dp_test_send_link_training()`, `dp_test_get_audio_test_data()`, `dp_test_send_phy_test_pattern()`, and `set_crtc_test_pattern()`.

Control flow: automated DP CTS starts from a DPCD test request. Link training requests ACK first, read requested lane count/rate, update verified link caps, and retrain. Link pattern requests delegate to `dm_helpers_dp_handle_test_pattern_request()`. Audio requests populate `link->audio_test_data`. PHY requests read requested pattern and lane adjustments, translate them to hardware and DPCD lane settings, then call `dp_set_test_pattern()`. For video patterns, `dp_set_test_pattern()` finds the OTG master pipe on the link, locks double-buffering or DMUB HW locks, updates color space/MSA/VSC infoframes, programs CRTC patterns, waits for vactive/vblank sequencing, and records test-pattern state.

State and persistence: mutates `link->verified_link_cap`, `cur_link_settings` through retraining paths, `link->audio_test_data`, `link->pending_test_pattern`, `link->test_pattern_enabled`, `link->current_test_pattern`, `preferred_link_setting`, and `preferred_training_settings`. It also changes hardware state: DPMS, CRTC enable, pixel clocks, HPO control, audio configuration, lane settings, test pattern generators, DPCD receiver registers, and stream colorimetry/infoframes.

Dependencies and integration points: depends on link resources, DPCD access, DP training, DP PHY, fixed VS/PE retimer support, DP capability helpers, DPMS, resource management, DM helpers, DMUB services, DMUB hardware lock manager, and clock manager. It integrates compliance test tools, MST bandwidth updates, HPO/DIO encoder switching, audio setup, and stream update paths.

Risks: this file performs invasive live-link reconfiguration. Incorrect locking or missing unlock paths can cause display corruption. It assumes a valid master pipe and stream for most pattern operations. `dp_retrain_link_dp_test()` caches streams before `dc_update_planes_and_stream()` because current state can be replaced. DPCD pattern translation must match DP spec revisions; wrong DPCD writes can fail compliance. Audio pattern period copying uses stream audio mode count and should be bounded against channel/array sizes.

Test signals: DP CTS automated test suites, PHY compliance equipment, link training at RBR/HBR/HBR2/HBR3/UHBR rates, 8b/10b and 128b/132b paths, fixed retimer platforms, MST branch bandwidth tests, audio test pattern verification, and visual/video pattern checks across ODM and non-ODM pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_cts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_cts.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_cts.h

Purpose: public interface for DisplayPort compliance test support.

Important APIs/types/functions: declares `dp_handle_automated_test()`, `dp_set_test_pattern()`, `dp_set_preferred_link_settings()`, and `dp_set_preferred_training_settings()`. Includes `link_service.h` for `dc_link`, `dc`, link settings, training overrides, and DP test-pattern types.

Control flow and integration: protocol and HPD/test handling code can include this header to respond to DP CTS DPCD requests or user/debug preferred-link overrides.

State and persistence: no header state. Declared functions mutate `dc_link` state and hardware/DPCD state in the C implementation.

Dependencies, risks, and test signals: API changes affect DP compliance, link training, and debug override callers. Build coverage plus DP CTS runtime testing validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_cts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_trace.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_trace.c

Purpose: lightweight DisplayPort link-training and eDP power trace helpers stored on `struct dc_link`.

Important APIs and functions: `dp_trace_init()` and `dp_trace_reset()` clear trace state; `dp_trace_detect_lt_init()` and `dp_trace_commit_lt_init()` clear separate detection/commit link-training traces; count helpers update total/fail/link-loss counts; result and logged-flag helpers track reporting state; timestamp setters/getters store LT start/end and eDP power on/off times; `dp_trace_source_sequence()` optionally writes a debug source-sequence value to DPCD.

Control flow: link-training code calls init/reset at lifecycle boundaries, increments totals/failures around LT attempts, records result and timestamps, and uses logged flags to avoid duplicate logging. eDP power code records power transition timestamps. Debug sequence writing is gated by `link != NULL` and `link->dc->debug.enable_driver_sequence_debug`.

State and persistence: all state is stored in `link->dp_trace`, including initialized flag, detect and commit traces, counts, timestamps, and eDP power timestamps. It persists for the link object lifetime until reset.

Dependencies and integration points: depends on `link_dp_trace.h`, DPCD protocol helpers, `dm_get_timestamp()`, and link-training result types. It integrates with DP training diagnostics and optional source-sequence debug DPCD writes.

Risks: functions generally assume non-NULL `link` except `dp_trace_source_sequence()`. `dp_trace_reset()` clears `is_initialized`, unlike detect/commit init helpers; callers must understand lifecycle. Timestamp values are only meaningful if the DC context clock is valid.

Test signals: link-training logs showing correct totals/failures/results, no duplicate logging when flags are set, eDP power timing traces, and DPCD source-sequence writes only when debug is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_trace.h

Purpose: header for DP trace helper functions.

Important APIs/types/functions: declares initialization/reset helpers, detect/commit LT trace reset, link-loss and LT count updates, logged-flag accessors, LT result/timestamp accessors, eDP power timestamp accessors, and `dp_trace_source_sequence()`.

Control flow and integration: included by DP link training, diagnostics, and eDP power sequencing code to update `dc_link.dp_trace` without exposing implementation details.

State and persistence: no header state; declared functions read/write `struct dc_link` trace fields.

Dependencies, risks, and test signals: includes `link_service.h` for link and training result types. Build coverage catches prototype drift; runtime signals are correct diagnostic output and debug DPCD behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_trace.h -->
