## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.h

Purpose: defines RLC firmware identifiers, table-of-content layouts, RLC function callbacks, RLCG register-access control registers, the `struct amdgpu_rlc` runtime state, and the public RLC helper prototypes.

Important APIs and types: `FIRMWARE_ID`, `SOC21_FIRMWARE_ID`, and `SOC24_FIRMWARE_ID` enumerate firmware table IDs for RLC, SDMA, CP, MES, RS64, debug, SR-IOV, and related images. `RLC_TABLE_OF_CONTENT` and V2 define bitfield layouts for RLC autoload/TOC entries. `struct amdgpu_rlc_funcs` supplies ASIC-specific safe-mode, init/resume/stop/reset/start, clear-state, CP table, SPM VMID update, and RLCG access-range hooks. `struct amdgpu_rlcg_reg_access_ctrl` stores scratch and VFI registers for indirect RLCG access. `struct amdgpu_rlc` stores BOs, firmware metadata, safe-mode flags, autoload/TOC buffers, and RLCG support data.

Control flow: the header defines callback and state contracts consumed by GFX IP code and `amdgpu_rlc.c`. Generic helpers allocate and populate buffers using sizes and hooks stored here; ASIC-specific code fills `funcs`, register lists, CP table sizes, and register-access controls.

State and persistence: all fields are runtime driver state or pointers to firmware blobs/BO mappings. Hardware-visible persistence is via GPU BOs for save/restore, clear-state, CP table, autoload, and TOC content.

Dependencies and integration points: includes `clearstate_defs.h` and references `struct amdgpu_device` and `struct amdgpu_ring`. It integrates with GFX firmware loading, RLC autoload, SR-IOV RLCG register access, power gating, and CP setup.

Risks: bitfield TOC layouts are ABI-sensitive with firmware; changing packing or enum IDs can break firmware loading. `AMDGPU_MAX_RLC_INSTANCES` bounds per-XCC safe-mode and register-control arrays; callers must validate instance IDs. Firmware pointer fields reference loaded firmware memory and require lifetime coordination.

Test signals: firmware TOC parsing for SOC21/SOC24, safe-mode across multiple RLC instances, RLCG register access on SR-IOV devices, and GFX init/resume/reset flows using each `amdgpu_rlc_funcs` callback.
