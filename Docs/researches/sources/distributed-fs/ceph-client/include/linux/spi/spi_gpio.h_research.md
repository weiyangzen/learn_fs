<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi_gpio.h

Purpose: This header provides platform data for the `spi_gpio` bitbanged SPI host controller.

Important APIs/types/functions: `spi_gpio_platform_data` contains `num_chipselect`, the number of target devices the GPIO-backed controller should allow.

Control flow: Platform code creates a `spi_gpio` platform device and passes this data; the driver registers a bitbang SPI controller with the requested chip-select count.

State and persistence: Static platform data only. GPIO line state and bitbang controller state are driver-owned.

Dependencies/integration: Integrates platform devices, SPI board info, GPIO-backed SPI, and the bitbang helper.

Risks and test signals: Risks include stale platform devices when switching to native controllers, wrong chip-select count, and GPIO descriptor mismatch. Test controller registration, multiple chip selects, transfer timing, and replacement with native controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_gpio.h -->
