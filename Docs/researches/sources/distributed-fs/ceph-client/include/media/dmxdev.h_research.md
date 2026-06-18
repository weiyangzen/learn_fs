# sources/distributed-fs/ceph-client/include/media/dmxdev.h

Purpose: Defines the DVB demux character-device layer that exposes demux and DVR devices on top of `struct dmx_demux`, ring buffers, and optional VB2 mmap streaming.

Important APIs/types/functions: `enum dmxdev_type` differentiates section and PES filters. `enum dmxdev_state` tracks free, allocated, set, running, one-shot done, and timed-out filters. `dmxdev_feed`, `dmxdev_filter`, and `dmxdev` store feed lists, section/PES parameters, ring buffers, VB2 contexts, timers, locks, device nodes, capabilities, DVR frontend state, and release flags. APIs are `dvb_dmxdev_init` and `dvb_dmxdev_release`.

Control flow: Initialization registers demux and DVR DVB devices. Userspace ioctls allocate filters, set section or PES parameters, start feeds through `dmx_demux`, buffer data into `dvb_ringbuffer` or `dvb_vb2_ctx`, and transition states. Release tears down devices and active feeds.

State and persistence: Runtime state is per-filter and per-device: filter state machine, buffers, timers, mutex/spinlock, DVR buffer, mmap context, exit flag, and original frontend for DVR routing. No persistent storage exists.

Dependencies and integration: Depends on `dvbdev.h`, `demux.h`, `dvb_ringbuffer.h`, `dvb_vb2.h`, timers, wait queues, mutexes, spinlocks, and DVB `dmx.h` ioctl structures.

Risks and test signals: Risks include state transition bugs, timeout races, buffer overflow, mmap and read path divergence, duplex capability misreporting, and release while filters are active. Test one-shot and timed section filters, PES capture, DVR read/write, mmap streaming, poll behavior, and disconnect/release races.
