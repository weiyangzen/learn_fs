<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602-spi.c

## Purpose
This is the SPI transport wrapper for the SSM2602 codec. It creates an SPI regmap and delegates all codec logic to the shared core.

## Important APIs, Types, And Functions
`ssm2602_spi_probe()` calls `ssm2602_probe(&spi->dev, SSM2602, devm_regmap_init_spi(...))`. The SPI driver matches OF compatible `adi,ssm2602` and registers as `ssm2602`.

## Control Flow
SPI core matches the device, probe creates the regmap, and the shared driver handles reset, controls, DAPM, DAI, and registration.

## State And Persistence
No local state exists. Core state is stored by `ssm2602_probe()`.

## Dependencies And Integration Points
It depends on SPI, regmap, ASoC declarations, and `ssm2602.h`. It only supports the `SSM2602` variant over SPI in this file.

## Risks And Edge Cases
SSM2603/SSM2604 are not exposed through this wrapper. SPI regmap failure is delegated to shared probe via error pointer handling.

## Test Signals
SPI/OF binding, regmap creation failure handling, and successful shared component registration for an SSM2602 SPI device are the useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602-spi.c -->
