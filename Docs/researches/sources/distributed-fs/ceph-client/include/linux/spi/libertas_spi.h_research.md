<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/libertas_spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/libertas_spi.h

Purpose: This header defines board-specific configuration for the Libertas SPI WLAN driver.

Important APIs/types/functions: `libertas_spi_platform_data` exposes `use_dummy_writes` to select one of two module read methods and optional board-specific `setup()`/`teardown()` callbacks receiving the `spi_device`.

Control flow: During probe, the WLAN driver uses platform data to perform board setup and choose read protocol behavior; removal calls teardown if provided.

State and persistence: The data is static board policy. Runtime WLAN state, firmware loading, and SPI transaction state are driver-owned.

Dependencies/integration: Integrates SPI, WLAN/Libertas driver setup, and board-specific power/reset/IRQ glue.

Risks and test signals: Risks include selecting a read method incompatible with clock speed or module wiring, setup/teardown imbalance, and callback failures during probe unwind. Test firmware load, network bring-up, slow SPI clock operation, dummy-write toggle, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/libertas_spi.h -->
