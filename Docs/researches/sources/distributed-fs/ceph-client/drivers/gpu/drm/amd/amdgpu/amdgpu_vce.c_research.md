# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vce.c

## Purpose

`amdgpu_vce.c` implements legacy VCE video encode support. It loads chip-specific firmware, allocates the firmware/VCPU BO, tracks encode sessions per DRM file, validates and patches VCE command streams, submits kernel-generated create/destroy messages, emits VCE ring commands, handles idle power gating, and runs ring/IB tests.

## Important APIs And Functions

`amdgpu_vce_firmware_name()` maps ASICs to firmware filenames. `amdgpu_vce_early_init()` requests firmware and decodes version fields. `amdgpu_vce_sw_init()` allocates the VCPU BO, initializes handle ownership arrays, delayed idle work, and idle mutex. `amdgpu_vce_sw_fini()` tears down scheduler entity, rings, firmware, mutex, and BO. `amdgpu_vce_suspend()` refuses suspend when active handles exist because running encode sessions cannot be preserved; `amdgpu_vce_resume()` zeros and reloads firmware into the BO.

Handle and cleanup helpers include `amdgpu_vce_validate_handle()` and `amdgpu_vce_free_handles()`. The kernel message helpers `amdgpu_vce_get_create_msg()` and `amdgpu_vce_get_destroy_msg()` build direct or delayed IBs with session, task, feedback, initialize, or destroy commands.

The parser has two modes. `amdgpu_vce_ring_parse_cs()` validates command lengths, checks and constrains referenced BO placement with `amdgpu_vce_validate_bo()`, then relocates addresses with `amdgpu_vce_cs_reloc()`, enforces session-first ordering, create-before-use for new handles, destroy semantics, and ASIC-specific command acceptance. `amdgpu_vce_ring_parse_cs_vm()` performs the lighter VM-mode handle/session validation without reloc patching.

Ring helpers emit IB and fence packets (`amdgpu_vce_ring_emit_ib`, `amdgpu_vce_ring_emit_fence`), test ring pointer movement, test IB execution through create/destroy messages, and map encode rings to scheduler priorities.

## Dependencies And Integration

The file integrates with firmware loading, AMDGPU BO/TTM placement, CS parser and IB helpers, DRM scheduler entity, dma-fence, ring submission, DPM/powergating, SR-IOV skip behavior, and common command definitions from `amdgpu_vce.h`/`cikd.h`. File-close cleanup is necessary because hardware sessions outlive individual submissions unless explicitly destroyed.

## State, Risks, And Tests

Device state lives in `adev->vce`: firmware, VCPU BO, atomic handle array, owner file array, image size per session, delayed idle work, ring array, scheduler entity, harvest config, and keyselect. Risks include command length under-validation before reading `idx + n`, handle leaks or collisions across files, freeing allocated handles on parser error but not clearing owner/image metadata, BO relocation crossing 4 GB boundaries, suspend failure with active sessions, and idle power gating while fences are still pending.

Test signals include firmware lookup and missing-firmware fallback, parser rejection of bad command lengths/order/opcodes, create/destroy state transitions, VM parser behavior, cross-file handle collision, BO too-small and boundary cases, cleanup on file close, ring emit packet shape, SR-IOV ring-test skip, idle begin/end behavior, and active-session suspend rejection.
