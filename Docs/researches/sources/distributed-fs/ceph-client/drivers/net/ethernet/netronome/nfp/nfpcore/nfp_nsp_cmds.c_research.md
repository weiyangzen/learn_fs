# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp_cmds.c

Purpose: Implements smaller NSP-derived commands for board identity and hardware monitor sensors.

Important APIs/types/functions: `struct nsp_identify` mirrors the firmware identify buffer. `__nfp_nsp_identify()` converts it into `struct nfp_nsp_identify`. `struct nfp_sensors` mirrors sensor readings. `nfp_hwmon_read_sensor()` opens NSP, reads selected sensors, and returns one value.

Control flow: Identify requires ABI minor >= 15, allocates raw and public structures, calls `nfp_nsp_read_identify()`, converts endian fields, and frees raw memory. Sensor reads open NSP, issue `nfp_nsp_read_sensors()` with `BIT(id)`, close NSP, then select the requested little-endian value.

State and persistence: No persistent kernel state. Values are snapshots from NSP firmware.

Dependencies/integration: Depends on `nfp_nsp.c` command functions and `nfp_nsp.h` public structs/enums. Used by version reporting and hwmon integration.

Risks: Sensor ID bounds are checked only after command completion, so invalid IDs can request an invalid bit before returning `-EINVAL`. Identify returns NULL on unsupported ABI or errors, so callers must distinguish unavailable from allocation/read failure only by context.

Test signals: ABI <15 identify returns NULL; valid identify converts strings and fields; each sensor ID returns expected value; invalid sensor ID returns `-EINVAL`; NSP open/read failures propagate.
