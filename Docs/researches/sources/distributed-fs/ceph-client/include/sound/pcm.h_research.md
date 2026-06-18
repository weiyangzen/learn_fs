# sources/distributed-fs/ceph-client/include/sound/pcm.h

Source read summary: 1595 lines, central ALSA PCM kernel API.

Purpose: defines the kernel-facing ALSA PCM model: hardware capability descriptors, driver callbacks, runtime/substream/card structures, state/trigger/rate/format constants, hardware-parameter constraints, timestamp packing, stream locking, availability helpers, transfer helpers, buffer allocation, mmap, channel maps, and 32/64-bit status ioctls.

Important APIs, types, and functions: key types include `struct snd_pcm_hardware`, `snd_pcm_ops`, `snd_pcm_file`, `snd_pcm_hw_rule`, `snd_pcm_hw_constraints`, `snd_ratnum`, `snd_ratden`, constraint lists/ranges, timestamp config/report, `snd_pcm_runtime`, `snd_pcm_group`, `snd_pcm_substream`, `snd_pcm_str`, `snd_pcm`, `snd_pcm_chmap_elem`, `snd_pcm_chmap`, and status structs. APIs/macros cover state setting/getting, stream locks, frame/byte/sample conversion, playback/capture availability/readiness, hw param mask/interval access, params accessors, interval refine/list/ranges/ratnum, constraint registration, format queries/silence, PCM creation/ops/sync, period elapsed, userspace/kernel transfer, rate masks, runtime DMA buffer setup, timestamp selection, preallocation/managed/fixed buffers, SG helpers, mmap, channel maps, and iov_iter I/O helpers.

Control flow: card drivers create PCM devices, set ops, advertise hardware capabilities and constraints, allocate buffers, then ALSA core drives open, hw_params, prepare, trigger, pointer, copy/page/mmap, ack, period elapsed, drain, stop, and close. Hardware/software params refine masks and intervals before runtime fields are committed; transfer helpers advance application and hardware pointers under stream locks.

State and persistence behavior: PCM state is rich but volatile: runtime status, hw/sw params, mmap status/control, waitqueues, async notifications, DMA buffer metadata, timestamp config, OSS emulation state, substream groups, refcounts, PM QoS, and channel maps. Audio sample data persists only while buffers remain allocated.

Dependencies and integration points: depends on ALSA UAPI/asound, memalloc, minors, poll/mm/bitops/PM QoS/refcount/uio, optional OSS emulation, and all PCM drivers. It is the main contract between ALSA core, hardware drivers, and userspace PCM ioctls.

Risks and edge cases: ABI layout changes, duplicate fields visible in this source snapshot, pointer boundary wrap, XRUN detection, stream lock ordering, mmap buffer lifetime, noncoherent DMA sync, 32-bit compat status, timestamp accuracy, and constraint refinement loops are critical.

Test signals: ALSA PCM selftests and userspace playback/capture, mmap and read/write transfers, all trigger commands, hw_params refinement matrices, nonstandard rates/formats, suspend/resume, XRUN recovery, 32-bit compat ioctls, channel map controls, and OSS emulation builds.
