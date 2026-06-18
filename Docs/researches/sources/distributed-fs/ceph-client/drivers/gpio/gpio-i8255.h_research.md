<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.h

## Purpose
`gpio-i8255.h` defines the public configuration contract for the shared 8255 gpio-regmap helper in `gpio-i8255.c`.

## Important APIs, types, and functions
It declares `struct i8255_regmap_config`, `devm_i8255_regmap_register()`, and the helper macro `i8255_volatile_regmap_range(_base)` for data-port volatile ranges.

## Control flow
Consumers include this header, create a regmap with appropriate volatile/cache policy, populate the config, and call the devm registration helper during probe.

## State and persistence behavior
The header documents that the regmap must have cache enabled and that control registers must not be volatile. That is a persistence contract for software direction state rather than durable storage.

## Dependencies and integration points
The header forward-declares `struct device`, `struct irq_domain`, and `struct regmap`, keeping dependencies light for wrapper drivers. It integrates with regmap and gpio-regmap users that need one-to-many 8255 wrappers.

## Risks and edge cases
Misdeclaring volatile ranges or omitting cache support can make GPIO direction reporting and modification incorrect. `num_ppi` is an `int`, so callers should keep values sane and positive before registration.

## Test signals
Compile tests for consumers, namespace import checks for `I8255`, regmap-cache behavior tests, and wrapper probe tests that pass invalid parent/map/num_ppi values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.h -->
