# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2_scratch.c

Purpose: implements Global2 scratch/misc indirect register access for GPIO control, external SMI pin muxing, and SerDes strap detection.

Important APIs/types/functions: private helpers `mv88e6xxx_g2_scratch_read/write()`, bit get/set helpers, GPIO callbacks for data/direction/pin-control, exported `mv88e6352_gpio_ops`, `mv88e6390_g2_scratch_gpio_set_smi()`, `mv88e6393x_g2_scratch_gpio_set_smi()`, and `mv88e6352_g2_scratch_port_has_serdes()`.

Control flow: scratch reads write the pointer then read back data; writes set update plus pointer/data. GPIO operations map pin offsets into paired scratch registers. SMI mux helpers inspect strap/config bits, account for inverted semantics on some chips, then set or clear `NORMALSMI`. SerDes detection reads strap data and reports whether port 4 or 5 owns the SerDes.

State and persistence: scratch registers reflect hardware straps and mutable GPIO/mux state. `chip->gpio_data[]` caches output data bytes so set operations preserve other pins.

Dependencies/integration: used by GPIO registration, MDIO external SMI setup, PCS initialization, and `global2.h` scratch constants. Callers are expected to hold register lock.

Risks: `mv88e6352_g2_scratch_gpio_set_pctl()` masks `func` before shifting using the shifted mask, which can drop function bits. SMI muxing can fail with `-EBUSY` when port 0 is strapped to conflicting modes. Cached GPIO output can diverge if hardware changes outside this driver.

Test signals: GPIO direction/data/pinmux operations, external SMI mux toggling on 6390/6393x, SerDes port detection for 6352, and preservation of neighboring GPIO bits.
