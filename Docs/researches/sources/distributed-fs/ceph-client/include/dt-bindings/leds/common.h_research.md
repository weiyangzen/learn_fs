<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/common.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/common.h

## Purpose
This common LED binding header defines standardized LED color IDs, functions, trigger type values, and boost mode values for device-tree LED nodes.

## Important APIs, types, and functions
It exports trigger type macros `LEDS_TRIG_TYPE_EDGE` and `LEDS_TRIG_TYPE_LEVEL`, boost mode macros `LEDS_BOOST_OFF`, `LEDS_BOOST_ADAPTIVE`, `LEDS_BOOST_FIXED`, color IDs from `LED_COLOR_ID_WHITE` through `LED_COLOR_ID_LIME`, and function strings such as `LED_FUNCTION_STATUS`, `LED_FUNCTION_POWER`, `LED_FUNCTION_KBD_BACKLIGHT`, `LED_FUNCTION_WLAN`, and `LED_FUNCTION_WPS`.

## Control flow
DTS LED nodes include the header and use the constants in properties such as `color`, `function`, trigger-related properties, or driver-specific boost settings. LED class drivers and schema validation consume the resulting values.

## State and persistence
No runtime state exists. The string and numeric constants form shared DT ABI and influence stable LED names exposed to userspace.

## Dependencies and integration points
It integrates with LED class device naming, multicolor LED bindings, flash/torch/backlight drivers, netdev/activity triggers, and YAML schemas that restrict color/function values.

## Risks and test signals
Risks include creating nonstandard LED names, using obsolete function strings instead of standardized ones, assigning colors beyond `LED_COLOR_ID_MAX`, and changing values visible to userspace naming policy. Test signals include `dtbs_check`, LED class device names under `/sys/class/leds`, trigger behavior, multicolor LED registration, and board LED smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/common.h -->
