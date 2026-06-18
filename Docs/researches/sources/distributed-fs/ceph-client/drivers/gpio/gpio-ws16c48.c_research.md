# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ws16c48.c

## Purpose
Supports WinSystems WS16C48 ISA GPIO cards using `gpio-regmap` for 48 I/O-port-backed GPIOs and `regmap-irq` for edge interrupts on the first 24 lines.

## Important APIs, Types, And Functions
- Module parameters `base[]` and `irq[]` define ISA card instances and interrupt lines.
- `ws16c48_regmap_config` defines an 8-bit I/O-port regmap with access and volatility tables plus flat cache.
- `struct ws16c48_gpio` stores regmap, raw spinlock, and cached IRQ masks.
- `ws16c48_handle_pre_irq`, `ws16c48_handle_post_irq`, `ws16c48_handle_mask_sync`, and `ws16c48_set_type_config` implement page-lock-safe regmap-IRQ callbacks.
- `ws16c48_irq_init_hw` disables interrupts and selects the interrupt-ID page.
- `ws16c48_probe` requests/maps the I/O port range, creates regmap and regmap IRQ chip, then registers a gpio-regmap chip.

## Control Flow
Probe reserves the ISA I/O range, maps it, initializes a regmap, configures the regmap IRQ chip with status/mask/ack bases on paged registers, disables all interrupts, adds the IRQ chip for the supplied IRQ line, and registers a 48-line `gpio_regmap`. Direction and value operations are delegated to gpio-regmap with the data register used for data, set, and output-direction semantics; writing a 0 allows a line to be used as input. IRQ mask sync and type configuration temporarily select ENAB or POL pages, update registers, and return to INT_ID page under the raw spinlock.

## State And Persistence
Hardware page, data, polarity, enable, and interrupt-ID registers are the source of truth. The driver caches the last IRQ mask per register in `irq_mask` to avoid redundant page writes. Module parameters define instance identity for the module lifetime.

## Dependencies And Integration Points
Depends on ISA helper macros, ioport mapping, regmap MMIO over I/O ports, regmap-IRQ, gpio-regmap, module hardware parameter arrays, and raw spin locking to coordinate page selection between GPIO and IRQ flows.

## Risks And Edge Cases
The card uses a page/lock register shared by interrupt polarity, enable, and ID registers; missing lock coverage can target the wrong page. Only rising and falling edge types are supported despite regmap IRQ entries allowing edge-both support. `base[]` and `irq[]` module arrays must have matching instances. Direction semantics are unusual because output data also controls whether a line can float as input.

## Test Signals
Probe with multiple base/IRQ pairs, region-busy failure, regmap access-table enforcement, initial interrupt-disable programming, rising/falling IRQ polarity writes, mask sync cache behavior, page restoration to INT_ID, and gpio-regmap get/set/direction behavior across all six 8-bit ports.
