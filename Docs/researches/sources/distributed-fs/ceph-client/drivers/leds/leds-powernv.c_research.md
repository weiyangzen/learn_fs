# sources/distributed-fs/ceph-client/drivers/leds/leds-powernv.c

Purpose: IBM PowerNV OPAL LED driver exposing firmware-controlled identify, fault, and attention LEDs.

Important APIs/types/functions: `powernv_led_common` stores max LED type, global mutex, and unload-disable flag. `powernv_led_data` stores LED class device, location code, LED type, and common pointer. `powernv_led_set()` performs asynchronous OPAL set calls; `powernv_led_get()` queries OPAL state; `powernv_led_classdev()` walks OPAL LED device-tree nodes and `led-types` strings.

Control flow: probe locates `/ibm,opal/leds`, initializes common state, then registers one LED class device per location-code child and supported `led-types` string. Brightness set locks globally, obtains an OPAL async token, submits a set-indicator call, waits for completion, checks async return code, and releases the token. Remove marks operations disabled and destroys the mutex, intentionally preserving firmware LED state.

State and persistence: LED state is firmware/service-processor controlled and intentionally persists across driver unload/reboot. The driver caches only static type/location metadata and a disabled flag to avoid writes during teardown.

Dependencies and integration: depends on PowerNV OPAL firmware APIs, Open Firmware device tree, LED class, platform device matching `ibm,opal-v3-led`, and asynchronous OPAL token management.

Risks: OPAL calls can sleep and fail asynchronously, so blocking brightness callbacks and mutex serialization are necessary. Unsupported LED type strings abort registration for that path. Location code is taken from node name. Destroying the mutex while devm LED devices still exist is safe only because remove disables operations and device teardown ordering prevents later callbacks.

Test signals: OPAL DT nodes with multiple `led-types`, set/get success and OPAL_PARTIAL handling, async token interruption, unsupported type warnings, remove-time no-reset behavior, and service-processor state changes visible through brightness_get.
