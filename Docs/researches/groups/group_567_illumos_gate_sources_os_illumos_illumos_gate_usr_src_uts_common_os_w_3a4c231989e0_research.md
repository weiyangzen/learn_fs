# Group Research:

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/watchpoint.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/watchpoint.c

Kernel implementation of procfs-style user watchpoints. It modifies page protections for watched areas, detects watchpoint faults, coordinates trap-before/trap-after delivery, and installs copy-operation wrappers so kernel copy paths honor user watchpoints during system calls.

Key elements:
- `watch_copyops` replaces normal thread copy operations with watch-aware `copyin`, `copyout`, string copy, `fuword`, `suword`, and `physio` wrappers.
- `pr_do_mappage()` is the core protection remapping routine. It walks `as->a_wpage`, reference-counts temporary map-ins per watched page, sets `WP_NOWATCH`, updates segment protections through `SEGOP_SETPROT`, and coordinates with `holdwatch()`/`continuelwps()` through `p_maplock` and `p_mapcnt`.
- `setallwatch()` reapplies watch protections after a stopped LWP resumes and frees `watched_page` records whose watched area counts dropped to zero.
- `pr_is_watchpage_as()` / `pr_is_watchpage()` test whether a virtual address falls on a page whose current protections were reduced for watchpoint handling.
- `pr_is_watchpoint()` checks `p->p_warea` AVL ranges for read, write, or execute watchpoint overlap and returns the trap code plus trap-after and length metadata.
- `do_watch_step()` temporarily maps a watched page, enables single-step with `prstep()`, and records the pending trap-after state in `lwp_watch`.
- `undo_watch_step()` reverses trap-after single-step state, unmaps any temporary page mappings, and fills `k_siginfo_t` for `SIGTRAP`/`FLTWATCH` if needed.
- `sys_watchpoint()` handles watchpoints hit inside system-call copy paths: it can stop for `FLTWATCH`, post `SIGTRAP`, temporarily mask other signals, and reports whether a debugger cleared the condition.
- `watch_xcopyin()`, `watch_xcopyout()`, `watch_copyinstr()`, and `watch_copyoutstr()` split operations by page and watched-area boundaries, temporarily restore access through `pr_mappage()`, perform `_noerr` copies under `on_fault()`, and invoke `sys_watchpoint()` at the right point for trap-before/trap-after.
- `watch_fuword*()` and `watch_suword*()` provide scalar load/store variants with the same watchpoint semantics.
- `watch_physio()` splits multi-iovec physical I/O so each user iovec can be checked and temporarily mapped separately.
- `wa_compare()`, `wp_compare()`, and `pr_find_watched_area()` provide AVL ordering and overlap lookup helpers for watched areas/pages.
- `watch_enable()` / `watch_disable()` install or remove the watch copyops on a thread and toggle `TP_WATCHPT`.
- `copyin_nowatch()`, `copyout_nowatch()`, `fuword*_nowatch()`, `suword*_nowatch()`, `watch_disable_addr()`, and `watch_enable_addr()` provide internal ways to perform accesses while temporarily disabling watchpoint trapping for a range.

Dependencies:
- Uses process and LWP state from `proc_t`, `klwp_t`, `lwp_watch`, `p_warea`, `p_wprot`, `p_maplock`, and `p_mapcnt`.
- Uses address-space and segment APIs: `as_segat`, `AS_LOCK_ENTER`, `SEGOP_GETPROT`, `SEGOP_SETPROT`, `seg_rw`, and VM protection flags.
- Uses procfs/watchpoint types and trap codes from `sys/procfs.h`, `sys/watchpoint.h`, and fault/signal infrastructure.
- Wraps low-level copy helpers such as `copyin_noerr`, `copyout_noerr`, `copyinstr_noerr`, `copyoutstr_noerr`, `fuword*_noerr`, and `suword*_noerr`.
- Interacts with scheduler/stop logic through `holdwatch()`, `stop()`, `continuelwps()`, `prstep()`, `ISSIG_FAST()`, and `schedctl_finish_sigblock()`.

Research notes:
- Page remapping pairs are nestable; correctness depends on `wp_kmap[]`/`wp_umap[]` reference counts and paired `pr_mappage()`/`pr_unmappage()` calls.
- The implementation explicitly compensates for MMU limitations by mapping execute and write requests with read permission as needed.
- `pr_is_watchpoint()` may adjust the fault address to the first watched byte inside a larger fault/copy range.
- Copy wrappers return `EFAULT` when watchpoint processing is aborted, when the debugger does not clear the condition, or when `lwp_sysabort` is set.
- The `watch_copyin()` parameter names are misleading relative to normal copyin direction, but it forwards to `watch_xcopyin()` and participates in the copyops vector contract.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/watchpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/zone.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/zone.c

Core kernel implementation of illumos zones. It owns zone lifecycle state, global zone initialization, zone-specific data callbacks, resource controls, kstats, zone lookup and reference accounting, zone system-call dispatch, `zsched` creation, process zone entry, shutdown/destroy, ZFS dataset visibility, datalink assignment, and zone network metadata.

Key elements:
- The opening design comment documents the zone state machine from `ZONE_IS_UNINITIALIZED` through `ZONE_IS_FREE`, lock ordering, visible syscall operations, and zone-specific data semantics.
- Global state includes `zone0`/`global_zone`, active and deathrow zone lists, hash tables by id/name/label, zone ID space, ZSD key list, resource-control handles, and zone event channel.
- Mount synchronization uses `block_mounts()`, `resume_mounts()`, `mount_in_progress()`, and `mount_completed()` to prevent racing VFS mounts with zone state transitions.
- Zone Specific Data support includes `zone_key_create()`, `zone_key_delete()`, `zone_setspecific()`, `zone_getspecific()`, `zone_zsd_configure()`, `zone_zsd_callbacks()`, and apply/wait helpers. Callbacks are marked under locks, then executed after dropping locks to avoid callback-induced lock inversions.
- Resource-control callbacks implement zone usage/test/set logic for CPU shares/cap, max LWPs, max processes, System V IPC IDs/memory, locked memory, swap reservation, and lofi limits.
- Kstat helpers create and update per-zone `lockedmem`, `swapresv`, `nprocs`, `memory_cap`, and `zone_misc` kstats.
- `zone_zsd_init()` performs very early setup and partially initializes `zone0`; `zone_init()` registers rctls, finalizes global-zone state, initializes label/kstat/hash structures, and binds the zone sysevent channel.
- `zone_free()` tears down all zone-owned resources: CPU caps, ZSD entries, dataset list, datalink/network nvlists, CPU accounting arrays, vnodes, labels, strings, privileges, rctls, boot/init data, doors, locks, and the zone ID.
- `zone_status_set()` publishes zone state-change sysevents and wakes waiters; wait helpers provide blocking, signal-aware, timed, and CPR-safe state waits.
- Reference management distinguishes general references, credential references, task references, and tracked subsystem crumbs through `zone_hold()`, `zone_rele()`, `zone_hold_ref()`, `zone_rele_ref()`, `zone_cred_hold()`, `zone_cred_rele()`, `zone_task_hold()`, and `zone_task_rele()`.
- Lookup APIs find held zones by id, name, label, root path, or any zone path while filtering by externally visible state.
- Load and CPU visibility helpers update per-zone load averages and pool/processor-set visibility.
- `zone_set_root()`, `zone_set_name()`, `zone_set_privset()`, `zone_set_brand()`, `zone_set_secflags()`, `zone_set_initname()`, `zone_set_bootargs()`, `zone_set_fs_allowed()`, `zone_set_sched_class()`, and `zone_set_phys_mcap()` validate and store zone attributes.
- `zsched()` builds the per-zone kernel parent process, moves it into the new zone, creates project/task/rctl context, chroots it to the zone root, marks the zone initialized/ready, launches init after `ZONE_IS_BOOTING`, then waits for `ZONE_IS_DYING`.
- `zone_create()` allocates a zone ID, validates root/name/privileges/rctls/ZFS datasets/labels, serializes against mounts, installs a restricted `zone_kcred`, inserts the zone into hashes/lists, starts `zsched`, creates kstats, waits until ready, and returns the new zone ID.
- `zone_boot()` transitions a ready zone to booting and waits for running or boot failure.
- `zone_shutdown()` blocks mounts, transitions to shutting down/empty/down as appropriate, kills zone processes, rebinds pool visibility, runs ZSD shutdown callbacks, and waits for zone kernel threads to drain.
- `zone_destroy()` requires the zone to be down, tells `zsched` to exit, runs destroy callbacks, waits for remaining references with periodic reference-count logging, removes hashes/lists/kstats/brand state, and drops the final hold.
- `zone_getattr()` and `zone_setattr()` implement the user-visible zone attribute API, including root/name/status/flags/privileges/uniqid/pool/label/init/brand/bootargs/memory cap/scheduler/hostid/filesystem/security/network attributes plus brand-specific extensions.
- `zone_enter()` injects the current global-zone process into a ready/running non-global zone. It stops sibling LWPs, validates files/mappings/contracts/privileges, binds pools, transfers task/project/process/LWP/memory/swap/crypto accounting, resets contracts/session/scheduler state, chroots, restricts credentials and privileges, adjusts UID counts, and resets core defaults.
- `zone()` is the syscall dispatcher for create, boot, destroy, getattr, setattr, enter, list, shutdown, lookup, version, and datalink operations, including 32-bit `zone_def` translation.
- `zone_kadmin()` handles in-zone `uadmin()` shutdown/reboot by marking the zone shutting down, killing zone processes, and starting a global-zone kernel thread to call `zoneadmd` through a door.
- `zone_shutdown_global()` marks the global zone and running zones as shutting down during system shutdown.
- `zone_dataset_visible()` checks delegated ZFS datasets and mounted ZFS filesystems for read/write visibility from the current zone.
- Datalink support maintains per-zone `zone_dl_t` entries through add/remove/check/list/walk APIs and ensures a link ID belongs to only one zone.
- Network metadata support maps address/default-router entries into per-datalink nvlists through `zone_set_network()` and `zone_get_network()`.

Dependencies:
- Deeply integrated with process, task, project, credential, privilege, contract, session, signal, scheduler, pool, processor-set, vnode/VFS, VM segment, resource-control, kstat, brand, MAC/datalink, ZFS visibility, Trusted Extensions label, sysevent, door, and uadmin subsystems.
- Uses `mod_hash` for zone lookup, `id_space` for zone IDs, `list_t` for active/deathrow/ZSD/dataset/datalink lists, `nvlist` for rctl/network payloads, and many kernel locks/CVs.
- Depends on external policy gates such as `secpolicy_zone_config()`, `secpolicy_pool()`, and `secpolicy_zone_admin()`.

Research notes:
- State transitions are intentionally monotonic; callers wait for "at least this state" rather than exact reversibility.
- The code separates visible lifecycle removal from memory freeing so credential references can survive a destroyed zone; dead zones may remain on `zone_deathrow`.
- Mount synchronization is explicitly per-zone but biased toward the current operation, and comments acknowledge possible shutdown starvation during rapid mount activity.
- Zone ID allocation avoids reusing IDs whose corresponding netstack ID is still referenced, warning and retrying instead.
- `zone_destroy()` logs subsystem reference counts after a timeout to aid leaked-reference debugging.
- `zone_enter()` has a large "cannot fail from now on" point after accounting and zone membership are transferred; rollback is only attempted before that point.
- A notable local quirk appears in `zone_create()`: while initializing a newly allocated zone, it assigns `zone0.zone_lockedmem_kstat` and `zone0.zone_swapresv_kstat` to `NULL`, which looks inconsistent with the surrounding per-zone initialization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/zone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394.h

Umbrella private header for the illumos IEEE 1394 OpenHCI adapter driver. It collects core driver headers and declares driver entry points that do not have a narrower dedicated header.

Key elements:
- Includes DDI, 1394 service-layer, OpenHCI, descriptor, CSR, vendor, buffer, queue, async, isochronous, ioctl, state, and ID headers needed by the adapter implementation.
- Defines `HCI1394_INITIAL_STATES` as the initial soft-state allocation count for `ddi_soft_state_init()`.
- Defines `HCI1394_ADDR_MAP_SIZE` as four service-layer address map sections: physical, posted write, normal, and CSR.
- Defines `HCI1394_ALIGN_QUAD(addr)` to round addresses up to a quadlet boundary.
- Declares attach/detach/quiesce and hardware cleanup routines.
- Declares misc character-device entry points: state access, open, close, shutdown, getinfo, and ioctl.
- Declares interrupt setup/fini and mask setup routines.

Dependencies:
- Depends on `hci1394_state_t`, `hci1394_drvinfo_t`, `hci1394_statevar_t`, and OpenHCI/1394 service-layer types from the included adapter headers.
- Exposes interfaces implemented across `hci1394_attach.c`, `hci1394_detach.c`, `hci1394_misc.c`, `hci1394_ioctl.c`, and `hci1394_isr.c`.

Research notes:
- This is an internal aggregation/interface header, not an implementation file.
- The include order makes it the broad dependency point for adapter modules that need access to most driver subsystems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_async.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_async.h

Private interface and state definitions for the IEEE 1394 OpenHCI asynchronous DMA engines. It covers outgoing requests/responses, incoming requests/responses, command tracking, queue handles, transaction labels, and race handling between request completion and response arrival.

Key elements:
- Defines descriptor/data buffer sizes for ATREQ, ARRESP, ARREQ, and ATRESP queues.
- Declares opaque `hci1394_async_handle_t`.
- Defines `hci1394_async_cstate_t` with `IN_PROGRESS`, `PENDING`, and `COMPLETED` states to handle races between ATREQ completion interrupts and ARRESP interrupts.
- `hci1394_async_cmd_t` stores:
  - service-layer command pointer and HAL/service private command state,
  - transaction label allocation state and label info,
  - ARREQ mblk ownership flag,
  - response/ack status and destination,
  - async command state,
  - backpointer to async state,
  - pending-list node,
  - queue command metadata used by `hci1394_q_at*()` routines.
- Warlock `_NOTE` annotations document fields used by only one thread or protected by scheme.
- `hci1394_async_t` stores pending-list, OHCI, tlabel, CSR, four queue handles, driver info, ARREQ flush state, PHY reset generation, and `as_atomic_lookup` mutex for ARRESP vs pending-timeout races.
- Declares lifecycle routines: `hci1394_async_init()`, `hci1394_async_fini()`, suspend/resume, command overhead query, flush/reset helpers, and pending-timeout update.
- Declares interrupt/queue processing routines for ATREQ, ARRESP, ARREQ, and ATRESP.
- Declares command submission routines for PHY, write, read, lock, and their response forms.
- Declares `hci1394_async_response_complete()` for freeing response-side ARREQ resources.

Dependencies:
- Depends on DDI headers, `h1394` service-layer command types, driver info, transaction list/label support, OHCI handle, CSR handle, and queue command/handle types.
- The queue comments tie this header directly to `hci1394_q` descriptor/data-buffer management and OpenHCI async DMA processing.

Research notes:
- The async command state exists specifically because hardware ordering and software interrupt observation can differ.
- ARREQ flush state is tied to bus reset processing; processing suppresses service-layer delivery until a current-generation PHY reset token is seen.
- The mblk ownership rule allows a target driver to keep received block-write data by nulling the command mblk before release.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_async.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_buf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_buf.h

Private buffer-allocation interface for IEEE 1394 OpenHCI adapter DMA-bound memory. It describes caller parameters, returned DMA/access handles, and the opaque handle used to free allocated buffers.

Key elements:
- `hci1394_buf_parms_t` describes requested buffer length, maximum DMA cookie count, and alignment. The cookie/alignment fields override adapter default DMA attributes for scatter-gather length and alignment.
- `hci1394_buf_info_t` returns the DMA cookie, cookie count, kernel virtual address, requested and real allocation lengths, access handle, and DMA handle.
- `hci1394_buf_t` privately tracks access handle, DMA handle, and driver info pointer.
- `hci1394_buf_handle_t` is the opaque allocation handle passed to `hci1394_buf_free()`.
- Declares `hci1394_buf_attr_get()` for default DMA attributes.
- Declares `hci1394_buf_alloc()` and `hci1394_buf_free()` for allocation lifecycle.
- Warlock annotation marks the buffer structures as single-user protected.

Dependencies:
- Depends on illumos DDI DMA/access-handle types and adapter driver info type.
- Intended consumers are queue, descriptor, async, and isochronous code needing memory mapped for device DMA.

Research notes:
- The API separates allocation metadata returned to the caller from the opaque free handle, allowing clients to use cookies/addresses while the module retains enough private state to unbind/free correctly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_csr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_csr.h

Private interface and state for IEEE 1394 CSR registers implemented in software by the HAL. Hardware-backed CSR registers live in the OHCI layer; this header covers software register storage, split-timeout handling, bus-reset state, and accessors.

Key elements:
- Documents CSR context from IEEE 1212, IEEE 1394-1995, and P1394A.
- Explains split timeout representation in 1394 bus cycles and its split into `split_timeout_hi` and `split_timeout_lo`, including legal low-register bounds of 800 to 7999 cycle units.
- Notes the inherent race when updating split timeout through two non-atomic CSR writes.
- Defines CSR register address offsets for state clear/set, node IDs, reset start, split timeout hi/lo, cycle/bus/busy time, bus manager ID, bandwidth available, and channel availability registers.
- `hci1394_csr_t` stores software CSR state, split timeout in observed cycles, previous-root state, node capabilities, OHCI handle, driver info pointer, and mutex.
- Defines opaque `hci1394_csr_handle_t`.
- Declares lifecycle functions: `hci1394_csr_init()`, `hci1394_csr_fini()`, and `hci1394_csr_resume()`.
- Declares accessors for node capabilities, CSR state get/set/clear, split-timeout hi/lo get/set, combined split-timeout get, and bus-reset handling.

Dependencies:
- Depends on DDI headers and adapter definitions for `hci1394_ohci_handle_t` and `hci1394_drvinfo_t`.
- Integrated with async transaction timeout behavior and OHCI CSR/hardware register support.

Research notes:
- The implementation behind this header must clamp split-timeout writes to legal 1394 values.
- The exposed `hci1394_csr_bus_reset()` suggests CSR state is refreshed or adjusted on bus reset, including root-status tracking.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_csr.h -->