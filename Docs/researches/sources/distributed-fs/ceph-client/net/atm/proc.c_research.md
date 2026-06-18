# sources/distributed-fs/ceph-client/net/atm/proc.c

## Purpose
`proc.c` provides the ATM procfs inspection interface under `/proc/net/atm`. It lists ATM devices, PVCs, SVCs, all VCCs, and optional per-device driver proc data.

## Important APIs, Types, and Functions
- `atm_proc_init` / `atm_proc_exit`: create and remove the `/proc/net/atm` subtree and seq files.
- `atm_proc_dev_register` / `atm_proc_dev_deregister`: exported-style helpers used by `resources.c` to create per-device entries named `<type>:<number>`.
- Device seq operations use `atm_dev_seq_start`, `atm_dev_seq_next`, and `atm_dev_seq_stop` from `resources.c`.
- VCC seq traversal uses `struct vcc_state`, `vcc_seq_start`, `vcc_seq_next`, `vcc_seq_stop`, and `__vcc_walk` over `vcc_hash` under `vcc_sklist_lock`.
- Formatters `atm_dev_info`, `pvc_info`, `vcc_info`, and `svc_info` render state into seq files.

## Control Flow
Initialization creates `devices`, `pvc`, `svc`, and `vc` seq files. Device listing traverses the global `atm_devs` list under `atm_dev_mutex`. VCC listings traverse the global VCC hash table with a family filter stored as proc private data. Per-device proc entries call a driver-provided `dev->ops->proc_read`, copy one page to userspace, and advance the file position.

## State and Persistence
The proc root pointer `atm_proc_root` persists while procfs support is active. Per-device proc state is stored in `dev->proc_name` and `dev->proc_entry`. The file exposes live state only; it does not persist configuration.

## Dependencies and Integration
Depends on `resources.h` for device traversal, `common.h` for init prototypes, `signaling.h` to display SVC state involving `sigd`, Linux seq_file/proc APIs, and ATM socket/device internals.

## Risks and Test Signals
Risks include stale pointer exposure (mitigated by `%pK`), lock ordering during VCC traversal, per-device proc read length validation, and proc entry cleanup on device deregistration. Test signals are `/proc/net/atm/devices`, `pvc`, `svc`, and `vc` output under live sockets/devices, builds without `CONFIG_PROC_FS`, device register/deregister cleanup, and access checks for kernel pointer formatting.
