# sources/distributed-fs/coda/coda-src/venus/nt_util.cc

## Purpose
This Cygwin-only file implements Windows/NT support routines for Venus pseudo-mount management and kernel-to-Venus IPC. When `__CYGWIN32__` is not defined, it compiles to no runtime behavior.

## Important APIs, Types, and Functions
`nt_mount()` and `nt_umount()` wrap `nt_do_mounts()` to mount or dismount a pseudo volume using Windows device-control calls. `nt_initialize_ipc()` opens the Coda kernel device, starts the `listen_kernel` thread, and records the socket used to pass kernel messages into the normal Venus path. `nt_msg_write()` sends responses back to the kernel through `CODA_FSCTL_ANSWER`. `nt_stop_ipc()` terminates and closes the monitor thread. The local `wcslen()` and static `DEV_BROADCAST_VOLUME` support pseudo-device link creation and broadcast device-change notifications.

## Control Flow
Mounting first dismounts any existing drive mapping, creates a DOS device alias for `\\Device\\codadev`, opens `\\\\.\\codadev`, fills `OW_PSEUDO_MOUNT_INFO`, and issues either mount or dismount FSCTLs. A successful mount/dismount broadcasts a Windows `WM_DEVICECHANGE` message. IPC initialization opens or attempts to start the Coda service, then launches `listen_kernel`, which repeatedly issues `CODA_FSCTL_FETCH`, writes message length and payload to the Venus socket, and exits only when `doexit` is set or the thread is terminated.

## State and Persistence Behavior
State is transient and process-local: static `drive`, `mount`, `sockfd`, `doexit`, `kerndev`, and `kernelmon`. The only persistent external effects are Windows device namespace changes, service startup attempts, and kernel-driver mount state. Fatal mount/setup failures kill Venus because the kernel bridge is required for this platform path.

## Dependencies and Integration Points
It depends on Windows APIs (`DefineDosDevice`, `CreateFile`, `DeviceIoControl`, `CreateThread`, `BroadcastSystemMessage`), OSR pseudo-mount control structures from `nt_util.h`, Coda kernel message sizes, and Venus logging/error helpers. It integrates with `venus.cc` shutdown through `nt_stop_ipc()`.

## Risks and Test Signals
Risks include hard-coded device names, static argument passing to a thread, unsafe `TerminateThread`, incomplete cleanup of DOS device aliases, and FSCTL constants noted as broken in the header. Tests should run mount/unmount cycles, device-change observation, kernel fetch/answer loops, missing service startup, and failure paths where `CreateFile` or FSCTL calls fail.
