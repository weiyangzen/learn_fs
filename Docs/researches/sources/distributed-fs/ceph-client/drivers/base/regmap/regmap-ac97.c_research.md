# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ac97.c

## Purpose
This file provides the regmap bus adapter for AC'97 codecs. It lets AC'97 codec drivers use generic regmap APIs over `snd_ac97` bus read/write operations and supplies a default volatile-register policy for common AC'97 status/identity registers.

## Important APIs, Types, And Functions
Exports include `regmap_ac97_default_volatile()`, `__regmap_init_ac97()`, and `__devm_regmap_init_ac97()`. Internal bus callbacks are `regmap_ac97_reg_read()` and `regmap_ac97_reg_write()`, referenced by `ac97_regmap_bus`.

## Control Flow And State
The volatile helper returns true for reset, powerdown, paging, extended ID/status, GPIO status, vendor IDs, codec class/revision, PCI subsystem IDs, function select/info, and sense info registers. Reads and writes cast bus context to `struct snd_ac97` and call `ac97->bus->ops->read()` or `write()`. Init wrappers pass `&ac97->dev`, the static regmap bus, and the codec context to core managed or unmanaged regmap initialization.

## Dependencies And Integration Points
This file depends on ALSA AC'97 codec definitions and regmap core initialization. Kconfig/Makefile include it behind `CONFIG_REGMAP_AC97`. Driver integrations typically use the volatile helper in `struct regmap_config`.

## Risks And Test Signals
Risks include AC'97 bus ops returning no error status, volatile list omissions that cause stale cache values, and lifetime mismatch between `snd_ac97` and managed regmap instances. Test signals include AC'97 driver probe using regmap, read/write passthrough verification with a fake bus, cache behavior for volatile registers, and remove-path checks for devm initialization.
