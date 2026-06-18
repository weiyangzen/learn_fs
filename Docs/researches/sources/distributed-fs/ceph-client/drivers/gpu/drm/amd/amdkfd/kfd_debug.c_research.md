<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.c

## Purpose

`kfd_debug.c` implements KFD debugger event delivery and trap-control state. It records process/device/queue exceptions, notifies debugger event files, forwards unsubscribed runtime exceptions, programs shader debugger state, handles watchpoints and wave-launch controls, and activates/deactivates debug sessions across all GPUs attached to a KFD process.

## Important APIs, Types, and Entry Points

- Event paths: `kfd_dbg_ev_query_debug_event()`, `kfd_dbg_ev_raise()`, `kfd_set_dbg_ev_from_interrupt()`, and `debug_event_write_work_handler()`.
- Runtime forwarding: `kfd_dbg_send_exception_to_runtime()`.
- Session lifecycle: `kfd_dbg_trap_enable()`, `kfd_dbg_trap_activate()`, `kfd_dbg_trap_deactivate()`, and `kfd_dbg_trap_disable()`.
- Hardware programming: `kfd_dbg_set_mes_debug_mode()`, wave-launch override/mode helpers, address-watch set/clear helpers, and debug flag setup.
- Query paths: `kfd_dbg_trap_query_exception_info()`, `kfd_dbg_trap_device_snapshot()`, and `kfd_dbg_set_enabled_debug_exception_mask()`.

## Control Flow

`kfd_dbg_ev_raise()` locks `event_mutex`, records the event on a matching PDD, process, or queue, optionally stores one VM-fault payload, and writes one byte to the debugger event file if the mask is subscribed. Interrupts call `kfd_set_dbg_ev_from_interrupt()`, which looks up the process by PASID and either raises a debugger event or forwards queue/runtime and memory-fault events when unsubscribed.

Trap enable validates supported devices and GWS/debug compatibility, takes an event-file reference, optionally activates immediately if runtime debug is already enabled, takes a debug-session process reference, marks debug enabled, and copies runtime info to userspace. Activation enables queue workarounds, reserves debug VMID where needed, disables GFX off around hardware programming, enables KGD debug trap state, sets QPD debug flags, and refreshes DQM runlists or MES state. Failures unwind prior PDD changes.

Deactivation resumes queues, cancels pending event-work writes, clears address watches, resets wave launch mode and flags, disables hardware trap state, releases non-per-VMID debug VMIDs, refreshes scheduler state, and disables workarounds. Disable additionally closes the event file, drops debugger references, clears exception status, and releases the debug-session process reference.

Watchpoint setup allocates one of four IDs under a device spinlock, locks/unmaps debug scheduling for non-MES, programs every active XCC through KGD callbacks, then remaps/unlocks or updates MES. Exception-info and snapshot queries lock `event_mutex`, find the requested queue/device/process source, copy optional payloads to userspace, and clear bits when requested.

## State and Persistence Behavior

Process state includes `debug_trap_enabled`, `dbg_ev_file`, `debug_event_workarea`, `exception_enable_mask`, `exception_status`, `dbg_flags`, `runtime_info`, semaphore state, and optional `debugger_process`. PDD state includes exception status, VM-fault payload, `spi_dbg_override`, `spi_dbg_launch_mode`, watchpoint arrays, allocated watch IDs, and optional MES process-context BO pointers. Queue exception status lives in `queue->properties.exception_status`.

## Dependencies and Integration Points

The file integrates with `kfd_chardev.c` debug ioctls, KFD process/PQM/DQM internals, queue suspend/resume, runtime exception signaling, topology capability lookup, KGD hardware callbacks, AMDGPU GFX-off control, MES shader debugger APIs, workqueues, file writes, spinlocks, and user-copy helpers.

## Risks and Edge Cases

- Only one VM-fault payload is saved per PDD until queried and cleared.
- Event notification depends on a debugger-supplied file and exact `fget`/`fput` balancing.
- Activation touches hardware incrementally; unwind count must match touched devices.
- Address-watch setup releases IDs on late errors but may not fully roll back hardware watch registers.
- GFX-off pairing and RLC-restore capability checks are power-management sensitive.
- Runtime fallback delivery and debugger delivery share exception state and can diverge based on subscription masks.

## Test and Validation Signals

Test subscribed/unsubscribed event delivery, VM-fault payload query/clear, activation/deactivation on MES and non-MES devices, per-VMID and reserved-VMID paths, CWSR workaround failures, watchpoint exhaustion, wave launch controls, flag capability validation, snapshots, runtime semaphore wakeups, and reference/file cleanup on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.c -->
