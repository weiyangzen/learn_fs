## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reg_access.h

Purpose: declares the register-access abstraction used by AMDGPU IP blocks. It defines callback types, per-register-space state containers, the aggregate `struct amdgpu_reg_access`, and public helper prototypes for direct, block, PCIe, extended, SMN, indirect, XCC, and wait-on-register access.

Important APIs and types: callback typedefs cover 32-bit register operations, extended 64-bit-address register operations, 64-bit data operations, block-qualified register operations, and SMN base resolution. `struct amdgpu_reg_ind`, `amdgpu_reg_ind_blk`, and `amdgpu_reg_pcie_ind` pair spinlocks with dispatch functions for each register namespace. `struct amdgpu_reg_smn_ext` stores an optional SMN base callback. `struct amdgpu_reg_access` groups SMC, UVD context, DIDT, GC/SE CAC, audio endpoint, PCIe, and SMN helpers under `adev->reg`.

Control flow: the header does not implement logic, but it defines the contracts used by `amdgpu_reg_access.c`: initialization must set locks and callback pointers, IP-specific setup code installs callbacks, and callers access hardware through wrapper functions rather than calling function pointers directly.

State and persistence: all structures are runtime-only members of `struct amdgpu_device`; spinlocks protect shared indirect windows and function-pointer-backed register spaces. No persistent storage is represented.

Dependencies and integration points: depends on Linux types/spinlocks and AMD HW IP block enums from `amdgpu_ip.h`. It is included by low-level register access code and transitively by common AMDGPU headers/macros. The prototypes integrate with NBIO, SMU/SMC, audio endpoint, SR-IOV, RLCG, and XCC code paths.

Risks: callback signatures must match the hardware block semantics exactly; register offsets are a mix of dword and byte units depending on helper family, so callers can easily pass the wrong unit. Missing callback initialization results in zero-returning read wrappers or ignored writes.

Test signals: compile coverage catches signature drift. Runtime validation should include unsupported callback cases, all registered callback families on supported ASICs, and lockdep around indirect register access.
