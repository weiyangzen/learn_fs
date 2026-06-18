<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca953x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca953x.c

## Purpose
Broad I2C GPIO expander driver for PCA953x/PCA957x/PCAL/TCA/Maxim/OnSemi-compatible devices. It supports 4-40 GPIOs, direction/value/multiple operations, PCAL bias config, optional IRQs, reset GPIOs, regulators, ACPI quirks, and PM regcache restore.

## Important APIs, types, and functions
`struct pca953x_chip` stores locks, regmap, IRQ bitmaps, wake count, client, chip, encoded match data, regulator, register layout, and address/register callbacks. Important helpers include register validators, address recalculation for normal/PCAL6534/TCA6418 layouts, bulk read/write, GPIO callbacks, IRQ setup/pending handling, probe, and PM save/restore.

## Control flow
Probe decodes match data, enables `vcc`, chooses auto-increment regmap mode, installs special callbacks, initializes regmap cache and locks, selects register layout, initializes hardware, configures IRQs, and registers the chip. IRQ handling snapshots input state, handles PCAL latched status, filters by requested edge/level bitmaps, and dispatches nested IRQs.

## State and persistence behavior
Regmap cache tracks direction, output, polarity, pull, latch, and IRQ mask registers. IRQ bitmaps track masks, previous status, trigger types, and wake path. Suspend disables parent IRQ and goes cache-only; resume powers up and syncs direction before output and then full cache.

## Dependencies and integration points
Integrates I2C, regmap, regulator framework, optional reset GPIO, OF/ACPI/DMI matching, optional IRQ support, pinconf bias parameters, and gpiolib. It registers at `subsys_initcall()`.

## Risks and edge cases
PCAL6534 compact addressing, TCA6418 reversed bits/inverted direction, PCAL latched IRQ status, and I2C mux lockdep subclassing are high-risk. IRQ emulation depends on prior input snapshots. PM sync ordering prevents output glitches.

## Test signals
Cover PCA953x, PCA957x, PCAL6524/6534, and TCA6418; direction/output order, multiple operations, PCAL pulls, ACPI IRQ quirk, IRQ edge/level/short-pulse behavior, and suspend/resume with regulator off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca953x.c -->
