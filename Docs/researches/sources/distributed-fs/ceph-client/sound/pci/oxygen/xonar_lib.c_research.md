
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_lib.c

Purpose: shared helper implementation for Xonar board drivers.

Important functions: `xonar_enable_output` configures output-enable GPIO, waits anti-pop delay, then enables output; `xonar_disable_output` clears the output GPIO. `xonar_init_ext_power` enables GPI/GPIO interrupt masks, installs `gpio_changed`, and snapshots power state; `xonar_ext_power_gpio_changed` logs restore/loss events. `xonar_init_cs53x1` and `xonar_set_cs53x1_params` configure CS53x1 ADC mode GPIOs by sample rate. `xonar_gpio_bit_switch_get/put` expose GPIO bits as ALSA boolean controls with optional inversion.

State/persistence: uses `xonar_generic` fields inside model_data and shared `chip->interrupt_mask`; GPIO writes are saved by Oxygen I/O helpers. External power state is cached in `has_power`.

Dependencies: Oxygen GPIO/register helpers, ALSA control framework, and model_data layout convention.

Risks: helper assumes `xonar_generic` is at offset zero in model data; external power loss currently does not stop active PCMs. Test signals: output enable delay, power cable interrupt logging, GPIO mixer controls, inverted HDMI switch, CS53x1 rate-family changes, and resume output sequencing.
