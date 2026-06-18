# sources/distributed-fs/ceph-client/drivers/pinctrl/devicetree.c

Purpose: Converts generic pinctrl device-tree properties into runtime pinctrl mapping tables and provides helpers for bindings that use indexed pinctrl argument arrays.

Important APIs and functions: Exports `of_pinctrl_get()`, `pinctrl_dt_to_map()`, `pinctrl_dt_free_maps()`, `pinctrl_count_index_with_args()`, and `pinctrl_parse_index_with_args()`. Internally, `dt_to_map_one_config()` finds the owning controller node, calls the controller's `dt_node_to_map()`, and `dt_remember_or_free_map()` registers and tracks generated maps.

Control flow: `pinctrl_dt_to_map()` walks `pinctrl-0`, `pinctrl-1`, etc. on a consumer node, resolves optional names from `pinctrl-names`, follows each phandle to a config node, finds the parent pin controller, asks that controller to produce maps, and registers each map chunk. Empty states become `PIN_MAP_TYPE_DUMMY_STATE`. On any error, all DT-derived maps for that consumer are freed.

State and persistence: `struct pinctrl_dt_map` records each generated map chunk on `p->dt_maps`. Map entries get duplicated `dev_name` strings and borrow state-name strings from DT property storage after taking a node reference. Registered maps persist until `pinctrl_dt_free_maps()` unregisters them and calls controller `dt_free_map()`.

Dependencies and integration points: Depends on OF, `core.c` map registration, controller `pctlops->dt_node_to_map`, optional `dt_free_map`, module probe deferral, and `#pinctrl-cells` conventions for argument helpers.

Risks: Parent-walking defers probe unless `pinctrl-use-default` allows missing controllers, so DT hierarchy mistakes can become probe loops. Map memory ownership is split between this file and controller callbacks; leaks or double frees occur if callbacks do not match allocation strategy. Indexed argument helpers assume a parent or grandparent supplies `#pinctrl-cells`.

Test signals: DT overlays with named, unnamed, empty, invalid-phandle, missing-controller, hog, and `pinctrl-use-default` states; module deferral tests; and bindings using `pinctrl_parse_index_with_args()` cover the important paths.
