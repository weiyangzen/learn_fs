# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss.c

Purpose: top-level OSS sequencer emulation module. It registers `/dev/sequencer` and `/dev/music`, the OSS synth sequencer-device driver, file operations, module init/exit, and optional proc output.

Important APIs, types, and functions: defines `seq_oss_synth_driver`, `alsa_seq_oss_init()`, `alsa_seq_oss_exit()`, `odev_open()`, `odev_release()`, `odev_read()`, `odev_write()`, `odev_ioctl()`, `odev_poll()`, `register_device()`, `unregister_device()`, `register_proc()`, and `unregister_proc()`.

Control flow: init registers OSS minors, proc entry, creates the OSS sequencer kernel client, registers the synth-driver probe/remove hooks, then initializes the MIDI synth pseudo-device. File open maps the minor to synth or music mode and delegates to `snd_seq_oss_open()`. File operations forward to the per-application `seq_oss_devinfo`; ioctl serializes most commands with `register_mutex` but leaves `SNDCTL_SEQ_SYNC` unlocked because it can wait.

State and persistence: holds a module-level `register_mutex`, optional proc `info_entry`, and the registered OSS device state managed by ALSA core. Per-open state lives in `seq_oss_init.c`'s `seq_oss_devinfo`.

Dependencies and integration: depends on ALSA OSS minor registration, `seq_oss_device.h` facade functions, synth registration in `seq_oss_synth.c`, and procfs when enabled.

Risks: init unwind must unregister in exact reverse order to avoid stale OSS minors or synth driver callbacks. File private data must be valid for all forwarded operations. `SNDCTL_SEQ_SYNC` deliberately bypasses the global mutex, so sync code must tolerate concurrent release/reset behavior.

Test signals: load/unload module, open both OSS minors, issue read/write/ioctl/poll on valid and released file descriptors, verify proc `oss` output, and force init failures in each registration stage.
