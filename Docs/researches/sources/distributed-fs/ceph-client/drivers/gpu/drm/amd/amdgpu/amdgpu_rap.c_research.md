
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rap.c

## Purpose
Adds a debugfs test interface for RAP TA L0 policy validation. It lets a privileged user write an opcode to `rap_test` and reports validation success or detailed RAP output through kernel logs.

## Important APIs, Types, and Functions
`amdgpu_rap_debugfs_write` is the write handler. It parses a tiny userspace opcode, powers the device, disables GFX off, invokes `psp_rap_invoke`, decodes `struct ta_rap_shared_memory` output on failure, then restores power/GFX state. `amdgpu_rap_debugfs_init` creates the `rap_test` file only when the RAP TA context is initialized.

## Control Flow
The write path only accepts offset zero and size two, parses the integer opcode, runtime-resumes the DRM device, disables GFX off because RAP cannot handle that state, supports opcode `2` (`TA_CMD_RAP__VALIDATE_L0`), logs success or failure details, then re-enables GFX off and drops runtime PM. Unsupported opcodes are logged but still return the write size after cleanup.

## State and Persistence Behavior
The file does not persist state beyond PSP/RAP shared memory side effects and runtime PM activity. It reads RAP output fields such as last subsection, total validations, valid count, last address, and observed/expected values from the RAP shared buffer.

## Dependencies and Integration Points
Depends on debugfs, runtime PM, GFX off control, RAP TA protocol types, and the PSP RAP invocation path in `amdgpu_psp.c`. It is exposed under the primary DRM minor debugfs root.

## Risks and Test Signals
Risks include strict write-size parsing, power-management imbalance on early errors, RAP invocation while the TA is not initialized, and GFX-off handling around validation. Test by checking `rap_test` visibility only after RAP init, writing valid and invalid opcodes, forcing runtime PM failures, and confirming GFX-off is restored.
