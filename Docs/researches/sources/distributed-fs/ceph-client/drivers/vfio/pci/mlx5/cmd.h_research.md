# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/cmd.h

Purpose: declares the shared mlx5 VFIO migration data model and command APIs used by `cmd.c` and `main.c`.

Important APIs and types: defines migration file states (`MLX5_MIGF_STATE_*`), resume stream parser states, migration record tags and flags, `mlx5_vf_migration_header`, `mlx5_vhca_data_buffer`, async save state, stop-copy work state, `mlx5_vf_migration_file`, CQ/QP/page-tracker structs, and the top-level `mlx5vf_pci_core_device`. It also declares VFIO command, migration-file, buffer, and page-tracker helpers.

Control flow and state: this header encodes the lifecycle shared across the driver: migration files own anonymous FDs, stream positions, record sizes, per-chunk buffers, poll wait queues, async command context, and buffer reuse lists. The device object embeds the VFIO core device, capability flags, current VFIO migration state, active save/restore files, reset coordination, tracker state, workqueue, notifier, and mlx5 core handle.

Dependencies and integration: includes VFIO PCI core, mlx5 driver, vport, CQ, and QP headers. Its prototypes are the internal contract between `main.c` state-machine/file operations and `cmd.c` firmware operations.

Risks: bitfield state flags and arrayed chunk buffers are shared across async and synchronous paths, so any API misuse can produce leaks or stale stream state. Locking assumptions are implicit in callers; several helpers require `state_mutex`.

Test signals: compile coverage across mlx5 capability options, lockdep paths for functions requiring `state_mutex`, chunk and non-chunk migration, and page-tracker start/stop/read cycles.
