<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpib_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gpib_ioctl.h

## Purpose
`gpib_ioctl.h` defines the ioctl command ABI for Linux GPIB character devices. It describes the data structures used to configure boards, open logical devices, transfer data and command bytes, wait for status, serial/parallel poll, control bus lines, and select hardware.

## Important APIs, types, and functions
The ioctl namespace is `GPIB_CODE`. Important structures include `gpib_read_write_ioctl`, `gpib_open_dev_ioctl`, `gpib_close_dev_ioctl`, `gpib_serial_poll_ioctl`, `gpib_eos_ioctl`, `gpib_wait_ioctl`, `gpib_online_ioctl`, `gpib_spoll_bytes_ioctl`, `gpib_board_info_ioctl`, `gpib_select_pci_ioctl`, `gpib_ppoll_config_ioctl`, `gpib_pad_ioctl`, `gpib_sad_ioctl`, `gpib_select_device_path_ioctl`, and `gpib_request_service2`. `enum gpib_ioctl` names commands such as `IBRD`, `IBWRT`, `IBCMD`, `IBOPENDEV`, `IBWAIT`, `IBSIC`, `IBSRE`, `IBLINES`, `IBPAD`, `IBSAD`, `IBTMO`, `IBRSP`, `IBEOS`, `IBPPC`, `IBBOARD_INFO`, `IBSELECT_PCI`, `IBEVENT`, `IBAUTOSPOLL`, `IBONL`, and `IBRSV2`.

## Control flow
User space opens the board device, optionally selects hardware, opens a board or addressed device handle, configures addresses, EOS, timeout, controller state, autopolling, or online state, then uses read/write/command ioctls. `IBWAIT` blocks until status masks are satisfied or timeout expires.

## State and persistence behavior
Handles identify open board/device contexts. Board configuration such as PAD/SAD, EOS, timeout, controller mode, autopolling, request service reason, and selected PCI/sysfs device path persists in the driver until reset, close, or explicit ioctl changes.

## Dependencies and integration points
It depends on `<asm/ioctl.h>` and `<linux/types.h>`, and relies on status and mode definitions from `gpib.h`. It integrates with GPIB controller hardware, sysfs device identification, and userspace GPIB libraries.

## Risks and test signals
Risks include unsafe user pointers, 32/64-bit layout mismatches, partial transfer accounting errors, stale handles, bitfield ABI portability in board-info and ppoll config structs, and long blocking waits. Test signals include compat ioctl tests, transfer-count verification, invalid-handle rejection, timeout behavior, PCI/path selection, service-request updates, and board-info round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpib_ioctl.h -->
