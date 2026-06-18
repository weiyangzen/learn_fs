# subset-b-005253 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/dc395x.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/dc395x.c

Purpose: implements the Tekram DC395/DC315 PCI SCSI host adapter driver for TRM-S1040 ASIC cards. It binds the PCI device, reads or repairs the adapter EEPROM configuration, programs SCSI/DMA registers, exposes a SCSI mid-layer host, scans devices, queues `scsi_cmnd` requests, handles SCSI phase interrupts, and completes commands back to the block/SCSI stack.

Important APIs/types/functions: the file owns `struct AdapterCtlBlk`, `struct DeviceCtlBlk`, `struct ScsiReqBlk`, `struct NvRamType`, and hardware scatter/gather entries. The SCSI host contract is `dc395x_driver_template` with `queuecommand`, `sdev_init`, `sdev_destroy`, `eh_abort_handler`, `eh_bus_reset_handler`, and `show_info`. PCI entry points are `dc395x_init_one()` and `dc395x_remove_one()`. Core command paths include `dc395x_queue_command_lck()`, `build_srb()`, `send_srb()`, `waiting_process_next()`, `start_scsi()`, `dc395x_interrupt()`, `dc395x_handle_interrupt()`, phase handlers such as `data_in_phase0/1()`, `msgin_phase0/1()`, `disconnect()`, `reselect()`, `srb_done()`, `request_sense()`, and reset helpers. EEPROM and hardware setup are handled by `check_eeprom()`, `eeprom_override()`, `adapter_init_params()`, `adapter_init_chip()`, `set_basic_config()`, and the `trms1040_*` serial EEPROM helpers.

Control flow: PCI probe enables the device, allocates a `Scsi_Host` with adapter-private storage, reserves I/O and IRQ resources, reads EEPROM/default/module-parameter settings, allocates per-SRB hardware SG tables, initializes the chip, registers the SCSI host, and starts scanning. Device discovery calls `dc395x_sdev_init()` to allocate a DCB per target/LUN. Queueing pulls an SRB from the adapter free list, DMA-maps the command payload into TRM-S1040 SG format, and either starts selection immediately or links the SRB into a per-device waiting list. Interrupt handling acknowledges SCSI interrupt status, dispatches selection timeout/disconnect/reselection/reset events, or runs a two-stage phase state machine: phase0 reconciles previous transfer state and phase1 programs the next hardware transfer. Completion unmaps DMA, handles autosense for CHECK CONDITION, updates inquiry-derived queueing/negotiation state, sets result/residual fields, returns the SRB to the free list, calls `scsi_done()`, and schedules the next waiting request.

State and persistence: persistent hardware configuration is the TRM-S1040 serial EEPROM represented by `struct NvRamType`; `check_eeprom()` rewrites defaults when checksum validation fails and applies module-wide overrides. Runtime state lives in adapter, device, and request blocks: free/waiting/going SRB lists, per-target tag masks, active DCB/SRB, sync/wide negotiation state, device maps, timers, reset deadline, and cached EEPROM values. The driver has no filesystem persistence, but it may modify adapter EEPROM when defaults are repaired.

Dependencies and integration: integrates with PCI, I/O port access, IRQs, DMA mapping, timers, SCSI mid-layer, SPI transport helpers for SDTR/WDTR message formatting, `/proc/scsi`-style `show_info`, and kernel scatterlist mapping helpers. `dc395x.h` supplies hardware register definitions and protocol constants. It is legacy parallel SCSI hardware code with direct register programming rather than a firmware mailbox interface.

Risks: the driver relies on many timing-sensitive busy waits and register side effects, including EEPROM bit-banging, SCSI phase counters, FIFO cleanup, and reset delays. `build_srb()` uses `BUG_ON(nseg < 0)` for DMA-map failure, which can panic instead of failing a command. Some error paths are suspicious: DMA interrupt error handling sets `acb = NULL` under `#else`, `doing_srb_done()` calls `scsi_done(cmd)` in one waiting-list path rather than `scsi_done(p)`, and aborting already-started commands is unimplemented. EEPROM repair writes hardware NVRAM from in-kernel defaults. Wide-transfer padding and last-four-byte PIO paths are hardware-bug workarounds and need regression care.

Test signals: build with `CONFIG_SCSI_DC395x` as module and built-in, probe/remove on matching PCI IDs, IRQ sharing, `scsi_scan_host()` discovering targets/LUNs, INQUIRY updating tag queue state, sync/wide negotiation messages, queued I/O under disconnect/reselect, autosense after CHECK CONDITION, abort/reset error handling, proc `show_info`, unload with active devices, and EEPROM checksum fallback on a test adapter or emulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/dc395x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/dc395x.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/dc395x.h

Purpose: defines the constants and hardware register map used by the Tekram DC395/DC315 TRM-S1040 SCSI host adapter driver. It provides queue limits, request state bits, target/adapter feature flags, SCSI phase/status constants, EEPROM configuration bits, and all SCSI/DMA/general register offsets and bit masks consumed by `dc395x.c`.

Important APIs/types/functions: this header has no callable functions. Important exported definitions include `DC395x_MAX_*` queue and SG sizing limits, SRB state flags such as `SRB_WAIT`, `SRB_DATA_XFER`, `SRB_COMPLETED`, and negotiation flags, status constants like `H_SEL_TIMEOUT` and `SCSI_STAT_SEL_TIMEOUT`, `struct ScsiInqData`, inquiry capability masks, TRM-S1040 PCI/SCSI/DMA/general register offsets, SCSI command opcodes such as `SCMD_SEL_ATN` and `SCMD_DMA_IN`, DMA control bits, NVRAM pins, and EEPROM target/adapter option masks like `NTC_DO_SYNC_NEGO`, `NTC_DO_TAG_QUEUEING`, and `NAC_POWERON_SCSI_RESET`.

Control flow: there is no runtime control flow in the header. The constants drive control-flow decisions in the C file, especially phase-machine dispatch, DMA setup, EEPROM parsing, negotiation enablement, queue depth selection, reset handling, and adapter initialization.

State and persistence: no state is stored by the header, but many definitions describe persistent EEPROM layout and semantics. `NTC_*` and `NAC_*` bits decide per-target sync/wide/tag/disconnect behavior and adapter scan/reset behavior after `dc395x.c` reads or repairs EEPROM.

Dependencies and integration: depends on kernel integer typedefs already available to the including C file and SCSI peripheral type constants from SCSI headers. It is tightly coupled to `dc395x.c`; changing values can affect direct hardware register programming and on-card EEPROM interpretation.

Risks: register and bit definitions are hardware contracts, so off-by-one offsets or wrong masks can corrupt DMA, SCSI bus phases, termination control, or EEPROM contents. Queue limits must stay consistent with `struct AdapterCtlBlk` fixed arrays and SG allocation logic. The header includes legacy aliases and comments for unsupported paths, increasing the chance that cleanup changes alter hardware behavior.

Test signals: compile coverage of `dc395x.c`, probe-time register programming on TRM-S1040 hardware, SCSI phase transitions, EEPROM read/write checksum behavior, sync/wide negotiation, and SG boundary behavior indirectly validate these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/dc395x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Kconfig

Purpose: declares the SCSI device-handler configuration menu and the individual multipath hardware-handler symbols for RDAC, HP/Compaq MSA, EMC CLARiiON, and generic SPC-3 ALUA devices.

Important APIs/types/functions: Kconfig symbols are `SCSI_DH`, `SCSI_DH_RDAC`, `SCSI_DH_HP_SW`, `SCSI_DH_EMC`, and `SCSI_DH_ALUA`. `SCSI_DH` is a boolean parent depending on `SCSI`; each implementation symbol is tristate and depends on both `SCSI_DH` and `SCSI`.

Control flow: there is no runtime flow. At configuration time, enabling `SCSI_DH` exposes the handler choices; each tristate decides whether the matching `scsi_dh_*.c` object is built in, built as a module, or omitted.

State and persistence: state is the kernel `.config` selection. The chosen symbols persist in build artifacts and determine which handlers can be registered with the SCSI device-handler core.

Dependencies and integration: integrates the device-handler directory into the SCSI Kconfig hierarchy. The handlers are intended for dm-multipath style path management where vendor-specific failover commands and `prep_fn` access-state filtering are needed.

Risks: missing or too-weak dependencies surface as compile failures or handlers that can be configured without the SCSI device-handler core. Since `SCSI_DH` defaults to `n`, distributions must intentionally enable it or multipath hardware handlers will be unavailable.

Test signals: Kconfig coverage with `allmodconfig`, `allyesconfig`, and `SCSI=n`; module build checks for each handler; runtime `scsi_register_device_handler()` success when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Makefile

Purpose: maps SCSI device-handler Kconfig symbols to their implementation objects.

Important APIs/types/functions: Kbuild entries compile `scsi_dh_rdac.o`, `scsi_dh_hp_sw.o`, `scsi_dh_emc.o`, and `scsi_dh_alua.o` for the corresponding `CONFIG_SCSI_DH_*` symbols.

Control flow: no runtime flow exists. Kbuild evaluates the `obj-$(CONFIG_...)` assignments and links or modules the selected handlers.

State and persistence: build state comes from `.config`; the Makefile itself does not carry runtime state.

Dependencies and integration: this is the build integration point for the adjacent Kconfig options and the SCSI device-handler source files. It expects each object to register and unregister itself with the SCSI device-handler core at module init/exit.

Risks: object-name drift or missing entries make a selectable handler fail to build or silently not appear. Built-in combinations should preserve registration ordering assumptions.

Test signals: build all four handlers as modules and built-ins; inspect generated modules or vmlinux link for the selected object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_alua.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_alua.c

Purpose: implements the generic SPC-3 ALUA SCSI device handler for multipath. It discovers target port group support, groups paths by VPD device identity and target port group ID, reports and changes target port group states through RTPG/STPG commands, filters I/O on unusable path states, and reacts to ALUA-related sense codes.

Important APIs/types/functions: central types are `struct alua_port_group`, `struct alua_dh_data`, and `struct alua_queue_data`. SCSI command helpers are `submit_rtpg()`, `submit_stpg()`, and `alua_tur()`. Discovery and grouping are handled by `alua_check_tpgs()`, `alua_check_vpd()`, `alua_alloc_pg()`, and `alua_find_get_pg()`. Runtime state changes are driven by `alua_rtpg()`, `alua_stpg()`, `alua_rtpg_queue()`, `alua_rtpg_work()`, and `alua_check()`. The registered handler `alua_dh` provides `attach`, `detach`, `prep_fn`, `check_sense`, `activate`, `rescan`, and `set_params`.

Control flow: attach allocates per-device handler data, checks that the device is a disk with TPGS support, extracts VPD target port group descriptors, attaches the device to a shared port group, and queues an initial RTPG. `prep_fn` allows optimized, active, LBA-dependent, and transitioning states while failing standby/unavailable/offline states quietly. Sense handling detects ALUA transition and state-change unit attentions, marks or rechecks the port group, and requests retry or mid-layer requeue. Activation allocates callback data and queues work that first refreshes RTPG, then issues STPG if needed, then retries RTPG until a stable usable state or timeout is reached. Work executes on `kaluad_wq` and may switch to another path in the same group if RTPG returns temporary unavailability.

State and persistence: all state is in memory. Global `port_group_list` holds refcounted `alua_port_group` objects protected by `port_group_lock`, per-port-group locks, RCU `dh_list` links, delayed work, retry interval/expiry, access state, supported states, preference, and optimization flags. Per-device `alua_dh_data` stores its RCU port-group pointer, init error, disabled retry marker, and init mutex. No disk persistence exists.

Dependencies and integration: depends on SCSI VPD helpers (`scsi_vpd_lun_id()`, `scsi_vpd_tpg_id()`, `scsi_device_tpgs()`), `scsi_execute_cmd()`, TEST UNIT READY, SCSI sense interpretation, RCU/kref/list locking, workqueues, and dm-multipath through the SCSI device-handler callbacks. The `optimize_stpg` module parameter and `set_params` allow policy tuning.

Risks: concurrency is subtle because port groups are shared across paths with krefs, RCU, delayed work, and path disabling during retry. Incorrect reference or list handling can race detach with queued RTPG work. RTPG buffer parsing trusts descriptor lengths from devices after resizing and needs malformed-array coverage. The handler deliberately allows I/O during transitioning, which depends on upper layers retrying correctly. Vendor deviations around extended RTPG headers are handled by fallback flags but remain compatibility-sensitive.

Test signals: ALUA-capable multipath arrays or scsi_debug-style ALUA tests should verify attach, VPD parsing, RTPG extended-header fallback, STPG activation, transition timeout/retry behavior, access-state propagation to all paths, sense-code handling, `optimize_stpg`/`set_params`, detach while work is queued, module unload, and non-disk/TPGS-none rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_alua.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_emc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_emc.c

Purpose: implements the EMC CLARiiON AX/CX/FC-family SCSI device handler for active/passive multipath failover. It identifies CLARiiON service processor state through inquiry/VPD page data, blocks I/O on non-owned LUN paths, and activates paths by sending CLARiiON trespass MODE SELECT commands.

Important APIs/types/functions: `struct clariion_dh_data` stores handler flags, command buffer, LUN state, port, default SP, and current SP. Important helpers include `parse_sp_info_reply()`, `parse_sp_model()`, `clariion_std_inquiry()`, `clariion_send_inquiry()`, `send_trespass_cmd()`, `trespass_endio()`, `clariion_check_sense()`, `clariion_prep_fn()`, `clariion_activate()`, and `clariion_set_params()`. The registered `clariion_dh` supplies attach/detach/check_sense/activate/prep_fn/set_params callbacks.

Control flow: attach allocates per-device state, parses standard inquiry data to decide whether short trespass is needed for older FC models, reads VPD page `0xC0`, parses SP ownership/failover mode, updates `sdev->access_state`, and stores handler data. `prep_fn` fails requests unless the LUN is owned by this path. Activation refreshes VPD page `0xC0`; if the LUN is not owned, it builds either a short MODE SELECT(6) or long MODE SELECT(10) page `0x22` trespass request, sends it, then refreshes SP state and invokes the completion callback. Parameter changes update short-trespass and honor-reservation flags, optionally sending a new trespass if the path is already owned.

State and persistence: per-device memory caches the latest CLARiiON LUN/SP state and policy flags. Firmware-side ownership changes persist on the storage array after successful trespass; the handler itself has no persistent local storage. Static trespass templates are copied into the per-device buffer before command execution, but their reservation bit is modified before copy.

Dependencies and integration: depends on SCSI inquiry/VPD, `scsi_execute_cmd()`, MODE SELECT(6/10), sense handling, `sdev->access_state`, and the SCSI device-handler core used by multipath. It integrates with arrays that report failover mode through EMC-specific VPD layout.

Risks: the code mutates static `short_trespass`/`long_trespass` arrays when setting the honor-reservations bit, so parameter changes can have process-wide effects that are not fully reversible. VPD page offsets are vendor-specific and sensitive to malformed or short buffers. The code recognizes ALUA failover mode but remains a CLARiiON trespass handler, so mixed firmware behavior needs care. Passive-path sense handling intentionally returns `SUCCESS` in some cases to let upper layers bypass paths.

Test signals: attach on supported and unsupported CLARiiON models, short versus long trespass selection, VPD page `0xC0` parsing for owned/bound/unbound states, activation from passive to owned, honor-reservation parameters, array-copy/NDU sense handling, `prep_fn` quiet failure on passive paths, and module registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_emc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_hp_sw.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_hp_sw.c

Purpose: implements a minimal HP/Compaq MSA 1000 active/passive SCSI device handler for firmware that requires START STOP UNIT to activate a passive path. It detects active versus passive paths using TEST UNIT READY sense data and blocks I/O on passive paths until activation succeeds.

Important APIs/types/functions: `struct hp_sw_dh_data` stores path state, retry settings, and the SCSI device pointer. Core helpers are `hp_sw_tur()`, `tur_done()`, `hp_sw_start_stop()`, `hp_sw_prep_fn()`, `hp_sw_activate()`, `hp_sw_bus_attach()`, and `hp_sw_bus_detach()`. The registered handler `hp_sw_dh` provides attach/detach/activate/prep_fn callbacks.

Control flow: attach allocates handler data, sends TEST UNIT READY, marks the path active on success or passive on NOT READY `04/02`, and rejects unknown states. `prep_fn` fails requests quietly unless `path_state` is active. Activation repeats TEST UNIT READY and, when the path is passive, sends START STOP UNIT with retries for switch-over-in-progress sense `04/03`; it then calls the multipath completion callback.

State and persistence: per-device in-memory state records only current path state and retry values. START STOP UNIT changes array path ownership externally, but no local persistence exists. `retry_cnt` is present in the struct but not actively used by the implementation.

Dependencies and integration: depends on SCSI command execution, TEST UNIT READY, START STOP UNIT, sense parsing, failure-definition retry handling, request `RQF_QUIET`, and the SCSI device-handler core. It is intended for dm-multipath active/passive path activation on old MSA firmware.

Risks: support is intentionally narrow and keyed to specific sense codes. No explicit `check_sense` callback means runtime path-state changes are learned only through activation/attach, not arbitrary I/O sense. The driver stores retry fields with limited use, and activation is synchronous around command execution. Unsupported firmware may be misdetected or fail I/O until multipath retries another path.

Test signals: TEST UNIT READY success and NOT READY `04/02` paths, START STOP UNIT activation with retry on `04/03`, `prep_fn` blocking passive paths, attach rejection for unknown TUR failures, callback result propagation, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_hp_sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_rdac.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_rdac.c

Purpose: implements the LSI/Engenio/NetApp E-Series RDAC SCSI device handler for multipath. It identifies arrays and LUN ownership from vendor VPD pages, groups paths by controller, blocks passive paths, and performs failover by sending RDAC MODE SELECT pages that transfer selected LUN ownership.

Important APIs/types/functions: important data structures include RDAC MODE SELECT page layouts (`rdac_pg_legacy`, `rdac_pg_expanded`), vendor inquiry page structures (`c2`, `c4`, `c8`, `c9`), `struct rdac_controller`, `struct rdac_dh_data`, and `struct rdac_queue_data`. Discovery helpers are `get_lun_info()`, `initialize_controller()`, `check_ownership()`, and `set_mode_select()`. Failover and execution use `rdac_failover_get()`, `queue_mode_select()`, `send_mode_select()`, `mode_select_handle_sense()`, and `rdac_activate()`. Runtime filtering and sense handling are `rdac_prep_fn()` and `rdac_check_sense()`.

Control flow: attach allocates per-path handler data, reads VPD `0xC8` for LUN and array ID/name, reads VPD `0xC4` for controller index and joins or creates a shared controller object, reads VPD `0xC9` for ownership/mode/preference/access state, reads VPD `0xC2` to select MODE SELECT(6) or MODE SELECT(10), then stores handler data. Activation refreshes ownership; in RDAC mode it transfers unowned LUNs, and in IOSHIP mode it transfers only unowned preferred paths. Transfers are queued on a controller work item so multiple LUN activations can be coalesced into one MODE SELECT command. `prep_fn` rejects I/O unless the cached path state is active. Sense handling retries quiescence/reset conditions and marks paths passive on current-ownership illegal requests.

State and persistence: global `ctlr_list` holds refcounted controller objects with array ID/name, controller index, host pointer, MODE SELECT format choice, queued work state, pending activation list, and RCU-linked handler list. Per-device `rdac_dh_data` caches LUN number, mode, active/passive state, ownership, preference, and vendor page data. The array persists ownership changes after MODE SELECT; local state is in memory only.

Dependencies and integration: depends on SCSI VPD page retrieval, SCSI command execution, mode select, workqueues, krefs, RCU lists, spinlocks, `sdev->access_state`, request quiet failure, and the SCSI device-handler core. It integrates with dm-multipath active/passive path activation and priority hints.

Risks: controller objects are shared and manipulated under both `list_lock` and per-controller `ms_lock`; detach must flush queued work and synchronize RCU to avoid stale handler pointers. The MODE SELECT payload uses vendor-defined table indices and assumes LUN fits the selected table. VPD page parsing copies UTF-16-like array labels by taking every second byte and trusts page-specific lengths. `rdac_init()` registers the handler before allocating the workqueue, briefly exposing a handler without a queue if allocation fails later.

Test signals: supported array attach using VPD pages `0xC8`, `0xC4`, `0xC9`, and `0xC2`; MODE SELECT(6) versus MODE SELECT(10) selection; coalesced failover for multiple queued LUNs; RDAC/AVT/IOSHIP mode behavior; passive-path `prep_fn`; sense handling for quiescence and ownership failures; detach while failover work is queued; module init failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_rdac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/dmx3191d.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/dmx3191d.c

Purpose: implements a small PCI SCSI host driver for the Domex DMX3191D card by adapting the generic NCR5380 core to the card's I/O-port register layout. It provides probe/remove glue, resource ownership, and SCSI host registration while delegating command processing to `NCR5380.c`.

Important APIs/types/functions: macros define `NCR5380_read()` and `NCR5380_write()` using `inb/outb` against `hostdata->base`, and disable DMA by mapping the NCR5380 DMA hooks to `*_none` helpers. The `dmx3191d_driver_template` points at `NCR5380_info`, `NCR5380_queue_command`, `NCR5380_abort`, and `NCR5380_host_reset`. PCI callbacks are `dmx3191d_probe_one()` and `dmx3191d_remove_one()`, registered through `dmx3191d_pci_driver`.

Control flow: PCI probe enables the device, reserves an 8-byte I/O region from BAR0, allocates a `Scsi_Host` with `NCR5380_hostdata`, sets the base I/O address and `NO_IRQ`, initializes the generic NCR5380 core, possibly resets the bus, registers the host, and scans it. Remove unregisters the host, exits the NCR5380 core, releases the SCSI host, frees the I/O region, and disables the PCI device.

State and persistence: runtime state is limited to SCSI host private NCR5380 data, especially the base I/O port. There is no persistent configuration or firmware state managed by this file.

Dependencies and integration: depends on PCI, legacy port I/O, SCSI host mid-layer, and the in-tree generic NCR5380 implementation included directly after macro specialization. The card is operated without interrupts because the driver comments indicate it does not appear to raise `pdev->irq`.

Risks: including `NCR5380.c` directly makes macro contracts critical. Polling/no-IRQ operation can be slow and sensitive to generic core assumptions. Resource cleanup is straightforward but relies on matching probe failure labels. This is legacy hardware with limited automated test coverage.

Test signals: build with the generic NCR5380 core, probe on the Domex PCI ID, successful I/O-region reservation, host scan without IRQ, command execution through polling, abort/host-reset behavior, and clean remove/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/dmx3191d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/Kconfig

Purpose: declares the Emulex/Broadcom `SCSI_EFCT` Fibre Channel target-mode driver configuration symbol.

Important APIs/types/functions: the sole symbol is `SCSI_EFCT`, a tristate named "Emulex Fibre Channel Target". It depends on `PCI`, `SCSI`, `TARGET_CORE`, and `SCSI_FC_ATTRS`, and selects `CRC_T10DIF`.

Control flow: no runtime flow exists. At configuration time, enabling the symbol includes the efct target driver and its supporting libraries in the build.

State and persistence: persistent state is the selected `.config` value. The symbol controls whether the PCI target-mode driver can register at runtime.

Dependencies and integration: ties efct to PCI hardware discovery, the SCSI stack, LIO target core, Fibre Channel transport attributes, and DIF CRC support.

Risks: dependency drift can produce build failures in `efct_driver.c`, target integration, or FC transport code. Selecting `CRC_T10DIF` is required for protection-information support used elsewhere in the efct stack.

Test signals: Kconfig builds with dependencies enabled/disabled, `CONFIG_SCSI_EFCT=m/y`, and link checks for target-core and FC transport symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/Makefile

Purpose: defines the composite `efct` module/object layout for the Emulex Fibre Channel target driver and its local protocol libraries.

Important APIs/types/functions: `obj-$(CONFIG_SCSI_EFCT) := efct.o` builds the composite object. `efct-objs` includes driver, I/O, SCSI target, transport, hardware queue, LIO, unsolicited-frame code, `libefc` discovery/state-machine files, and `libefc_sli/sli4.o`.

Control flow: no runtime flow exists. Kbuild links the listed objects into one `efct` module or built-in object when `CONFIG_SCSI_EFCT` is enabled.

State and persistence: no runtime state is stored here; build graph state follows `.config`.

Dependencies and integration: this file is the build integration point connecting `efct/`, `libefc/`, and `libefc_sli/` into one driver. `efct_driver.c` provides PCI/module entry points, while the other objects provide target I/O, FC discovery, SLI-4 hardware, and LIO integration.

Risks: missing or misordered object entries can cause unresolved symbols or partially linked driver functionality. Since this is a composite module, new cross-file helpers require Makefile updates.

Test signals: module and built-in builds of `CONFIG_SCSI_EFCT`, modpost symbol checks, and load-time availability of PCI, libefc, hardware, and LIO entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_driver.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_driver.c

Purpose: implements the top-level Broadcom/Emulex EFCT PCI Fibre Channel target driver lifecycle. It registers target/FC transport support, probes supported PCI adapters, maps BARs, initializes hardware and MSI-X interrupts, attaches the transport/libefc target stack, optionally performs firmware updates, handles PCI error recovery, and tears everything down on remove/module exit.

Important APIs/types/functions: global `efct_devices` tracks allocated devices. `efct_device_init()` and `efct_device_shutdown()` initialize/release target and FC transport driver-wide state. Per-device lifecycle is handled by `efct_device_alloc()`, `efct_device_attach()`, `efct_device_detach()`, `efct_device_free()`, `efct_pci_probe()`, and `efct_pci_remove()`. Hardware/transport integration uses `efct_device_interrupts_required()`, `efct_setup_msix()`, `efct_teardown_msix()`, `efct_intr_thread()`, `efct_efclib_config()`, and the `efct_libefc_templ` callback table. Firmware support is in `efct_request_firmware_update()`, `efct_firmware_write()`, `efct_fw_write_cb()`, and `efct_fw_reset()`. PCI AER hooks are `efct_pci_io_error_detected()`, `efct_pci_io_slot_reset()`, and `efct_pci_io_resume()`.

Control flow: module init initializes the target/FC transport layer, then registers the PCI driver. Probe enables memory access, sets bus mastering/MWI, requests BAR regions, allocates a NUMA-local `struct efct`, maps memory BARs, sets 64-bit DMA masks, asks hardware setup for the required event queues/MSI-X vectors, registers threaded IRQs then disables them, and attaches the device. Attach allocates and initializes xport, configures libefc with hardware WWNs/FCFI/SLI information, enables IRQs, marks the device attached, and requests a firmware update. IRQ threads call `efct_hw_process()` for the vector index. Remove detaches xport/libefc, tears down MSI-X, unmaps BARs, frees the device, releases PCI regions, and disables the PCI device. PCI error recovery detaches or aborts hardware I/O, resets/re-enables PCI state, rebuilds MSI-X, and reattaches the device.

State and persistence: `struct efct` instances hold PCI device, BAR mappings, MSI-X contexts, attached flag, target/xport/libefc/hardware state, logmask, model, filter, lookup xarray, SCSI host pointer, and debugfs handles. Firmware image changes are persistent on the adapter after successful write/reset/reboot; local runtime state is rebuilt on attach. The module parameter `logmask` is read-only at runtime.

Dependencies and integration: depends on PCI/MSI-X/AER, DMA coherent allocation, firmware loader, completions, `efct_hw`, `efct_xport`, `efct_scsi`, `efct_unsol`, libefc, SLI-4 helpers, LIO target core, FC transport registration, and CRC/DIF support selected by Kconfig. The libefc function template connects FC discovery callbacks to hardware mailbox/ELS/BLS and target node creation/deletion.

Risks: firmware update runs during attach and may reset firmware, detaching and reattaching the device from inside the attach sequence. `efct_firmware_write()` reuses one completion result object across chunks and assumes each async callback completes cleanly before the next write. Probe failure cleanup must handle partially mapped BARs and partially initialized MSI-X. PCI slot reset/resume call detach/attach without checking all intermediate return codes. Global `efct_devices` is modified without an explicit lock in this file.

Test signals: build/link with all efct composite objects, probe/remove on supported Lancer G6/G7 IDs, BAR mapping and 64-bit DMA setup, MSI-X allocation and threaded interrupt processing, xport attach/detach, libefc initialization/destruction, FC target registration, firmware-not-found and firmware-update paths, AER frozen/permanent/slot-reset flows, module unload after active target sessions, and debug/logmask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_driver.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_driver.h

Purpose: defines the EFCT driver's shared top-level device structure, constants, interrupt context, firmware-write result container, includes, and external device-list declaration used by the EFCT PCI/target stack.

Important APIs/types/functions: key constants include `EFCT_DRIVER_NAME`, `EFCT_DRIVER_VERSION`, `EFCT_DEFAULT_FILTER`, `EFCT_OS_MAX_ISR_TIME_MSEC`, FC SG/DIF limits, watermark defaults, `EFCT_PCI_MAX_REGS`, `MAX_PCI_INTERRUPTS`, and `FW_WRITE_BUFSIZE`. `struct efct_intr_context` links an interrupt vector index to an `efct` device. `struct efct` stores PCI/BAR/MSI-X state, target transport state, libefc pointer, SCSI host pointer, hardware object, filter/topology, node lookup xarray, timers/debug fields, and runtime policy values. `struct efct_fw_write_result` bridges asynchronous firmware-write callbacks to synchronous waits.

Control flow: the header has no direct runtime flow. Its fields are populated during PCI probe and device attach, consumed by interrupt handlers, xport/libefc/hardware code, firmware update paths, and cleanup routines.

State and persistence: `struct efct` is the main in-memory state container for each adapter. It does not itself persist state, but includes fields controlling firmware upgrade requests and target I/O behavior. `efct_fw_write_result` carries transient completion state for one firmware write operation.

Dependencies and integration: includes Linux module/debugfs/firmware headers, common EFC definitions, libefc, and local `efct_hw`, `efct_io`, and `efct_xport` contracts. The external `efct_devices` list is defined in `efct_driver.c` and provides global device enumeration within the driver.

Risks: this structure is shared across many EFCT objects, so field lifetime and ownership must match attach/detach ordering. Fixed interrupt and BAR array sizes must stay aligned with hardware setup. Watermark and SGL constants affect I/O throttling and target resource sizing elsewhere in the module.

Test signals: compile coverage across all `efct-objs`, probe-time initialization of every required field, interrupt context indexing, firmware write completion, target session creation, teardown after partial attach failure, and static analysis for structure ownership and bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_driver.h -->
