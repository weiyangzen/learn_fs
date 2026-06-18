# sources/distributed-fs/ceph-client/sound/soc/soc-ac97.c

Purpose: implements ASoC AC97 component allocation/registration, optional AC97 GPIO exposure, and generic GPIO/pinctrl-based AC97 reset operation setup.

Important APIs and data: `soc_ac97_bus` is the shared AC97 bus with ops set by `snd_soc_set_ac97_ops()`. `snd_soc_alloc_ac97_component()` allocates and initializes an `snd_ac97` device under the card. `snd_soc_new_ac97_component()` optionally resets/checks codec ID, registers the device, and initializes GPIOs. `snd_soc_free_ac97_component()` removes GPIOs/device and releases the ref. Under `CONFIG_GPIOLIB`, `snd_ac97_gpio_priv` and `snd_soc_ac97_gpio_chip` map AC97 GPIO register access to gpiolib callbacks. `snd_soc_set_ac97_ops_of_reset()` parses pinctrl states and GPIOs, installs warm/cold reset callbacks, and stores `snd_ac97_rst_cfg`.

Control flow and state: AC97 creation is allocate, optional reset, `device_add`, GPIO registration. Free reverses those steps. Reset config is a single static global and includes pinctrl state handles and GPIO descriptors. AC97 bus ops are also global and protected only by busy checks.

Dependencies and integration: uses ALSA AC97 core, ASoC component register read/write helpers, gpiolib, pinctrl, platform device resources, and device-tree named `ac97` GPIOs/states.

Risks: global `soc_ac97_ops` and reset config limit concurrent differing controllers. Error path after GPIO init failure calls `put_device()` without `device_del()` after successful `device_add()`, which is a lifecycle-sensitive path to audit. GPIO direction debug strings include a likely typo for input.

Test signals: AC97 device appears with card-derived name, reset toggles expected pins/states, GPIO chip exposes 8 AC97 GPIOs when enabled, and `snd_soc_set_ac97_ops()` returns `-EBUSY` when replacing active ops.
