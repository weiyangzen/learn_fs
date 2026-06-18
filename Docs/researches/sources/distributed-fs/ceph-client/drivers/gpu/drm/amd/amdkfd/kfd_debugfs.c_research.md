<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debugfs.c

## Purpose

`kfd_debugfs.c` creates KFD debugfs diagnostics and fault-injection entries. It exposes root files for MQD/HQD/RL inspection, HWS hang triggering, and memory-limit diagnostics, and creates per-process debugfs directories with PASID files per GPU.

## Important APIs, Types, and Entry Points

- `kfd_debugfs_init()` creates the `kfd` root, `proc` subdirectory, initializes the process-entry list, and registers root files.
- `kfd_debugfs_fini()` removes debugfs directories recursively.
- `kfd_debugfs_add_process()` creates `proc/<pid>/pasid_<gpu_id>` entries for each PDD.
- `kfd_debugfs_remove_process()` removes and frees a process entry by PID.
- `kfd_debugfs_hang_hws_write()` parses a GPU ID and calls `kfd_debugfs_hang_hws()`.
- `kfd_debugfs_pasid_read()` returns the PDD PASID as text.

## Control Flow

Root debugfs files use `single_open()` with show callbacks stored in `inode->i_private`. `hang_hws` accepts a short decimal GPU ID, validates/copies/parses it, looks up the KFD device, and invokes the HWS hang helper. Process add allocates a list entry, creates a PID-named directory, then creates one PASID file per PDD. Removal searches the process list under `kfd_processes_mutex`, removes the directory recursively, unlinks, and frees the entry.

## State and Persistence Behavior

Global state is `debugfs_root`, `debugfs_proc`, and the `procs` list. Each `debugfs_proc_entry` persists a PID and process dentry until removal. PASID files store raw `struct kfd_process_device *` in `i_private`, so debugfs teardown must precede PDD lifetime end.

## Dependencies and Integration Points

The file depends on Linux debugfs, seq_file, user-copy helpers, KFD process/device state, KFD device lookup, and external KFD debugfs show/fault helpers such as MQD/HQD/RL dumpers, memory-limit display, and HWS hang injection.

## Risks and Edge Cases

- Add modifies `procs` without taking `kfd_processes_mutex`, while remove iterates under it; caller-side serialization must be correct.
- PASID files can dereference stale PDD pointers if process debugfs removal races teardown.
- `hang_hws` is intentional fault injection and should remain debugfs-only.
- PID reuse after missed removal can confuse process debugfs directories.

## Test and Validation Signals

Test init/fini idempotence, add/remove for multi-GPU processes, PASID read format, invalid and valid `hang_hws` writes, and concurrent read/remove teardown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debugfs.c -->
