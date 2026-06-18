# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/gpio_interface.h

Purpose: Declares the object-level GPIO handle interface for AMD Display Abstraction Layer code. It treats `struct gpio` as opaque and exposes operations for opening a pin, reading/writing it, changing mode, locking, querying identity/configuration, and retrieving specialized DDC/HPD/generic views.

Important APIs and types: `dal_gpio_open`, `dal_gpio_open_ex`, `dal_gpio_close`, `dal_gpio_get_value`, `dal_gpio_set_value`, `dal_gpio_get_mode`, `dal_gpio_change_mode`, `dal_gpio_lock_pin`, `dal_gpio_unlock_pin`, `dal_gpio_get_id`, `dal_gpio_get_enum`, `dal_gpio_set_config`, `dal_gpio_get_pin_info`, `dal_gpio_get_sync_source`, and `dal_gpio_get_output_state`. Accessors `dal_gpio_get_ddc`, `dal_gpio_get_hpd`, and `dal_gpio_get_generic` expose typed hardware wrappers.

Control flow: The header establishes a lifecycle: create or obtain a GPIO handle from the service layer, open it in a `gpio_mode`, optionally configure it, perform IO or query operations, then close it. Lock/unlock are separate from open/close and likely protect shared physical pins from concurrent users.

State and persistence: State lives in the opaque `struct gpio` implementation: mode, open/closed status, lock state, pin identity, and output polarity. The API returns `enum gpio_result` for most mutating operations, so callers must preserve and check status instead of assuming writes succeed.

Dependencies and integration points: Includes `gpio_types.h` for modes/results/config data and `grph_object_defs.h` for sync-source related enums. Integrates with DDC and HPD services used by display detection, AUX/I2C, hotplug, and interrupt routing.

Risks: The API accepts raw `uint32_t` values for pin values and enum IDs, so implementation-side validation is critical. Misordered lifecycle calls can leave pins locked, configured to the wrong mode, or driven while hardware expects input. `open_ex` semantics are not documented here, increasing caller ambiguity.

Test signals: Tests should exercise open/change/close sequencing, invalid handle behavior, simultaneous lock contention, active-low output state handling, and DDC/HPD wrapper retrieval for each supported GPIO ID.
