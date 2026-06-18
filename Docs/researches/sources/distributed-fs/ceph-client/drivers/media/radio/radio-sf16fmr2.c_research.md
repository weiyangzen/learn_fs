# sources/distributed-fs/ceph-client/drivers/media/radio/radio-sf16fmr2.c

Purpose: supports MediaForte SF16-FMR2 and SF16-FMD2 radio cards by adapting their ISA/PnP I/O pins to the common `snd_tea575x` tuner helper and, when present, controlling the TC9154A/PT2254A audio attenuator.

Important APIs and functions: module lifecycle is `fmr2_init`/`fmr2_exit`, registering both PnP and ISA drivers. Core setup is `fmr2_probe`; removal is `fmr2_remove`. TEA575x operations are `fmr2_tea575x_set_pins`, `fmr2_tea575x_get_pins`, and `fmr2_tea575x_set_direction`. Audio controls use `tc9154a_set_attenuation`, `fmr2_s_ctrl`, and `fmr2_tea_ext_init`.

Control flow: PnP probe allocates an FMD2 instance using the PnP port, while ISA matching probes the hardwired FMR2 port `0x384`. `fmr2_probe` rejects duplicate ports, reserves I/O, registers a V4L2 device, configures the embedded `snd_tea575x`, and calls `snd_tea575x_init`. The TEA helper drives tuning and standard radio ioctls, calling back into the port pin functions. Extra volume/balance controls are added only for FMR2 cards that report a volume-control presence bit.

State and persistence: each card has a dynamically allocated `struct fmr2` containing I/O base, V4L2 device, embedded TEA575x state, optional volume/balance controls, and an FMD2 flag. Global arrays track up to two cards and which bus drivers registered.

Dependencies and integration points: depends on ISA and PnP bus APIs, `media/drv-intf/tea575x.h`, V4L2 device/control support through the TEA helper, direct port I/O, and microsecond delays for the volume shift register.

Risks: if `snd_tea575x_init` fails, `fmr2_probe` releases the I/O region but leaves the V4L2 device registered, which looks like a cleanup bug. The global `num_fmr2_cards` is incremented on probe but never decremented on remove. Volume attenuation mapping uses inverted absolute values around a max of 68 and is easy to regress. `set_direction` is a no-op because hardware direction is fixed/implicit.

Test signals: PnP FMD2 and ISA FMR2 probe/remove cycles, duplicate-port rejection, TEA575x detection failure cleanup, `v4l2-compliance` through the TEA helper, frequency and stereo tuning, optional volume/balance controls on hardware with the attenuator, and unload/reload checking global card count behavior.
