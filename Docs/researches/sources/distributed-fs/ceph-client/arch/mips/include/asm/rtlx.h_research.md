# sources/distributed-fs/ceph-client/arch/mips/include/asm/rtlx.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/rtlx.h

### Purpose
`rtlx.h` declares the MIPS RTLX communication channel interface used between Linux and another VPE/SP in MIPS MT/APRP environments.

### Important APIs, Types, And Functions
Constants include `RTLX_MODULE_NAME`, `LX_NODE_BASE`, `MIPS_CPU_RTLX_IRQ`, `RTLX_VERSION`, `RTLX_ID`, `RTLX_BUFFER_SIZE`, `RTLX_CHANNELS`, and standard channel IDs. APIs include `rtlx_starting`, `rtlx_stopping`, `rtlx_open`, `rtlx_release`, `rtlx_read`, `rtlx_write`, read/write poll helpers, module init/exit, and `_interrupt_sp`. Types/state include `enum rtlx_state`, `struct chan_waitqueues`, `struct rtlx_channel`, global `channel_wqs`, `rtlx_notify`, `rtlx_fops`, `aprp_hook`, and `struct rtlx_info *rtlx`.

### Control Flow
VPE lifecycle notifications start/stop RTLX, userspace device operations open channels and perform buffered reads/writes, poll helpers expose readiness, and `_interrupt_sp` is the low-level interrupt bridge to the service processor side.

### State, Persistence, Dependencies, And Integration
State is shared memory rings (`rt_buffer`/`lx_buffer` with read/write indices), channel state, wait queues, mutexes, and atomic open guards. Dependencies include IRQ and VPE notification infrastructure plus file operations. Integration is with character devices, poll/select, MIPS MT VPE management, and APRP hooks.

### Risks
Ring indices are shared with another execution context; ordering, cache coherency, and wakeups must be correct. Channel open serialization and sleeping behavior must avoid deadlocks. Buffer IDs and version constants must match the remote side.

### Test Signals
Build MIPS MT/APRP configs, run open/read/write/poll tests across all channels, start/stop remote VPEs, stress concurrent opens, and verify interrupt-driven wakeups and buffer wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/rtlx.h -->
