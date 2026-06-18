
# sources/distributed-fs/ceph-client/include/linux/nvmem-consumer.h

Purpose: declares the NVMEM consumer API for drivers that read or write named cells or raw offsets from EEPROM/OTP/FRAM/battery-backed memory providers.

Important APIs/types/functions: `struct nvmem_cell_lookup` maps provider name, cell name, consumer device ID, and connection ID. Notifier events cover provider, cell, and layout add/remove. Cell APIs get/put cells, read/write cell buffers, and read typed fixed or variable little-endian integers. Device APIs get/put NVMEM devices, read/write raw offsets, read/write cells by `nvmem_cell_info`, query name/size, add/remove lookup tables, register notifiers, and find devices. OF helpers get cells/devices by device node. Disabled builds return `-EOPNOTSUPP`, `ERR_PTR()`, zero, or NULL stubs.

Control flow: a consumer driver obtains a cell or provider by device and name, reads or writes data, and releases it manually or through devm. Platform lookup entries or device tree map consumer names to provider cells. Notifiers let interested code react to provider/cell/layout registration changes.

State and persistence: NVMEM data may be persistent hardware storage. Consumer handles are kernel references to provider devices/cells; lookup tables and notifier registrations are in-memory configuration state.

Dependencies and integration points: depends on errno/ERR_PTR helpers, notifier chains, device and device-tree types, and provider cell metadata. It integrates board data, OF bindings, driver probe code, and NVMEM provider implementations.

Risks and test signals: risks include assuming NVMEM exists when config stubs return unsupported, endian/variable-length misreads, writing read-only OTP cells, leaking cell/device references, and notifier unregister races. Test signals include provider/consumer probe ordering tests, OF and lookup-table resolution, typed read helpers with short/long cells, disabled-config builds, and read-only/write-failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvmem-consumer.h -->
