# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.h

## Purpose

`ixgbe_fw_update.h` is the small public interface for the ixgbe E610 firmware update implementation. It lets the devlink layer and other driver code call into `ixgbe_fw_update.c` without exposing the PLDM callback internals or the private flash-session state.

## Important APIs

`ixgbe_flash_pldm_image(struct devlink *devlink, struct devlink_flash_update_params *params, struct netlink_ext_ack *extack)` is the devlink flash entry point. It validates hardware and overwrite policy, cancels previous pending updates, locks NVM, delegates image parsing to `pldmfw_flash_image()`, and flashes supported components.

`ixgbe_get_pending_updates(struct ixgbe_adapter *adapter, u8 *pending, struct netlink_ext_ack *extack)` discovers device capabilities and returns a bitmap of pending NVM, OROM, and NETLIST updates using `IXGBE_ACI_NVM_ACTIV_SEL_*` bits.

## Control Flow and Integration Points

`devlink/devlink.c` includes this header to register `.flash_update = ixgbe_flash_pldm_image` and to query pending updates around reload/update actions. The header assumes prior declarations for `struct devlink`, `struct devlink_flash_update_params`, `struct netlink_ext_ack`, and `struct ixgbe_adapter` from the surrounding ixgbe/devlink include graph.

## State and Persistence Behavior

The header itself stores no state. Its two functions operate on persistent NVM state in firmware and transient adapter/devlink state. Callers should treat `ixgbe_flash_pldm_image()` as a persistent flash mutation and `ixgbe_get_pending_updates()` as a hardware state query.

## Dependencies, Risks, and Test Signals

The key dependency is keeping this interface synchronized with `ixgbe_fw_update.c` and devlink registration code. Because the header exposes only two functions, ABI risk inside the driver is low. Compile test signals are missing forward declarations or changed devlink signatures. Functional tests should verify devlink flash registration and pending-update status paths still build and link when firmware update support is compiled.
