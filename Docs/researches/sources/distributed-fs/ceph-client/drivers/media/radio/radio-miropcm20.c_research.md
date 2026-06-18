# sources/distributed-fs/ceph-client/drivers/media/radio/radio-miropcm20.c

Purpose: implements V4L2 radio support for the ISA Miro PCM20 tuner, relying on the ALSA `snd-miro` ACI interface for tuner and RDS hardware access. It exposes a `/dev/radioX` device with frequency, tuner, mute, stereo/mono, and RDS controls.

Important APIs and functions: module entry/exit are `pcm20_init` and `pcm20_cleanup`. V4L2 operations include `vidioc_querycap`, `vidioc_g_tuner`, `vidioc_s_tuner`, `vidioc_g_frequency`, `vidioc_s_frequency`, event subscription, and control status logging. RDS transport helpers are `rds_waitread`, `rds_rawwrite`, `rds_write`, `rds_readcycle`, `rds_ack`, and `rds_cmd`. `pcm20_setfreq` programs tuner frequency through `snd_aci_cmd`. `pcm20_thread` polls RDS status and updates V4L2 RDS controls.

Control flow: initialization obtains the global ACI object with `snd_aci_get_aci`, registers a standalone `v4l2_device`, creates mute and RDS controls, sets mono/stereo mode, tunes the default frequency, and registers a radio video device. Opening the first file handle starts a kernel thread that polls the RDS decoder every two seconds. Frequency changes clamp to 87-108 MHz, reset RDS, and write ACI tune bytes. The RDS thread queries availability, clears controls after repeated no-RDS intervals, and updates PS name, radio text, PTY, TA, TP, and music/speech controls when valid data appears.

State and persistence: state is process-global in `pcm20_card`, including cached frequency, audio mode, V4L2 objects, ACI pointer, mutex, RDS controls, and optional polling thread. Hardware state lives in the PCM20/ACI device until changed; no settings persist across unload.

Dependencies and integration points: depends on `sound/aci.h`, low-level `inb/outb`, V4L2 device/ioctl/control/event APIs, and the `snd-miro` ALSA driver being loaded first. Userspace consumes radio tuning through V4L2 ioctls and RDS metadata through controls/events.

Risks: the module uses one static device instance, so it is not multi-card capable. RDS reads are timing-sensitive and include a magic microsecond delay. `rds_cmd` sometimes returns `-1` instead of a standard errno. The RDS thread updates controls from a polling context and depends on first-open/last-close lifetime. Tuner stereo detection is known to be affected by mute state.

Test signals: build with Miro/ACI dependencies, module load ordering with `snd-miro`, `v4l2-compliance` for tuner and control ioctls, frequency clamp tests, first-open/last-close thread lifetime, mute/mono commands on hardware, and real RDS station tests observing control events and no-RDS clearing.
