# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/cmd.c

Purpose: implements the mlx5 VFIO PCI vendor command layer for migration and dirty-page logging. It wraps mlx5 firmware commands for VHCA suspend/resume, migration-state query/save/load, protection-domain and mkey-backed DMA buffers, and the page-tracker object used by VFIO log ops.

Important APIs and functions: `mlx5vf_cmd_suspend_vhca()`, `mlx5vf_cmd_resume_vhca()`, `mlx5vf_cmd_query_vhca_migration_state()`, `mlx5vf_cmd_save_vhca_state()`, `mlx5vf_cmd_load_vhca_state()`, `mlx5vf_cmd_set_migratable()`, `mlx5vf_start_page_tracker()`, `mlx5vf_stop_page_tracker()`, and `mlx5vf_tracker_read_and_clear()`. Buffer helpers allocate pages, DMA map them with IOVA when possible, create mlx5 mkeys, and cache buffers on migration-file lists.

Control flow: initialization checks that the PCI function is a VF, obtains the mlx5 core device, validates migration capabilities, resolves VF id and VHCA id, registers an SR-IOV notifier, and installs migration/log callbacks. Save commands are asynchronous: they acquire `save_comp`, submit `SAVE_VHCA_STATE`, then the callback appends a migration header and data buffer to the readable stream or queues cleanup work on errors. Dirty logging builds a CQ plus host/FW RC QPs, creates a PAGE_TRACK object over VFIO IOVA ranges, modifies it to REPORTING on read-and-clear, drains CQEs into an `iova_bitmap`, and reposts receive WQEs.

State and persistence: state is in memory only in `mlx5vf_pci_core_device`, `mlx5_vf_migration_file`, buffer lists, completions, and tracker resources. Firmware state is serialized through the migration stream, where records use `mlx5_vf_migration_header` with mandatory FW data and optional stop-copy-size tags. Resources are freed on close, detach, stop logging, or reset.

Dependencies and integration: depends on mlx5 core command layouts, SR-IOV notifications, DMA/IOMMU APIs, VFIO migration/log ops, completion workqueues, and `iova_bitmap`. It integrates with `main.c` state transitions and exposes capability-dependent pre-copy, stop-copy, P2P, chunk-mode, and logging behavior.

Risks: concurrency is subtle around `state_mutex`, `save_comp`, async callbacks, and reset/detach paths. DMA mapping and mkey cleanup must stay balanced. Page-tracker error events, CQ poll errors, and firmware state errors must propagate to VFIO callers or migration can silently lose dirty pages. Chunk mode also relies on preserving buffer/header ownership across reads.

Test signals: exercise capability gating on supported and unsupported VFs, save/load migration streams including pre-copy cleanup and optional tags, async save failure paths, detach notifications, reset while migration/logging is active, dirty log start/read/stop, combined IOVA range fallback, and DMA mapping failure injection.
