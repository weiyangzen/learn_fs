# sources/distributed-fs/coda/coda-src/venus/nt_util.h

## Purpose
This header declares Cygwin/Windows-only pseudo-mount and kernel IPC support for Venus. On non-Cygwin builds it contributes no declarations.

## Important APIs, Types, and Functions
It defines pseudo filesystem control codes `OW_FSCTL_MOUNT_PSEUDO` and `OW_FSCTL_DISMOUNT_PSEUDO`, the `OW_PSEUDO_MOUNT_INFO` structure passed to the Windows filesystem device, and Coda-specific control codes `CODA_FSCTL_ANSWER`, `CODA_FSCTL_FETCH`, and `CODA_FSCTL_PIOCTL`. It declares `nt_mount`, `nt_umount`, `nt_initialize_ipc`, `nt_msg_write`, and `nt_stop_ipc`.

## Control Flow
The header has no runtime flow, but it defines the contract implemented by `nt_util.cc`: mount/dismount are drive-name calls, IPC initialization accepts a socket descriptor, message writes return byte counts on success, and shutdown stops the kernel monitor.

## State and Persistence Behavior
No state is declared here. Implementations use these declarations to mutate Windows kernel-device state and pseudo-drive mount state.

## Dependencies and Integration Points
It depends on Windows headers and `winioctl.h` for `CTL_CODE`. It integrates with Venus startup/shutdown only under the Cygwin build path.

## Risks and Test Signals
The header itself calls out mismatched/broken FSCTL definitions that must match the NT filesystem driver. Build tests should verify Cygwin-only inclusion, and integration tests should confirm the FSCTL numbers still match the installed Coda driver.
