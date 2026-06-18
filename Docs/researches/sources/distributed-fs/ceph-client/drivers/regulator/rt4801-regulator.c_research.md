# sources/distributed-fs/ceph-client/drivers/regulator/rt4801-regulator.c

Purpose: implements the Richtek RT4801 display bias regulator with positive and negative DSV outputs. Each output has a voltage selector and optional dedicated enable GPIO.

Important APIs/types/functions: `struct rt4801_priv` tracks enable GPIOs, a software enable bitmask, and cached voltage selectors. `rt4801_of_parse_cb()` lets child regulator nodes override or provide per-rail enable GPIOs. Custom ops cache voltage while disabled and write voltage on enable.

Control flow: I2C probe assumes outputs were enabled by firmware, initializes regmap, obtains optional indexed `enable` GPIOs, reads current VOP/VON selector values, and registers DSVP and DSVN descriptors. `set_voltage_sel()` writes hardware only when the rail is marked enabled; otherwise it updates the cached selector. `enable()` asserts GPIO, writes the cached selector to the rail register, and marks enabled. `disable()` deasserts GPIO and clears the software bit.

State and persistence: enable state is software-only and initialized to both rails enabled. Voltage selection is cached per rail so disabled rails can accept regulator-core voltage changes before the next enable. Hardware does not provide an enable status register in this implementation.

Dependencies and integration: depends on I2C, regmap, GPIO descriptors, regulator OF matching for `DSVP` and `DSVN`, and optional per-regulator `enable-gpios`.

Risks and test signals: software enable state can diverge from hardware if GPIOs are absent or external logic changes power. `of_parse_cb()` silently ignores failed child GPIO lookups. Tests should check bootloader-enabled assumption, voltage changes while disabled, GPIO present/absent cases, duplicate enable GPIO properties, and regmap read/write failures.
