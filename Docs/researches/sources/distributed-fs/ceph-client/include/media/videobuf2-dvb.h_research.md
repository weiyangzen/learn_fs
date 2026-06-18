# sources/distributed-fs/ceph-client/include/media/videobuf2-dvb.h

Purpose: This header bridges videobuf2 queue/thread support with DVB demux, frontend, network, and adapter registration. It lets media drivers expose DVB streaming using vb2-backed queues.

Important APIs, types, and functions: `struct vb2_dvb` contains driver-filled name/frontend and a `struct vb2_queue`, plus DVB-managed state: mutex, feed count, demux, dmxdev, hardware and memory frontends, and DVB network object. `struct vb2_dvb_frontend` wraps one frontend and list node. `struct vb2_dvb_frontends` stores all frontends, adapter, active frontend ID, and gate control. Registration helpers are `vb2_dvb_register_bus()`, `vb2_dvb_unregister_bus()`, `vb2_dvb_alloc_frontend()`, `vb2_dvb_dealloc_frontends()`, `vb2_dvb_get_frontend()`, and `vb2_dvb_find_frontend()`.

Control flow: A driver allocates frontends, initializes each frontend's DVB and vb2 queue data, registers the bus with module/device/media-device context, and feeds transport-stream data through the vb2 queue/thread machinery. Unregistration tears down DVB demux devices, net interfaces, frontends, and vb2 queues.

State and persistence behavior: Runtime state includes frontend list membership, active frontend selection, feed count, DVB demux state, and the embedded vb2 queue. No persistent storage is defined. The lock protects feed and frontend management state.

Dependencies and integration points: It depends on DVB core headers, `videobuf2-v4l2.h`, and optionally a media controller device. It integrates with DVB adapters, demux devices, DVB network support, frontends, and the special-purpose `vb2_thread` API noted by the header.

Risks: The header notes that vb2 thread support is not purely core and has V4L2 dependencies, so layering is fragile. Multi-frontend gate and active ID management can race if not protected. Feed count leaks can keep hardware active after unregister. Queue shutdown must happen before DVB objects disappear.

Test signals: Register/unregister single and multi-frontend adapters, start/stop feeds repeatedly, exercise frontend gate selection, verify vb2 thread start/stop, hot-unplug during active demux, and media-controller integration when an `mdev` is supplied.
