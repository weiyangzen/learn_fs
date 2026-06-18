# sources/distributed-fs/ceph-client/drivers/power/supply/cros_peripheral_charger.c

Purpose: exposes ChromeOS EC peripheral charging ports, such as ports that charge detachable peripheral devices, as one battery-like power supply per EC PCHG port.

Important APIs/types/functions: `struct charger_data` tracks EC devices, registered port supplies, and the EC notifier. `struct port_data` caches per-port name, status, capacity, charge type, and `last_update`. `cros_pchg_ec_command()` wraps EC command transfer; `cros_pchg_port_count()`, `cros_pchg_cmd_ver_check()`, `cros_pchg_get_status()`, and `cros_pchg_get_prop()` form the runtime path.

Control flow: probe queries the number of PCHG ports, verifies EC command version 1, bounds the count by `EC_PCHG_MAX_PORTS`, registers `peripheral%d` battery-type supplies, then registers a blocking notifier on the ChromeOS EC event chain. Property reads refresh cached status/capacity/charge type with a 500 ms ratelimit. EC MKBP PCHG device events refresh all ports immediately and call `power_supply_changed()` on changes. Resume also refreshes all ports in case events were lost.

State and persistence: each port keeps only volatile cached state and a jiffies timestamp. There are no writable properties and no persistence. The EC remains authoritative for peripheral charge state.

Dependencies and integration: depends on ChromeOS EC `EC_CMD_PCHG_COUNT`, `EC_CMD_PCHG`, `EC_CMD_GET_CMD_VERSIONS`, EC MKBP event parsing, unaligned little-endian event data, and the platform device named `cros-ec-pchg`.

Risks and test signals: lack of explicit notifier unregister in this file relies on platform/driver lifetime assumptions and should be reviewed against EC notifier ownership. The tree snapshot also shows an extra brace near the notifier path, so compile coverage matters. Test with zero ports, too many ports, unsupported command versions, EC transfer failures, event-driven updates, ratelimited property reads, and suspend/resume event loss.
