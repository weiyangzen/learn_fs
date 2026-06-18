# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/delta-ahe50dc-fan.c

Purpose: PMBus driver for the integrated fan-control module in the Delta AHE-50DC Open19 power shelf.

Important APIs/types/functions: `ahe50dc_fan_write_byte()` blocks `PMBUS_CLEAR_FAULTS` to avoid hardware output glitches. `ahe50dc_fan_read_word_data()` restricts reads to supported commands and remaps virtual page 1 temperature 1 to manufacturer command `0xd0`. `ahe50dc_fan_info` declares two virtual pages with direct-format fan, temperature, and VIN coefficients. `ahe50dc_fan_data` sets `PMBUS_NO_CAPABILITY` because the device returns misleading capability data.

Control flow: probe installs platform data and delegates to PMBus core. PMBus core uses two virtual pages: page 0 for VIN, temps, fans, and fan status; page 1 for remapped fourth temperature. Write-byte and read-word hooks filter unsafe or unsupported operations.

State and persistence: no private runtime state. The driver intentionally avoids sending clear-faults writes that could disturb hardware outputs.

Dependencies and integration: depends on PMBus core, I2C, OF/I2C matching, and direct-format PMBus conversion coefficients.

Risks: blackholing `CLEAR_FAULTS` means generic PMBus fault clearing will report unsupported and faults may remain latched elsewhere. Unsupported commands returning `-EOPNOTSUPP`/`-ENODATA` are deliberate to avoid confusing `0xffff` reads. Direct coefficients are hard-coded from observed device behavior.

Test signals: no `CLEAR_FAULTS` SMBus write on fault-clearing requests, virtual temp4 mapping, supported command reads only, fan speed/control attributes, and operation with `PMBUS_NO_CAPABILITY`.
