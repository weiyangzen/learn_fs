# sources/distributed-fs/ceph-client/drivers/crypto/ccp/hsti.c

## Purpose

`hsti.c` exposes PSP security-reporting attributes through sysfs and can populate missing HSTI/security bits by issuing a platform-access query to PSP firmware.

## Important APIs, Types, And Functions

The exported objects are `psp_security_attr_group` and `psp_init_hsti()`. The `security_attribute_show()` macro creates read-only attributes such as `fused_part`, `boot_integrity`, `debug_lock_on`, `tsme_status`, and RPMC/HSP/ROM armor flags. `psp_populate_hsti()` sends `PSP_CMD_HSTI_QUERY` and merges the returned HSTI bits into `psp->capability.raw`.

## Control Flow

During PSP initialization, `psp_init_hsti()` optionally calls `psp_populate_hsti()` if the platform feature says HSTI is available. The sysfs group is visible only when `psp->capability.security_reporting` is true. If TSME is enabled, initialization logs whether SME is redundant or TSME is active.

## State And Persistence Behavior

Security state is cached in `psp->capability`. The sysfs attributes are read-only views of that cached capability register. No background updates occur after initialization.

## Dependencies And Integration Points

It depends on `platform-access.c` for the HSTI query, `cc_platform_has()` for SME reporting, and `sp-pci.c` for attaching the attribute group to PCI devices.

## Risks And Test Signals

Risks include exposing attributes before data is valid, shifting returned HSTI bits into the wrong capability region, and failing PSP init on transient HSTI query errors. Test by inspecting sysfs visibility on devices with and without security reporting, validating each bit against firmware documentation, and checking logs on TSME/SME systems.
