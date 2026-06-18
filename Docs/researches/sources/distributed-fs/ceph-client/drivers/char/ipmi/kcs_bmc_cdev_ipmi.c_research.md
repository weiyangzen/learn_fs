<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_cdev_ipmi.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_cdev_ipmi.c

## Purpose
Provides a BMC-side IPMI character device client for KCS channels. It translates host KCS protocol events into request buffers readable by userspace and accepts userspace response buffers to send back to the host.

## Important APIs, Types, and Functions
- `struct kcs_bmc_ipmi` stores client linkage, protocol phase, error code, waitqueue, input/output buffers, mutex, spinlock, and miscdevice.
- KCS protocol phases include idle, write start/data/end/done, wait read, read, abort error stages, and error.
- `kcs_bmc_ipmi_event()` dispatches IBF events to command or data handlers.
- `kcs_bmc_ipmi_handle_cmd()` handles KCS control codes: write start, write end, and get-status/abort.
- `kcs_bmc_ipmi_handle_data()` receives request bytes, sends response bytes, and completes abort handshakes.
- File operations expose open, poll, read, write, ioctl, and release.

## Control Flow
Opening the misc device exclusively enables the KCS BMC device for this client. Host write-start/data/write-end events fill `data_in`; write-end marks a complete request and wakes readers. Userspace `read()` copies the request and moves to wait-read phase. Userspace `write()` copies a response, primes the first output byte, and moves to read phase. Host read-byte commands drain output until the final zero and return to idle. Abort or protocol errors force error states and status responses.

## State and Persistence
Per-channel protocol state is in `phase`, `error`, `data_in_avail`, indexes, and buffers. `queue` synchronizes userspace. `mutex` protects userspace buffer copies while `lock` protects IRQ-visible protocol state. Instances are tracked in `kcs_bmc_ipmi_instances`.

## Dependencies and Integration Points
Registers as a `kcs_bmc_driver` with the generic KCS core. Exposes misc devices named `ipmi-kcs<channel>`. Uses `linux/ipmi_bmc.h` ioctls for SMS attention and force abort.

## Risks
The protocol is IRQ-driven and phase-sensitive; userspace latency leaves the channel in `WAIT_READ`. Buffer size is fixed at 1000 bytes and length overflow forces abort. Release always force-aborts the channel, which is correct for cleanup but visible to host software.

## Test Signals
Exercise full KCS request/response, invalid command aborts, host abort handshake, userspace read too-small buffer, write before read returning `-EINVAL`, ioctl SMS_ATN set/clear, force abort, and concurrent open returning busy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_cdev_ipmi.c -->
