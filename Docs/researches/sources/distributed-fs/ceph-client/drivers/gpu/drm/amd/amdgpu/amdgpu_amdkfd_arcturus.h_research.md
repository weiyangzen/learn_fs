# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.h

Purpose: this header declares the Arcturus SDMA HQD operations that are shared outside `amdgpu_amdkfd_arcturus.c`, most notably by the Aldebaran KFD/KGD callback table.

Important APIs: `kgd_arcturus_hqd_sdma_load` loads an SDMA MQD and optionally seeds the write pointer from userspace memory. `kgd_arcturus_hqd_sdma_dump` returns an allocated register/value array for one SDMA engine queue. `kgd_arcturus_hqd_sdma_is_occupied` reports whether the MQD's SDMA RLC queue is enabled in hardware. `kgd_arcturus_hqd_sdma_destroy` disables an SDMA queue, waits for idle, clears doorbell state, and saves the read pointer.

Control flow and integration: the declarations are consumed by `amdgpu_amdkfd_aldebaran.c` and by Arcturus's own callback table. They match the SDMA slots in `struct kfd2kgd_calls`, allowing KFD queue-management code to call through the table without knowing the ASIC-specific register layout.

State and persistence: no state is stored in the header. The declared functions mutate SDMA RLC registers and MQD read-pointer fields in their implementation.

Dependencies: the file assumes `struct amdgpu_device`, `struct mm_struct`, `bool`, `uint32_t`, and `__user` annotations are already visible through the including source. It is a private driver header, not a user ABI.

Risks and test signals: signature mismatches surface as compile failures in Aldebaran/Arcturus builds. Because no include guard is present in the shown file, keeping the header limited to declarations avoids duplicate-definition issues. Tests should cover both direct Arcturus callback-table use and Aldebaran reuse.
