# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-moore.c

Purpose: Implements the MediaTek "Moore" generic DeviceTree binding pinctrl framework. It registers generic pin groups/functions from SoC tables, provides mux and pinconf operations, builds a GPIO chip, and optionally attaches the common MediaTek EINT library.

Important APIs/types/functions: Public entry is `mtk_moore_pinctrl_probe()`. Runtime callbacks include `mtk_pinmux_set_mux()`, `mtk_pinmux_gpio_request_enable()`, `mtk_pinmux_gpio_set_direction()`, `mtk_pinconf_get()`, `mtk_pinconf_set()`, group config helpers, `mtk_gpio_get()`, `mtk_gpio_set()`, `mtk_gpio_to_irq()`, and `mtk_gpio_set_config()`. Custom DT pinconf parameters are `mediatek,tdsel`, `mediatek,rdsel`, `mediatek,pull-up-adv`, and `mediatek,pull-down-adv`.

Control flow: Probe maps all named register bases from `soc->base_names`, copies pin descriptors, registers pinctrl without enabling it, adds generic groups/functions from SoC data, enables pinctrl so hogs can be claimed, tries to build EINT support, then registers the gpiochip. Mux setting iterates pins in a group and writes per-pin modes from group data. Pinconf get/set dispatches to common-v2 helpers and SoC callbacks for bias, drive strength, advanced pull, TDSEL/RDSEL, direction, level, and Schmitt input.

State and persistence: Runtime state lives in `struct mtk_pinctrl`: mapped bases, SoC data, spinlock, pinctrl device, optional EINT state, and gpiochip. Hardware state persists in SoC register fields reached through `mtk_hw_get_value()`/`mtk_hw_set_value()` and SoC-specific callbacks.

Dependencies and integration points: Depends on `pinctrl-mtk-common-v2.h`, `mtk-eint.h`, generic pinctrl/pinmux functions, GPIO library, and DT pinconf parsing. Moore SoC files provide `struct mtk_pin_soc` tables with pins, groups, functions, register calculators, and EINT metadata.

Risks: Group `data` must be an array of pin modes matching group pin count. Several operations return `-ENOTSUPP` when SoC callbacks are absent, so tables must advertise only supported properties. EINT failure is warning-only, leaving pinctrl/GPIO working but `to_irq` and debounce unavailable. The static `mtk_desc` is mutated at probe time; concurrent probes of multiple Moore instances would need scrutiny.

Test signals: Build all Moore SoC users, probe with and without `gpio-ranges`, DT mux group selection, GPIO direction/value, custom pinconf parsing, drive/bias/Schmitt/TDSEL/RDSEL get-set, EINT to_irq and debounce, and behavior when EINT init fails.
