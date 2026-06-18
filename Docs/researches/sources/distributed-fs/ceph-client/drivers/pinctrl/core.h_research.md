# sources/distributed-fs/ceph-client/drivers/pinctrl/core.h

Purpose: Defines private data structures and internal helper prototypes shared by the pinctrl core, DT parser, pinmux, pinconf, and generic group/function helpers.

Important APIs and types: Key structures are `struct pinctrl_dev`, `struct pinctrl`, `struct pinctrl_state`, `struct pinctrl_setting`, `struct pin_desc`, `struct pinctrl_maps`, and generic `struct group_desc`. It declares lookup helpers, group helpers, pin name helpers, GPIO range lookup, forced PM state helpers, and the global `pinctrl_maps` list/mutex.

Control flow: The header contains only declarations and the inline `pin_desc_get()` radix-tree lookup. It defines the private object graph used by `core.c`: controllers own pin descriptors, consumers own states, states own settings, and settings point back to the controller that applies mux/config operations.

State and persistence: No state is allocated here, but fields define lifetime rules. `struct pinctrl_dev` persists for controller lifetime, `struct pinctrl` is kref-counted per consumer, DT maps are linked to a consumer handle, and `pin_desc` tracks runtime mux/GPIO ownership.

Dependencies and integration points: Depends on Linux list, radix-tree, mutex, kref, and `linux/pinctrl/machine.h`. It is not a public driver ABI; external drivers generally use public pinctrl headers instead.

Risks: Because this is a private header, structure changes require synchronized updates across core, pinmux, pinconf, devicetree, and generic helper files. Conditional fields under `CONFIG_GENERIC_PINCTRL_GROUPS`, `CONFIG_GENERIC_PINMUX_FUNCTIONS`, `CONFIG_DEBUG_FS`, and `CONFIG_PINMUX` can hide build-only bugs.

Test signals: Matrix builds across pinmux/pinconf/generic-group/debugfs configs, controller registration, debugfs rendering, GPIO request paths, and DT map free paths validate structure layout assumptions.
