# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/main.c

Purpose: implements the VFIO device operations and migration-file userspace ABI for mlx5 VFs. It converts VFIO migration state transitions into mlx5 firmware suspend/resume/save/load commands and exposes anonymous read/write FDs for migration data.

Important APIs and functions: save-side file ops (`mlx5vf_save_read()`, `mlx5vf_save_poll()`, `mlx5vf_precopy_ioctl()`), restore-side write parser (`mlx5vf_resume_write()` and helpers), migration transitions (`mlx5vf_pci_step_device_state_locked()` and `mlx5vf_pci_set_device_state()`), reset cleanup (`mlx5vf_state_mutex_unlock()`, AER reset handler), and VFIO ops/probe/remove glue.

Control flow: save setup allocates a migration file, PD, buffers, optional stop-copy chunk buffers, optional pre-copy tracking, and submits an initial save. Reads are stream based and consume queued header/data buffers; in pre-copy, temporary lack of data returns `-ENOMSG`, while final completion acts as EOF. Pre-copy ioctl reports initial/dirty bytes and can trigger new incremental saves. Restore writes parse headers, optional tag data, and FW image records, reallocating buffers as needed before invoking `LOAD_VHCA_STATE`.

State and persistence: no persistent disk state. Migration state lives in `mvdev->mig_state`, active `saving_migf`/`resuming_migf`, stream offsets, buffer lists, and firmware image records. `deferred_reset` ensures reset cleanup occurs after lock-sensitive paths complete.

Dependencies and integration: relies on `cmd.c` for mlx5 firmware commands and buffer cleanup, VFIO core for state arcs and common PCI ops, anon inodes for migration FDs, and pci driver override matching for Mellanox VF devices.

Risks: stream-position expectations are strict; out-of-order reads put the file into error. Reset and close paths must cancel async work and cleanup resources without deadlocking with VFIO/mm locks. Resume parser validates record size against `MAX_LOAD_SIZE` but optional unknown mandatory tags fail migration.

Test signals: migration arc tests for RUNNING/P2P/PRE_COPY/STOP_COPY/RESUMING, blocking and nonblocking reads, pre-copy `VFIO_DEVICE_FEATURE_MIG_PRECOPY_INFO`, optional stop-copy-size tag handling, reset during active migration, FD close while async save is inflight, and malformed restore streams.
