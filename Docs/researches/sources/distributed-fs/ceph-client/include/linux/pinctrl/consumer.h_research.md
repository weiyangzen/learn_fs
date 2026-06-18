# sources/distributed-fs/ceph-client/include/linux/pinctrl/consumer.h

## Purpose
Consumer-facing pinctrl API for devices and GPIO controllers. It lets drivers acquire pinctrl handles, select named states, and coordinate GPIO line ownership/direction/configuration with pin controllers.

## Important APIs, Types, and Functions
Declares opaque `struct pinctrl` and `struct pinctrl_state`. Enabled APIs include GPIO arbitration/config helpers, `pinctrl_get()`, `pinctrl_put()`, `pinctrl_lookup_state()`, `pinctrl_select_state()`, devm variants, default-state selection, and PM state selection helpers. Always-available convenience wrappers include `pinctrl_get_select()`, `pinctrl_get_select_default()`, `devm_pinctrl_get_select()`, and `devm_pinctrl_get_select_default()`.

## Control Flow
Typical flow gets a handle for a device, looks up a named state, selects it, and later releases the handle. Convenience helpers perform get/lookup/select with error unwinding. PM helpers select default/init/sleep/idle states when configured. Disabled `CONFIG_PINCTRL` builds return permissive GPIO results and NULL/no-op pinctrl state selection.

## State and Persistence
Pinctrl core owns persistent handles and states. Consumers hold returned handles and selected pin states affect hardware mux/config until another state is selected.

## Dependencies and Integration Points
Depends on error pointer helpers, `pinctrl-state.h`, GPIO chip integration, device model, and optional PM. Integrates driver probe/remove and suspend/resume state management.

## Risks
NULL stubs in disabled builds differ from error pointers, so callers must use standard helper semantics. Missing error unwinding can leak handles. Incorrect state selection can break GPIO or peripheral muxing.

## Test Signals
Driver probe tests with default/init/sleep/idle pin states, GPIO request/direction conflict tests, disabled-config build tests, and PM suspend/resume pin state checks.
