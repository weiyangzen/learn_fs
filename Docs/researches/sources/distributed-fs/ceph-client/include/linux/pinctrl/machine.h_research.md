# sources/distributed-fs/ceph-client/include/linux/pinctrl/machine.h

## Purpose
Board/machine pinctrl mapping API. It lets platform code describe how device state names map to controller mux groups and pin/group configuration entries.

## Important APIs, Types, and Functions
Defines `enum pinctrl_map_type`, `struct pinctrl_map_mux`, `struct pinctrl_map_configs`, and `struct pinctrl_map`. Provides macros for dummy states, mux-group states, default states, hog states, pin config states, and group config states. Enabled APIs include `pinctrl_register_mappings()`, `devm_pinctrl_register_mappings()`, `pinctrl_unregister_mappings()`, and `pinctrl_provide_dummies()`; disabled stubs return success/no-op.

## Control Flow
Machine code builds static `pinctrl_map` arrays using macros, registers them during platform setup or device-managed probe, and unregisters when appropriate. Pinctrl consumers later resolve state names against these mappings.

## State and Persistence
Registered mapping tables persist in the pinctrl core until explicitly unregistered or devm cleanup. The mapping entries point at device names, state names, controller names, mux functions, and configuration arrays.

## Dependencies and Integration Points
Depends on array-size macros and pinctrl state names. Integrates board files, platform data, pinmux providers, pinconf providers, and consumer state lookup.

## Risks
String names must match device/controller names exactly. Config arrays must outlive registered mappings. Disabled stubs can let board code build without pinctrl but no hardware muxing occurs.

## Test Signals
Board boot/probe tests, mapping registration/unregistration tests, pinmux hog tests, default/sleep state lookup tests, and disabled pinctrl build tests.
