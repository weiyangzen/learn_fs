# sources/distributed-fs/ceph-client/drivers/i2c/i2c-atr.c

## Purpose

`i2c-atr.c` implements the I2C Address Translator framework. It creates child I2C adapters behind an address-translation device, maps child-bus client addresses to aliases on the parent bus, and calls device-specific attach/detach operations when mappings are created or removed.

## Important APIs, Types, and Functions

Core types are `struct i2c_atr`, `struct i2c_atr_chan`, `struct i2c_atr_alias_pool`, and `struct i2c_atr_alias_pair`. Exported APIs include `i2c_atr_new()`, `i2c_atr_delete()`, `i2c_atr_add_adapter()`, `i2c_atr_del_adapter()`, `i2c_atr_set_driver_data()`, and `i2c_atr_get_driver_data()`. Transfer hooks are `i2c_atr_master_xfer()` and `i2c_atr_smbus_xfer()`.

## Control Flow

`i2c_atr_new()` validates ops, allocates the ATR, mirrors parent adapter capabilities into a child algorithm, parses a shared `i2c-alias-pool`, and registers an I2C bus notifier. Adding a channel allocates `struct i2c_atr_chan`, sets up locks and fwnode, chooses a per-channel or shared alias pool, registers the adapter, and creates sysfs links. Transfers map each child message address to an alias, call the parent transfer, and restore original addresses.

## State and Persistence Behavior

Alias pools track use with a bitmap protected by spinlock. Each channel tracks alias pairs under `alias_pairs_lock` and original message addresses under `orig_addrs_lock`. Dynamic mode may evict non-fixed alias mappings; mappings touched by a current multi-message transaction are marked fixed until unmapping. Static and passthrough flags change behavior when no mapping exists.

## Dependencies and Integration Points

The framework depends on I2C core, bus notifiers, fwnode properties, sysfs links, lockdep keys, and driver-supplied `attach_addr`/`detach_addr` callbacks. It exports symbols in namespace `I2C_ATR`.

## Risks

Mapping replacement detaches the old address before attaching the new one; attach failure destroys the pair and releases the alias, leaving the old mapping gone. `i2c_atr_map_msgs()` uses a static local `c2a` pointer unnecessarily, although locks prevent functional cross-channel corruption in the current code path. Shared alias pools require correct release on detach and channel removal. Notifier attach failures are logged but do not block client creation.

## Test Signals

Test static, dynamic, passthrough, shared-pool, and per-channel-pool modes; alias exhaustion; eviction with fixed mappings in multi-message transfers; SMBus and master transfer address restoration after parent errors; bus notifier add/remove; fwnode channel lookup; sysfs link creation/removal; and deleting ATR only after all adapters are removed.
