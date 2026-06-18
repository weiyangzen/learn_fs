# sources/distributed-fs/ceph-client/sound/usb/fcp.c

## Purpose
Implements a Focusrite Control Protocol kernel shim for supported Focusrite USB audio interfaces. It exposes a privileged hwdep device for user-space protocol drivers, maintains a vendor notification URB, executes FCP USB command/response transactions, and provides one kernel ALSA control for frequent level-meter polling.

## Important APIs, Types, and Functions
`snd_fcp_init()` is the public initializer called from mixer setup. `struct fcp_data` stores mixer backpointer, protocol mutex, command completion, active hwdep file pointer, notify waitqueue/spinlock, vendor interface/endpoint coordinates, init opcodes/response sizes, sequence number, and meter-control buffers. `fcp_usb()` sends request packets with opcode/size/seq, waits for ACK from the notification URB, reads the response, and validates sequence/opcode/error/size. hwdep operations implement `FCP_IOCTL_PVERSION`, `FCP_IOCTL_INIT`, `FCP_IOCTL_CMD`, `FCP_IOCTL_SET_METER_MAP`, `FCP_IOCTL_SET_METER_LABELS`, read, poll, open, and release. Meter control callbacks provide integer level values and optional FCP TLV labels.

## Control Flow
Initialization allocates private state, finds the vendor-specific Focusrite control interface, and creates an exclusive hwdep device. User space opens hwdep with `CAP_SYS_RAWIO`, sends init parameters, and `fcp_init()` performs step0, starts the interrupt notification URB, resets sequence, sends two init opcodes, and returns init responses. Later `FCP_IOCTL_CMD` copies bounded user data, rejects dangerous flash erase/write requests against App_Gold segment 0, executes `fcp_usb()`, and copies the response back. Notification URB completion completes command ACKs and queues non-ACK event bits for `read()`/`poll()`, then resubmits while the device is alive. Meter reads reinitialize after suspend if needed, send `FCP_USB_GET_METER`, and remap device slots to ALSA channels.

## State and Persistence
All state is in `fcp_data` and `mixer->urb`. Sequence numbers increment per request. Meter map/labels persist only while the mixer instance exists. Suspend frees the notification URB; `fcp_reinit()` restores protocol state lazily. Device firmware state can be changed by user commands, except guarded App_Gold flash operations.

## Dependencies and Integration
Depends on ALSA hwdep/control/TLV APIs, USB mixer internals, `snd_usb_ctl_msg()`, UAPI `sound/fcp.h`, and Focusrite vendor descriptors. The private free/suspend hooks attach to `usb_mixer_interface`, while controls are registered through USB mixer helpers with `USB_MIXER_BESPOKEN`.

## Risks and Test Signals
Risks include protocol deadlock if ACKs are lost, reinit races around suspend, user-space ABI mistakes, label TLV access before meter control setup, notification URB resubmit failures, and insufficient command validation for destructive vendor commands. Test signals include hwdep open permission checks, init/cmd/read/poll behavior with fcp-server, meter map bounds, label TLV add/remove notifications, suspend/resume reinit, disconnect during blocked read or command, and malformed response sizes.
