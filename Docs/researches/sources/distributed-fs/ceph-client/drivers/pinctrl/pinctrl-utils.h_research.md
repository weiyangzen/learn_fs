# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-utils.h

## Purpose
Declares the shared pinctrl map/config construction helpers implemented in `pinctrl-utils.c`.

## Important APIs, Types, And Functions
The header exposes prototypes for reserving map capacity, adding mux maps, adding group/pin config maps, appending single packed configs, and freeing generated maps. It includes `<linux/pinctrl/machine.h>` for `struct pinctrl_map` and `enum pinctrl_map_type`, and forward declares `struct pinctrl_dev`.

## Control Flow
There is no runtime control flow in the header. It defines a compile-time interface consumed by pinctrl drivers and DT parsers.

## State And Persistence
No state is stored here. The API contract describes caller-owned allocation state passed through pointer parameters.

## Dependencies And Integration Points
Integrated with pinctrl core map registration and with drivers that use `pinconf_generic_dt_node_to_map_all()` or custom map assembly. The include guard is `__PINCTRL_UTILS_H__`.

## Risks
Because the API is pointer-counter based, misuse can compile cleanly but corrupt map accounting at runtime. Any signature change affects many platform pinctrl drivers.

## Test Signals
Build all pinctrl drivers that include this header, especially DT-enabled drivers using `.dt_free_map = pinctrl_utils_free_map`.
