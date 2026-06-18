
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-fxl6408.c

Purpose: supports Fairchild/ON FXL6408 8-bit I2C GPIO expanders using regmap and gpio-regmap.

Important APIs/types/functions: `fxl6408_identify()` verifies the manufacturer bits in `FXL6408_REG_DEVICE_ID`; `fxl6408_probe()` creates the I2C regmap, disables output high-Z, and registers gpio-regmap; `fxl6408_resume()` dirties and syncs regcache. Register access tables constrain readable, writable, and volatile registers.

Control flow: probe initializes an 8-bit regmap with MAPLE cache and access tables, reads device ID, stores regmap as client data, writes zero to `OUTPUT_HIGH_Z` so output values drive pins, then registers an 8-line gpio-regmap with input status, output, and output-direction bases. Resume marks regcache dirty and syncs it to hardware.

State and persistence behavior: regmap cache stores nonvolatile output/direction/high-Z state; input status and device ID are volatile. No private state exists outside the regmap pointer. Resume restores cached state after power loss or suspend.

Dependencies and integration points: depends on I2C, regmap, gpio-regmap, OF compatible `fcs,fxl6408`, and I2C id `fxl6408`.

Risks: interrupt status register is defined but not exposed for IRQ support. Output high-Z is globally disabled at probe; boards relying on high-Z defaults need explicit GPIO direction management. Device ID only checks manufacturer bits, not a full part revision.

Test signals: invalid ID rejection, access-table enforcement, output high-Z write, 8-line gpio-regmap operations, regcache sync on resume, and I2C error propagation.
