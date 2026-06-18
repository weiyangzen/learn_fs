# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hwmon.c

Purpose: `hwmon.c` exposes HSMP socket power readings and power-limit control through the Linux hwmon subsystem.

Important APIs, types, and functions: `hsmp_hwmon_read()` maps `hwmon_power_input`, `hwmon_power_cap`, and `hwmon_power_cap_max` to `HSMP_GET_SOCKET_POWER`, `HSMP_GET_SOCKET_POWER_LIMIT`, and `HSMP_GET_SOCKET_POWER_LIMIT_MAX`. `hsmp_hwmon_write()` maps writable `hwmon_power_cap` to `HSMP_SET_SOCKET_POWER_LIMIT`. `hsmp_hwmon_is_visble()` defines permissions, `hsmp_chip_info` describes the channel, and exported `hsmp_create_sensor()` registers a devm hwmon device named `amd_hsmp_hwmon`.

Control flow: front ends call `hsmp_create_sensor(dev, sock_ind)` after validating a socket. The socket index is stored as hwmon drvdata via `(void *)(uintptr_t)sock_ind`. Hwmon reads and writes construct `struct hsmp_message` and call the common `hsmp_send_message()`.

State and persistence: no local persistent state. Writes can persist in SMU/platform firmware for the runtime power limit. Values are converted between HSMP milliwatts and hwmon microwatts.

Dependencies and integration points: depends on hwmon, units constants, and the common HSMP namespace. It integrates with standard `/sys/class/hwmon` power attributes.

Risks: conversion uses `long val / MICROWATT_PER_MILLIWATT` for writes and multiplication for reads, so bounds depend on `long` size and firmware-supported limits. Only power sensors are accepted; all other types return `-EOPNOTSUPP`. There is no channel distinction beyond one power channel per registered sensor.

Test signals: hwmon device creation per socket, readable `power1_input`, `power1_cap`, `power1_cap_max`, writable `power1_cap`, unit conversions, and failure propagation from `hsmp_send_message()`.
