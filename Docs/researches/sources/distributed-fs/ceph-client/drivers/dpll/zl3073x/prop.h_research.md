# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/prop.h

## Purpose
This header declares the ZL3073x property helper model used to register DPLL devices and pins with meaningful metadata.

## Important APIs and types
`struct zl3073x_pin_props` contains an optional firmware node, `struct dpll_pin_properties`, generated package label storage, and the `esync_control` flag. It declares pin property get/put and DPLL type lookup.

## Integration, state, risks, and tests
`dpll.c` allocates these objects during pin registration and releases them after DPLL core registration. The header owns no persistent state. Tests should catch lifetime errors around fwnode references and supported frequency arrays.
