# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_hdcp.c

## Purpose
`amdgpu_dm_hdcp.c` bridges DRM content-protection properties, AMD DC HDCP state-machine code, DP AUX/I2C DDC operations, PSP secure services, and sysfs SRM handling. It maintains per-link HDCP workqueues, tracks connectors, processes authentication events, and exposes `hdcp_srm` for userspace SRM persistence.

## Important APIs, types, and functions
Public APIs are `hdcp_create_workqueue()`, `hdcp_destroy()`, `hdcp_update_display()`, `hdcp_reset_display()`, and `hdcp_handle_cpirq()`. DDC callbacks include `lp_write_i2c()`, `lp_read_i2c()`, `lp_write_dpcd()`, `lp_read_dpcd()`, and atomic write-poll-read variants. PSP helpers are `psp_get_srm()` and `psp_set_srm()`. Work handlers include `event_callback()`, `event_property_update()`, `event_property_validate()`, `event_watchdog_timer()`, and `event_cpirq()`. `update_config()` and `enable_assr()` integrate with CP PSP stream configuration.

## Control flow
Creation allocates one `struct hdcp_workqueue` per DC link, initializes mutexes/work items, wires DDC callbacks to DC links, installs CP PSP callbacks, and creates the `hdcp_srm` sysfs binary attribute. Stream configuration adds/removes `mod_hdcp` displays. Content-protection updates set HDCP type policy, locality-check behavior, and display enablement, then `process_output()` schedules callback, watchdog, and validation work. Validation queries `mod_hdcp`; property update waits for pending commits and updates DRM content-protection to `ENABLED` or `DESIRED`.

## State and persistence behavior
Runtime state includes work items, connector references, per-display encryption status, saved MST content-protection/type values, current `mod_hdcp` link/display/output objects, SRM buffers, SRM version/size, and the sysfs attribute. SRM durability is delegated to userspace; PSP loses SRM across some power transitions, so userspace reads/writes the sysfs file to persist it externally.

## Dependencies and integration points
The file depends on `mod_hdcp`, PSP HDCP/DTM trusted applications, DRM HDCP property helpers, DC link/sink data, DP AUX/DPCD, I2C, workqueues, sysfs binary attributes, and CP PSP callbacks. It connects atomic commit state, MST connector lifecycle, CPIRQ, and secure firmware commands.

## Risks and edge cases
Authentication races with commit completion, unplug, MST connector destruction, reset, and delayed work cancellation. Sysfs SRM writes can arrive in PAGE_SIZE chunks, so partial writes intentionally fail until a full signed SRM validates. PSP TA contexts may be uninitialized. Connector references must be balanced on replacement, reset, removal, and destroy.

## Test signals
Test HDCP 1.4/2.2 over HDMI, DP SST, and MST; content type 0/1; CPIRQ/watchdog recovery; unplug/reset during authentication; MST reconnect property preservation; suspend/resume SRM restore; valid/invalid chunked SRM read/write; PSP-unavailable paths; and DRM property transitions.
