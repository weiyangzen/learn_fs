# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_flat_memory.c

`kfd_flat_memory.c` defines per-process GPU virtual address apertures for flat shader memory, LDS, scratch, GPUVM/SVM, CWSR trap memory, and kernel IB reservations. It supplies the address layout consumed by SH_MEM programming in the DQM ASIC files.

The public entry point is `kfd_init_apertures`. Helpers `kfd_init_apertures_vi`, `kfd_init_apertures_v9`, and `kfd_init_apertures_v12` fill generation-specific aperture fields. Macros define GPUVM, scratch, LDS, SVM user, CWSR, and IB base/limit values.

`kfd_init_apertures` enumerates topology KFD devices, skips devices denied by cgroups, creates `kfd_process_device` records, and fills each PDD. For 32-bit processes all aperture fields are zero because apertures are unsupported. VI-style devices use fixed high LDS/scratch regions, reserve low SVM space for CWSR/IB, and set GPUVM from `SVM_USER_BASE` to device GPUVM size. GFX9 uses 48-bit LDS/scratch aperture bases and moves CWSR to `AMDGPU_VA_RESERVED_TRAP_START`. GFX12+ uses GMC shared/private apertures and the same trap-side placement strategy.

Dependencies include topology enumeration, process-device creation, device cgroup checks, amdgpu VM reserved address helpers, GMC aperture fields, and KFD CWSR constants. DQM consumes `lds_base`, `scratch_base`, `gpuvm_base`, and QPD CWSR/IB bases. Risks are overlapping address ranges, canonical/noncanonical mistakes, SH_MEM extraction mismatches, 32-bit behavior, and GFX12 aperture changes. Test process creation across devices, cgroup-denied devices, 32-bit processes, VI/GFX9/GFX12 aperture values, SVM boundaries, CWSR placement, and flat-memory workloads.
