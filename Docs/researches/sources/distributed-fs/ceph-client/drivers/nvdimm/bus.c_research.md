# sources/distributed-fs/ceph-client/drivers/nvdimm/bus.c

## Purpose
`bus.c` implements the private `nd` bus type, bus and DIMM character-device ioctl dispatch, asynchronous device registration/removal, badblock/poison clearing coordination, device matching, and generic NVDIMM bus/device sysfs attributes. It is the central libnvdimm integration layer between provider drivers, NVDIMM child devices, namespace/personality drivers, and userspace ndctl ioctls.

## Important APIs, Types, And Functions
Key exported functions include `to_nvdimm_bus()`, `nvdimm_to_bus()`, `nvdimm_bus_register()`, `nvdimm_bus_unregister()`, `nd_device_register()`, `nd_device_unregister()`, `__nd_driver_register()`, `nd_synchronize()`, `nd_device_notify()`, `nvdimm_region_notify()`, `nvdimm_check_and_set_ro()`, `nvdimm_clear_poison()`, `nd_cmd_dimm_desc()`, `nd_cmd_bus_desc()`, `nd_cmd_in_size()`, and `nd_cmd_out_size()`.

The file defines `nvdimm_bus_type`, `nd_bus_driver`, the `nd` class for `ndctl<N>` devices, character-device file operations for bus and DIMM ioctls, command descriptor tables for bus and DIMM ND commands, and common `modalias`, `devtype`, `numa_node`, and `target_node` attributes.

## Control Flow
Provider registration calls `nvdimm_bus_register()`, which allocates a bus, initializes lists/waitqueue/reconfiguration mutex/badrange state, assigns an ID, initializes the device, and adds it to the `nd` bus. The internal `nd_bus_driver` probes the bus, creates the `ndctl` class device, adds the bus to `nvdimm_bus_list`, and exposes provider context.

Child device registration is asynchronous by default. `nd_device_register()` sets the bus, inherits NUMA node, references parent/device, and schedules `device_add()` in a private async domain. Removal can be async or sync, using `kill_device()` to serialize races, flushing bus operations with the reconfiguration mutex, and synchronizing the async domain when needed.

Driver matching maps devices to ND device type bits, including regions, DIMMs, BTT/PFN/DAX namespace personalities, and namespace types derived from the parent region. Bus probe wraps child driver probe with provider module pinning, probe-active accounting, and region seed advancement after successful or unsupported probes.

Ioctls open on `ndctl<N>` or `dimmctl<N>` store the minor in `file->private_data`. `nd_ioctl()` finds the selected bus or DIMM under `nvdimm_bus_list`, increments `ioctl_active`, and invokes `__nd_ioctl()`. `__nd_ioctl()` validates command descriptor, support masks, read-only restrictions, variable input/output envelope sizes, maximum buffer length, provider family support for `ND_CMD_CALL`, and `clear_to_send()` policy before forwarding to provider `ndctl()`.

## State And Persistence Behavior
The file manages in-kernel bus state: global bus list, bus IDs, active probes, active ioctls, badrange lists, and async registration. It does not persist data directly, but it forwards ND commands that read/write DIMM label storage and clear poison. `nvdimm_clear_poison()` checks ARS capability, validates clear granularity and alignment, sends `ND_CMD_CLEAR_ERROR`, then updates bus badranges and region badblocks for the cleared physical range.

Bus removal waits for active ioctls to drain, synchronizes async work, unregisters children, frees badrange entries, and destroys the `ndctl` device. This makes bus lifetime dependent on both userspace file operations and child driver operations.

## Dependencies And Integration Points
`bus.c` integrates with Linux driver core, async framework, char devices, sysfs, module ownership, badblocks/badrange management, ACPI/ND command ABIs from `ndctl.h`, and libnvdimm provider callbacks in `struct nvdimm_bus_descriptor`. It coordinates with `core.c` for bus locking, `dimm_devs.c` for DIMM deletion, `namespace_devs.c` for region seed advancement, and personality drivers through `nd_device_driver`.

## Risks And Edge Cases
Ioctl envelope parsing is security-sensitive: it copies bounded input/output prefixes first to determine variable sizes, enforces `ND_IOCTL_MAX_BUFLEN`, and then copies the whole user buffer. Any descriptor mismatch can lead to wrong copy lengths. Clear-error ioctls are deliberately blocked if the affected pmem namespace is active under a driver, forcing poison clearing through pmem where page/block state can be coordinated.

Async registration/removal races are controlled by `kill_device()`, `nd_synchronize()`, and probe-active wait queues; regressions here can cause use-after-free or stale sysfs devices. Read-only file descriptors block mutating commands, but provider `clear_to_send()` can add further restrictions. Bus removal must not free badrange or destroy ndctl while ioctls are active.

## Test Signals
Tests should cover bus registration/unregistration with multiple child devices, async add/remove races, driver type matching and modalias emission, ioctl rejection for unsupported commands and read-only mutating commands, variable-sized command envelopes, `ND_CMD_CALL` family masks, active namespace protection for `ND_CMD_CLEAR_ERROR`, badblock clearing notifications, `wait_probe` flushing, NUMA attribute visibility, and disk read-only synchronization with region `ro`.
