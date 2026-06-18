# sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118-hw.c

## Purpose
Platform wrapper for ADAU7118 standalone hardware mode, where serial configuration is controlled by pins rather than I2C registers.

## APIs, Types, and Functions
`adau7118_probe_hw()` calls `adau7118_probe(&pdev->dev, NULL, true)`. The file declares OF and platform ID matches for `adau7118` and registers a `platform_driver`.

## Control Flow, State, and Persistence
All state lives in the shared `adau7118.c` implementation. Passing `hw_mode = true` suppresses regmap usage and selects the simpler hardware-mode DAPM graph and no DAI ops assignment.

## Dependencies and Integration
Depends on platform-device infrastructure, OF matching, and the common ADAU7118 header. Integrates with device tree nodes using `adi,adau7118` when the chip is strap-configured.

## Risks and Test Signals
Risks include sharing the same OF compatible with the I2C driver and therefore depending on bus topology to bind the intended wrapper, and limited software observability in hardware mode. Test signals are platform probe, regulator enable/disable through the shared bias path, and capture path routing from PDM inputs to a single AIF output.
