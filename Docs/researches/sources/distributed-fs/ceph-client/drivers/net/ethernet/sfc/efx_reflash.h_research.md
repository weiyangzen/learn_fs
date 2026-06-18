# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_reflash.h

Purpose: Declares the SFC devlink firmware reflash entry point.

Important APIs: `efx_reflash_flash_firmware(struct efx_nic *efx, const struct firmware *fw, struct netlink_ext_ack *extack)` updates adapter NVRAM from a firmware blob and reports user-visible errors.

Control flow and integration: Included by `efx_devlink.c`, which calls the function from the devlink `.flash_update` operation.

State and persistence: The header owns no state. Its function mutates persistent NVRAM on success.

Dependencies: Includes `net_driver.h` and `<linux/firmware.h>`; extack type is available through netlink/devlink includes in users.

Risks: This API is high impact because it can rewrite firmware partitions. Callers must pass a valid devlink-provided firmware object and extack context.

Test signals: Build devlink flash update path and run firmware update negative tests for parse, metadata, protection, size, erase, write, and finish failures.
