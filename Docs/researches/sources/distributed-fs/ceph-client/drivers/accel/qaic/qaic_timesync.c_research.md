# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_timesync.c

Purpose: implements QAIC host/device time synchronization over two MHI services: periodic `QAIC_TIMESYNC_PERIODIC` and boot-time/on-demand `QAIC_TIMESYNC`.

Important APIs and types: public functions are `qaic_timesync_init`, `qaic_timesync_deinit`, and `qaic_mqts_ch_stop_timer`. Internal protocol types include `qts_hdr`, `qts_timeval`, `qts_host_time_sync_msg_data`, `mqts_dev`, and `qts_resp`.

Control flow: the periodic probe allocates an `mqts_dev`, prepares the MHI channel, stores the QTimer MMIO address, and starts a timer. Each timer callback reads host real time and the device QTimer, computes a UTC offset in seconds/useconds, queues a sync message, and reschedules itself. The boot-time service queues response buffers; received device commands are handled in a workqueue, which requeues RX first, then sends current host time or logs ACKs.

State and persistence: periodic state includes one sync buffer, an atomic in-use flag, a timer, and channel/device pointers. Boot-time state is per-response work item. State is freed on channel remove, and suspend stops the periodic timer through `qaic_mqts_ch_stop_timer`.

Dependencies and integration: depends on MHI, `ktime_get_real*`, QTimer MMIO in `bar_mhi`, `qaic_device` workqueues, and module registration from `qaic_drv.c`.

Risks and test signals: test readq and 32-bit fallback QTimer reads, `mhi_queue_buf` `-EAGAIN`, timer deletion during suspend/remove, malformed boot responses, repeated ACK/command cycles, and registration unwind when the second MHI driver registration fails.
