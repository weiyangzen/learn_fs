# sources/distributed-fs/ceph-client/drivers/pinctrl/devicetree.h

Purpose: Declares the internal interface between the pinctrl core and its device-tree parser, with no-op or `-ENODEV` stubs when `CONFIG_OF` is disabled.

Important APIs and types: Declares `pinctrl_dt_to_map()`, `pinctrl_dt_free_maps()`, `pinctrl_count_index_with_args()`, and `pinctrl_parse_index_with_args()`. Forward declarations cover `device_node`, `of_phandle_args`, `pinctrl`, and `pinctrl_dev`.

Control flow: With OF enabled, `core.c` calls these functions during handle creation and destruction. Without OF, parsing is skipped and indexed helper users get `-ENODEV`.

State and persistence: The header owns no state. It gates whether `struct pinctrl` instances may accumulate `dt_maps` from device-tree parsing.

Dependencies and integration points: Includes only `linux/errno.h` and is consumed by `core.c` plus other pinctrl internals needing indexed phandle parsing.

Risks: Stub behavior must match callers' expectations. A caller that treats `-ENODEV` as fatal under non-OF builds can regress platform-data users. Signature changes must stay synchronized with `devicetree.c`.

Test signals: Build and boot with `CONFIG_OF=y` and `CONFIG_OF=n`, plus compile coverage for consumers of the indexed parsing helpers.
