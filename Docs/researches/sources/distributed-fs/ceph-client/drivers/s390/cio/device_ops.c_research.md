# sources/distributed-fs/ceph-client/drivers/s390/cio/device_ops.c

Purpose: exports the public CCW device operation API used by s390 device drivers to start, halt, clear, resume, query, and allocate DMA memory for CCW and transport-mode I/O.

Important APIs/types/functions: option APIs include `ccw_device_set_options_mask()`, `ccw_device_set_options()`, and `ccw_device_clear_options()`. I/O APIs include `ccw_device_start_timeout_key()`, wrappers for default key/timeout, `ccw_device_halt()`, `ccw_device_clear()`, `ccw_device_resume()`, `ccw_device_tm_start_timeout_key()` and wrappers, and `ccw_device_tm_intrg()`. Query/allocation helpers include `ccw_device_get_ciw()`, path and channel descriptor getters, `ccw_device_get_id()`, `ccw_device_get_schid()`, `ccw_device_pnso()`, CSSID/IID/CHPID/CHID getters, and `ccw_device_dma_zalloc()`/`ccw_device_dma_free()`.

Control flow: start paths validate device/subchannel state, optionally queue a fake command or transport IRB if verification is underway, mask caller path selection against `sch->lpm`, apply CIO options, and call `cio_start_key()` or `cio_tm_start_key()`. Halt/clear/resume validate online or W4SENSE states before invoking low-level CIO instructions. Query helpers read sense-id CIWs, SCHIB path fields, channel-path descriptors, or CSS metadata.

State and persistence behavior: updates in-memory driver options, `private->intparm`, timers, fake IRB flags, QDIO data pointer indirectly, and device reference counts for DMA allocations. Hardware state is changed through CIO start/halt/clear/resume and CHSC/PNSO calls; no long-term persistence exists.

Dependencies and integration points: integrates `ccw_device_private`, `subchannel`, low-level CIO operations, channel-path descriptors, CHSC PNSO, transport-command support from FCX, and exported symbols consumed by CCW class drivers, QDIO users, and vfio-ccw.

Risks and test signals: state validation and fake IRB queuing are sensitive to races with verification. Path masks must not allow varied-off paths. `ccw_device_get_util_str()` assumes a valid channel path object after `chpid_to_chp()`. Tests should cover all state-dependent return codes, path mask filtering, mutually exclusive early/report-all options, transport start with timeout, DMA allocation reference balancing, and descriptor queries for missing paths.
