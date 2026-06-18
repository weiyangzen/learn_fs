# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/guc_capture_fwif.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/guc_capture_fwif.h

### Purpose
`guc_capture_fwif.h` defines the firmware interface and driver-side bookkeeping for GuC error-state capture before engine resets.

### Important APIs, Types, And Functions
Key types include `struct __guc_capture_bufstate`, `struct __guc_capture_parsed_output`, `struct guc_debug_capture_list_header`, `struct guc_debug_capture_list`, `struct __guc_mmio_reg_descr`, `struct __guc_mmio_reg_descr_group`, `struct guc_state_capture_header_t`, `struct guc_state_capture_t`, `struct guc_state_capture_group_header_t`, `struct guc_state_capture_group_t`, `struct __guc_capture_ads_cache`, and `struct intel_guc_state_capture`.

### Control Flow
The header describes two flows: ADS registration of register lists for GuC to capture, and runtime parsing of logged capture groups into preallocated per-engine parsed-output nodes. It has no executable code.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is owned by `intel_guc_state_capture`: static/ext register lists, ADS caches, null cache, preallocated cachelist, output list, and max register count. Dependencies include GuC firmware interface types, list heads, engine classes, and MMIO register descriptors. Integration points are `intel_guc_capture`, ADS capture-list population, G2H state capture notifications, and i915 GPU coredump reporting. Risks include packed layout mismatch, allocation constraints during reset/G2H handling, partial captures, and steered-register list validity. Test signals are populated ADS capture pointers, parsed coredump register groups, partial-capture flags, and no allocations in reset-sensitive paths.
