# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic.h

## Purpose

`fbnic.h` is the central internal header for the Meta fbnic Ethernet driver. It defines the main device object, low-level CSR and firmware access helpers, interrupt/vector constants, driver-wide prototypes, self-test result codes, and board metadata used by the fbnic component files.

## Important APIs, Types, And Functions

`struct fbnic_dev` is the primary device state. It holds Linux device and netdev pointers, debugfs/hwmon/devlink health objects, mapped CSR bases for host and firmware windows, MAC ops, MSI-X vector metadata, NAPI IRQ names, service work, firmware mailboxes and completion slots, firmware capabilities, heartbeat state, PCI tuning values, local TCAM and MAC/IP address mirrors, queue limits, PTP clock state and time lock, PMD state, hardware stats, firmware time/log state, MDIO bus, and power-save timeout.

Inline helpers include `fbnic_present()` for CSR availability, `fbnic_wr32()`, `fbnic_rd32()`, `fbnic_wrfl()`, `fbnic_rmw32()`, firmware CSR accessors, `fbnic_bmc_present()`, and `fbnic_init_failure()`. The header declares devlink, firmware mailbox, hwmon, MAC IRQ, NAPI IRQ, generic IRQ allocation, MSI-X self-test, debugfs, RPC reset, MDIO creation, CSR register dump/test helpers, coalescing configuration, and driver board info.

## Control Flow

Driver components include this header to operate on `struct fbnic_dev`. PCI probing allocates it through devlink helpers, maps CSR regions, initializes firmware/mailbox, IRQs, netdev, phylink/MAC, stats, and time support. Runtime register access goes through `rd32`/`wr32` wrappers that tolerate absent hardware by checking `uc_addr0` for writes and using the out-of-line read helper for reads.

## State And Persistence

Persistent runtime state is concentrated in `struct fbnic_dev`. It mirrors hardware TCAM, MAC/IP filters, queue capacity, firmware state, PTP timekeeping, PMD training status, statistics, MDIO, and service work. There is no disk persistence; state is rebuilt across probe/reset. `time_lock` serializes PTP time CSR machinery, while `fw_tx_lock` serializes firmware mailbox Tx queue access.

## Dependencies And Integration Points

The header depends on Linux interrupt, MMIO, PTP, workqueue, netdevice, PCI, MDIO, devlink, hwmon, and fbnic subsystem headers for CSR, firmware, logs, stats, MAC, and RPC. It is the integration surface across all fbnic source objects listed in the Makefile.

## Risks And Edge Cases

CSR access can occur while the device is removed or reset; `fbnic_present()` and guarded writes reduce but do not remove lifetime concerns. The fixed `FBNIC_MAX_NAPI_VECTORS` and mailbox completion slot counts must match hardware and IRQ allocation. Local TCAM mirrors must stay synchronized with firmware/hardware RPC programming. Timekeeping fields require correct locking to avoid inconsistent high/offset reads. Init-failure logic treats missing netdev as a special state used by cleanup paths.

## Test Signals

Useful tests include probe/remove, reset during register access, firmware mailbox traffic, devlink health reporting, IRQ allocation/free and MSI-X self-test codes, PTP clock operations, MDIO creation, TCAM programming, debugfs and hwmon registration, and netdev open/close. No local executable tests were run for this research item.
