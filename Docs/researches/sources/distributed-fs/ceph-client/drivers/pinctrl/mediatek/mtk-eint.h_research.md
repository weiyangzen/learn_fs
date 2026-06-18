# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/mtk-eint.h

Purpose: Defines the public MediaTek EINT data structures, SoC hardware descriptors, pin maps, pinctrl callback interface, exported debounce tables, and optional stubs when `CONFIG_EINT_MTK` is disabled.

Important APIs/types/functions: Important types are `struct mtk_eint_regs`, `struct mtk_eint_hw`, `struct mtk_eint_pin`, `struct mtk_eint_xt`, and `struct mtk_eint`. Function prototypes mirror the implementation exports: initialization, suspend/resume, debounce setting, and IRQ lookup. When EINT support is disabled, inline stubs return `-EOPNOTSUPP`.

Control flow: The header itself has none. Pinctrl drivers allocate/fill `struct mtk_eint`, attach `gpio_xlate` callbacks, provide register bases and hardware metadata, then call `mtk_eint_do_init()`. GPIO chips later call `mtk_eint_find_irq()` and `mtk_eint_set_debounce()`.

State and persistence: Declares all persistent EINT state: base pointers, per-base pin counts, irqdomain, wake/current masks, dual-edge flags, pin list lookup arrays, register layout, SoC debounce timings, and callback linkage to the pinctrl instance.

Dependencies and integration points: Depends on `linux/irqdomain.h` and GPIO/pinctrl consumers through opaque callback signatures. Integrated by old common MediaTek pinctrl, Moore/Paris variants, and SoC drivers that expose GPIO interrupt support.

Risks: Structure layout is a cross-file contract. `u16` pin numbers and base counts must be large enough for SoC descriptors. Callback correctness is critical: `get_gpio_n`, `get_gpio_state`, and `set_gpio_as_eint` are invoked while requesting IRQ resources and during dual-edge handling. Stub behavior means drivers must tolerate absent EINT support.

Test signals: Compile with `CONFIG_EINT_MTK=y/m/n`, build all users, validate callbacks are populated before init, and run GPIO IRQ/debounce/wake tests on drivers that include EINT hardware data.
