# sources/distributed-fs/ceph-client/drivers/mfd/wm8350-regmap.c

`wm8350-regmap.c` defines the WM8350 register access table and exported `regmap_config`. It tells regmap which registers are readable, writable, volatile, and precious, with extra lock-aware write blocking for GPIO function-select and charger-control registers.

Important pieces are `struct wm8350_reg_access`, the 256-entry `wm8350_reg_io_map[]`, `wm8350_readable()`, `wm8350_writeable()`, `wm8350_volatile()`, `wm8350_precious()`, and exported `wm8350_regmap`. The config uses 8-bit register addresses, 16-bit values, Maple cache, `WM8350_MAX_REGISTER`, and the access callbacks. `wm8350_writeable()` checks `wm8350->unlocked` before allowing protected GPIO function and battery charger registers.

State is static except for dynamic lock state read from `struct wm8350`. Hardware is not modified here, but regmap cache behavior and access permission are controlled by these callbacks. Dependencies include WM8350 core definitions and the core security lock helpers.

Risks: callbacks index the table directly, so out-of-range reg values would be unsafe; bit-mask return values are reduced to boolean access decisions by regmap callbacks; stale `wm8350->unlocked` state can diverge from hardware lock state; precious interrupt status registers must remain accurate to avoid accidental clear-on-read loss. Test signals include invalid-register blocking, volatile cache behavior, lock/unlock writeability transitions, and IRQ status preservation under diagnostics.
