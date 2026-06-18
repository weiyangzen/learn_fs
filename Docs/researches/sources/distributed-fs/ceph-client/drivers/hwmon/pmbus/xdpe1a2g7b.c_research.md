# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe1a2g7b.c

Purpose: PMBus driver for Infineon XDPE1A2G5B/XDPE1A2G7B multi-phase VR controllers. It supports two pages and identifies whether VOUT is linear or NVIDIA PWM VID.

Important APIs/types/functions: `xdpe1a2g7b_identify()` reads page 0 `PMBUS_VOUT_MODE`, selects linear or VID format, and sets `nvidia195mv` VRM version for both pages when the VID code type is supported. `xdpe1a2g7b_info` holds capabilities and the identify callback.

Control flow: probe copies the info template and calls PMBus core. During PMBus identification, VOUT mode bits choose format; unsupported VID parameters return `-EINVAL`, and unsupported mode classes return `-ENODEV`.

State and persistence: per-client PMBus info stores format and VRM version; comments note the loops are not fully independent and should not be programmed separately.

Dependencies/integration: PMBus core and I2C/OF matching. VOUT VID semantics depend on PMBus core VRM conversion support for `nvidia195mv`.

Risks: only one NVIDIA VID code type is accepted. Page 1 inherits page 0 configuration, which is intentional for shared device configuration but risky if future hardware has independent pages.

Test signals: linear and NVIDIA VID probes, VOUT readings on both pages, rejection of unsupported VOUT params, and PMBus sysfs visibility.
