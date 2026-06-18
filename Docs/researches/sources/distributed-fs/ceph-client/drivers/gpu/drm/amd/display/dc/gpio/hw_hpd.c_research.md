# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_hpd.c

Purpose: Implements the HPD-specific GPIO subclass for hot-plug-detect pins. It reuses generic GPIO behavior for normal modes and overrides value/config handling needed for interrupt/sense debounce.

Important APIs and functions: `dal_hw_hpd_init` allocates and constructs an HPD pin. `dal_hw_hpd_get_pin` returns the embedded `hw_gpio_pin` from a higher-level `gpio`. `dal_hw_hpd_get_value` reads `DC_HPD_SENSE_DELAYED` when in `GPIO_MODE_INTERRUPT`; otherwise it delegates to `dal_hw_gpio_get_value`. `dal_hw_hpd_set_config` programs connect/disconnect interrupt delays in `toggle_filt_cntl`. The local function table binds common open/set/change/close with HPD-specific get/config/destroy.

Control flow: initialization allocates `struct hw_hpd`, calls the common GPIO constructor, then assigns the HPD vtable. During interrupt-mode reads, the code bypasses the generic GPIO `Y` register and reads HPD interrupt status. Config updates divide millisecond-like delay fields by 10 before writing hardware fields.

State and persistence: lifecycle state lives in the embedded `hw_gpio`. HPD-specific register table pointers are expected to be assigned by ASIC factory code after allocation. There is no persisted state; hardware debounce configuration persists in registers until reprogrammed.

Dependencies and integration: depends on `gpio_interface.h`, `hw_gpio.h`, `hpd_regs.h`, and `reg_helper.h`. It integrates with GPIO factory setup and with display link detection/interrupt handling that obtains HPD pins through `dal_hw_hpd_get_pin`.

Risks and test signals: `dal_hw_hpd_init` sets `*hw_hpd = NULL` for invalid `en` but does not immediately return, so later allocation may overwrite that unless callers never pass invalid values. Tests should cover interrupt-mode sense reads, debounce programming units, invalid/null config handling, allocation failure, and factory population of `regs`, `shifts`, and `masks`.
