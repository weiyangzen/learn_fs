# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_util.h

Purpose: ABI declaration for TUXEDO NB04 WMI method wrappers. It defines device-status constants, keyboard layout and lighting enums, fixed-size input/output unions, and public helper prototypes.

Important APIs and types: `union tux_wmi_xx_8in_80out_in_t/out_t` models the 8-byte input and 80-byte output for `TUX_GET_DEVICE_STATUS`. `union tux_wmi_xx_496in_80out_in_t/out_t` models the 496-byte input and 80-byte output for `TUX_KBL_SET_MULTIPLE_KEYS`, including up to 120 RGB key configurations. Enums define WMI method IDs `2` and `6`.

State and dependencies: no state. The header depends on `<linux/wmi.h>` and packed layout matching the firmware ABI exactly. It is consumed by both the WMI helper implementation and the virtual LampArray driver.

Risks and test signals: all structure offsets are firmware contract. Any packing, count, or method-ID change must be validated against real NB04 firmware. Build tests should include sparse/compile coverage, and runtime tests should confirm `sizeof()` for the unions remains 8, 80, 496, and 80 bytes respectively.
