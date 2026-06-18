<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.c

## Purpose
Implements the shared BMC-side KCS device/client registry and access helpers. It lets hardware-specific KCS providers register channels and lets consumer drivers, such as the IPMI char device and serio adapter, attach to those channels.

## Important APIs, Types, and Functions
- Data helpers: `kcs_bmc_read_data()`, `kcs_bmc_write_data()`, `kcs_bmc_read_status()`, `kcs_bmc_write_status()`, and `kcs_bmc_update_status()`.
- Event and ownership helpers: `kcs_bmc_handle_event()`, `kcs_bmc_enable_device()`, `kcs_bmc_disable_device()`, and `kcs_bmc_update_event_mask()`.
- Registry APIs: `kcs_bmc_add_device()`, `kcs_bmc_remove_device()`, `kcs_bmc_register_driver()`, and `kcs_bmc_unregister_driver()`.
- Global lists `kcs_bmc_devices` and `kcs_bmc_drivers` are protected by `kcs_bmc_lock`.

## Control Flow
Hardware providers call `kcs_bmc_add_device()`, which initializes the channel lock, records the device, and calls every registered consumer driver's `add_device()`. Consumer drivers can register later and are attached to all existing devices. Active client ownership is exclusive via `kcs_bmc_enable_device()`, which enables IBF events. Hardware IRQs call `kcs_bmc_handle_event()`, which dispatches to the active client's event callback.

## State and Persistence
Persistent state is the global device/driver lists and each `kcs_bmc_device`'s active `client`. Interrupt mask state is delegated to the hardware provider through `ops->irq_mask_update()`.

## Dependencies and Integration Points
Sits between hardware drivers (`kcs_bmc_aspeed.c`, `kcs_bmc_npcm7xx.c`) and consumers (`kcs_bmc_cdev_ipmi.c`, `kcs_bmc_serio.c`). Exports symbols for loadable modules.

## Risks
There is no rollback in `kcs_bmc_add_device()` if one consumer driver's `add_device()` fails after earlier consumers succeeded. `kcs_bmc_remove_device()` calls all registered consumers and logs failures but cannot force recovery. Active-client locking uses spinlocks and hardware callbacks can run in IRQ context.

## Test Signals
Register devices before and after consumers, verify exclusive client open, event mask changes on enable/disable, IRQ dispatch with and without active client, and consumer add/remove failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.c -->
