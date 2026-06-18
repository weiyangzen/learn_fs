# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/power.c

Purpose: Provides the pSeries `auto_poweron` sysfs control used to choose normal RTAS power-off versus UPS auto-restart power-off.

Important APIs/types/functions: Defines global `rtas_poweron_auto`, sysfs show/store helpers, `auto_poweron_attr`, and init routines for PM and non-PM builds.

Control flow: Init creates or extends the `power` kobject with `auto_poweron`. Reads print the current global value. Writes parse an unsigned long and accept only `0` or `1`; `setup.c` later uses this flag in `pseries_power_off()`.

State and persistence: The flag is a runtime global and is not persisted across boot. Firmware behavior changes only at power-off call time.

Dependencies and integration points: Integrates with generic power sysfs, pseries initcalls, and RTAS power-off handling in `setup.c`.

Risks: The store path uses `sscanf()` and accepts trailing data after a valid 0/1. When `CONFIG_PM` is enabled it assumes `power_kobj` is already available from generic PM code.

Test signals: Sysfs read/write, invalid values, PM and non-PM build coverage, power-off path with and without `ibm,power-off-ups`, and permissions on the attribute.

Source read size: 72 lines, 1598 bytes.
