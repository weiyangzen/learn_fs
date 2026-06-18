<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi-fsl-dspi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi-fsl-dspi.h

Purpose: This header defines platform data for Freescale DSPI controllers.

Important APIs/types/functions: `fsl_dspi_platform_data` contains chip-select count, bus number, SCK-to-CS delay, and CS-to-SCK delay.

Control flow: Board code provides these values at controller probe; the DSPI driver configures bus identity, chip-select capacity, and timing.

State and persistence: Static platform data only. Runtime transfer and register state are driver-owned.

Dependencies/integration: Integrates with SPI controller registration and Freescale/NXP platform setup.

Risks and test signals: Risks include wrong bus numbering, too few chip selects, and timing delays that violate peripheral setup/hold constraints. Test chip-select enumeration, transfer timing on a logic analyzer, and multiple attached devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi-fsl-dspi.h -->
