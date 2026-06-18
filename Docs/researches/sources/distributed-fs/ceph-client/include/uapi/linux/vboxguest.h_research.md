# sources/distributed-fs/ceph-client/include/uapi/linux/vboxguest.h

## Purpose
Defines the Linux VBoxGuest character-device ioctl ABI. Userspace uses it to negotiate driver version, submit VMMDev requests, connect and call HGCM services, log messages, wait for guest events, change event filters and capabilities, handle memory ballooning, and request core dumps.

## Important APIs, Types, And Constants
`struct vbg_ioctl_hdr` is the common 24-byte header with input/output sizes, version, request type, VBox status code, output size, and reserved field. `VBG_IOC_VERSION` identifies the ioctl interface version. `struct vbg_ioctl_driver_version_info` negotiates session and driver versions. VMMDev request ioctls include a size-parameterized small request and `VBG_IOCTL_VMMDEV_REQUEST_BIG` for larger requests. HGCM structs cover connect, disconnect, and variable-length calls with client id, function, timeout, interruptible flag, and parameter count; 32/64-bit ioctl selectors follow pointer width. Other structs cover logging, event waits, filter changes, guest capability acquisition/change, balloon checks, and core dump requests.

## Control Flow, State, And Persistence
Typical userspace flow opens the VBoxGuest node, negotiates version, optionally connects to an HGCM service, issues calls or waits for events, updates filters/capabilities, and closes the session. Driver/session state includes negotiated interface version, HGCM client IDs, event wait cancellation state, per-session/global capability masks, and memory balloon requests. Some operations are handled entirely by the guest driver; VMMDev and HGCM requests cross to the host.

## Dependencies And Integration Points
Depends on `<asm/bitsperlong.h>`, `<linux/ioctl.h>`, `vbox_err.h`, and `vbox_vmmdev_types.h`. It integrates with `/dev/vboxguest` or related nodes, VirtualBox host services, guest additions daemons, vboxsf, display integration, and memory ballooning helpers.

## Risks And Test Signals
Risks include trusting user-supplied sizes, 32/64-bit HGCM parameter mismatch, incorrect `size_in`/`size_out` handling, stale session version fallback, blocked event waits after interruption, and host-returned VBox status being confused with ioctl `errno`. Tests should cover version negotiation, ioctl size validation, HGCM scalar/buffer calls on 32- and 64-bit userspace, wait cancellation, capability masks, balloon check handling, and status-code propagation.
