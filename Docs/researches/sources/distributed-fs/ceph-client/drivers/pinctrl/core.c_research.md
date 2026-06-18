# sources/distributed-fs/ceph-client/drivers/pinctrl/core.c

Purpose: Implements the Linux pinctrl core: controller registration, pin descriptor storage, per-consumer pinctrl handles, mapping registration, device-tree map ingestion, state lookup/selection, GPIO range mediation, hog handling, power-management state forcing, and debugfs views.

Important APIs and functions: Exported entry points include `pinctrl_get()`, `pinctrl_put()`, `pinctrl_lookup_state()`, `pinctrl_select_state()`, devm variants, `pinctrl_register()`, `pinctrl_register_and_init()`, `pinctrl_enable()`, `pinctrl_unregister()`, `pinctrl_register_mappings()`, GPIO helpers such as `pinctrl_gpio_request()`, and PM helpers `pinctrl_force_sleep()`/`pinctrl_force_default()`. Core globals are `pinctrldev_list`, `pinctrl_list`, and `pinctrl_maps` with dedicated mutexes.

Control flow: Controller drivers register descriptors; pins are inserted into a radix tree and hog states are claimed when enabled. Consumers call `pinctrl_get()`, which parses DT maps, scans registered maps for the device, creates `pinctrl_state` objects, and attaches mux/config settings. `pinctrl_select_state()` disables old mux ownership, applies all new mux settings first, then config settings, links consumers to controllers, and partially rolls back mux ownership on errors.

State and persistence: Software state lives in global lists, radix trees, `kref`-counted `struct pinctrl`, current `p->state`, map chunks, GPIO ranges, and per-pin mux/GPIO ownership fields in `struct pin_desc`. Hardware state persists through driver callbacks in pinmux/pinconf layers and is not fully restorable if config application fails after mux changes.

Dependencies and integration points: Integrates with OF parsing (`devicetree.c`), pinmux/pinconf validators and appliers, gpiolib ranges, device links, debugfs, PM state names, and all controller drivers.

Risks: Lifetime and locking are central risks: maps retain caller-owned arrays, DT map chunks must unregister and free driver-allocated map data, and controller unregister races with active consumers are only partially guarded. Rollback after failed state selection can disable mux ownership but cannot generally restore prior hardware config. GPIO range readiness is heuristic when a GPIO line has no backing pin controller.

Test signals: Kernel pinctrl selftests if available, compile with `CONFIG_PINMUX`, `CONFIG_PINCONF`, `CONFIG_OF`, `CONFIG_GPIOLIB`, and `CONFIG_DEBUG_FS`; probe/remove controllers, request/free GPIOs, select default/init/sleep/idle states, exercise hogs, inspect debugfs, and inject invalid maps for error paths.
