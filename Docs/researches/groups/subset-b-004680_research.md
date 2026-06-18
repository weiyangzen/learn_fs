# Research: subset-b-004680

Grouped research for Qualcomm IPA driver files under `sources/distributed-fs/ceph-client/drivers/net/ipa/`. Each section preserves the source path and is intended to split directly into the mapped source-tree-aligned research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_endpoint.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_endpoint.c

Purpose: implements IPA endpoint validation, register programming, enable/disable, suspend/resume, TX SKB submission, RX buffer replenishment, RX status parsing, and endpoint reset behavior. It is the main bridge between IPA endpoint configuration data and GSI channels.

Important APIs/functions: `ipa_endpoint_init()` validates endpoint tables, builds `ipa->name_map`, `ipa->channel_map`, and endpoint state bitmaps, and records filtering/modem TX state. `ipa_endpoint_config()` reads `FLAVOR_0` to validate hardware endpoint availability and direction. `ipa_endpoint_setup()` programs all defined AP endpoints; `ipa_endpoint_enable_one()` starts a GSI channel and enables RX replenish/suspend interrupts; `ipa_endpoint_disable_one()`, `ipa_endpoint_suspend_one()`, and `ipa_endpoint_resume_one()` reverse those states. `ipa_endpoint_skb_tx()` converts a netdev SKB into a GSI transaction, optionally linearizing excessive fragments. `ipa_endpoint_trans_complete()` and `ipa_endpoint_trans_release()` are the GSI callbacks for RX/TX ownership cleanup.

Control flow: initialization first checks mandatory endpoint roles and per-entry validity, then setup programs registers in `ipa_endpoint_program()`: checksum, NAT bypass, QMAP header insertion/extraction, DMA mode, aggregation/deaggregation, HOL blocking, resource group, sequencer, and status endpoint registers. TX submission allocates a GSI transaction, attaches the SKB/fragments, stores the SKB in `trans->data`, and commits with a doorbell depending on `netdev_xmit_more()`. RX enable starts replenishment; each replenish transaction owns a page. RX completion parses IPA status-prefixed aggregates when status is enabled, otherwise builds an SKB directly from the page.

State/persistence: endpoint state lives in `ipa->defined`, `ipa->set_up`, `ipa->enabled`, `ipa->available`, per-endpoint `replenish_flags`, `replenish_count`, `netdev`, and `skb_frag_max`. Hardware state is persistent until explicit reset/programming and depends heavily on IPA version. Delayed replenish work retries transient allocation starvation.

Dependencies/integration: depends on GSI transactions/channels, IPA register metadata, immediate command helpers, IPA interrupt TX_SUSPEND control, modem netdev RX delivery, power clock rate for HOL timers, table/filter validation, and RMNet/QMAP header formats.

Risks: most risk is version-specific bitfield programming and ordering around aggregation reset/suspend. RX status parsing trusts hardware length/status layout enough that malformed status can drop or mis-account packets. Replenishment uses page ownership through `trans->data`; bugs here leak pages or double free. `ipa_endpoint_modem_exception_reset_all()` and modem pause flow are crash recovery critical.

Test signals: probe/setup succeeds on supported IPA versions, netdev TX/RX counters move, RX replenish recovers after low memory, modem SSR resets routes/endpoints without wedging, suspend/resume preserves queues, and debug logs do not show invalid endpoint direction, active aggregation reset, or missing status endpoint errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_endpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_endpoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_endpoint.h

Purpose: declares the IPA endpoint model, endpoint names, configuration structures, replenish state flags, and public endpoint lifecycle/data-path APIs used by the rest of the driver.

Important APIs/types: `enum ipa_endpoint_name` gives stable logical names for AP and modem command/data endpoints. `struct ipa_endpoint_tx` describes TX sequencer and status destination. `struct ipa_endpoint_rx` describes RX buffer sizing, alignment, aggregation timeout/limits, EOF close, and HOL drop behavior. `struct ipa_endpoint_config` combines resource group, checksum, QMAP, aggregation, status, DMA mode, and direction-specific configuration. `struct ipa_endpoint` is the runtime object tying an IPA endpoint to a GSI EE/channel/event ring, default config, optional netdev, and RX replenish work.

Control flow: this header exposes the operations used by the probe/setup path (`ipa_endpoint_init`, `config`, `setup`, `enable_one`, `disable_one`, `teardown`, `exit`), runtime PM (`suspend`, `resume`), modem crash recovery (`modem_pause_all`, `modem_exception_reset_all`, `modem_hol_block_clear_all`), routing (`default_route_set/clear`), netdev TX (`skb_tx`), and GSI callbacks (`trans_complete`, `trans_release`).

State/persistence: persistent endpoint state is represented by bitmaps in the parent `struct ipa` plus fields in `struct ipa_endpoint`. `replenish_flags` separates whether RX replenishment is enabled from whether a replenish loop is active. `replenish_work` is global workqueue delayed state and must be cancelled during teardown.

Dependencies/integration: includes register/version definitions for sequencer and version-sensitive config values, Linux workqueue/types, and forward-declares GSI transactions, netdev, SKB, IPA, and data-table endpoint records.

Risks: the endpoint-name enum is used as an index into data arrays and `ipa->name_map`; ordering changes require coordinated config data updates. The direction-sensitive union in `ipa_endpoint_config` must match `toward_ipa`. RX buffer and aggregation comments document constraints enforced in the C file and data tables.

Test signals: compile-time users should include this header without circular dependencies, every required endpoint name maps to a non-empty config, runtime setup sets AP command/LAN/modem endpoint objects, and netdev endpoints have expected QMAP/checksum capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_endpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_gsi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_gsi.c

Purpose: provides the IPA-side callbacks consumed by the generic software interface (GSI) layer and a helper for detecting empty endpoint data entries.

Important APIs/functions: `ipa_gsi_trans_complete()` maps a GSI transaction back to the owning `struct ipa` and dispatches completion to `ipa_endpoint_trans_complete()`. `ipa_gsi_trans_release()` dispatches resource release to `ipa_endpoint_trans_release()`. `ipa_gsi_channel_tx_queued()` and `ipa_gsi_channel_tx_completed()` update Linux netdev byte queue accounting for endpoint-backed netdevices. `ipa_gsi_endpoint_data_empty()` treats AP entries with zero channel TLVs as unused config slots.

Control flow: GSI owns transaction progress; when it calls into IPA, this file uses `container_of(trans->gsi, struct ipa, gsi)` or `container_of(gsi, struct ipa, gsi)` and `ipa->channel_map[channel_id]` to find the endpoint. The endpoint module then handles SKB/page ownership and RX replenish. TX queue accounting is conditional on `endpoint->netdev`.

State/persistence: no durable state is owned here. It relies on `ipa->channel_map[]` being populated by endpoint init and netdev pointers being set by modem netdev start/stop.

Dependencies/integration: integrates `gsi_trans`, `gsi`, endpoint callbacks, endpoint config data from `ipa_data`, and netdev BQL helpers (`netdev_sent_queue`, `netdev_completed_queue`).

Risks: stale or missing `channel_map` entries would crash callback dispatch. Queue accounting assumes byte/count values passed by GSI match netdev-visible SKB traffic. Empty endpoint detection is part of endpoint validation semantics; changing it changes which data-table slots are ignored.

Test signals: GSI TX/RX completions reach endpoint handlers, netdev BQL counters advance and complete, and endpoint data arrays with empty AP slots are skipped without invalid endpoint errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_gsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_gsi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_gsi.h

Purpose: declares the IPA-to-GSI callback surface implemented by `ipa_gsi.c`.

Important APIs: transaction callbacks `ipa_gsi_trans_complete()` and `ipa_gsi_trans_release()` are invoked by GSI when transfer work finishes or resources are about to be freed. Channel accounting callbacks `ipa_gsi_channel_tx_queued()` and `ipa_gsi_channel_tx_completed()` report queued/completed byte counts for netdev queue management. `ipa_gsi_endpoint_data_empty()` centralizes the empty endpoint-data predicate used during endpoint initialization.

Control flow: the header has no logic, but it defines the callback contract: GSI gives only a transaction or `(gsi, channel_id)` pair; IPA must recover endpoint context via the parent `struct ipa` and channel map.

State/persistence: no state is defined here. It forward-declares `struct gsi`, `struct gsi_trans`, and endpoint-data records.

Dependencies/integration: included by GSI and IPA endpoint/data code to avoid direct knowledge of endpoint internals in the GSI layer.

Risks: callback signatures are part of the GSI/IPA integration boundary; count/byte semantics must stay aligned with GSI queue accounting.

Test signals: successful compilation of GSI callback registration, TX BQL accounting in modem netdev traffic tests, and endpoint init skipping only intended empty entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_gsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_interrupt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_interrupt.c

Purpose: manages the IPA hardware interrupt line, interrupt masks, TX_SUSPEND endpoint bits, wake IRQ registration, and threaded interrupt dispatch for IPA-specific events distinct from GSI events.

Important APIs/functions: `ipa_interrupt_init()` allocates the interrupt wrapper after resolving the `"ipa"` IRQ. `ipa_interrupt_config()` allocates endpoint suspend bitmap, disables all IPA IRQ types, requests the threaded IRQ, and configures device wakeup/wakeirq. `ipa_interrupt_enable()`/`disable()` update the IPA IRQ mask register. `ipa_interrupt_suspend_enable()`/`disable()` toggle per-endpoint TX_SUSPEND bits and enable the global TX_SUSPEND IRQ only while needed. `ipa_interrupt_simulate_suspend()` lets endpoint code invoke the suspend path for an aggregation hardware quirk.

Control flow: `ipa_isr_thread()` takes a runtime PM reference, reads `IPA_IRQ_STTS`, intersects pending bits with the enabled mask, and processes each set interrupt until no enabled pending bits remain. UC interrupts are cleared before calling `ipa_uc_interrupt_handler()`. TX_SUSPEND clears endpoint suspend status via `IRQ_SUSPEND_INFO`/`IRQ_SUSPEND_CLR` before clearing the IRQ. Disabled pending interrupts are logged at debug level and cleared.

State/persistence: `struct ipa_interrupt` persists IRQ number, enabled mask, per-endpoint suspend bitmap, and back pointer to `ipa`. Wakeup state is registered with the device until deconfig.

Dependencies/integration: depends on register definitions, runtime PM, Linux wakeirq helpers, endpoint availability bitmap, and the IPA microcontroller interrupt handler.

Risks: interrupt handling requires IPA power; PM failures currently warn and still put. The suspend bitmap and hardware bit updates must stay synchronized, especially the transition from zero to one enabled endpoint and back. On IPA v3.0, suspend clear/control behavior differs.

Test signals: IRQ request/wakeirq setup succeeds, UC interrupt tests reach `ipa_uc_interrupt_handler()`, suspend/resume wake works for RX endpoints, and disabled pending interrupts are cleared without storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_interrupt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_interrupt.h

Purpose: exposes the IPA interrupt lifecycle and control functions to the main, endpoint, power, and microcontroller code.

Important APIs: per-endpoint suspend interrupt control (`ipa_interrupt_suspend_enable`, `ipa_interrupt_suspend_disable`, `ipa_interrupt_simulate_suspend`), IRQ type masking (`ipa_interrupt_enable`, `ipa_interrupt_disable`), Linux IRQ line control (`ipa_interrupt_irq_enable`, `ipa_interrupt_irq_disable`), and lifecycle (`ipa_interrupt_init`, `config`, `deconfig`, `exit`).

Control flow: main probe first calls `ipa_interrupt_init()` before the full IPA object exists, then `ipa_interrupt_config()` after registers/power are available. Endpoint enable/disable drives TX_SUSPEND bits. System suspend/resume uses IRQ line disable/enable around forced runtime PM.

State/persistence: the opaque `struct ipa_interrupt` owns the IRQ, enabled IPA interrupt mask, and endpoint suspend bitmap. The header keeps it opaque so callers cannot mutate state directly.

Dependencies/integration: forward-declares `struct ipa`, `struct platform_device`, `struct ipa_interrupt`, and `enum ipa_irq_id` from the register header.

Risks: callers must distinguish IPA interrupt-type masking from Linux IRQ line enable/disable. Simulated suspend is intentionally a hardware workaround and should not be treated as a generic software event path.

Test signals: probe/deconfig ordering has no use-after-free, endpoint RX enable toggles suspend interrupts, and system suspend does not run the threaded IPA handler while runtime PM is forced off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_interrupt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_main.c

Purpose: is the platform driver entry point and top-level IPA orchestration layer. It probes hardware, selects firmware loading mode, initializes subsystems, configures registers/resources, performs setup with immediate commands, and tears everything down.

Important APIs/functions: `ipa_probe()` is the main initialization state machine. `ipa_setup()` initializes GSI, endpoint programming, AP command and exception endpoints, memory/table setup, default route, and QMI setup. `ipa_config()` handles powered register configuration, memory config, interrupts, microcontroller, endpoint/resource config, and SSR notifier registration. `ipa_remove()` shuts down modem traffic, setup, config, and all initialized subsystems. Hardware helpers program BCR, TX config, clock-on workarounds, COMP_CFG, QSB limits, aggregation/Qtime timing, hashing/cache behavior, and dynamic clock division. `ipa_firmware_load()` loads MDT firmware to reserved memory and authenticates via SCM.

Control flow: probe obtains matched `ipa_data`, resolves loader mode (`self`, `modem`, `skip`, legacy `modem-init`), initializes interrupt/power/IPA object/registers/memory/cmd/GSI/endpoints/table/SMP2P, takes runtime PM, runs `ipa_config()`, then either waits for modem SMP2P setup-ready or loads firmware and calls `ipa_setup()`. Setup enables the command endpoint first because later steps issue immediate commands, then enables the LAN exception endpoint and starts QMI handshake.

State/persistence: `struct ipa` stores device, version, power, interrupt, memory mappings, GSI, endpoint maps/bitmaps, modem route count, setup flag, and completion. Hardware register state persists until deconfig/reset; runtime PM autosuspend gates access.

Dependencies/integration: integrates Linux platform/of/module/firmware/PM APIs, Qualcomm SCM/MDT loader, IPA data tables, GSI, command, memory, tables, resources, modem, SMP2P, QMI, microcontroller, sysfs attribute groups, and register metadata.

Risks: probe has many staged resources; unwind ordering is critical. Firmware loader properties are mutually constrained, and SCM availability can defer probe. `ipa_remove()` can leak resources if modem stop repeatedly fails. Version-specific register programming must match the matched `ipa_data`.

Test signals: platform probe succeeds on listed compatibles, firmware load paths behave for self/modem/skip modes, sysfs groups appear, runtime PM autosuspends/resumes, modem setup completes after QMI, and remove/shutdown do not warn or leak initialized subsystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_mem.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_mem.c

Purpose: manages IPA local/shared memory definitions, validation, mapping, canary setup, DMA zero buffer, IMEM/SMEM IOMMU mappings, and immediate-command initialization/zeroing of AP/modem memory regions.

Important APIs/functions: `ipa_mem_find()` locates configured local-memory regions. `ipa_mem_init()` validates memory data, maps `"ipa-shared"`, maps optional SRAM/IMEM and SMEM through the IOMMU, and sets DMA mask. `ipa_mem_config()` reads `SHARED_MEM_SIZE`, bounds configured regions, allocates a coherent zero buffer, writes canaries, and checks UC event-ring alignment. `ipa_mem_setup()` uses immediate commands to initialize header memory and zero processing/modem memory, then programs `LOCAL_PKT_PROC_CNTXT`. `ipa_mem_zero_modem()` re-zeroes modem-owned regions after SSR.

Control flow: early init validates all config-table regions for version applicability, required presence, size/alignment, duplicate IDs, and table memory consistency. Config, under power, reconciles hardware-advertised shared memory with mapped resources and prepares DMA zeroing. Setup, after command endpoint is enabled, performs hardware memory initialization via GSI immediate commands.

State/persistence: `ipa->mem`, `mem_count`, `mem_virt`, `mem_addr`, `mem_size`, `mem_offset`, `zero_virt/addr/size`, `imem_iova/size`, and `smem_iova/size` persist until exit/deconfig. SMEM allocation itself is persistent until AP reboot and cannot be freed.

Dependencies/integration: depends on `ipa_data` memory tables, IPA table validation, immediate command DMA helpers, Linux DMA/IOMMU/memremap APIs, Device Tree resources, Qualcomm SMEM, and register field helpers.

Risks: memory offsets are hardware-visible and also sent to the modem via QMI; off-by-one or size-unit mistakes can corrupt shared tables. `ipa_mem_valid()` logs missing required regions but returns true, so required-region enforcement may be weaker than intended. IOMMU direct mappings assume physical-address IOVA layout. Canary writes do not appear to be checked later in this file.

Test signals: probe validates memory tables, `ipa_mem_config()` accepts hardware shared memory size, QMI init-driver request contains expected offsets, modem SSR zeroing succeeds, and no IOMMU unmap size warnings occur on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_mem.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_mem.h

Purpose: defines IPA local memory region IDs, memory-region descriptors, constraints, and public memory lifecycle/setup APIs.

Important APIs/types: `enum ipa_mem_id` lists all IPA-resident regions for UC shared/info, v4/v6 filter and route tables, modem/AP header and processing contexts, modem scratch, UC event ring, PDN config, statistics, AP filter tables, NAT table, and an end-marker pseudo-region. `struct ipa_mem` stores region ID, offset, size, and canary count. `IPA_MEM_MAX` limits individual region zero-buffer handling.

Control flow: exported functions split responsibilities: `ipa_mem_init/exit()` map resources and persistent external memory; `ipa_mem_config/deconfig()` validate hardware shared memory and allocate/free zero DMA buffer; `ipa_mem_setup()` issues one-time immediate-command initialization; `ipa_mem_zero_modem()` is called during modem crash recovery.

State/persistence: the header documents constraints that data tables must satisfy: offsets are relative to the IPA shared memory base, region sizes exclude canaries, offsets point after canaries, most regions are 8-byte aligned/sized, modem memory is 4-byte sized, and UC event ring is 1024-byte aligned.

Dependencies/integration: forward-declares `struct ipa`, `struct platform_device`, and `struct ipa_mem_data`; implementation interacts with `ipa_data`, IPA tables, QMI, and immediate commands.

Risks: region IDs are cross-file contracts used by memory setup, table setup, QMI messages, and SSR zeroing. Reordering or adding IDs requires synchronized data tables and version validation.

Test signals: all configured `ipa_mem_data` entries use valid IDs and alignments, required IDs are present for the IPA version, and modem/QMI boot succeeds with advertised memory windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_modem.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_modem.c

Purpose: implements the modem-facing RMNet raw-IP network device and modem subsystem restart handling for IPA.

Important APIs/functions: `ipa_modem_start()` allocates/registers `rmnet_ipa%d`, binds AP modem TX/RX endpoints to the netdev, and transitions modem state to running. `ipa_modem_stop()` unregisters the netdev and clears endpoint backpointers. `ipa_open()`/`ipa_stop()` enable and disable modem endpoints under runtime PM. `ipa_start_xmit()` validates QMAP SKBs, coordinates runtime PM and netdev queue stop/wake, and calls `ipa_endpoint_skb_tx()`. `ipa_modem_skb_rx()` injects received SKBs into the network stack. `ipa_modem_config()` registers a Qualcomm SSR notifier.

Control flow: netdev open powers IPA, enables TX then RX endpoints, and starts the queue. TX always stops the queue before runtime PM get to avoid racey wake/stop ordering; if power is inactive it returns `NETDEV_TX_BUSY` and resume work later wakes the queue. RX completion from endpoint code calls `ipa_modem_skb_rx()`. SSR before shutdown invokes crash cleanup: disable setup-ready IRQ, pause modem endpoints, clear HOL blocking, reset route tables, flush hash caches, reset modem exception endpoints, unpause, stop netdev, and zero modem memory.

State/persistence: `atomic_t ipa->modem_state` serializes start/stop transitions. `ipa->modem_netdev`, endpoint `netdev` pointers, and per-netdev `struct ipa_priv` persist while the modem netdev is registered. The SSR notifier persists until deconfig.

Dependencies/integration: depends on netdevice/RMNet/QMAP APIs, runtime PM, endpoint TX/RX lifecycle, table reset/flush, memory zeroing, SMP2P reset notification, microcontroller power, and qcom remoteproc SSR notifiers.

Risks: modem start/stop races are controlled by atomics but failed remove may intentionally leak if modem stop cannot complete. TX drops zero-length, wrong-protocol, or too-fragmented packets. Crash recovery ordering is critical to prevent modem endpoints from sending into stale route/status state.

Test signals: `rmnet_ipa` appears after QMI readiness, open/close enables endpoints, QMAP traffic updates stats, runtime resume wakes TX queue, and SSR cycles stop/restart modem traffic without endpoint or memory errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_modem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_modem.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_modem.h

Purpose: declares the modem netdev and SSR integration surface for the IPA driver.

Important APIs: `ipa_modem_start()` and `ipa_modem_stop()` create/destroy the modem network device; `ipa_modem_skb_rx()` is the endpoint RX delivery callback; `ipa_modem_suspend()` and `ipa_modem_resume()` coordinate endpoint suspend/resume with runtime PM; `ipa_modem_config()` and `ipa_modem_deconfig()` manage SSR notifier registration.

Control flow: QMI readiness calls start; driver remove and crash handling call stop; endpoint RX completion calls SKB RX; power runtime suspend/resume calls modem suspend/resume when the netdev exists.

State/persistence: state is opaque to this header and lives in `ipa_modem.c` via netdev private data and `ipa` fields.

Dependencies/integration: forward-declares `struct ipa`, `struct net_device`, and `struct sk_buff` for use by endpoint, power, main, and QMI code.

Risks: callers must respect lifecycle: no SKB RX after endpoints clear their `netdev` pointer, and start/stop are serialized in implementation.

Test signals: modem netdev starts after handshake, packet RX path compiles without circular dependencies, and runtime PM hooks can call suspend/resume safely when netdev is down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_modem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_power.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_power.c

Purpose: implements IPA clock/interconnect power management, runtime/system PM callbacks, and optional AOSS/QMP register-retention signaling.

Important APIs/functions: `ipa_power_init()` gets and sets the core clock, allocates interconnect bulk data, sets bandwidth, initializes retention QMP, and enables runtime PM autosuspend. `ipa_power_exit()` reverses that. `ipa_core_clock_rate()` supplies endpoint timing code. `ipa_power_retention()` sends AOSS QMP messages to enable/disable register retention. `ipa_pm_ops` wires system and runtime suspend/resume callbacks.

Control flow: runtime resume enables interconnects then the core clock, then resumes GSI/endpoints if setup is complete. Runtime suspend suspends modem/AP endpoints and GSI before disabling clock/interconnects. System suspend disables the IPA IRQ line before forcing runtime suspend; resume forces runtime resume and re-enables IRQ so threaded interrupt handling cannot race while PM runtime is disabled.

State/persistence: `struct ipa_power` owns device pointer, core clock, optional QMP handle, interconnect count, and flexible interconnect array. Runtime PM autosuspend delay is 500 ms. Power state is otherwise managed by PM core reference counts.

Dependencies/integration: depends on Linux clock, interconnect, runtime/system PM, Qualcomm AOSS QMP, endpoint suspend/resume, GSI suspend/resume, interrupt IRQ enable/disable, and modem resume queue wake behavior.

Risks: ordering matters: buses before clock on enable, endpoints/GSI before power off on suspend, IRQ disabled around forced runtime PM. Fixed interconnect bandwidth/clock rates come from `ipa_data`; wrong data can underpower traffic. Retention QMP failures are logged but not fatal.

Test signals: runtime autosuspend occurs without traffic loss, system suspend wakes through IPA IRQ when configured, core clock rate is nonzero during endpoint timer programming, and interconnect/clock errors unwind cleanly at probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_power.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_power.h

Purpose: declares IPA power management APIs and exposes `ipa_pm_ops` to the platform driver.

Important APIs: `ipa_core_clock_rate()` is used by endpoint HOL timer encoding on pre-Qtime IPA versions. `ipa_power_retention()` controls optional register retention across power collapse. `ipa_power_init()` and `ipa_power_exit()` own clock, interconnect, QMP, and runtime PM lifecycle. `ipa_pm_ops` supplies suspend/resume/runtime callbacks.

Control flow: main probe initializes power before allocating the full IPA structure because config needs clocks/interconnects ready. Main driver registers `ipa_pm_ops`; endpoint/main code uses runtime PM references around register and channel work.

State/persistence: the `struct ipa_power` type is opaque; persistence is managed in `ipa_power.c`.

Dependencies/integration: forward-declares `struct device`, `struct ipa`, and `struct ipa_power_data` from configuration tables.

Risks: consumers should not assume power is enabled merely because `ipa_power_init()` succeeded; register access still requires runtime PM active.

Test signals: platform driver binds with PM ops, runtime PM references allow register access, and endpoint timer calculations see the configured core rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi.c

Purpose: implements the AP/modem QMI handshake that gates normal IPA modem operation after IPA setup and after modem restarts.

Important APIs/functions: `ipa_qmi_setup()` creates a host QMI server for modem requests and a client lookup for the modem service. `ipa_qmi_teardown()` cancels pending init work and releases handles. Server handlers process `INDICATION_REGISTER` and `DRIVER_INIT_COMPLETE` requests. Client work sends `INIT_DRIVER` to the modem and waits up to one minute. `ipa_qmi_ready()` starts the modem netdev when modem driver and microcontroller readiness requirements are satisfied.

Control flow: when the modem QMI service appears, `ipa_client_new_server()` records its QRTR address and schedules `ipa_client_init_driver_work()`. That work builds an init request from IPA memory/endpoints, sends it, and marks `modem_ready` on response. The modem sends `DRIVER_INIT_COMPLETE`, setting `uc_ready`. On first boot, the modem must also register for and receive `INIT_COMPLETE`; subsequent boots only require modem and UC readiness. `server_bye` resets modem-ready and indication flags when the modem node disappears.

State/persistence: `struct ipa_qmi` stores server/client handles, modem QRTR address, work item, and readiness flags. The init request is a static structure reused after one-time field population, with `skip_uc_load` refreshed for each request.

Dependencies/integration: depends on Linux QRTR/QMI, QMI element-info tables, IPA local memory offsets, endpoint name map, modem netdev start, and UC loaded state.

Risks: the static init request assumes a single IPA instance and mostly immutable memory configuration. Stats size fields appear to add `ipa->mem_offset` to sizes, which should be scrutinized against modem protocol expectations. Handshake ordering is subtle: first boot requires an indication, later boots intentionally do not.

Test signals: QMI services register, init-driver requests contain expected TLVs, first modem boot waits for indication registration, subsequent SSR boot restarts after init-driver/UC ready, and modem netdev starts only once readiness is complete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi.h

Purpose: defines QMI handshake state embedded in `struct ipa` and declares setup/teardown functions.

Important APIs/types: `struct ipa_qmi` contains the QMI client handle, server handle, modem QRTR socket address, init-driver work item, and flags for `initial_boot`, `uc_ready`, `modem_ready`, `indication_requested`, and `indication_sent`. `ipa_qmi_setup()` starts the QMI service/lookup; `ipa_qmi_teardown()` stops them.

Control flow: called at the end of `ipa_setup()` after AP command/exception endpoints and local memory/table setup are ready. On modem crash/shutdown, QMI core bye handling resets the state and a new handshake begins when the modem service returns.

State/persistence: readiness flags persist across messages; `initial_boot` is cleared only after the first complete handshake. QMI handles persist while IPA setup is active.

Dependencies/integration: includes Linux QMI and workqueue support; implementation depends on IPA memory/endpoints, modem start, and QMI message definitions.

Risks: the header documents that the modem must not touch IPA hardware until handshake completion; callers should preserve setup ordering so the advertised memory and endpoint IDs are valid before QMI starts.

Test signals: setup creates both QMI handles, teardown cancels work safely, and SSR cycles reset only per-boot flags while preserving UC/initial boot semantics as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi_msg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi_msg.c

Purpose: provides QMI element-info descriptors that serialize and deserialize IPA QMI request, response, indication, and nested memory structures.

Important APIs/data: exported descriptor arrays include `ipa_indication_register_req_ei`, response descriptors for indication/register and driver-init-complete, `ipa_init_complete_ind_ei`, nested `ipa_mem_bounds_ei`, `ipa_mem_array_ei`, `ipa_mem_range_ei`, and full `ipa_init_modem_driver_req_ei`/`rsp_ei`.

Control flow: the QMI framework uses these arrays in `qmi_send_request()`, `qmi_send_response()`, `qmi_send_indication()`, and handler registration to map TLV type IDs to C structure offsets. Optional fields are represented by `QMI_OPT_FLAG` immediately followed by the value/struct with the same TLV type.

State/persistence: no mutable state; the arrays are constant protocol metadata. They must remain synchronized with `struct ipa_*` definitions and max message sizes in `ipa_qmi_msg.h`.

Dependencies/integration: depends on `linux/soc/qcom/qmi.h`, `offsetof`, `sizeof_field`, and the message structures in `ipa_qmi_msg.h`. Used exclusively by `ipa_qmi.c` and QMI core.

Risks: TLV IDs, field sizes, signed/unsigned enum types, or offsets that drift from the modem protocol will silently produce incompatible wire messages. Optional valid flags must match their value field TLV. Max receive/send sizes must cover encoded descriptors.

Test signals: QMI init-driver messages decode on the modem side, AP correctly decodes responses, QMI tracing shows expected TLV IDs, and protocol fuzz/compat tests do not report malformed element arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi_msg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi_msg.h

Purpose: defines the IPA QMI protocol message IDs, maximum encoded sizes, wire-facing C structures, platform/memory helper structures, and extern descriptors implemented by `ipa_qmi_msg.c`.

Important APIs/types: message IDs cover modem indication registration, AP init-driver request, AP init-complete indication, and modem driver-init-complete request. Structures include standard-response wrappers, `ipa_init_modem_driver_req` with platform, route/filter/header/modem memory, endpoint, UC load, hash table, and stats fields, and `ipa_init_modem_driver_rsp` with modem control/default endpoint information.

Control flow: `ipa_qmi.c` populates `ipa_init_modem_driver_req` from runtime IPA memory and endpoint state, sends it to the modem, responds to modem requests using response structures, and sends `ipa_init_complete_ind` when the modem has registered for it.

State/persistence: the header itself is static protocol definition. The request fields encode persistent shared-memory layout and boot-state (`skip_uc_load`) that affect modem initialization.

Dependencies/integration: includes Linux QMI types and is intentionally limited to `ipa_qmi` and descriptor code. It shares memory IDs/offset meaning with `ipa_mem.c`.

Risks: protocol structures are ABI-like. Changing field order/types or size constants without matching descriptor and modem firmware expectations breaks boot. Several fields use "end" as maximum table index rather than byte end; misuse can over-advertise memory.

Test signals: encoded message sizes stay within constants, QMI descriptor arrays compile against every field, modem accepts AP init-driver request, and first/subsequent boot handshakes follow documented message sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_reg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_reg.c

Purpose: selects the correct IPA register table for a hardware version, validates register IDs against version support, maps the `"ipa-reg"` MMIO resource, and exposes register metadata lookup.

Important APIs/functions: `ipa_reg()` warns on invalid register use for the active version and returns `reg(ipa->regs, reg_id)`. `ipa_reg_init()` resolves `ipa_regs_*` table by version, checks table size, maps the platform memory resource named `"ipa-reg"`, and stores `ipa->regs`/`reg_virt`. `ipa_reg_exit()` unmaps MMIO.

Control flow: probe sets `ipa->version` from match data, then calls `ipa_reg_init()`. All hardware configuration code later calls `ipa_reg()` before register offsets/field encodings. Version validation whitelists base registers and conditionally allows hash/cache, BCR/counter, Qtime timers, resource group, endpoint control/cache, and suspend-clear registers.

State/persistence: `ipa->regs` and `ipa->reg_virt` persist from init until exit. No register values are cached here.

Dependencies/integration: depends on generated/static `ipa_regs_v*` tables declared in `ipa_reg.h`, platform resources, `ioremap`, and common `reg.h` helpers used by all IPA modules.

Risks: incomplete or overly permissive version validation can allow invalid MMIO accesses or block legitimate registers. The v5.2 path reuses v5.0 register metadata. Any caller that ignores a NULL `ipa_reg()` result can fault after a warning.

Test signals: probe maps `"ipa-reg"`, all supported compatibles select a non-NULL register table, register validation warnings are absent in normal boot, and deconfig unmaps once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_reg.h

Purpose: defines the register ID namespace, per-register field IDs, hardware enum values, IPA IRQ IDs, extern register tables, and register lifecycle APIs.

Important APIs/types: `enum ipa_reg_id` lists global, resource, endpoint, and IRQ registers. Field enums cover `COMP_CFG`, `CLKON_CFG`, route/default pipe, shared memory, QSB limits, hash/cache, timers, resource groups, endpoint configuration, status, and IRQ microcontroller fields. Hardware value enums define checksum offload, NAT type, endpoint mode, aggregation enable/type, sequencer types, pulse granularities, and IPA IRQ bit positions. `ipa_reg()`, `ipa_reg_init()`, and `ipa_reg_exit()` are the public lookup/lifecycle APIs.

Control flow: modules use `ipa_reg()` plus `reg_offset`, `reg_n_offset`, `reg_encode`, `reg_decode`, and `reg_bit` to avoid open-coded bit masks. Parameterized registers use per-endpoint, per-resource, or per-unit offsets through register metadata.

State/persistence: no mutable state is stored in the header, but enum values are cross-module contracts and sometimes hardware ABI values.

Dependencies/integration: includes common `reg.h`; register tables are version-specific and selected by `ipa_reg.c`. Endpoint, main, memory, interrupt, resource, table, UC, and command code all depend on these IDs.

Risks: enum ordering/indexing must match field-mask arrays in `ipa_regs_v*`. Hardware value enums must not be renumbered. Version comments are documentation only; runtime validity is enforced in `ipa_reg.c`.

Test signals: all field IDs used by code are present in the selected register table, boot logs have no invalid register warnings, and register programming produces expected hardware behavior across supported IPA versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_resource.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_resource.c

Purpose: programs IPA internal source and destination resource group limits from version-specific configuration data.

Important APIs/functions: `ipa_resource_config()` validates resource data and writes all source and destination resource type limits. Helpers split group pairs across `{SRC,DST}_RSRC_GRP_{01,23,45,67}_RSRC_TYPE` registers, encoding X/Y min/max limits.

Control flow: `ipa_config()` calls this after table and endpoint config. Validation ensures source and destination group counts are nonzero and at most eight, and that unsupported trailing groups have zero limits. For each resource type, group 0/1 are programmed first, then 2/3, 4/5, and 6/7 if supported.

State/persistence: no software state is retained. Register programming persists in hardware until reset/reconfiguration; there is intentionally no deconfig.

Dependencies/integration: depends on `ipa_data` resource tables, `IPA_RESOURCE_GROUP_MAX`, register metadata, and MMIO helpers. Endpoint configuration separately assigns each endpoint to a resource group.

Risks: group count and resource-type array sizes must match hardware/register table expectations. Wrong limits can starve endpoints or over-allocate scarce internal resources. No runtime verification reads the values back.

Test signals: `ipa_resource_config()` returns zero during probe, traffic does not stall under load, resource group registers match data-table expectations, and invalid nonzero limits beyond group count fail probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_resource.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_resource.h

Purpose: exposes the resource configuration entry point used by top-level IPA config.

Important APIs: `ipa_resource_config(struct ipa *ipa, const struct ipa_resource_data *data)` validates and programs source/destination resource group limits. The comment says there is no deconfig path because hardware defaults or later reset cover cleanup.

Control flow: called once during `ipa_config()` after endpoint/table configuration and before modem notifier setup.

State/persistence: no header-visible state. Hardware programmed limits persist after the function returns.

Dependencies/integration: forward-declares `struct ipa` and `struct ipa_resource_data` from data tables.

Risks: the documented return text says true/false, but the function actually returns `0` or a negative errno. Callers correctly use errno semantics.

Test signals: compile-time callers treat return as errno, probe fails on invalid resource data, and supported data tables configure without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_smp2p.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_smp2p.c

Purpose: implements SMP2P communication with the modem for two events: modem-loaded GSI setup readiness and modem queries about AP IPA power state during crash/shutdown scenarios.

Important APIs/functions: `ipa_smp2p_init()` acquires SMEM state bits, installs the `"ipa-clock-query"` IRQ, registers a high-priority panic notifier, and optionally installs `"ipa-setup-ready"` when the modem initializes GSI. `ipa_smp2p_exit()` frees IRQs/notifier and releases any held power reference. `ipa_smp2p_irq_disable_setup()` prevents future setup-ready handling during remove/crash. `ipa_smp2p_notify_reset()` clears notification state for the next modem boot.

Control flow: on clock-query IRQ or panic, `ipa_smp2p_notify()` records whether runtime PM is currently active with `pm_runtime_get_if_active()`, writes the enabled bit, then writes the valid bit for the modem to observe. If the modem loaded GSI firmware, the setup-ready IRQ takes runtime PM, calls `ipa_setup()`, and releases power. On panic, if IPA power is on, UC panic handling is invoked.

State/persistence: `struct ipa_smp2p` stores SMEM states/bits, IRQ numbers, last power_on/notified flags, setup-disabled flag, mutex, and panic notifier. A runtime PM reference may be held after notifying the modem that power is on and is released on reset/exit.

Dependencies/integration: uses Qualcomm SMEM state, platform IRQs, panic notifier chain, runtime PM, `ipa_setup()`, and IPA UC panic handling.

Risks: power notification intentionally can hold a PM reference; failure to reset/release leaks active power. Setup-ready IRQ must be disabled before teardown to avoid concurrent `ipa_setup()`. Panic notifier priority is deliberately high.

Test signals: modem-init boot completes only after setup-ready IRQ, clock-query updates both SMEM bits in order, SSR reset clears bits and releases PM ref, and driver removal cannot race a new setup-ready interrupt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_smp2p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_smp2p.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_smp2p.h

Purpose: declares the SMP2P lifecycle and control APIs for top-level IPA probe/remove and modem crash paths.

Important APIs: `ipa_smp2p_init()` sets up SMEM state bits and interrupts, with `modem_init` selecting whether the setup-ready IRQ is required. `ipa_smp2p_exit()` tears it down. `ipa_smp2p_irq_disable_setup()` blocks modem-triggered setup. `ipa_smp2p_notify_reset()` resets modem power-state notification bits after crash handling.

Control flow: main probe calls init after table init and before powered config; remove/crash paths disable setup-ready before teardown; modem before-powerup notification calls notify reset.

State/persistence: implementation-owned state is opaque and attached to `ipa->smp2p`.

Dependencies/integration: forward-declares `struct platform_device` and `struct ipa`; uses bool from Linux types.

Risks: callers must pass the correct `modem_init` value from firmware-loader selection. Disabling setup-ready is a teardown interlock, not a full SMP2P shutdown.

Test signals: probe succeeds with both AP-loaded and modem-loaded GSI firmware modes, setup-ready IRQ exists only when required, and reset notification is called during modem SSR boot sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_smp2p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_sysfs.c

Purpose: defines read-only sysfs attribute groups attached to the IPA platform device for hardware version, MAP offload type, and modem endpoint IDs.

Important APIs/data: exported groups are `ipa_attribute_group`, `ipa_feature_attribute_group`, `ipa_endpoint_id_attribute_group`, and `ipa_modem_attribute_group`. Attribute show helpers render IPA version, RX/TX offload (`MAPv4` before IPA v4.5 and `MAPv5` after), endpoint IDs for AP modem RX/TX, and legacy modem endpoint paths.

Control flow: the platform driver lists these groups in `dev_groups`, so sysfs files are created during device registration. Endpoint ID visibility checks `ipa->name_map[]` and hides attributes for undefined endpoints. Show functions recover `struct ipa` from `dev_get_drvdata()`.

State/persistence: no mutable state; sysfs output reflects `ipa->version` and endpoint mappings initialized during probe.

Dependencies/integration: depends on Linux device/sysfs helpers, `ipa_version`, endpoint names, and top-level platform driver group registration.

Risks: show functions assume drvdata and endpoint mappings are valid while attributes exist. The version string returns `"0.0"` for unexpected versions, which should not happen if match data is valid.

Test signals: sysfs exposes `/version`, `/feature/rx_offload`, `/feature/tx_offload`, `/endpoint_id/modem_rx`, `/endpoint_id/modem_tx`, and legacy `/modem/*_endpoint_id` with values matching configured endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_sysfs.h

Purpose: declares the sysfs attribute groups registered by the IPA platform driver.

Important APIs/data: extern declarations for the base IPA attribute group, feature group, endpoint ID group, and legacy modem group.

Control flow: `ipa_main.c` includes this header and installs the groups in the platform driver's `dev_groups`; `ipa_sysfs.c` provides the definitions and show callbacks.

State/persistence: no state is defined here. Attribute values are computed dynamically from `struct ipa`.

Dependencies/integration: relies on Linux `struct attribute_group` being visible through included sysfs/device headers in users.

Risks: adding/removing groups requires coordinating this header, definitions, and platform-driver group list.

Test signals: driver builds with all externs resolved and sysfs group registration succeeds during platform device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_sysfs.h -->
