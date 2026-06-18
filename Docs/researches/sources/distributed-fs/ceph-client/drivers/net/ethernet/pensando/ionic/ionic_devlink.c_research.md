# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_devlink.c

Purpose: Provides the Ionic devlink instance, information reporting, firmware flashing entry point, and devlink port registration.

Important APIs and flow: `ionic_devlink_alloc()` allocates a devlink object with private `struct ionic` storage. `ionic_dl_info_get()` publishes running firmware version, fixed ASIC ID/revision, and serial number. `ionic_dl_flash_update()` delegates firmware data to `ionic_firmware_update()`. `ionic_devlink_register()` registers a physical devlink port, attaches it to the netdev with `SET_NETDEV_DEVLINK_PORT()`, and registers the devlink instance. `ionic_devlink_unregister()` reverses port and instance registration.

State and persistence: Devlink private storage owns the main `struct ionic` from PCI probe until remove. The devlink port is embedded in `struct ionic`.

Dependencies and integration: Integrates with PCI probe/remove, netdev LIF registration, devlink core, and firmware update implementation in `ionic_fw.c`.

Risks and test signals: Register ordering matters because the netdev uses the devlink port pointer. Firmware flash assumes `ionic->lif` and firmware command registers are valid. Test `devlink info`, port visibility, flash success/failure extack messages, probe unwind after devlink port registration failure, and unregister during device reset/remove.
