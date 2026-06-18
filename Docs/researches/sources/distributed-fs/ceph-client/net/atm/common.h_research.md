# sources/distributed-fs/ceph-client/net/atm/common.h

## Purpose
`common.h` is the internal coordination header for the ATM socket core. It declares shared VCC socket operations used by both PVC and SVC protocol families, initialization/teardown hooks for ATM subcomponents, and the conditional procfs interface.

## Important APIs and Types
- Declares common socket lifecycle and data-plane functions: `vcc_create`, `vcc_release`, `vcc_connect`, `vcc_recvmsg`, `vcc_sendmsg`, `vcc_poll`, `vcc_ioctl`, `vcc_compat_ioctl`, `vcc_setsockopt`, `vcc_getsockopt`, and `vcc_process_recv_queue`.
- Declares protocol-family init/exit hooks: `atmpvc_init`, `atmpvc_exit`, `atmsvc_init`, `atmsvc_exit`, `atm_sysfs_init`, and `atm_sysfs_exit`.
- Declares procfs hooks behind `CONFIG_PROC_FS`; otherwise inline no-op versions let callers compile without procfs.
- Declares SVC-specific `svc_change_qos` and device cleanup helper `atm_dev_release_vccs`.

## Control Flow and Integration
PVC (`pvc.c`) and SVC (`svc.c`) install `proto_ops` that delegate most common behavior to the `vcc_*` functions declared here. `ioctl.c` supplies the common VCC ioctl handlers, `raw.c` supplies AAL protocol handlers consumed by `vcc_connect`, and `resources.c`/`proc.c` expose device and inspection hooks referenced by this header.

## State and Persistence
The header owns no storage. It defines access to persistent in-kernel ATM state: sockets/VCCs, registered devices, sysfs/procfs entries, and SVC signaling state. Compile-time state is represented by conditional inline no-ops for procfs.

## Dependencies
Depends on Linux socket and poll definitions (`linux/net.h`, `linux/poll.h`) and the ATM types made visible by including users. It is a private `net/atm` header, not a UAPI contract.

## Risks and Test Signals
Risks concentrate in ABI expectations: changes to prototypes ripple through PVC, SVC, raw AAL, ioctl, resource, sysfs, and procfs code. Test signals include successful builds with and without `CONFIG_PROC_FS`/`CONFIG_COMPAT`, PVC/SVC socket creation, common send/recv behavior, and module init/exit paths that call every declared initializer and cleanup function.
