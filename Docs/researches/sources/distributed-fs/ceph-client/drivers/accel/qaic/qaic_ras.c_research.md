# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ras.c

Purpose: implements the QAIC reliability, availability, and serviceability receiver on the `QAIC_STATUS` MHI channel. It decodes firmware-pushed error records, prints human-readable syndromes, maintains error counters, exposes those counters through sysfs, and triggers a device reset for fatal uncorrectable errors.

Important APIs and types: public functions are `qaic_ras_register` and `qaic_ras_unregister`. Core types include packed `ras_data` plus syndrome structs for SoC memory, PCIe, DDR, system bus, NSP memory, and thermal sensors.

Control flow: probe prepares the MHI channel, queues one receive buffer, adds `ce_count`, `ue_count`, and `ue_nonfatal_count` sysfs attributes, and stores `qdev`. The DL callback converts little-endian fields in place, validates magic/version/type/length/source/type, logs source-specific syndrome details, increments saturated counters, invokes `mhi_soc_reset` on fatal UE, then requeues the buffer.

State and persistence: counters are stored in `qdev` and persist until device removal or reset of the structure. Incoming messages are transient MHI buffers.

Dependencies and integration: uses MHI, PCI device logging, sysfs device groups, and the MHI controller reset path. It is registered from `qaic_drv.c` module init.

Risks and test signals: malformed firmware messages must be dropped without reusing corrupt data; source-specific endian conversion must match firmware layout; fatal UE reset must not race removal. Test all error sources, invalid threshold values, saturated counters, MHI requeue failure, sysfs add/remove, and fatal reset behavior.
