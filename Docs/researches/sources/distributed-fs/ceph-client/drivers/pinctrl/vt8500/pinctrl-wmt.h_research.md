# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wmt.h

Purpose: private interface for WMT/vt8500-family pinctrl implementations. It defines register-bank descriptors, pin/group encoding helpers, the shared per-controller state container, and the `wmt_pinctrl_probe()` entry point.

Important APIs, types, and functions: `NO_REG` marks unsupported bank registers. `WMT_PINCTRL_BANK()` initializes `struct wmt_pinctrl_bank_registers`. `WMT_PIN()`, `WMT_BANK_FROM_PIN()`, and `WMT_BIT_FROM_PIN()` encode bank and bit into a linear pin number. `WMT_GROUP()` initializes a named pin group. `struct wmt_pinctrl_data` carries device pointers, MMIO base, bank descriptors, pin descriptors, group names, counts, and embedded GPIO/pinctrl range storage.

Control flow: SoC-specific source files include this header, statically define banks/pins/groups with these macros, initialize `wmt_pinctrl_data`, then call `wmt_pinctrl_probe()` from their platform probe. The shared C file consumes the register offsets and counts directly.

State and persistence: the header declares no storage by itself. Its structures describe runtime state owned by each platform instance and hardware register layout. The MMIO base is documented as needing initialization before probe, but the shared probe also maps it itself, so the comment is partially stale.

Dependencies and integration points: includes `linux/gpio/driver.h` and relies on pinctrl descriptors from the including C files. It is internal to `drivers/pinctrl/vt8500`.

Risks and edge cases: `NO_REG` uses `0xFFFF`, so real register offsets must not collide with that sentinel. Pin encoding assumes 32 pins per bank. `WMT_GROUP()` can describe multi-pin groups, but the shared implementation effectively treats groups as single pin descriptors, so users must align group arrays with shared driver expectations.

Test signals: compile coverage of all including SoC drivers, static inspection of bank offsets/counts, and hardware probe confirming `ngpio == nbanks * 32` matches the actual controller.
