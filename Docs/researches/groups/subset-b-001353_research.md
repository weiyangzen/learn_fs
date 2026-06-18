# subset-b-001353 research

This grouped report covers AMDGPU Navi PM4 packet definitions, PSP mailbox/ring interfaces and generation-specific PSP implementations, and the VI-era SDMA v2.4 engine. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nvd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nvd.h

Purpose: provides Navi-era PM4 command processor packet definitions used by AMDGPU command emission and parsing code. It is a macro-only hardware ABI header for type 0/2/3 packet construction, opcode constants, and bitfield encoders for graphics, compute, memory, queue, cache, and synchronization commands.

Important APIs/types/functions: primary helpers are `PACKET0()`, `PACKET2()`, `PACKET3()`, `PACKET3_COMPUTE()`, `CP_PACKET_GET_TYPE()`, `CP_PACKET_GET_COUNT()`, `CP_PACKET0_GET_REG()`, and `CP_PACKET3_GET_OPCODE()`. Major opcode groups include `PACKET3_WRITE_DATA`, `WAIT_REG_MEM`, `INDIRECT_BUFFER`, `COPY_DATA`, `EVENT_WRITE`, `RELEASE_MEM`, `DMA_DATA`, `ACQUIRE_MEM`, register load/set packets, queue management packets, `INVALIDATE_TLBS`, `MAP_PROCESS`, `MAP_QUEUES`, `UNMAP_QUEUES`, `QUERY_STATUS`, and GFX11 `SET_Q_PREEMPTION_MODE`.

Control flow: there is no runtime control flow. Consumers combine opcode constants and field macros into dwords placed into GPU rings or indirect buffers. The macros encode packet headers, register offsets, GPU virtual addresses, cache policy, temporal hints, event selectors, queue masks, VMID/PASID fields, and memory synchronization operations.

State and persistence behavior: no driver state is stored. The definitions must exactly match the hardware packet ABI; emitted values persist only as command stream contents consumed by the GPU command processor.

Dependencies and integration points: relies on common bitfield helper macros such as `REG_SET()` and integer types from surrounding AMDGPU headers. It integrates with GFX, KIQ/MES, VM/TLB, fence, and queue-management emitters that need Navi PM4 packet encodings, and it overlaps conceptually with SDMA packet headers that use a separate packet format.

Risks and test signals: risks are off-by-one packet counts, incorrect register ranges, stale opcode aliases, duplicate opcode values with different meanings, and field-width truncation hidden by macros. Test signals include ring tests on graphics and compute queues, VM flush and TLB invalidation tests, fence and release-memory validation, SR-IOV queue map/unmap paths, command parser validation, and GPU hang/regression coverage when adding new packet fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nvd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_gfx_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_gfx_if.h

Purpose: defines the host-driver to PSP Trusted Execution Environment graphics interface ABI. It describes mailbox command IDs, ring control registers, command-buffer structures, firmware type identifiers, TA command layouts, command responses, and ring-buffer frame layout used by `amdgpu_psp.c` and the generation-specific PSP backends.

Important APIs/types/functions: important definitions include `PSP_GFX_CMD_BUF_VERSION`, command/response masks, `C2PMSG_CMD_GFX_USB_PD_FW_VER`, `enum psp_gfx_crtl_cmd_id`, `struct psp_gfx_ctrl`, `enum psp_gfx_cmd_id`, boot config enums, `struct psp_gfx_cmd_load_ta`, `struct psp_gfx_cmd_unload_ta`, `struct psp_gfx_buf_desc`, `struct psp_gfx_buf_list`, `struct psp_gfx_cmd_invoke_cmd`, `struct psp_gfx_cmd_setup_tmr`, the large `enum psp_gfx_fw_type`, `union psp_gfx_commands`, `struct psp_gfx_resp`, `struct psp_gfx_cmd_resp`, and `struct psp_gfx_rb_frame`.

Control flow: no executable control flow exists in the header. Runtime code populates a fixed 1024-byte `psp_gfx_cmd_resp`, points a 64-byte ring frame at it, advances PSP ring write pointers, and waits for PSP status/fence updates. Register-control commands initialize or destroy RBI/GPCOM rings, enable interrupts, request mode1 reset, reroute IH state, or notify PSP that a VF produced commands.

State and persistence behavior: the structures define transient shared-memory command and response state. Persistent runtime state is owned by `struct psp_context`, its `km_ring`, TA contexts, TMR/VMR allocations, and PSP firmware; this header fixes field offsets, address alignment requirements, and response unions so host and PSP firmware agree.

Dependencies and integration points: consumed by `amdgpu_psp.h/c` and the PSP version files. Firmware type IDs connect AMDGPU firmware descriptors to `GFX_CMD_ID_LOAD_IP_FW`, while TA structures support XGMI, RAS, HDCP, DTM, RAP, secure display, spatial partitioning, memory partitioning, SQ perfmon configuration, firmware reservation queries, and attestation database access.

Risks and test signals: ABI drift is the main risk: structure padding, enum values, buffer sizes, command IDs, and alignment rules must match PSP firmware. The `GFX_BUF_MAX_DESC` scatter/gather limit and fixed command-buffer reserved regions are contract-sensitive. Test signals include PSP ring command submission, TA load/invoke/unload, TMR setup/destruction, firmware load through PSP, SR-IOV GPCOM operation, USB-C PD firmware version reads, boot config queries, and checks that command responses report expected `TEE_SUCCESS` or device-specific errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_gfx_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.c

Purpose: implements PSP function callbacks for MP0/PSP v10 Raven-family APUs. It initializes ASD and TA firmware and provides the mailbox sequence for creating, stopping, destroying, and advancing the kernel PSP ring.

Important APIs/types/functions: file-local callbacks are `psp_v10_0_init_microcode()`, `psp_v10_0_ring_create()`, `psp_v10_0_ring_stop()`, `psp_v10_0_ring_destroy()`, `psp_v10_0_mode1_reset()`, `psp_v10_0_ring_get_wptr()`, and `psp_v10_0_ring_set_wptr()`. `psp_v10_0_funcs` installs those callbacks through exported `psp_v10_0_set_psp_funcs()`. Firmware declarations cover Raven, Picasso, and Raven2 ASD/TA blobs.

Control flow: initialization decodes the MP0 firmware prefix, loads ASD, then TA microcode. A Raven GC 9.1.0 revision-specific secure-display workaround zeroes the secure display TA size for firmware versions at or above `0x27000008`. Ring creation writes the ring GPU address low/high and size to `C2PMSG_69/70/71`, writes the ring type shifted into `C2PMSG_64`, delays 20 ms, and waits for the PSP response flag. Stop writes the destroy command to `C2PMSG_64`; destroy stops and frees `adev->firmware.rbuf`.

State and persistence behavior: persistent state is in `psp->km_ring`, `adev->firmware.rbuf`, and firmware/TA descriptors loaded by common PSP helpers. The ring write pointer is stored in hardware register `C2PMSG_67`. No mode1 reset state is supported; the callback returns `-EINVAL`.

Dependencies and integration points: depends on `amdgpu_psp` helpers, firmware naming from `amdgpu_ucode_ip_version_decode()`, SOC15 MP0 register macros, Raven GC/SDMA register headers, and the common PSP lifecycle that calls this `struct psp_funcs` table.

Risks and test signals: risks include mailbox timeout, incorrect ring address alignment, the fixed 20 ms handshake delay masking races, failure to free the ring buffer after partial stop failures, and the secure-display workaround being too narrow or too broad. Test signals are PSP firmware load success on Raven/Picasso/Raven2, ring command submission, write-pointer updates through `C2PMSG_67`, clean suspend/remove teardown, and explicit mode1 reset rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.h

Purpose: declares the PSP v10 callback installer for Raven-family PSP support.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v10_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no direct control flow. Device discovery or ASIC setup calls the setter so the common PSP layer dispatches through v10-specific callbacks.

State and persistence behavior: no state is defined here. The setter persists a pointer to the file-local `psp_v10_0_funcs` table in `psp->funcs`.

Dependencies and integration points: integrated by AMDGPU PSP discovery and built via the AMDGPU Makefile with other PSP generation objects.

Risks and test signals: risks are declaration/definition drift and missing inclusion where v10 PSP blocks are selected. Test signals are successful builds and runtime selection of PSP v10 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0.c

Purpose: implements the broad PSP v11 backend for Vega20, Navi1x/2x, Arcturus, Vangogh, and related ASICs. It handles firmware selection, bootloader component loads, PSP ring setup for PF and SR-IOV VF modes, mode1 reset, memory training, USB-C PD firmware load/version operations, and bootloader wait behavior.

Important APIs/types/functions: key callbacks include `psp_v11_0_init_microcode()`, `psp_v11_0_wait_for_bootloader()`, `psp_v11_0_bootloader_load_kdb/spl/sysdrv/sos()`, `psp_v11_0_ring_create/stop/destroy()`, `psp_v11_0_mode1_reset()`, `psp_v11_0_memory_training()`, `psp_v11_0_ring_get_wptr()`, `psp_v11_0_ring_set_wptr()`, `psp_v11_0_load_usbc_pd_fw()`, and `psp_v11_0_read_usbc_pd_fw()`. The `psp_v11_0_funcs` table wires these into common PSP code.

Control flow: microcode initialization switches on MP0 IP version, loading SOS, ASD, TA, or TOC combinations and disabling secure display on unsupported families. Bootloader component loading first checks the SOS sign-of-life register, waits for the bootloader, copies the selected binary through `psp_copy_fw()`, writes the 1 MiB-aligned firmware buffer address to `C2PMSG_36`, sends a bootloader command through `C2PMSG_35`, and waits again. Ring creation branches for SR-IOV: VFs use `C2PMSG_101/102/103` and `GFX_CTRL_CMD_ID_INIT_GPCOM_RING`; PFs wait for `C2PMSG_64` ready, then program `C2PMSG_69/70/71` and send the ring type. Memory training derives needed save/restore/short/long operations from system-cache and P2C headers, protects the bottom of visible VRAM around long training, and exchanges training data through VRAM access helpers.

State and persistence behavior: state is held in `psp->sys/sos/kdb/spl`, `psp->km_ring`, `psp->mem_train_ctx`, `adev->psp.securedisplay_context`, and hardware C2PMSG registers. The VF write pointer is mirrored in `psp->km_ring.ring_wptr`; PFs read and write `C2PMSG_67`. Memory training increments `ctx->training_cnt` and persists training cache contents in system memory across resets.

Dependencies and integration points: depends on Linux firmware/vmalloc/drm device helpers, `amdgpu_psp`, `amdgpu_ras`, SOC15 MP0/GC/SDMA/NBIO/OSS register definitions, common firmware naming, SR-IOV detection, VRAM aperture access, HDP flush, and common PSP wrappers for boot, TA, TMR, and firmware loading.

Risks and test signals: risks include IP-version switch omissions, bootloader wait timeouts, stale sign-of-life checks after S3/S4 reset, SR-IOV mailbox divergence, VRAM corruption during long memory training, leaked vmalloc buffers on early failures, and USB-C PD firmware operations taking up to 240 seconds. Test signals include firmware load on every declared family, suspend/resume and GPU reset paths, SR-IOV VF GPCOM ring tests, mode1 reset, memory training with forced long/short modes, secure-display TA availability checks, and USB-C PD firmware load/version status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0.h

Purpose: declares the PSP v11 callback installer.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v11_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no executable flow. The setter is invoked by AMDGPU IP discovery when a PSP v11 block is selected.

State and persistence behavior: no direct state. The setter stores the v11 `struct psp_funcs` pointer in `psp->funcs`.

Dependencies and integration points: built with the PSP v11 implementation and referenced from AMDGPU discovery and PSP setup paths.

Risks and test signals: declaration drift would break builds or wrong generation dispatch. Test signals are compile coverage and correct runtime function table selection for v11 ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0_8.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0_8.c

Purpose: provides a narrow PSP v11.0.8 callback set focused on PSP ring management for an ASIC variant whose firmware loading and bootloader handling are supplied elsewhere or not needed through this backend.

Important APIs/types/functions: implements `psp_v11_0_8_ring_stop()`, `psp_v11_0_8_ring_create()`, `psp_v11_0_8_ring_destroy()`, `psp_v11_0_8_ring_get_wptr()`, `psp_v11_0_8_ring_set_wptr()`, and exports `psp_v11_0_8_set_psp_funcs()`. `psp_v11_0_8_funcs` contains only ring callbacks.

Control flow: ring stop branches on SR-IOV VF mode, writing destroy commands to `C2PMSG_101` for GPCOM or `C2PMSG_64` for PF rings, then delays and waits for the response flag. Ring create in VF mode first stops any existing ring, writes address low/high to `C2PMSG_102/103`, sends `GFX_CTRL_CMD_ID_INIT_GPCOM_RING`, and waits. PF mode waits for trust-OS readiness, programs `C2PMSG_69/70/71`, sends the shifted ring type through `C2PMSG_64`, and waits. Destroy stops then frees the kernel ring buffer.

State and persistence behavior: ring memory state lives in `psp->km_ring` and `adev->firmware.rbuf`. PF write pointer state uses `C2PMSG_67`; VF write pointer access uses `C2PMSG_102` and consume-command notification without keeping the local mirror used by some earlier versions.

Dependencies and integration points: depends on `amdgpu_psp`, SOC15 MP 11.0.8 register definitions, SR-IOV detection, and common PSP ring allocation/freeing.

Risks and test signals: risks include no local firmware initialization callback, VF write-pointer semantics differing from v11.0, mailbox timeout, and freeing ring memory after failed stop. Test signals include PF and VF PSP ring command submission, write-pointer synchronization, teardown after reset/remove, and IP-discovery selection of this backend only where the missing callbacks are acceptable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0_8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0_8.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0_8.h

Purpose: declares the PSP v11.0.8 callback installer.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v11_0_8_set_psp_funcs(struct psp_context *psp);`.

Control flow: no direct flow; common discovery invokes the setter to install the variant ring callbacks.

State and persistence behavior: no local state. Runtime state is the function table pointer assigned to `psp->funcs`.

Dependencies and integration points: integrated with the AMDGPU PSP build and IP-discovery tables.

Risks and test signals: build and dispatch drift are the main risks. Test signal is successful compilation and correct selection on PSP 11.0.8 hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v11_0_8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v12_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v12_0.c

Purpose: implements PSP v12 callbacks for Renoir/Green Sardine APUs, covering ASD/TA firmware initialization, bootloader system driver and SOS loading, PSP ring management, and mode1 reset.

Important APIs/types/functions: key callbacks are `psp_v12_0_init_microcode()`, `psp_v12_0_bootloader_load_sysdrv()`, `psp_v12_0_bootloader_load_sos()`, `psp_v12_0_ring_create()`, `psp_v12_0_ring_stop()`, `psp_v12_0_ring_destroy()`, `psp_v12_0_mode1_reset()`, `psp_v12_0_ring_get_wptr()`, and `psp_v12_0_ring_set_wptr()`. `psp_v12_0_set_psp_funcs()` installs `psp_v12_0_funcs`.

Control flow: initialization loads ASD and TA microcode, then disables secure-display TA use unless the APU is Renoir. Bootloader loaders skip work when `C2PMSG_81` sign-of-life is set, otherwise wait on `C2PMSG_35`, copy firmware through `psp_copy_fw()`, provide the firmware buffer address through `C2PMSG_36`, and send v12 bootloader commands through `C2PMSG_35`. Ring create programs `C2PMSG_69/70/71` and `C2PMSG_64`; stop handles both VF GPCOM and PF ring destroy paths. Mode1 reset waits for PSP ready, sends `GFX_CTRL_CMD_ID_MODE1_RST`, sleeps, and verifies `C2PMSG_33` response.

State and persistence behavior: firmware descriptors, secure-display context, ring buffer, and mailbox state are persistent across the PSP lifecycle. VF write pointers are held in `C2PMSG_102`, PF write pointers in `C2PMSG_67`.

Dependencies and integration points: depends on common PSP firmware helpers, Renoir/Green Sardine firmware names, SOC15 MP12 register definitions, SR-IOV detection, and AMDGPU reset paths.

Risks and test signals: risks include secure-display gating errors, using hard-coded shifted bootloader command values, missing delay behavior compared with v11, and mailbox timeouts in mode1 reset. Test signals are Renoir and Green Sardine firmware load, secure-display availability only on Renoir, PF/VF ring operation, bootloader SOS/sysdrv path after cold boot, and mode1 reset success/failure logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v12_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v12_0.h

Purpose: declares the PSP v12 callback installer.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v12_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no direct flow. AMDGPU device setup calls the setter for v12 PSP IP blocks.

State and persistence behavior: no state here; `psp->funcs` is assigned by the implementation.

Dependencies and integration points: tied to AMDGPU PSP discovery and the `psp_v12_0.c` implementation.

Risks and test signals: declaration mismatch and missing discovery wiring are the relevant risks. Test signals are build coverage and proper v12 dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v12_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0.c

Purpose: implements the main PSP v13 backend for SOC21/CDNA/RDNA families and some PSP 14.0.x TOC-based variants. It covers microcode selection, bootloader component loading, bootloader steady-state waits, ring operation, memory training, USB-C PD firmware operations, SPI ROM update/dump, fatal-error quirks, RAS capability discovery, auxiliary SOS/reload decisions, and SR-IOV no-ring register programming.

Important APIs/types/functions: key callbacks include `psp_v13_0_init_microcode()`, `psp_v13_0_wait_for_bootloader_steady_state()`, `psp_v13_0_bootloader_load_kdb/spl/sysdrv/soc_drv/intf_drv/dbg_drv/ras_drv/spdm_drv/sos()`, `psp_v13_0_ring_create/stop/destroy()`, `psp_v13_0_memory_training()`, `psp_v13_0_load_usbc_pd_fw()`, `psp_v13_0_read_usbc_pd_fw()`, `psp_v13_0_update_spirom()`, `psp_v13_0_dump_spirom()`, `psp_v13_0_vbflash_status()`, `psp_v13_0_fatal_error_recovery_quirk()`, `psp_v13_0_get_ras_capability()`, `psp_v13_0_is_aux_sos_load_required()`, `psp_v13_0_is_reload_needed()`, and `psp_v13_0_reg_program_no_ring()`.

Control flow: initialization chooses SOS/TA versus TOC/TA loading by MP0 IP version and skips RAS TA on SR-IOV guests for 13.0.2. Bootloader waits are short for older versions and extended through VMBX readiness plus boot-status logging/RAS queries for 13.0.6/12/14/15. Component loaders skip if SOS is alive, clear the 1 MiB primary firmware buffer, copy the requested descriptor, pass the shifted buffer address through `C2PMSG_36`, send a `PSP_BL__*` command through `C2PMSG_35`, and wait. Ring create/stop follow PF and VF mailbox paths. Memory training mirrors v11 logic. SPI ROM update and dump write low/high firmware addresses to `C2PMSG_116`, execute commands through `C2PMSG_115`, ring doorbell `C2PMSG_73`, wait for ready/status, and mark `psp->vbflash_done` before flash update.

State and persistence behavior: persistent state includes firmware descriptors for multiple PSP boot components, `psp->sos.fw_version` read from `C2PMSG_58`, `psp->km_ring`, `psp->mem_train_ctx`, `psp->vbflash_done`, `adev->ras_hw_enabled`, and `amdgpu_ras` poison support. Reload decisions compare firmware-header SOS version with hardware-reported SOS version. Auxiliary SOS load is conditioned by MP1 public scratch PMFW version.

Dependencies and integration points: depends on `amdgpu_psp`, `amdgpu_ras`, SOC15 MP13 registers, Linux `drm_dev_enter()`/vmalloc for VRAM preservation, firmware naming, SR-IOV detection, RAS boot status queries, USB-C PD support, VBIOS flashing, and common PSP command dispatch through `struct psp_funcs`.

Risks and test signals: risks include IP-version switch coverage, long bootloader waits hiding firmware faults, incorrect VMBX status interpretation, `psp_v13_0_bootloader_load_spl()` using `psp->kdb` as its descriptor, VRAM corruption around long memory training, SPI flash timeout/error handling, host-only RAS capability gating, and register namespace differences across IP versions. Test signals include firmware load on all listed IP versions, VF/PF ring tests, memory training save/restore, VBIOS flash update and dump paths, RAS capability values from `C2PMSG_127`, auxiliary SOS decision on 13.0.6 PMFW versions, reload-needed detection, fatal-error recovery on 13.0.10, and no-ring GBR/IH programming on SR-IOV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0.h

Purpose: declares PSP v13 callback installation and the SPI ROM update timeout shared by the v13 implementation.

Important APIs/types/functions: defines `PSP_SPIROM_UPDATE_TIMEOUT` as 60000 ms and declares `void psp_v13_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no local flow. The timeout constant is consumed by SPI ROM update/dump command waits; the setter is called during PSP IP setup.

State and persistence behavior: no state. The implementation persists the callback table in `psp->funcs` and uses the timeout for hardware polling behavior.

Dependencies and integration points: includes `amdgpu_psp.h` and integrates with common PSP and VBIOS flashing code.

Risks and test signals: too-short or too-long SPI timeout values affect user-visible VBIOS flash operations. Test signals include compile coverage, callback selection, and SPI ROM update timing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0_4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0_4.c

Purpose: implements the PSP 13.0.4 variant backend. It is a slimmer v13-style implementation with TOC/TA microcode loading, bootloader component loading, SOS loading, and PF/VF PSP ring management.

Important APIs/types/functions: callbacks include `psp_v13_0_4_init_microcode()`, `psp_v13_0_4_wait_for_bootloader()`, bootloader loaders for KDB, SPL, sysdrv, soc driver, interface driver, debug driver, and SOS, plus `psp_v13_0_4_ring_create/stop/destroy()`, `psp_v13_0_4_ring_get_wptr()`, and `psp_v13_0_4_ring_set_wptr()`. `psp_v13_0_4_set_psp_funcs()` installs `psp_v13_0_4_funcs`.

Control flow: initialization only accepts MP0 IP 13.0.4 and loads TOC then TA microcode. Bootloader helpers skip when sign-of-life is present, retry `C2PMSG_35` readiness up to 10 times, clear the primary 1 MiB buffer, copy the selected firmware component, pass its shifted address through `C2PMSG_36`, issue the bootloader command, and wait. Ring setup follows the standard v13 PF path through `C2PMSG_64/69/70/71` and the VF GPCOM path through `C2PMSG_101/102/103`.

State and persistence behavior: firmware descriptors live in `psp_context`; the primary firmware buffer is reused for each bootloader component. Ring state is in `psp->km_ring` and `adev->firmware.rbuf`. PF write pointer uses `C2PMSG_67`, VF uses `C2PMSG_102`.

Dependencies and integration points: depends on MP 13.0.4 register definitions, common PSP firmware parsing/loading, SR-IOV detection, and AMDGPU discovery selecting this variant for IP 13.0.4.

Risks and test signals: risks include only supporting one IP version, no extended VMBX/boot-status handling, `bootloader_load_spl()` using `psp->kdb` rather than `psp->spl`, and mailbox timeouts. Test signals include TOC/TA firmware load, bootloader component sequencing, PF/VF ring creation and command submission, and clean ring teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0_4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0_4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0_4.h

Purpose: declares the PSP 13.0.4 callback installer.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v13_0_4_set_psp_funcs(struct psp_context *psp);`.

Control flow: no direct flow; discovery calls the setter for the 13.0.4 backend.

State and persistence behavior: no local state. The setter persists the implementation function table in `psp->funcs`.

Dependencies and integration points: tied to AMDGPU PSP build and IP-discovery selection for MP0 13.0.4.

Risks and test signals: risks are declaration drift and wrong ASIC dispatch. Test signals are build coverage and correct runtime function table installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v13_0_4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v14_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v14_0.c

Purpose: implements PSP v14 callbacks for MPASP-based 14.0.2/14.0.3/14.0.5 devices. It handles SOS or TOC firmware initialization, bootloader components including RAS/IP key manager drivers, ring management, memory training, USB-C PD firmware operations, and SPI ROM update/status.

Important APIs/types/functions: key callbacks are `psp_v14_0_init_microcode()`, `psp_v14_0_wait_for_bootloader()`, `psp_v14_0_bootloader_load_kdb/spl/sysdrv/soc_drv/intf_drv/dbg_drv/ras_drv/ipkeymgr_drv/sos()`, `psp_v14_0_ring_create/stop/destroy()`, `psp_v14_0_memory_training()`, `psp_v14_0_load_usbc_pd_fw()`, `psp_v14_0_read_usbc_pd_fw()`, `psp_v14_0_update_spirom()`, and `psp_v14_0_vbflash_status()`.

Control flow: microcode initialization loads SOS/TA for 14.0.2 and 14.0.3, or TOC/TA for 14.0.5. Bootloader component load is v13-like but uses `regMPASP_SMN_C2PMSG_*` registers; debug driver load maps to the v14-renamed HAD driver command. Ring create/stop branches for SR-IOV VF GPCOM versus PF rings. Memory training mirrors v13 behavior with MPASP mailbox registers. USB-C PD load passes a shifted LFB address, waits for readiness, sends `GFX_CMD_USB_PD_USE_LFB`, and polls up to 240 seconds. SPI update writes low/high firmware address words and runs update commands through `C2PMSG_115/116` plus doorbell `C2PMSG_73`.

State and persistence behavior: state lives in PSP firmware descriptors, the primary firmware buffer, `psp->km_ring`, memory-training context, and `psp->vbflash_done`. Mailbox state is maintained in MPASP C2PMSG registers. No SPI dump or RAS capability callback is provided in this file.

Dependencies and integration points: depends on MP 14.0.2 register definitions, common PSP helpers, SR-IOV detection, VRAM access and HDP flush for memory training, USB-C PD firmware support, VBIOS flashing, and the common PSP function table.

Risks and test signals: risks include register namespace changes from MP0 to MPASP, a double wait in `psp_v14_0_exec_spi_cmd()` after the conditional SPI update wait, long USB-C and SPI timeouts, bootloader component ordering, and memory-training VRAM preservation. Test signals include firmware load on all supported v14 versions, PF/VF ring command submission, memory-training long and short flows, USB-C PD load/version paths, VBIOS flash update and status, and bootloader HAD/RAS/IP-key-manager component loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v14_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v14_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v14_0.h

Purpose: declares PSP v14 callback installation and the SPI ROM update timeout.

Important APIs/types/functions: defines `PSP_SPIROM_UPDATE_TIMEOUT` as 60000 ms and declares `void psp_v14_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no local executable flow. The timeout is used by SPI update polling; the setter is used by PSP discovery.

State and persistence behavior: no state. Runtime state is assigned by `psp_v14_0_set_psp_funcs()` in the implementation.

Dependencies and integration points: includes `amdgpu_psp.h` and integrates with MPASP PSP support and VBIOS flash callbacks.

Risks and test signals: risk is timeout mismatch with actual PSP flash latency or missing callback selection. Test signals are compile coverage, function table installation, and SPI update timing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v14_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0.c

Purpose: implements PSP 15.0.0 callbacks for a TOC/TA firmware backend with PSP ring management. It is minimal compared with v13/v14 and primarily handles firmware table setup and ring mailbox differences for PF versus SR-IOV.

Important APIs/types/functions: callbacks are named `psp_v15_0_0_init_microcode()`, `psp_v15_0_0_ring_stop()`, `psp_v15_0_0_ring_create()`, `psp_v15_0_0_ring_destroy()`, `psp_v15_0_0_ring_get_wptr()`, and `psp_v15_0_0_ring_set_wptr()`. `psp_v15_0_0_set_psp_funcs()` installs `psp_v15_0_0_funcs`.

Control flow: initialization decodes the MP0 firmware prefix, loads TOC microcode, then loads TA microcode. Ring stop and create branch on SR-IOV. VF mode uses `regMPASP_SMN_C2PMSG_101/102/103`; PF mode uses the PCRU1 MPASP register aliases for `C2PMSG_64/67/69/70/71`. Ring creation waits for ready, writes ring address and size, sends the shifted ring type, delays, and waits for response. Destroy stops the ring and frees `adev->firmware.rbuf`.

State and persistence behavior: persistent PSP state is `psp->funcs`, firmware descriptors populated by common PSP helpers, and `psp->km_ring`. PF write pointer is in `regMPASP_PCRU1_MPASP_C2PMSG_67`; VF write pointer is in `regMPASP_SMN_C2PMSG_102`.

Dependencies and integration points: depends on MP 15.0.0 register headers, common PSP firmware helpers, SR-IOV detection, and AMDGPU IP discovery selecting the v15.0.0 backend.

Risks and test signals: risks include register alias misuse between PF and VF paths, copied error text naming v14 in v15 failures, mailbox mask changes, and absent bootloader/memory-training callbacks. Test signals include TOC/TA firmware load, PF and VF PSP ring command submission, write-pointer updates, and teardown after reset or driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0.h

Purpose: declares the PSP 15.0.0 callback installer.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v15_0_0_set_psp_funcs(struct psp_context *psp);`.

Control flow: no direct control flow. Device setup invokes the setter for PSP 15.0.0 hardware.

State and persistence behavior: no state. The setter stores a `struct psp_funcs` table in `psp->funcs`.

Dependencies and integration points: integrated with AMDGPU PSP discovery and `psp_v15_0.c`.

Risks and test signals: header guard naming and callback name drift are the main risks. Test signals are successful builds and correct PSP 15.0.0 dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0_8.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0_8.c

Purpose: implements PSP 15.0.8 callbacks for TOC-only firmware setup, PSP ring management, RAS capability query, and mapping AMDGPU firmware IDs to PSP graphics firmware type IDs.

Important APIs/types/functions: callbacks include `psp_v15_0_8_init_microcode()`, `psp_v15_0_8_ring_create/stop/destroy()`, `psp_v15_0_8_ring_get_wptr()`, `psp_v15_0_8_ring_set_wptr()`, `psp_v15_0_8_get_ras_capability()`, and `psp_v15_0_8_get_fw_type()`. The firmware-type mapper handles CAP, SDMA0-7, MES/KIQ stacks, RLC variants, SMU, PPTABLE, VCN, SDMA thread microcode, IMU, RS64 MEC stacks, UMSCH, and P2S table IDs.

Control flow: initialization loads only TOC microcode for the decoded MP0 prefix. Ring management follows MPASP PF/VF paths similar to v15.0.0, but PF uses `regMPASP_SMN_C2PMSG_*` rather than PCRU1 aliases. RAS capability returns false for SR-IOV VFs or missing RAS context, otherwise reads `C2PMSG_127`, stores `adev->ras_hw_enabled` from bits 0-23, and stores poison support from bit 24. Firmware-type mapping is a switch over `ucode->ucode_id` that returns `-EINVAL` for unsupported IDs.

State and persistence behavior: PSP state includes TOC descriptor state, ring buffer state, RAS hardware capability bits, and firmware-type translation used by PSP firmware loading. The mapper does not persist state but drives later load commands.

Dependencies and integration points: depends on MP 15.0.8 registers, `psp_gfx_fw_type` values from `psp_gfx_if.h`, AMDGPU firmware ID definitions, RAS context helpers, SR-IOV detection, and common PSP firmware-list loading.

Risks and test signals: risks include incomplete firmware ID mapping causing PSP firmware load failure, mapping `AMDGPU_UCODE_ID_SDMA_UCODE_TH0` and `SDMA_RS64` to `GFX_FW_TYPE_SDMA0` while TH1 has its own type, host-only RAS capability assumptions, and copied v14 error text. Test signals include TOC load, firmware-list load covering every mapped ID, RAS capability values on host, PF/VF ring command submission, and `-EINVAL` behavior for intentionally unsupported firmware IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0_8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0_8.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0_8.h

Purpose: declares the PSP 15.0.8 callback installer.

Important APIs/types/functions: includes `amdgpu_psp.h` and declares `void psp_v15_0_8_set_psp_funcs(struct psp_context *psp);`.

Control flow: no direct flow. AMDGPU discovery calls the setter to install 15.0.8 PSP callbacks.

State and persistence behavior: no local state; the implementation assigns the function table to `psp->funcs`.

Dependencies and integration points: integrated with `psp_v15_0_8.c`, common PSP code, and IP-discovery tables.

Risks and test signals: risks are declaration drift and missing function-table dispatch. Test signals are compilation and runtime callback selection on 15.0.8 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0_8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.c

Purpose: implements the older PSP v3.1 backend for Vega10/Vega12-era devices. It loads SOS/ASD firmware, boots system and secure OS drivers, reroutes interrupt handler clients, manages PF/VF PSP rings, supports an SMU reload quirk, and implements mode1 reset.

Important APIs/types/functions: key callbacks are `psp_v3_1_init_microcode()`, `psp_v3_1_bootloader_load_sysdrv()`, `psp_v3_1_bootloader_load_sos()`, `psp_v3_1_reroute_ih()`, `psp_v3_1_ring_create()`, `psp_v3_1_ring_stop()`, `psp_v3_1_ring_destroy()`, `psp_v3_1_smu_reload_quirk()`, `psp_v3_1_mode1_reset()`, `psp_v3_1_ring_get_wptr()`, and `psp_v3_1_ring_set_wptr()`. `psp_v3_1_set_psp_funcs()` installs the table.

Control flow: initialization loads SOS then ASD microcode. Bootloader loaders skip if `C2PMSG_81` sign-of-life is set, wait on `C2PMSG_35`, copy firmware, pass the shifted primary firmware address, issue `PSP_BL__LOAD_SYSDRV` or `PSP_BL__LOAD_SOSDRV`, delay, and wait for completion/sign-of-life change. Ring creation first reroutes IH settings for VMC and UMC by writing `IH_CLIENT_CFG_DATA` through PSP mailbox commands, then follows either VF `C2PMSG_101/102/103` or PF `C2PMSG_64/69/70/71` ring setup. Mode1 reset waits for PSP ready, sends reset command, then waits for `C2PMSG_33` response.

State and persistence behavior: persistent state includes firmware descriptors, `psp->km_ring`, `adev->firmware.rbuf`, and the PSP-programmed IH routing. VF write pointer is mirrored in `psp->km_ring.ring_wptr`; PF write pointer is `C2PMSG_67`. The SMU reload quirk reads MP1 firmware flags through PCIe/SMN space and returns whether interrupts are enabled.

Dependencies and integration points: depends on MP9, GC9, SDMA, NBIO, and OSS register headers, common PSP firmware helpers, SOC15 mailbox access, SR-IOV detection, and AMDGPU reset/SMU interaction.

Risks and test signals: risks include IH reroute command failures being ignored, stale sign-of-life causing skipped firmware reload, SR-IOV ring command differences, mode1 reset timeout, and SMN address assumptions in the SMU reload quirk. Test signals include Vega10/Vega12 firmware load, PSP ring command submission, VMC/UMC interrupt routing, VF write-pointer notification, mode1 reset success, and SMU reload behavior after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.h

Purpose: declares PSP v3.1 setup and several legacy PSP firmware-directory alignment constants.

Important APIs/types/functions: defines enum constants `PSP_DIRECTORY_TABLE_ENTRIES = 4`, `PSP_BINARY_ALIGNMENT = 64`, `PSP_BOOTLOADER_1_MEG_ALIGNMENT = 0x100000`, and `PSP_BOOTLOADER_8_MEM_ALIGNMENT = 0x800000`; declares `void psp_v3_1_set_psp_funcs(struct psp_context *psp);`.

Control flow: no executable flow. Constants are used by PSP firmware layout/parsing expectations in the wider PSP stack, while the setter installs v3.1 callbacks.

State and persistence behavior: no state. Runtime effect is through assigning `psp->funcs` in the implementation.

Dependencies and integration points: includes `amdgpu_psp.h` and integrates with older Vega PSP discovery/setup.

Risks and test signals: alignment constants are hardware/firmware ABI assumptions; changing them can break firmware loading. Test signals are firmware descriptor parsing, build coverage, and correct function-table selection on v3.1 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_common.h

Purpose: provides shared SDMA UTCL2 cache read/write policy enum values for SDMA packet emission code.

Important APIs/types/functions: defines `enum sdma_utcl2_cache_read_policy` with LRU, STREAM, NOA, and default NOA values; defines `enum sdma_utcl2_cache_write_policy` with LRU, STREAM, NOA, BYPASS, and default BYPASS values.

Control flow: no runtime control flow. Packet emitters select these values when programming SDMA packet cache-policy fields.

State and persistence behavior: no state. Values persist only in emitted command streams and hardware cache behavior.

Dependencies and integration points: included by SDMA generation implementations and packet-building helpers that need a common policy vocabulary across ASIC versions.

Risks and test signals: risks are mismatched enum values with hardware packet definitions or using defaults inappropriate for a given engine generation. Test signals include SDMA copy/fill/PTE operations under cache-coherency stress, VM update correctness, and performance/ordering validation with different cache policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v2_4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v2_4.c

Purpose: implements the AMDGPU SDMA v2.4 IP block for Topaz/Iceland-class VI hardware. It loads SDMA firmware, initializes SDMA register state and rings, emits SDMA packet streams for IBs, fences, VM PTE updates, flushes, copies, and fills, handles trap and illegal-instruction interrupts, and exposes AMDGPU IP/ring/buffer function tables.

Important APIs/types/functions: major functions include `sdma_v2_4_init_microcode()`, `sdma_v2_4_free_microcode()`, `sdma_v2_4_init_golden_registers()`, ring pointer and packet emitters (`ring_get_rptr`, `ring_get_wptr`, `ring_set_wptr`, `ring_insert_nop`, `ring_emit_ib`, `ring_emit_hdp_flush`, `ring_emit_fence`, `ring_emit_pipeline_sync`, `ring_emit_vm_flush`, `ring_emit_wreg`, `ring_pad_ib`), lifecycle callbacks (`early_init`, `sw_init`, `hw_init`, `hw_fini`, `suspend`, `resume`, `is_idle`, `wait_for_idle`, `soft_reset`), IRQ handlers, VM PTE functions, and buffer copy/fill functions. Exported state is `const struct amdgpu_ip_block_version sdma_v2_4_ip_block`.

Control flow: early init sets two SDMA instances, loads `topaz_sdma.bin` and `topaz_sdma1.bin`, records firmware/feature versions, handles SMU firmware-load bookkeeping, and installs ring/buffer/VM/IRQ callbacks. SW init registers trap and illegal-instruction IRQ IDs and creates one graphics ring per instance. HW init programs golden registers then starts engines by halting, programming ring base/size/readback/writeback/IB registers, enabling RB/IB, unhalting, and running ring tests. Packet emitters write SDMA-specific headers and operands for indirect buffers, fences plus trap interrupts, HDP flush polling, VM TLB flush waits, PTE copy/write/generate operations, and TTM copy/fill operations.

State and persistence behavior: persistent driver state includes per-instance firmware handles, firmware and feature versions, `burst_nop`, ring objects, ring write/read pointers, IRQ source state, buffer-function pointers, and VM PTE scheduler hooks. Hardware state includes SDMA halt bits, ring base and pointer registers, IB control, tiling config, trap enable bits, and SRBM soft reset bits. No compute RLC queues are implemented; related resume/stop paths are TODO/no-op.

Dependencies and integration points: depends on Linux firmware/module/delay APIs, AMDGPU ring/IB/fence/IRQ/GMC/MMAN/firmware helpers, VI register headers, `iceland_sdma_pkt_open.h` packet macros, and VISLANDS interrupt source IDs. It is selected by AMDGPU discovery as an `AMD_IP_BLOCK_TYPE_SDMA` implementation and supplies TTM buffer movement through `adev->mman.buffer_funcs`.

Risks and test signals: risks include firmware request failure, endian handling, ring pointer dword/byte conversion, IB 8-dword alignment, burst NOP count encoding, incomplete RLC compute queue support, soft reset using a reused `tmp` value for SDMA1 busy detection, IRQ ring_id decoding, illegal-instruction scheduler faults, and buffer copy/fill maximum-size limits. Test signals include firmware load for both instances, golden-register programming on Topaz, `amdgpu_ring_test_helper()`, direct ring write test, IB test writing `0xDEADBEEF`, VM PTE update tests, TTM copy/fill correctness, HDP/TLB flush ordering, trap IRQ fence processing for both instances, illegal-instruction fault injection, suspend/resume, idle wait, and soft reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v2_4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v2_4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v2_4.h

Purpose: exposes the SDMA v2.4 IP block descriptor to AMDGPU discovery and device initialization code.

Important APIs/types/functions: declares `extern const struct amdgpu_ip_block_version sdma_v2_4_ip_block;`.

Control flow: no direct flow. Discovery code references the descriptor and the AMDGPU IP framework calls the function table stored in the implementation.

State and persistence behavior: no state in the header. The descriptor in `sdma_v2_4.c` persists for the module lifetime and identifies block type, version, and callbacks.

Dependencies and integration points: included by AMDGPU discovery/setup code that adds the SDMA v2.4 IP block for supported ASICs.

Risks and test signals: risks are missing declaration or mismatch with the implementation symbol. Test signals are successful builds and SDMA v2.4 block registration during device discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v2_4.h -->
