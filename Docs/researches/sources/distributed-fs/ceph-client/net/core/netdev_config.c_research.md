<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_config.c -->
# sources/distributed-fs/ceph-client/net/core/netdev_config.c

## Purpose
Queue-configuration renderer and validator for drivers using the netdev queue management API. It merges driver defaults with per-RX-queue memory-provider overrides and optionally asks the driver to validate the effective configuration.

## APIs, Types, and Functions
`netdev_queue_config()` is the exported read-side helper for drivers. `netdev_queue_config_validate()` is the validating variant used by queue reconfiguration paths. Internal `__netdev_queue_config()` selects either `ndo_validate_qcfg` or a no-op validator, zeroes `struct netdev_queue_config`, calls `ndo_default_qcfg`, overlays `rx_page_size` from `rxq->mp_params`, and validates after defaults and again after overrides.

## Control Flow, State, and Persistence
The function does not persist state itself; it derives an output config from `dev->queue_mgmt_ops` and the addressed RX queue each time. Validation is two-phase so invalid driver defaults and invalid memory-provider overrides are both caught with the same driver callback.

## Dependencies and Integration
Depends on `netdev_queue_mgmt_ops`, `struct netdev_rx_queue`, memory-provider params, and netlink extack for human-readable validation failures. It is used by RX queue restart/reconfiguration and memory-provider open/close logic.

## Risks and Test Signals
Risks are sparse: missing `queue_mgmt_ops` assumptions in callers, driver validators that are not idempotent, and overrides that only set `rx_page_size` while future config fields may need similar treatment. Test signals are driver default propagation, invalid default rejection, invalid memory-provider page-size rejection, and `netdev_queue_config()` fully zero-initializing unset fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_config.c -->
