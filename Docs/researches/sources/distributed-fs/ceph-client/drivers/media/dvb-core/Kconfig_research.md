# sources/distributed-fs/ceph-client/drivers/media/dvb-core/Kconfig

## Purpose
This Kconfig file defines optional DVB core features: experimental memory-mapped DVB demux/DVR APIs, DVB network support, adapter count limits, dynamic minor allocation, and debug logging for demux section loss and ULE packet handling.

## Important APIs, Types, and Functions
The important configuration symbols are `DVB_MMAP`, `DVB_NET`, `DVB_MAX_ADAPTERS`, `DVB_DYNAMIC_MINORS`, `DVB_DEMUX_SECTION_LOSS_LOG`, and `DVB_ULE_DEBUG`. The file uses Kconfig primitives `config`, `bool`, `int`, `depends on`, `default`, `range`, `select`, and help text.

## Control Flow
When `DVB_CORE` is enabled, these options become available. `DVB_MMAP` additionally requires a compatible built-in or module relationship with `VIDEO_DEV` and selects `VIDEOBUF2_VMALLOC`. `DVB_NET` defaults to enabled when `NET` and `INET` are available. `DVB_MAX_ADAPTERS` bounds the number of adapter slots. The selected symbols drive conditional object inclusion in `drivers/media/dvb-core/Makefile` and conditional code in `dmxdev.c`.

## State and Persistence
Selections persist in the kernel `.config`. Runtime state is not stored here, but choices affect available device APIs, number of adapter minors, and debug verbosity compiled into the DVB subsystem.

## Dependencies and Integration Points
`DVB_MMAP` ties DVB demux/DVR mmap ioctls to vb2 vmalloc support and the video device core. `DVB_NET` controls inclusion of DVB network code. Debug options are consumed by DVB demux/net C files through preprocessor conditionals. `DVB_MAX_ADAPTERS` and `DVB_DYNAMIC_MINORS` influence DVB device registration behavior in core code.

## Risks and Edge Cases
`DVB_MMAP` is explicitly experimental and changes userspace-visible ioctl/mmap behavior. Its dependency on `VIDEO_DEV=y || VIDEO_DEV=DVB_CORE` prevents invalid module/built-in combinations for vb2/video helpers. Increasing `DVB_MAX_ADAPTERS` increases memory footprint. Debug logging options can be very verbose and should not be enabled casually on production systems.

## Test Signals
Build configurations should cover `DVB_CORE` with and without `DVB_MMAP`, `DVB_NET`, and debug symbols. Runtime checks include presence or absence of `DMX_REQBUFS`/mmap behavior, DVB net device availability, correct adapter numbering limits, and no Kconfig unmet-dependency warnings.
