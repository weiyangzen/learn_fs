# sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu-soc.c

Purpose: Queries i.MX SCU firmware for SoC identity, revision, unique ID, and registers a Linux SoC device.

Important APIs/types/functions: `imx_scu_soc_uid()` sends MISC unique-id RPC and composes a 64-bit ID. `imx_scu_soc_id()` reads the system ID control. `imx_scu_soc_name()` maps known ID values to i.MX8QM/i.MX8QXP/i.MX8DXL strings. `imx_scu_soc_init()` builds `soc_device_attribute` and registers the SoC device.

Control flow: Called from SCU core probe after IPC initialization. It gets the SCU handle, allocates soc attributes, reads the root DT model, queries firmware ID/UID, formats family, machine, SoC ID, revision, and serial number, then calls `soc_device_register()`.

State and persistence behavior: Uses global `imx_sc_soc_ipc_handle` and registers a SoC device. Firmware identity is read-only.

Dependencies and integration points: Depends on SCU MISC RPCs, OF root model property, sys_soc, and the SCU core handle exported by `imx-scu.c`.

Risks and test signals: Unknown SoC IDs return string `"NULL"`, which may be undesirable in sysfs. Revision bit formatting must match SCFW encoding. Test on supported i.MX8 variants, absent model property, SCU RPC failures, and `soc` sysfs output.
