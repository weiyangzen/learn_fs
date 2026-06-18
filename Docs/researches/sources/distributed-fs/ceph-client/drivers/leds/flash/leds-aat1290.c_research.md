# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-aat1290.c

## Purpose
This platform driver supports the Skyworks AAT1290 flash LED current regulator. It drives the part through FLEN and EN/SET GPIOs using the AS2Cwire pulse protocol, registers a flash LED class device, and optionally exposes a V4L2 flash subdevice.

## Important APIs, Types, and Functions
`struct aat1290_led` stores GPIOs, mutex, flash class device, V4L2 handle, movie-mode current scale, and mode cache. `struct aat1290_led_config_data` stores device-tree current/timeout limits. Protocol programming is `aat1290_as2cwire_write()`. LED operations are `aat1290_led_brightness_set()`, `aat1290_led_flash_strobe_set()`, and `aat1290_led_flash_timeout_set()`. Configuration helpers include `aat1290_led_parse_dt()`, `init_mm_current_scale()`, `aat1290_led_validate_mm_current()`, and `aat1290_init_flash_timeout()`.

## Control Flow
Probe allocates state, reads GPIOs and the first LED child node, initializes current scales from `flash-max-microamp`, validates `led-max-microamp`, registers `led_classdev_flash`, and creates a V4L2 flash device. Torch/movie brightness writes enter movie mode if needed, program current ratio, write current level, and enable movie mode. Flash strobe writes the cached timeout into the safety timer immediately before enabling FLEN. Strobe-off clears both GPIO lines and resets the software brightness/movie-mode cache.

## State and Persistence
State is volatile. `movie_mode` prevents redundant ratio programming while torch mode is active. The LED flash core caches timeout because directly writing the timer register can spuriously turn torch mode on. The nonlinear movie current scale is retained only when V4L2 flash class is enabled because V4L2 conversion callbacks need it.

## Dependencies and Integration Points
The driver depends on GPIO descriptors `flen` and `enset`, OF child properties `led-max-microamp`, `flash-max-microamp`, and `flash-max-timeout-us`, optional pinctrl states for external strobe source switching, LED flash class registration, and V4L2 flash integration. It binds `skyworks,aat1290`.

## Risks and Edge Cases
The macro `AAT1290_MM_TO_FL_RATIO` is integer arithmetic (`1000 / 1920`) and evaluates to zero, which can collapse default movie current calculations; this is a high-value review target. `aat1290_led_parse_dt()` assigns a `__free(device_node)` child to `*sub_node`, which needs care because the returned node must stay valid for later registration. Flash timer writes are deliberately delayed to strobe time due to side effects. External strobe switching depends on pinctrl state names `isp` and `host`.

## Test Signals
Test GPIO pulse timing with a scope or logic analyzer, torch brightness levels, flash strobe timeout programming, V4L2 intensity conversion, and external strobe pinctrl switching. Device-tree tests should cover missing child nodes and missing current/timeout properties. Verify no use-after-put for the LED child fwnode during probe.
