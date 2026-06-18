<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_oc_tiny.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi_oc_tiny.h

Purpose: This header defines platform data for the OpenCores tiny SPI controller.

Important APIs/types/functions: `tiny_spi_platform_data` provides input clock frequency and baud-rate divider width, used when the divider is programmable.

Control flow: Controller probe reads these values to compute and program SPI clock dividers.

State and persistence: Static platform data only. Runtime clock divider/register state is driver-owned.

Dependencies/integration: Integrates with SPI controller registration and OpenCores tiny SPI hardware.

Risks and test signals: Risks include wrong input frequency, invalid divider width, and resulting out-of-spec SCK rates. Test clock calculation, transfer speed requests, and logic analyzer SCK measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_oc_tiny.h -->
