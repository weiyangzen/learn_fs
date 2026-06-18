# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm63xx-power.c

Purpose: simple MMIO bitmask power-domain controller for BCM6318, BCM6328, BCM6362, and BCM63268 SoCs.

Important APIs/types/functions: `struct bcm63xx_power` holds the register base, spinlock, domain objects, and onecell data; `struct bcm63xx_power_dev` wraps genpd with bit mask; `struct bcm63xx_power_data` maps domain name, bit, and flags. Runtime helpers are `bcm63xx_power_get_state()`, `bcm63xx_power_set_state()`, `bcm63xx_power_on/off()`, and `bcm63xx_power_probe()`.

Control flow: probe maps the single power-control register, selects the compatible table, calculates onecell size from the highest bit, allocates domain arrays, reads each domain's current state where a cleared bit means on, initializes genpd with that state and flags, stores each domain at its binding bit index, initializes the spinlock, and registers the onecell provider. Power on clears the domain bit; power off sets it under the spinlock.

State and persistence: software state is one genpd per table entry and a spinlock for read-modify-write serialization. Hardware state is the power-control register. Always-on flags protect rails or core domains such as LDOs, MIPS, peripheral, or pad power.

Dependencies/integration: uses DT binding IDs for BCM6318/6328/6362/63268, OF match data, generic PM domains, MMIO, and built-in platform registration.

Risks: onecell indices are sparse by bit number; consumers must use binding IDs, not compact table order. `is_on` can be uninitialized if `bcm63xx_power_get_state()` failed before `pm_genpd_init()`, though masks are always set for table entries. Raw MMIO access lacks endianness abstraction. Wrong always-on flags can shut down CPU/peripheral rails.

Test signals: each compatible reports expected domain count, power register bits toggle correctly, always-on domains are not disabled, sparse xlate slots resolve as intended, and concurrent domain toggles preserve unrelated bits.
