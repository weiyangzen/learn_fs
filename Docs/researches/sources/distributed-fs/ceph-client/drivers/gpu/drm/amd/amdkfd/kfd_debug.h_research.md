<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.h

## Purpose

`kfd_debug.h` declares the internal KFD debugger event, trap, runtime-forwarding, snapshot, and capability-check APIs. It separates the debugger implementation in `kfd_debug.c` from ioctl, interrupt, process, and queue code that needs to raise events or manipulate debug state.

## Important APIs, Types, and Entry Points

- Lifecycle declarations: `kfd_dbg_trap_enable()`, `kfd_dbg_trap_disable()`, `kfd_dbg_trap_activate()`, and `kfd_dbg_trap_deactivate()`.
- Event declarations: query, raise, interrupt translation, work-handler, and exception-mask update helpers.
- Trap controls: wave launch override/mode, address-watch set/clear, flags, exception-info query, and device snapshot.
- Runtime forwarding: `kfd_dbg_send_exception_to_runtime()`.
- Hardware predicates: per-VMID support, RLC debug-register restore support, CWSR workaround range, debugger/GWS support, MES debug mode setup, and TTMP setup policy.

## Control Flow

Callers use these declarations after selecting and referencing the target KFD process or PDD. `kfd_chardev.c` calls the lifecycle and trap-control helpers from debug ioctls. Interrupt paths call `kfd_set_dbg_ev_from_interrupt()`. Process/runtime transitions call activate/deactivate helpers to synchronize software debug state with hardware and scheduler state.

Inline predicates choose the hardware strategy: per-VMID devices avoid reserved debug VMIDs, older devices may require special GFX-off handling when RLC cannot restore debug registers, CWSR workaround devices restrict GWS/debug coexistence, and MES version checks determine TTMP setup behavior.

## State and Persistence Behavior

The header stores no mutable state. Its inline predicates encode persistent device policy based on IP version, MEC firmware version, and MES scheduler version. Those decisions influence userspace-visible debug support and ioctl results.

## Dependencies and Integration Points

The header includes `kfd_priv.h` and relies on KFD/AMDGPU IP-version and MES version macros. It is included by the character device, debugger backend, and KFD subsystems that raise or consume debug events.

## Risks and Edge Cases

- New GPU generations require updates to hard-coded IP-version predicates.
- Firmware threshold mistakes in `kfd_dbg_has_gws_support()` can expose broken debugger/GWS behavior or block valid hardware.
- TTMP setup policy is version-sensitive and can under- or over-program debug scratch state.
- Function prototypes do not encode locking/reference preconditions; callers must hold the correct process locks and refs.

## Test and Validation Signals

Cover every IP-version boundary and firmware/MES threshold in predicate tests, then verify ioctl-level behavior maps unsupported capabilities to the expected error codes or no-op paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.h -->
