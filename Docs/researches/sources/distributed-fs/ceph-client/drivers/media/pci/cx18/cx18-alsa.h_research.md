<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa.h

Purpose: Defines cx18 ALSA private card state, debug macros, and lock helpers shared by cx18 ALSA main/PCM code.

Important APIs/types: `struct snd_cx18_card` stores the owning V4L2 device, ALSA card, capture period/hardware counters, active substream, and spinlock. `snd_cx18_lock()` and `snd_cx18_unlock()` reuse `cx->serialize_lock` so ALSA file operations serialize with V4L2 operations. Debug macros format logs using the cx18 V4L2 device name.

Control flow: ALSA PCM open/close use the lock helpers around stream claim/start/stop and callback changes. Pointer reads use `slock`.

State/persistence: Runtime-only ALSA state attached to `cx->alsa`. No persistent config.

Dependencies/integration: Depends on `to_cx18()` from cx18 core and ALSA card/substream types. Keeps ALSA stream manipulation consistent with cx18 file-operation serialization.

Risks: Debug macros reference a local `v4l2_dev` variable by name, so callers must have one in scope. The struct has limited locking; only pointer reads use `slock`, while other fields rely on ALSA/cx18 serialization.

Test signals: Compile coverage of macros in all call sites, lock ordering with V4L2 opens, and pointer/counter consistency during capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa.h -->
