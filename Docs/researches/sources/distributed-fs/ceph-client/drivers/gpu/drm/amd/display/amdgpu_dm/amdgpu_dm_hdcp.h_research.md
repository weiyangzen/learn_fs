# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_hdcp.h

## Purpose
`amdgpu_dm_hdcp.h` defines AMDGPU DM HDCP workqueue state and declares lifecycle/event functions for Display Manager.

## Important APIs, types, and functions
The main type is `struct hdcp_workqueue`, which holds work items, a mutex, connector references, `mod_hdcp` state, encryption status arrays, saved content-protection state, link count, SRM buffers/version/size, and the sysfs binary attribute. Public functions are `hdcp_create_workqueue()`, `hdcp_destroy()`, `hdcp_update_display()`, `hdcp_reset_display()`, and `hdcp_handle_cpirq()`.

## Control flow
DM creates the workqueue array at device setup, stream configuration adds/removes displays, atomic commit paths update HDCP intent, IRQ paths call CPIRQ handling, reset paths clear link state, and teardown destroys the workqueue.

## State and persistence behavior
The structures are runtime state. SRM bytes can be externally persisted by userspace through the sysfs attribute created by the implementation; connector-indexed arrays preserve MST property intent while connectors are destroyed and recreated.

## Dependencies and integration points
It depends on AMD DC HDCP, CP PSP, `dc.h`, and `amdgpu.h`, and is included by DM code that owns HDCP lifecycle.

## Risks and edge cases
Array indices must stay within `AMDGPU_DM_MAX_DISPLAY_INDEX`, and link indices must stay below `max_link`. Connector references and workqueue lifetime must not outlive `hdcp_destroy()`.

## Test signals
Creation/destruction, CPIRQ dispatch, MST reconnects, connector reference leak checks, SRM sysfs file lifecycle, and suspend/resume validate this interface.
