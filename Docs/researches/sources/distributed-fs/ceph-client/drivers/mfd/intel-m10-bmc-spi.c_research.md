# sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-spi.c

Purpose: SPI transport for Intel MAX 10 BMC on N3000/D5005/N5010 boards. It builds an SPI AVMM regmap, rejects legacy unsupported BMC versions, and registers generation-specific MFD children.

Important APIs/types/functions: `intel_m10_bmc_spi_probe()`, `check_m10bmc_version()`, `m10bmc_spi_id`, `intel_m10bmc_regmap_config`, `m10bmc_n3000_csr_map`, and platform-info instances for N3000, D5005, and N5010.

Control flow: probe allocates `intel_m10bmc`, initializes `devm_regmap_init_spi_avmm()`, stores SPI drvdata, validates the legacy build register, then calls `m10bmc_dev_init()` with matched platform info. Platform info determines child cells and handshake register ranges.

State and persistence: no private runtime state beyond the common `intel_m10bmc` object. Firmware state and handshake locking are handled by the shared core when configured.

Dependencies and integration: depends on SPI device IDs, regmap SPI AVMM support, MAX10 core namespace, and child drivers for hwmon, retimer, and secure update.

Risks: `id->driver_data` must be valid for all matched devices. Legacy-version filtering is critical to avoid driving incompatible firmware. The regmap access table must cover system and flash address ranges required by children.

Test signals: SPI modalias binding for `m10-n3000`, `m10-d5005`, and `m10-n5010`, legacy rejection path, sysfs version reads, child device creation, and secure-update handshake behavior on N3000/D5005.
