# sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf.h

Purpose: Defines the internal pin configuration interface used between the pinctrl core, generic pinconf code, and controller drivers. It supplies real declarations when relevant Kconfig options are enabled and no-op or `-ENOTSUPP` stubs otherwise.

Important APIs and types: Declares `struct pinctrl_dev`, `struct pinctrl_map`, `struct pinctrl_setting`, and the core functions from `pinconf.c`: operation checking, map validation, setting conversion/free/apply, direct pin config set, and pin/group config get. It also declares debugfs functions, generic pinconf dump helpers, DT parsing helpers, and generic pins-function DT mapping when their config options are enabled.

Control flow: The header has no runtime control flow, but compile-time conditionals determine whether callers are linked to real implementations or stubs. `CONFIG_PINCONF` gates core pinconf behavior; `CONFIG_DEBUG_FS` gates debug display; `CONFIG_GENERIC_PINCONF && CONFIG_OF` gates generic DT config and pinmux parsing.

State and persistence: No state is stored here. The main persistence implication is build-time: when pinconf is disabled, callers can still compile but configuration requests resolve to no-ops or unsupported errors, preventing accidental hardware mutation.

Dependencies and integration points: Includes `linux/errno.h` and participates in nearly every pinconf-related source file in this directory. It is consumed by core pinctrl code and by drivers that need internal helpers beyond public `<linux/pinctrl/pinconf.h>`.

Risks: Stub behavior must match caller expectations. Several disabled paths return success for validation/apply/free-style helpers, so code compiled without `CONFIG_PINCONF` may skip behavior silently. There is no non-`CONFIG_PINCONF` stub for `pin_config_group_get()`, consistent with current callers but a trap for new code if used outside the guarded build.

Test signals: Build matrix coverage is the main signal: `CONFIG_PINCONF=n`, `CONFIG_GENERIC_PINCONF=n`, `CONFIG_OF=n`, and `CONFIG_DEBUG_FS=n` should all compile. Runtime validation belongs to the implementation files selected by these guards.
