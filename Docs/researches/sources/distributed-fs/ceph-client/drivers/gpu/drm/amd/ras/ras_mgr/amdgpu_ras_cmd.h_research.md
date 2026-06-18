# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_cmd.h

## Purpose

`amdgpu_ras_cmd.h` declares the AMDGPU-specific extension command namespace and request/response structures for translating a memory file descriptor into a GPU memory range.

## Important APIs, Types, And Functions

It defines `enum amdgpu_ras_cmd_id` from `RAS_CMD_ID_AMDGPU_START`, currently including `RAS_CMD__TRANSLATE_MEMORY_FD`, and structures `ras_cmd_translate_memory_fd_req` and `ras_cmd_translate_memory_fd_rsp`. Public functions are `amdgpu_ras_handle_cmd()` and `amdgpu_ras_submit_cmd()`.

## Control Flow, State, And Persistence

The header has no runtime control flow. Its packed command structures are ABI-like data exchanged through `ras_cmd_ctx`; command execution state is stored in that context and in rascore/manager state.

## Dependencies And Integration Points

It includes `ras.h` and depends on the generic command ID ranges, device handles, and command context from `ras_cmd.h`. It integrates with manager command submission, VF forwarding, and possible userspace or firmware-facing RAS command interfaces.

## Risks And Test Signals

Risks are command ID collisions, request/response layout drift, and ABI alignment changes. Test signals include compile coverage, command size validation, userspace ABI tests for any memory-fd translation implementation, and unknown-command fallback behavior.
