# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_attrs.c

## Purpose

`fnic_attrs.c` exposes a small sysfs attribute group for FNIC SCSI hosts. It provides read-only host attributes for the driver state, driver version, and link state.

## Important APIs, Types, and Functions

- `fnic_show_state()`: retrieves `struct fnic *` from the SCSI host private data and emits `fnic_state_str[fnic->state]`.
- `fnic_show_drv_version()`: emits `DRV_VERSION`.
- `fnic_show_link_state()`: reports `"Link Up"` unless `iport.state` is `FNIC_IPORT_STATE_INIT` or `FNIC_IPORT_STATE_LINK_WAIT`; otherwise reports `"Link Down"`.
- `DEVICE_ATTR(fnic_state)`, `DEVICE_ATTR(drv_version)`, and `DEVICE_ATTR(link_state)`: read-only attributes.
- `fnic_host_attrs`, `fnic_host_attr_group`, and exported `fnic_host_groups[]`: SCSI host attribute group consumed by the host template.

## Control Flow

When user space reads a sysfs file, the device attribute callback converts the device to `Scsi_Host` with `class_to_shost()`, obtains the FNIC pointer from `shost_priv()`, formats the requested value with `sysfs_emit()`, and returns the byte count. `fnic_host_groups[]` is referenced by the SCSI host template so the attributes are registered with each FNIC host.

## State and Persistence Behavior

The file maintains no independent state. It reads live `fnic->state`, `fnic->iport.state`, and the compile-time driver version. Attribute output reflects current in-memory state and is not persisted.

## Dependencies and Integration Points

The file depends on Linux device/sysfs APIs, SCSI host helpers, and `fnic.h`. It integrates with `fnic_main.c`, where the SCSI host template assigns `.shost_groups = fnic_host_groups`, and with the state strings and iport state maintained by the rest of the driver.

## Risks and Edge Cases

- `fnic_show_state()` indexes `fnic_state_str` with `fnic->state`; invalid state values would read outside the expected string table.
- The link-state heuristic treats all states except INIT and LINK_WAIT as up, so FIP discovery, fabric discovery, or transitional failure states may be displayed as up even when SCSI targets are not ready.
- The callbacks do not take locks, so reads can race with state changes. The values are simple scalar snapshots, but output can be transient during reset/remove.

## Test Signals

Useful validation includes checking `/sys/class/scsi_host/host*/fnic_state`, `drv_version`, and `link_state` after probe, link down, FIP discovery, ready state, reset, and remove/reprobe. Confirm `drv_version` matches `DRV_VERSION` and host attribute registration occurs for each FNIC SCSI host.
