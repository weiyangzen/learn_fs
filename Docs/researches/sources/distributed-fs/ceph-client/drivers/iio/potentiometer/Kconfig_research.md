# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/Kconfig

## Purpose
Kconfig menu for digital potentiometer IIO drivers.

## Important APIs, Types, And Functions
Defines tristate symbols for AD5110, AD5272, DS1803, MAX5432, MAX5481, MAX5487, MCP4018, MCP4131, MCP4531, MCP41010, TPL0102, and X9250. Dependencies select the required bus, mostly I2C or SPI; `TPL0102` selects `REGMAP_I2C`.

## Control Flow
Enabling a symbol causes the corresponding Makefile object to build. Help text names the produced module for each driver.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
This is the build-selection entry point for the potentiometer directory.

## Risks And Test Signals
Build-test all symbols as modules and built-ins, especially ordering and required bus/regmap dependencies.
