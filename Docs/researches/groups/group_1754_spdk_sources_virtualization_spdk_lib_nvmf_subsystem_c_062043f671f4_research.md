# Group Research: group_1754_spdk_sources_virtualization_spdk_lib_nvmf_subsystem_c_062043f671f4

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. The listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/subsystem.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/subsystem.c

This file implements SPDK NVMe-oF subsystem management. It owns subsystem creation/destruction, NQN validation, subsystem state transitions, host access control and DH-HMAC-CHAP key storage, listener association, namespace attachment/removal/hotplug handling, ANA state, controller ID allocation, reservation state, and PTPL persistence.

NQN and option handling:
- `nvmf_nqn_is_valid()` validates discovery NQN, UUID-form NQN, and `nqn.yyyy-mm.reverse.domain:user-string` form. It enforces max/min length, date syntax, RFC-style reverse-domain labels, and UTF-8 user strings.
- Subsystem, listener, and namespace option init/copy helpers are ABI-size-aware and use field-offset checks before reading newer fields.
- Defaults include model number `"SPDK bdev Controller"`, 32 namespaces for non-discovery subsystems, discovery subsystems with zero namespaces, ANA disabled, passthrough disabled, NSSR disabled, `dmrsl` as 1 GiB in 512-byte logical blocks, and `wzsl` as 16 MiB.

Subsystem lifecycle:
- `spdk_nvmf_subsystem_create_ext()` validates uniqueness and NQN syntax, allocates a subsystem ID from the target bit array, initializes lists, mutexes, controller ID range, listener ID bitmap, namespace and ANA arrays, serial/model strings, and inserts the subsystem into the target RB tree.
- Discovery subsystems are forbidden from having namespaces. Non-discovery subsystems get default namespace capacity when zero is supplied.
- `spdk_nvmf_subsystem_destroy()` requires inactive state, prevents duplicate destroy, removes listeners and hosts from transports, then delegates to `_nvmf_subsystem_destroy()`.
- Destruction removes all namespaces, cancels queued state changes with `-ECANCELED`, removes the subsystem from the target tree, frees arrays/bitmaps/mutexes, and supports async completion when active controllers delay final destruction.

State machine:
- Public transitions are start, stop, stop-for-destroy, pause, and resume.
- Requests are queued on `subsystem->state_changes`; only the first runs, and later requests start after completion.
- State changes move through intermediate states: activating, deactivating, pausing, or resuming.
- Each transition walks all target poll-group channels and calls the corresponding poll-group operation: add subsystem, remove subsystem, pause subsystem, or resume subsystem.
- On poll-group failure, the code attempts a reverse transition back to the original state before completing the caller callback with failure.
- State updates use atomic compare/exchange and include special handling for activation failure, resume failure, active-after-resuming, and stopping a paused subsystem.

Host access and authentication:
- Subsystems can allow any host or maintain an explicit host list.
- `spdk_nvmf_subsystem_add_host_ext()` validates host NQN, optionally duplicates DH-HMAC-CHAP host/controller keys, inserts the host, updates discovery log notices, and notifies each transport that implements host hooks.
- Controller DH-HMAC-CHAP keys are rejected unless a host key is also configured.
- `spdk_nvmf_subsystem_set_keys()` updates per-host keys with the same host-key/controller-key constraint.
- Host lookup and key retrieval are mutex-protected; returned keys are duplicated so callers do not borrow internal pointers.
- Per-namespace visibility can be restricted by host NQN through `spdk_nvmf_ns_add_host()` and `spdk_nvmf_ns_remove_host()`. Visibility changes update existing controllers and send namespace async notices.

Host disconnect:
- `spdk_nvmf_subsystem_disconnect_host()` walks all poll groups, disconnects qpairs whose controller host NQN matches, then repeatedly counts remaining qpairs until they disappear or a timeout expires.
- The timeout defaults to controller shutdown timeout when the caller supplies zero.
- Completion reports poll-group errors or `-ETIMEDOUT` when qpairs remain past the deadline.

Listener management:
- Listeners can only be added or removed while the subsystem is inactive or paused.
- Add validates that the target transport and transport listener already exist, allocates a subsystem listener, copies listener options, assigns a listener ID, initializes ANA state per namespace, optionally calls transport `listen_associate`, then inserts the listener.
- Discovery listeners trigger mDNS PRR updates and discovery log notices.
- Removal clears controller listener pointers, removes discovery/mDNS state, sends discovery notices, frees ANA state and socket implementation strings, and clears the listener ID bit.
- Discovery subsystem connections are still allowed on missing listeners with a deprecation warning, preserving older behavior.

Namespace management:
- `spdk_nvmf_subsystem_add_ns_ext()` attaches an SPDK bdev as an NVMe-oF namespace. It validates state, NSID, ANA group, duplicate slots, metadata layout, passthrough requirements, zone constraints, FDP compatibility, and volatile-write-cache consistency while controllers are attached.
- Namespaces claim the bdev with a dummy `"NVMe-oF Target"` bdev module, open it read/write with event callbacks, cache zcopy support, derive UUID/NGUID defaults from the bdev UUID, and mark zoned namespaces as ZNS.
- Zoned namespace additions enforce consistent zone append support and max zone append size across all zoned namespaces in the subsystem.
- FDP capability must match between namespaces; the first namespace sets the subsystem FDP flag.
- Namespace removal requires inactive or paused state, clears the slot, decrements ANA group membership, frees per-namespace host visibility entries, clears reservations, releases and closes the bdev, updates FDP/VWC state, calls transport namespace-remove hooks, sends namespace-change notices, and clears visibility on controllers.
- Bdev remove and resize events are handled by pausing the subsystem, applying namespace removal or namespace-change notification, then resuming. Resize pauses with NSID 0 because growth does not require quiescing a specific namespace.
- Empty subsystems advertise volatile write cache present so a cache-backed namespace can later be added while controllers are connected; otherwise VWC reflects attached backend bdevs.

Controller management:
- Controller IDs are generated within configurable min/max CNTLID bounds, wrapping through the range and skipping IDs already in use.
- Dynamic controllers may be rejected under per-listener duplicate-host policy when another controller on the same listener has the same Host ID.
- Static controllers reject duplicate CNTLID.
- Removing the last controller refreshes VWC presentation.

Persistent reservations:
- The file implements NVMe reservation register, acquire, release, report, preempt, and preempt-and-abort behavior at namespace scope.
- Reservation-modifying commands are serialized through `ns->reservations`; only the head request executes, and later requests wait until state propagation completes.
- Registrants are keyed by Host ID and reservation key, with a hard limit of `SPDK_NVMF_MAX_NUM_REGISTRANTS`.
- Reservation state tracks generation, current reservation key, reservation type, holder, PTPL flag, and registrant list.
- Register supports register, unregister, replace, IEKEY behavior, PTPL clear/persist, and conflict/status handling.
- Acquire supports normal acquire, preempt, and preempt-and-abort. It updates registrants, holder/type, removed-host notification lists, and preempt-abort tracking.
- Release supports release and clear, including reservation-released/preempted notifications to affected controllers.
- Report requires extended data format, fills generation/type/PTPL/registrant count, and emits registered-controller extended records with CNTLID, holder status, key, and Host ID.
- Reservation updates propagate to each poll group’s namespace reservation cache. Unexpected propagation failures abort because poll groups would otherwise hold inconsistent reservation state.
- Preempt-and-abort records preempted Host IDs, marks matching outstanding I/O as reservation-waiting on each poll group, polls until those I/Os drain, and times out after 10 seconds by clearing wait flags and completing with command interrupted.

PTPL persistence:
- Default PTPL support is file-backed JSON when a namespace has a `ptpl_file`.
- Load parses a JSON object containing PTPL state, reservation type/key, bdev UUID, holder UUID, and registrants.
- Restore validates that the persisted bdev UUID matches the current bdev, verifies the current reservation key appears among registrants when nonzero, recreates registrants, and restores holder semantics.
- Store writes current reservation state back as JSON; disabling PTPL clears the file content.
- `spdk_nvmf_set_custom_ns_reservation_ops()` lets users replace PTPL capability, load, and store operations.

ANA:
- ANA reporting can be set only while inactive through deprecated setters or at subsystem creation.
- `spdk_nvmf_subsystem_set_ana_state()` validates ANA support, listener existence, ANA group ID, and supported ANA states, updates one ANA group or all groups for a listener, increments the listener ANA change count, and walks poll groups to send ANA change notices to matching controllers.
- `spdk_nvmf_subsystem_get_ana_state()` returns listener ANA state for a specific ANA group.
- Namespace ANA group assignment updates group reference counts and notifies controllers of namespace changes.

Public accessor and compatibility surface:
- Provides subsystem iteration, host iteration, listener iteration, namespace iteration, namespace ID/bdev/opts getters, NQN getter, CNTLID range getters, min/max CNTLID setter, allow-any-host getter/setter, listener allow-any flag, and discovery checks.
- Several older APIs are retained with deprecation logging: subsystem create, serial/model getters and setters, type getter, max NSID getter, max namespace getter, and ANA reporting getter/setter.

Key invariants:
- Many mutating operations require inactive or paused subsystem state to avoid racing active I/O.
- `subsystem->mutex` protects host access-control lists, allow-any-host, and state-change queue insertion/removal.
- Reservation modifications must run on the subsystem thread, while request completion is sent back to the original poll-group thread.
- Transport hooks must stay consistent with subsystem host/listener/namespace changes; partial host-add failure rolls back prior transport additions.
- Namespace attachment must not expose incompatible metadata, zone append, FDP, passthrough, or VWC behavior to already connected controllers.
- PTPL restore must match the current bdev UUID before accepting persisted reservation state.

Filesystem/storage relevance:
- This is target-side remote block storage control-plane code. It does not implement a filesystem, but it defines how SPDK bdevs become NVMe-oF namespaces, how hosts discover and access them, how namespace hotplug and resize are surfaced, how ANA multipath state is advertised, and how persistent reservations protect shared block devices.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/subsystem.c -->