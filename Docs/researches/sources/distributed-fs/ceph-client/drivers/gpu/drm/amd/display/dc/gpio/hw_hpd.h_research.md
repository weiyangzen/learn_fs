# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_hpd.h

Purpose: Declares the HPD GPIO subclass layout and construction helpers. HPD pins extend `hw_gpio` with HPD interrupt/status register metadata.

Important APIs and types: `struct hw_hpd` embeds `struct hw_gpio base` and stores `hpd_registers`, shift, and mask tables. `HW_HPD_FROM_BASE` converts from `hw_gpio_pin` to `hw_hpd` via the embedded GPIO. `dal_hw_hpd_init` allocates/constructs a hardware HPD pin, and `dal_hw_hpd_get_pin` adapts a high-level `gpio` object back to the base pin interface.

Control flow: ASIC-specific factories or GPIO manager code create HPD pins, fill the register metadata, then expose only `hw_gpio_pin` operations to the rest of display core. The header is intentionally small because all behavior is in the C file and inherited common GPIO code.

State and persistence: state is inherited from `hw_gpio` plus immutable register table pointers after initialization. The header defines no persistence or synchronization.

Dependencies and integration: includes `hpd_regs.h`; forward-declared `struct gpio` is used for conversion from the GPIO wrapper. Integrates with hotplug interrupt handling and connector detection logic.

Risks and test signals: new ASIC HPD register definitions must keep shift/mask tables compatible with this struct. Compile tests should catch missing register fields; runtime tests should validate delayed sense bit mapping for each HPD instance.
