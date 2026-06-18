<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.c

## Purpose
Implements VCN 5.0.1, adding AID-aware instance mapping, SR-IOV MMSCH initialization, per-queue reset gating by PSP/DPM capabilities, JPEG-coordinated VCN reset, and RAS/ACA poison reporting on top of the VCN 5 unified-ring model.

## Important APIs, Types, And Functions
`vcn_v5_0_1_ip_block` exports lifecycle callbacks including a `late_init()` that computes supported reset types. `vcn_v5_0_1_fw_shared_init()` lazily initializes `amdgpu_vcn5_fw_shared`. `vcn_v5_0_1_start_sriov()` builds and submits an MMSCH v5 init table for VF environments. `vcn_v5_0_1_start_dpg_mode()` and `stop_dpg_mode()` handle SOC24 DPG programming and PSP SRAM upload using `AMDGPU_UCODE_ID_VCN0_RAM`. `vcn_v5_0_1_ring_reset()` coordinates VCN reset with JPEG pre/post helpers. RAS logic is provided by `vcn_v5_0_1_query_poison_status()`, ACA bank parser/validator functions, and `vcn_v5_0_1_ras_late_init()`.

## Control Flow
Early init installs unified ring, IRQ, and RAS functions, assigns one encode ring per instance, and calls common VCN early init. Software init registers one shared VCN IRQ source and a separate poison IRQ source, initializes every instance, computes doorbell indices from `GET_INST(VCN, i)` with SR-IOV-specific spacing, sets the MMHUB from `aid_id`, initializes rings, allocates VF MM tables, initializes RAS if supported, and enables register dump/sysfs reset mask state. Hardware init either asks MMSCH to initialize VCN in SR-IOV and marks rings ready, or configures doorbells, refreshes firmware shared state, checks RRMT capability, and tests rings. Direct start follows VCPU boot sequencing with physical VCN instance IDs; DPG start also writes a dummy `0xDEADBEEF` DPG entry to communicate AID selection to PSP when using indirect SRAM. Interrupts map `entry->node_id` through `node_id_to_phys_map`, find the VCN instance with matching `aid_id`, and process fence interrupts.

## State And Persistence
State includes `aid_id`, `cur_state`, ring doorbell indices, firmware shared queue state, VF RB setup data inside shared memory, RAS block binding, poison IRQ registration, and per-instance reset mutexes. SR-IOV persists a guest-visible MMSCH table in `adev->virt.mm_table` and uses mailbox registers for completion status. Ring reset temporarily manipulates JPEG scheduler and power-gating state because VCN reset also resets JPEG.

## Dependencies And Integration Points
Depends on VCN 5.0 registers, VCN 4.0.3 ring emit helpers for VM flush/HDP/wreg/reg-wait, MMSCH v5 command formats, SR-IOV virtualization MM tables, DPM reset support, PSP SOS firmware version checks, JPEG power/scheduler helpers, RAS core, ACA bank decoding/cache logging, and AMDGPU IRQ/ring/fence infrastructure.

## Risks And Test Signals
Risks include logical-vs-physical instance mismatches, shared `adev->vcn.inst->irq` setup for multiple instances, SR-IOV mailbox timeout or incomplete status handling, incorrect MMSCH table sizes, and reset interactions with JPEG queues. RAS risks include filtering the wrong ACA banks or missing poison IRQ enablement. Test signals include VF MMSCH mailbox OK/pass status, ring and IB tests, AID-routed fence interrupts, JPEG rings recovering after VCN reset, DPM per-queue reset success, RAS poison query logs, ACA error counts, suspend/resume under reset, and RRMT capability detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.c -->
