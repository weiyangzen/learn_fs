<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/ipc.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/ipc.c

## Purpose
`ipc.c` implements the low-level MMIO IPC transport between the host and Intel ISH firmware. It owns register access, interrupt decoding, transmit queueing, management messages, reset handling, clock synchronization, DMA enable/disable, hardware reset, and the `ishtp_hw_ops` callbacks consumed by the ISHTP bus/core.

## Important APIs, Types, and Functions
Inline register helpers `ish_reg_read`/`ish_reg_write` access MMIO. Interrupt/readiness helpers include `check_generated_interrupt`, `ish_is_input_ready`, `ishtp_fw_is_ready`, host-ready setters, and `_ish_read_fw_sts_reg`. Message movement is handled by `_ishtp_read_hdr`, `_ishtp_read`, `write_ipc_to_queue`, `write_ipc_from_queue`, and `ipc_send_mng_msg`. Reset and PM helpers include `ish_send_reset_notify_ack`, `ish_fw_reset_handler`, `fw_reset_work_fn`, `_ish_sync_fw_clock`, `recv_ipc`, `ish_disable_dma`, `ish_wakeup`, `_ish_hw_reset`, `_ish_ipc_reset`, and `ish_hw_start`. `ish_dev_init` allocates and initializes the `ishtp_device`.

## Control Flow
Transmitters call the hardware `write` op, which copies a complete IPC frame into a free `wr_msg_ctl_info`, appends it to `wr_processing_list`, and tries immediate send. `write_ipc_from_queue` checks the host-to-ISH doorbell is idle, optionally refreshes clock-sync payload timestamps, writes message dwords and trailing bytes into host-to-ISH registers, rings the doorbell, updates counters, returns the control block to the free list, and calls completion outside the spinlock.

The IRQ handler first filters shared/spurious interrupts, reads the ISH-to-host doorbell, rejects disabled devices and overlong payloads, then dispatches management protocol to `recv_ipc` or ISHTP protocol to `ishtp_recv`. Management RX complete wakes suspend/resume waiters and drains the TX queue; reset notify sends ACK, marks hardware ready, and queues reset work. Reset work clears pending TX, notifies ISHTP reset, waits for input/FW readiness, then restarts HBM enumeration.

Hardware start sets host ready and sends IPC reset/wakeup. Hardware reset tries PCI function reset, disables DMA, cycles D3hot/D0 through PCI PM config, re-enables DMA, and sends reset. Clock sync is rate-limited to roughly every 20 seconds and writes boottime plus realtime values.

## State and Persistence Behavior
Persistent driver state lives in `struct ishtp_device`: device state, waitqueues, TX free/processing lists, IPC counters, suspend/resume flags, `prev_sync`, workqueue, and hardware ops. File-static `ishtp_dev` and `fw_reset_work` support the reset worker. Hardware state persists in IPC registers, doorbells, host communication bits, DMA remap, PCI power state, and firmware status. Spinlocks protect TX queues; waitqueues synchronize reset, suspend, and resume.

## Dependencies and Integration Points
The file depends on `client.h`, `hbm.h`, `hw-ish.h`, PCI power reset, workqueues, waitqueues, spinlocks, jiffies, and ktime. It exports the transport through `ishtp_hw_ops` to `ishtp-dev`/bus code and is driven by `pci-ish.c` IRQ and lifecycle callbacks.

## Risks and Edge Cases
Global `ishtp_dev` assumes a single active ISH instance. TX queue exhaustion returns `-ENOMEM`; callers must tolerate backpressure. Reset handling clears queued messages, so clients need robust reset callbacks. `timed_wait_for_timeout` subtracts sleep time from an unsigned timeout and depends on sane inputs. Manual cache-snooping platform detection must stay current for DMA correctness. Wrong interrupt path for a device generation can lose or fail to clear interrupts.

## Test Signals
Track IPC TX/RX counters, bad-length logs, reset-notify/ACK exchange, HBM restart after reset, suspend/resume ACKs, DMA inactive waits, host-ready recovery after OOB/power transitions, firmware clock sync messages, and HID sensor enumeration after forced `ish_hw_reset`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/ipc.c -->
