<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.c

## Purpose
`amdgpu_umsch_mm.c` implements the common AMDGPU IP-block glue for the UMSCH MM firmware scheduler. It initializes the UMSCH ring, loads firmware metadata and VRAM buffers, submits packets and command buffers, manages firmware logs, and wires the UMSCH v4.0 IP block into AMDGPU lifecycle callbacks.

## Important APIs, Types, And Functions
`amdgpu_umsch_mm_submit_pkt` writes packets directly to the no-scheduler UMSCH ring. `amdgpu_umsch_mm_query_fence` polls the ring sync sequence with the device timeout. Ring callbacks implement read/write pointer access through either doorbells or MMIO registers. `amdgpu_umsch_mm_ring_init` creates a 1024-DW ring using MMHUB0, a fixed doorbell index, and `AMDGPU_RING_TYPE_UMSCH_MM`.

`amdgpu_umsch_mm_init_microcode` requests `amdgpu/umsch_mm_4_0_0.bin` for VCN 4.0.5/4.0.6, reads `umsch_mm_firmware_header_v1_0`, records ucode/data sizes and start addresses, and registers UMSCH ucode/data entries in the global PSP firmware array. `amdgpu_umsch_mm_allocate_ucode_buffer` and `amdgpu_umsch_mm_allocate_ucode_data_buffer` copy firmware sections into VRAM BOs. `amdgpu_umsch_mm_psp_execute_cmd_buf` asks PSP to execute the generated command buffer. Lifecycle functions implement early/sw/hw init/fini, suspend/resume, and debugfs firmware-log setup.

## Control Flow
Early init selects v4.0 function tables based on VCN IP version and sets register addresses. SW init allocates a writeback slot, command buffer, debug-log BO, initializes hidden mutex and AGDB indices, initializes the firmware log buffer, initializes the ring, and requests firmware. HW init loads microcode through version-specific callbacks, starts the ring, and sets hardware resources. HW fini stops the ring and frees firmware ucode/data BOs; SW fini releases firmware, ring resources, mutex, command buffer, log BO, and writeback slot.

## State And Persistence
`adev->umsch_mm` stores ring state, MMIO register offsets, firmware pointer/version fields, ucode/data BOs and GPU addresses, command-buffer BO and current pointer, writeback index and scheduler context address, VMID/engine/HQD masks, AGDB doorbell indices, a hidden mutex, and a firmware log BO. Firmware log state is a circular buffer with header, rptr, wptr, size, and wrap fields.

## Dependencies And Integration Points
The file depends on Linux firmware, debugfs, DRM ring helpers, AMDGPU BO allocation, PSP firmware loading, doorbell assignment, VCN IP versioning, `umsch_mm_v4_0` function providers, and `amdgpu_ucode` UMSCH header definitions. It integrates with VPE/VCN queue scheduling through UMSCH resource and queue packets.

## Risks
Only VCN 4.0.5 and 4.0.6 are accepted. The fixed doorbell formula and AGDB index derivation must not collide with other assignments. Firmware BO allocation uses VRAM and alignment requirements that can fail under pressure. SW init error paths after command/log BO allocation do not unwind every earlier allocation locally, relying on upper-level teardown. Debugfs log reads trust firmware-maintained pointers within size checks and update `rptr` from the CPU side.

## Test Signals
Boot devices with VCN 4.0.5/4.0.6, verify firmware request and PSP UMSCH entries, run HW init/fini and suspend/resume loops, submit packets and poll fences, read `amdgpu_umsch_fwlog`, check doorbell writes versus MMIO fallback, inject allocation failures in SW init, and validate no leaks across repeated IP block teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.c -->
