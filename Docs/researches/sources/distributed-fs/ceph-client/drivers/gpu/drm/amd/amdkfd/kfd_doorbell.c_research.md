# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_doorbell.c

`kfd_doorbell.c` manages KFD doorbell apertures, the MMIO-like targets used by user and kernel queues to notify hardware of queue write-pointer updates. It handles the device-wide kernel doorbell page, per-process doorbell BOs, mmap of process slices, and reservation bitmaps.

Key APIs are `kfd_doorbell_process_slice`, `kfd_doorbell_init`, `kfd_doorbell_fini`, `kfd_doorbell_mmap`, `kfd_get_kernel_doorbell`, `kfd_release_kernel_doorbell`, `write_kernel_doorbell`, `write_kernel_doorbell64`, `kfd_alloc_process_doorbells`, `kfd_get_process_doorbells`, and `kfd_free_process_doorbells`. `init_doorbell_bitmap` masks SOC15 non-CP and mirrored doorbell ranges so queues do not collide with SDMA/IH/VCN reservations.

Device init creates the kernel page and bitmap. Per-process doorbells are allocated lazily on first access and exposed through `/dev/kfd` mmap only when the VMA size matches the process slice. Queue creation later allocates IDs from the QPD bitmap and converts them to BAR offsets through amdgpu helpers. State persists in `kfd->doorbell_bitmap`, `kfd->doorbells`, `kfd->doorbell_kernel_ptr`, `qpd->doorbell_bitmap`, and `qpd->proc_doorbells`.

Dependencies include amdgpu doorbell BO allocation, GEM doorbell domain, process device data, mmap routing, DQM doorbell assignment, and MES slice sizing. Risks are bitmap off-by-one errors, kernel doorbell leaks, wrong 32/64-bit alignment, mmap size errors, process BO lifetime bugs, and reserved range collisions. Test per-process mmap, max queues, MES/non-MES slices, SOC15 reserved ranges, kernel queue ring tests, 64-bit writes, and cleanup with active queues.
