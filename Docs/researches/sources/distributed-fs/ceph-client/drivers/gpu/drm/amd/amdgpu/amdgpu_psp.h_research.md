
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp.h

## Purpose
Defines the PSP public data model, firmware descriptors, TA contexts, runtime DB structures, command constants, function-table hooks, wrapper macros, IP block declarations, and exported PSP service prototypes.

## Important APIs, Types, and Functions
Important definitions include PSP command/fence buffer sizes, TMR sizing/alignment, mailbox masks, `enum ta_type_id`, `enum psp_bootloader_cmd`, `enum psp_ring_type`, `struct psp_ring`, `enum psp_reg_prog_id`, `struct psp_funcs`, `struct ta_funcs`, `struct psp_bin_desc`, `struct ta_mem_context`, `struct ta_context`, TA-specific contexts for XGMI/RAS/HDCP/DTM/RAP/SecureDisplay, memory-training structures, runtime DB entries, debugfs SPI ROM BO triplets, and the large `struct psp_context`.

## Control Flow
Version backends fill `struct psp_funcs`; generic code calls wrapper macros such as `psp_ring_create`, `psp_bootloader_load_sos`, `psp_mem_training`, `psp_load_usbc_pd_fw`, `psp_update_spirom`, and `psp_get_fw_type`. Public prototypes expose command waiting, firmware loading, reset, TA operations, XGMI/RAS/HDCP/DTM/RAP/SecureDisplay invocation, RLC autoload, register programming, microcode parsing, firmware reservation, partition changes, SQ perfmon config, and debugfs init.

## State and Persistence Behavior
The header documents persistent PSP state in `struct psp_context`: firmware BOs, command/fence BOs, TMR, firmware binary descriptors, loaded firmware handles, TA session contexts, memory training cache, boot config, flash support flags, IFWI staging, and debugfs dump ownership. TA shared memory sizes are fixed by enum and used to allocate host-visible buffers for PSP communication.

## Dependencies and Integration Points
Includes PSP GFX and TA interface headers, AMDGPU core structures, XGMI/RAS/RAP/SecureDisplay protocol types, and exports IP block version objects consumed by device discovery. It forms the contract between generic PSP code and ASIC-specific PSP implementations.

## Risks and Test Signals
Risks include macro wrappers dereferencing missing function pointers, protocol constant mismatch with firmware, TA shared buffer sizing drift, and incompatible runtime DB layout assumptions. Test through build coverage for every PSP generation, firmware-load tests that exercise optional hook absence, TA protocol version checks, and sysfs/debugfs feature visibility.
