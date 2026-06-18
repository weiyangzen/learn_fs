# subset-b-001346 research

This grouped report covers AMDGPU JPEG 5.x decode IP support, LSDMA 6/7 PIO helpers, MCA 3.0 RAS block descriptors, MES user-mode queue plumbing, and MES 11/12 scheduler IP bring-up. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_1.c

Purpose: implements AMDGPU JPEG IP block version 5.0.1 for VCN 5.0 based hardware. It wires the IP block lifecycle, ten decode rings per JPEG instance, interrupt routing, SR-IOV MMSCH initialization, per-ring reset, register dump coverage, and JPEG RAS/ACA poison handling into the common `amdgpu_jpeg` framework.

Important APIs and functions: `jpeg_v5_0_1_early_init()` validates `adev->jpeg.num_jpeg_inst`, sets `adev->jpeg.num_jpeg_rings = AMDGPU_MAX_JPEG_RINGS`, and installs ring, IRQ, and RAS callbacks. `jpeg_v5_0_1_sw_init()` registers JPEG trap source IDs plus DJPEG/EJPEG poison IRQs, calls `amdgpu_jpeg_sw_init()` and `amdgpu_jpeg_resume()`, initializes each `ring_dec[j]`, sets VM hub and doorbell indexing, initializes register dump support, and exposes reset masks through sysfs. `jpeg_v5_0_1_hw_init()` either delegates SR-IOV startup to `jpeg_v5_0_1_start_sriov()` or programs host-side doorbell ranges and ring tests. The exported `jpeg_v5_0_1_ip_block` binds these callbacks to AMD IP block dispatch.

Control flow: normal startup is early init, software init, firmware resume, ring object setup, hardware init, optional RRMT capability detection, doorbell programming, and `amdgpu_ring_test_helper()` per ring. Power ungating calls `jpeg_v5_0_1_start()`, which initializes each JPEG instance with static PG mode, global tiling config from `adev->gfx.config.gb_addr_config`, JMI enablement, JRBC interrupt enablement, ring buffer BARs, rptr/wptr reset, and ring size. Power gating calls `jpeg_v5_0_1_stop()` to reset JMI and restore the anti-hang mechanism. Suspend and resume wrap HW fini/init around common JPEG firmware suspend/resume.

State and persistence behavior: persistent device state lives in `adev->jpeg`, per-instance `adev->jpeg.inst[i]`, `ring_dec[j]`, the writeback slot used for doorbell wptr mirroring, and hardware JRBC/JMI/JPEG registers. Ring base addresses and sizes persist in JRBC registers until the block is stopped or reset. `adev->jpeg.cur_state` tracks PG state. `adev->jpeg.supported_reset` is seeded from soft/full reset capability and, outside SR-IOV, includes `AMDGPU_RESET_TYPE_PER_QUEUE`. RAS state is attached through `adev->jpeg.ras` and ACA bindings.

Dependencies and integration points: depends on SOC15 register access macros, VCN 5.0 offsets and IRQ source IDs, `jpeg_v4_0_3` command emission helpers, `mmsch_v5_0` SR-IOV table definitions, the NBIO doorbell range callback, `amdgpu_ring_init()`, `amdgpu_irq_add_id()`, `amdgpu_fence_process()`, `amdgpu_jpeg_*` common helpers, RAS core APIs, and ACA bank parsing helpers. Interrupt processing maps `entry->node_id` through `node_id_to_phys_map` and then locates a matching JPEG AID.

Risks and edge cases: `jpeg_v5_0_1_is_idle()` initializes `ret` to false and then ANDs status into it, so it cannot report idle as true; `wait_for_idle()` similarly initializes `ret` to zero and ANDs wait results, which can mask nonzero wait failures. Doorbell indexing differs between PF and SR-IOV VF paths and depends on `GET_INST(JPEG, i)` and `num_inst_per_aid` being correct. SR-IOV MMSCH setup reuses one init table and has delicate size/offset bookkeeping. RAS IRQ setup is stored on `adev->jpeg.inst` rather than per indexed instance. Per-ring reset takes the VCN instance reset mutex because VCN reset affects JPEG as well.

Test signals: successful probe should create ten decode rings per JPEG instance with names `jpeg_dec_<aid>.<ring>`, pass ring tests on bare metal, and mark rings ready after SR-IOV MMSCH setup. Useful tests include trap IRQ fence processing for all ten source IDs, reset sysfs mask reporting per-queue reset only outside SR-IOV, per-ring reset after a timed-out fence, suspend/resume with `idle_work` cancelled, RAS poison IRQ registration and ACA decoding, register dump coverage for all JRBC registers, and negative tests for unknown `entry->node_id`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_1.h

Purpose: declares the JPEG 5.0.1 IP block descriptor and local register constants used by `jpeg_v5_0_1.c` for JRBC ring registers, JMI stall/drop registers, core reset control, RRMT capability detection, and RAS sub-block selection.

Important APIs and types: exports `jpeg_v5_0_1_ip_block` for the AMDGPU IP discovery table. The `regUVD_JRBC*` constants provide per-ring RB write pointer, read pointer, and status offsets plus base-index metadata for ten JRBC rings. `regUVD_JMI0_*`, `regJPEG_CORE_RST_CTRL`, and `regVCN_RRMT_CNTL` support per-core stall/reset and capability probing. `enum amdgpu_jpeg_v5_0_1_sub_block` identifies `JPEG0`, `JPEG1`, and the maximum sub-block count for poison status queries.

Control flow and integration: this header has no executable control flow. It is included by the implementation so SOC15 helper macros can resolve local IP-version register names not provided by generated headers. The enum values are consumed by the RAS poison query loop.

State and persistence behavior: no runtime state is allocated here. The constants fix the ABI between driver code and hardware register layout; any mismatch persists as incorrect MMIO access in the implementation.

Dependencies: relies on the surrounding AMDGPU build including definitions for `struct amdgpu_ip_block_version`. The register naming follows generated AMD register-header conventions, allowing use in `SOC15_REG_ENTRY_STR`, `SOC15_REG_OFFSET`, and offset access macros.

Risks and test signals: risks are register-offset drift, incorrect base-index pairing, and sub-block enum mismatch with hardware poison status registers. Compile coverage of `jpeg_v5_0_1.c`, successful register dump initialization, ring rptr/wptr access for all ten rings, and poison status reads from both sub-blocks are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.c

Purpose: implements AMDGPU JPEG IP block version 5.0.2. It is a close variant of v5.0.1 for ten-ring JPEG decode support, but without active RAS registration and without the SR-IOV MMSCH startup path in this file.

Important APIs and functions: `jpeg_v5_0_2_early_init()` validates the JPEG instance count, sets ten rings, and installs ring and IRQ functions. `jpeg_v5_0_2_sw_init()` registers ten JPEG trap source IDs, initializes common JPEG software/firmware state, creates ring objects, records internal and external pitch-register addresses, initializes register-dump support, and publishes reset masks. `jpeg_v5_0_2_hw_init()` checks RRMT capability, disables the JPEG tile anti-hang bit, optionally configures doorbells, and runs ring tests. `jpeg_v5_0_2_ip_block` exports the AMD IP callbacks.

Control flow: the ungate path uses `jpeg_v5_0_2_start()` to initialize each hardware instance and JRBC ring. Ring initialization enables the appropriate JRBC interrupt bit, programs VMID zero, ring BAR low/high, rptr/wptr zero, RB control, and RB size. Gate/fini calls reset JMI, re-enable anti-hang, and cancel idle work. Interrupt handling maps an IH node to a physical JPEG AID and dispatches each VCN JPEG source ID to the corresponding decode ring fence driver.

State and persistence behavior: runtime state is in `adev->jpeg`, ring objects, doorbell or MMIO write pointers, JPEG current PG state, and programmed JRBC/JMI registers. Unlike v5.0.1, `ring->use_doorbell` is set false in software init despite doorbell indexes being calculated, so MMIO write-pointer commits are expected. `adev->jpeg.supported_reset` always includes per-queue reset after the soft/full reset mask is computed.

Dependencies and integration points: uses common AMDGPU JPEG helpers, SOC15/VCN register macros, `jpeg_v4_0_3` ring packet emitters, AMDGPU ring/fence/IRQ infrastructure, `node_id_to_phys_map`, and register dump support. The ring funcs omit `.parse_cs`, unlike v5.0.1 and v5.3.0, which is a visible integration difference.

Risks and edge cases: idle and wait helpers share the same false/zero initial aggregate issue as v5.0.1. The `hw_fini()` body has odd indentation but functionally gates when `cur_state` is not gate. Disabled `#if 0` ACA/RAS code suggests poison handling is not wired despite similar hardware error-code knowledge. Reset helper does not take the VCN reset mutex used in v5.0.1. Always advertising per-queue reset may be wrong if firmware or platform support is incomplete.

Test signals: probe should create ten rings per JPEG instance, register all ten trap IRQ IDs, pass ring tests, and expose reset masks. Exercise MMIO write-pointer mode, interrupt-to-ring mapping for each source ID, per-ring stall/drop/core reset, suspend/resume, register dump output, RRMT capability flagging, and reset recovery after a timed-out fence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.h

Purpose: declares the JPEG 5.0.2 IP block descriptor and local register offsets used by the implementation for ten JRBC decode rings, JMI reset/stall/drop control, core reset, RRMT probing, and JPEG sub-block IDs.

Important APIs and types: exports `jpeg_v5_0_2_ip_block`. Defines `regUVD_JRBC0` through `regUVD_JRBC9` rptr/wptr/status offsets, scratch and external MCM offsets, JMI clean/stall/drop offsets, `regJPEG_CORE_RST_CTRL`, and `regVCN_RRMT_CNTL`. `enum amdgpu_jpeg_v5_0_2_sub_block` mirrors the two JPEG RAS sub-blocks even though the active v5.0.2 implementation has ACA/RAS support disabled under `#if 0`.

Control flow and integration: no executable logic. The constants are consumed by ring setup, ring pointer accessors, register dump setup, and reset code in `jpeg_v5_0_2.c`.

State and persistence behavior: the file stores no state; it defines the hardware address contract. Incorrect values would persist as incorrect ring pointer, status, or reset MMIO programming.

Dependencies: follows AMDGPU register macro conventions and requires `struct amdgpu_ip_block_version` from AMDGPU headers. The implementation pairs these defines with generated `vcn_5_0_0_*` headers.

Risks and test signals: risks include copy-forward offset mismatch from v5.0.1 and unused RAS enum drift. Compile success, ring rptr/wptr/status access on all ten rings, register dump inclusion, core reset behavior, and RRMT capability reads validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.c

Purpose: implements JPEG IP block version 5.3.0 for a single JPEG decode instance and ring. It provides normal and dynamic power-gating startup paths, clock-gating controls, ring setup, interrupt processing, and reset integration with the common AMDGPU JPEG ring command helpers.

Important APIs and functions: `jpeg_v5_3_0_early_init()` forces one JPEG instance and one ring, then installs ring and IRQ funcs. `jpeg_v5_3_0_sw_init()` registers the JPEG trap IRQ, initializes common JPEG software/firmware, creates the single decode ring with a doorbell, records pitch register mappings, and initializes reset-mask sysfs. `jpeg_v5_3_0_start()`, `jpeg_v5_3_0_stop()`, `jpeg_v5_3_0_start_dpg_mode()`, and `jpeg_v5_3_0_stop_dpg_mode()` own power and ring programming. `jpeg_v5_3_0_ip_block` exports the AMD IP callbacks.

Control flow: hardware init programs the VCN doorbell range, skips ring testing when JPEG DPG is enabled because pause-DPG is not implemented, and otherwise tests the ring. Non-DPG start enables DPM JPEG clocks, disables power gating, disables clock gating, programs tiling, enables JMI and JRBC interrupts, configures doorbell control, programs the ring base/rptr/wptr/size, and reads back wptr. DPG start enables power gating, sets `JPEG_PG_MODE`, optionally writes DPG SRAM commands and asks PSP to update SRAM, then programs the same JRBC ring registers. Stop reverses DPG mode or resets JMI, enables clock gating, enables power gating, and disables DPM JPEG clocks.

State and persistence behavior: persistent state is in `adev->jpeg.cur_state`, `adev->jpeg.inst[0]`, the decode ring, the ring writeback pointer, DPG SRAM cursor when indirect SRAM is used, and JPEG power/clock/JRBC registers. The ring uses doorbell write pointers via `ring->wptr_cpu_addr` and `WDOORBELL32`. Reset is stop/start based rather than per-core stall/drop.

Dependencies and integration points: depends on VCN 5.3 generated offsets/masks, SOC15 and SOC24 JPEG DPG access macros, PSP SRAM update helpers, DPM JPEG enablement, common JPEG helpers, `jpeg_v4_0_3` packet emitters, and AMDGPU ring/IRQ infrastructure. The ring funcs include `amdgpu_jpeg_dec_parse_cs` and standard JPEG IB/fence/vm-flush emitters.

Risks and edge cases: DPG mode skips ring tests, reducing startup validation. `hw_fini()` only gates if `cur_state` is ungated and the JRBC status register is nonzero. Reset returns early on stop/start failure without calling `amdgpu_ring_reset_helper_end()`, which can leave helper state incomplete. The header guard comment names v5.0.0, a cosmetic but confusing mismatch. Power-gating waits depend on DLDO status bits and `pg_flags` correctness.

Test signals: validate single-ring creation, doorbell programming, normal and DPG start/stop, DPM JPEG toggling, ring test when DPG is disabled, interrupt fence processing for `VCN_5_0__SRCID__JPEG_DECODE`, reset after a timed-out fence, clock-gating enable refusal while not idle, PSP SRAM update on indirect DPG, and suspend/resume through power-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.h

Purpose: provides small JPEG 5.3.0-specific register constants for DPG SRAM programming and exports the `jpeg_v5_3_0_ip_block` descriptor.

Important APIs and constants: defines DPG-space register IDs for JPEG clock-gating gate/control, system interrupt enable, no-op command, and GFX10 address configuration. The implementation uses these with `ADD_SOC24_JPEG_TO_DPG_SRAM()` and `WREG32_SOC24_JPEG_DPG_MODE()` during dynamic power-gating startup. It also declares `extern const struct amdgpu_ip_block_version jpeg_v5_3_0_ip_block`.

Control flow and integration: no executable logic. Constants bridge normal generated SOC15 register names and the SOC24 JPEG DPG programming path.

State and persistence behavior: no state is stored. DPG SRAM and hardware registers are mutated by the `.c` file using these constants.

Dependencies: requires AMDGPU IP block declarations and the JPEG/VCN DPG helper macros available in the implementation context.

Risks and test signals: risks include DPG address mismatch causing PSP SRAM updates to program the wrong register and the closing include-guard comment incorrectly referring to `__JPEG_V5_0_0_H__`. Test by entering DPG mode, verifying clock-gating and interrupt DPG writes take effect, and compiling `jpeg_v5_3_0.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.c

Purpose: implements LSDMA 6.0 PIO helper functions for synchronous memory copy, constant fill, and memory power-gating updates. The exported function table lets common AMDGPU LSDMA code issue low-speed DMA PIO operations through IP-version-specific registers.

Important APIs and functions: `lsdma_v6_0_wait_pio_status()` polls `regLSDMA_PIO_STATUS` until both idle and FIFO-empty bits are set. `lsdma_v6_0_copy_mem()` writes source and destination addresses, clears PIO control, sets `BYTE_COUNT`, source/destination location, increment, overlap, and constant-fill fields, then waits for completion. `lsdma_v6_0_fill_mem()` programs fill data and destination address, sets `CONSTANT_FILL`, and waits. `lsdma_v6_0_update_memory_power_gating()` toggles `MEM_POWER_CTRL_EN`. `lsdma_v6_0_funcs` exports these callbacks.

Control flow: copy/fill operations are immediate and synchronous. They program registers directly, issue the command by writing `regLSDMA_PIO_COMMAND`, poll for completion through `amdgpu_lsdma_wait_for()`, and log an error on timeout/failure.

State and persistence behavior: no software state is retained in this file. Hardware state persists in PIO source/destination/data/control/command/status registers and in `regLSDMA_MEM_POWER_CTRL`. The power-gating helper explicitly clears then sets the enable field to force a transition.

Dependencies and integration points: depends on SOC15 LSDMA 6.0 generated offsets/masks, `amdgpu_lsdma_wait_for()`, AMDGPU MMIO helpers, and `struct amdgpu_lsdma_funcs`. Callers are expected to serialize operations if the PIO engine is shared.

Risks and edge cases: `size` is `uint64_t` but is assigned into the hardware `BYTE_COUNT` field, so oversized requests may truncate. The code assumes address increment fields of zero are the desired hardware encoding. There is no explicit pre-wait for idle before programming a new operation beyond the post-command wait. Memory power-gating updates are not protected by a local lock.

Test signals: issue small and maximum-sized copy/fill operations, verify destination contents, exercise timeout handling by forcing the status poll to fail, check register field encodings against LSDMA 6.0 docs, and validate memory power-gating toggles around suspend or low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.h

Purpose: declares the LSDMA 6.0 function table used by AMDGPU common LSDMA code.

Important APIs: includes `soc15_common.h` and exports `extern const struct amdgpu_lsdma_funcs lsdma_v6_0_funcs`.

Control flow and state: no executable logic and no runtime state. It is a build-time integration point connecting ASIC/IP discovery to the version-specific callbacks in `lsdma_v6_0.c`.

Dependencies and integration points: requires the common SOC15 and AMDGPU LSDMA type declarations to be visible to includers. Consumers assign the exported table to an AMDGPU device or IP-version dispatch path.

Risks and test signals: risk is limited to declaration drift from the implementation or missing includes for `struct amdgpu_lsdma_funcs`. Compile/link coverage and runtime invocation of copy/fill/power-gating callbacks validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.c

Purpose: implements LSDMA 7.0 PIO copy/fill and memory power-gating callbacks. The code mirrors v6.0 behavior against the 7.0 register namespace.

Important APIs and functions: `lsdma_v7_0_wait_pio_status()` polls idle and FIFO-empty status. `lsdma_v7_0_copy_mem()` writes source/destination address registers and command fields including `BYTE_COUNT`, location, increment, overlap, and `CONSTANT_FILL = 0`. `lsdma_v7_0_fill_mem()` writes constant-fill data and destination address with `CONSTANT_FILL = 1`. `lsdma_v7_0_update_memory_power_gating()` toggles `MEM_POWER_CTRL_EN`. `lsdma_v7_0_funcs` exports the callback table.

Control flow: operations are synchronous direct-MMIO sequences. Each request programs registers, writes `regLSDMA_PIO_COMMAND`, waits through the shared LSDMA poll helper, and logs a device error if the poll fails.

State and persistence behavior: no local software state. Operation parameters persist only in LSDMA PIO registers; memory power-gating state persists in `regLSDMA_MEM_POWER_CTRL`.

Dependencies and integration points: depends on `lsdma_7_0_0_offset.h`, `lsdma_7_0_0_sh_mask.h`, SOC15 register macros, and common `amdgpu_lsdma` interfaces. It is selected by hardware/IP version and called through `struct amdgpu_lsdma_funcs`.

Risks and edge cases: size truncation into `BYTE_COUNT`, no local serialization, no explicit idle wait before command programming, and reliance on v7.0 field encodings matching v6.0 semantics. Power-gating toggles may race with active PIO if callers do not order them.

Test signals: memory copy/fill correctness, poll timeout logging, successful use on v7.0 hardware, and low-power transitions that call `update_memory_power_gating()` without breaking later PIO operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.h

Purpose: declares the LSDMA 7.0 callback table.

Important APIs: includes `soc15_common.h` and exports `extern const struct amdgpu_lsdma_funcs lsdma_v7_0_funcs`.

Control flow and state: no executable control flow or storage; this is a header-level integration contract.

Dependencies and integration points: requires AMDGPU LSDMA type definitions from common headers. ASIC/IP setup code includes this header to bind v7.0 LSDMA operations.

Risks and test signals: declaration mismatch or missing type visibility would fail compile/link. Runtime validation is through successful invocation of v7.0 copy/fill and memory power-gating callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c

Purpose: implements LSDMA 7.1 PIO copy and constant-fill callbacks. Compared with v6.0/v7.0, the v7.1 command format uses `COUNT`, `RAW_WAIT`, and `CONSTANT_FILL` fields and does not expose a memory power-gating callback in its function table.

Important APIs and functions: `lsdma_v7_1_wait_pio_status()` polls idle and FIFO-empty status. `lsdma_v7_1_copy_mem()` programs source/destination addresses, clears PIO control, sets command `COUNT`, clears `RAW_WAIT`, clears `CONSTANT_FILL`, and waits. `lsdma_v7_1_fill_mem()` writes constant data, destination address, command `COUNT`, clears `RAW_WAIT`, sets `CONSTANT_FILL`, and waits. `lsdma_v7_1_funcs` exports copy and fill only.

Control flow: copy and fill are synchronous MMIO command sequences that complete only after `amdgpu_lsdma_wait_for()` observes idle and FIFO-empty status. Errors are reported with `dev_err()`.

State and persistence behavior: this file keeps no software state. The active request is represented by LSDMA PIO address, control, command, constant-fill, and status registers.

Dependencies and integration points: depends on generated LSDMA 7.1 offsets/masks, SOC15 register helpers, and common AMDGPU LSDMA polling/type definitions. The absence of `update_memory_power_gating` must be tolerated by common callers.

Risks and edge cases: size truncation into the hardware `COUNT` field, caller serialization requirements, no pre-command idle check, and behavior changes from v7.0 field names/semantics. Common code must not assume the memory power-gating callback exists.

Test signals: copy and fill data integrity, status polling on v7.1 hardware, timeout/error path coverage, and common LSDMA code safely handling a function table without memory power-gating support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.h

Purpose: declares the LSDMA 7.1 callback table.

Important APIs: includes `soc15_common.h` and exports `extern const struct amdgpu_lsdma_funcs lsdma_v7_1_funcs`.

Control flow and state: none; the header only publishes the function-table symbol.

Dependencies and integration points: used by AMDGPU IP/ASIC setup paths that select LSDMA 7.1 behavior. Requires common AMDGPU LSDMA type declarations.

Risks and test signals: compile/link errors catch declaration drift. Runtime signal is successful copy/fill dispatch through the v7.1 table, with callers tolerating the missing memory power-gating member.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.c

Purpose: defines MCA v3.0 RAS block descriptors for MP0, MP1, and MPIO machine-check banks. It supplies count-query callbacks that delegate to common MCA logic with block-specific SMN status-register addresses.

Important APIs and functions: `mca_v3_0_mp0_query_ras_error_count()`, `mca_v3_0_mp1_query_ras_error_count()`, and `mca_v3_0_mpio_query_ras_error_count()` call `amdgpu_mca_query_ras_error_count()` with `smnMCMP0_STATUST0`, `smnMCMP1_STATUST0`, or `smnMCMPIO_STATUST0`. `mca_v3_0_ras_block_match()` validates that an `amdgpu_ras_block_object` matches the requested RAS block and sub-block index. The exported `mca_v3_0_mp0_ras`, `mca_v3_0_mp1_ras`, and `mca_v3_0_mpio_ras` objects provide `ras_block.hw_ops` and the match callback.

Control flow: AMDGPU RAS registration code attaches one of the exported block objects. Later RAS queries call the relevant `query_ras_error_count` callback, which reads MCA count state through the shared MCA helper. Address queries are not implemented and are set to NULL.

State and persistence behavior: no dynamic state is allocated here. Persistent hardware state is in MCA SMN status registers. The exported RAS block structures are global descriptors whose function pointers remain constant.

Dependencies and integration points: depends on `amdgpu_ras.h`, `amdgpu_mca.h`, `struct amdgpu_mca_ras_block`, and the common RAS object matching contract. It integrates with ASIC-specific RAS setup that picks MP0/MP1/MPIO blocks.

Risks and edge cases: only count queries are supported, so address reporting is unavailable. Hard-coded SMN addresses must match MCA v3.0 hardware. `mca_v3_0_ras_block_match()` rejects null and exact block/sub-block mismatches but does no broader compatibility checks.

Test signals: RAS block registration for MP0, MP1, and MPIO, correct CE/UE count reporting from each SMN address, expected failure for mismatched sub-block index, and no calls to NULL address-query hooks in paths that require address details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.h

Purpose: declares the MCA v3.0 MP0, MP1, and MPIO RAS block descriptors for use by AMDGPU RAS setup code.

Important APIs: exports `extern struct amdgpu_mca_ras_block mca_v3_0_mp0_ras`, `mca_v3_0_mp1_ras`, and `mca_v3_0_mpio_ras`.

Control flow and state: no executable logic or allocation. The declarations expose global descriptor instances implemented in `mca_v3_0.c`.

Dependencies and integration points: requires includers to know `struct amdgpu_mca_ras_block`, normally through AMDGPU MCA/RAS headers. ASIC initialization uses these symbols to attach the correct hardware ops.

Risks and test signals: risks are missing type declarations in includers or symbol drift. Compile/link and successful RAS block registration for all three MCA domains validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_userqueue.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_userqueue.c

Purpose: implements the AMDGPU user-mode queue backend that maps user queues into MES. It creates MQD and firmware context BOs, validates user-provided queue-side virtual addresses, pins the write-pointer BO into GART, sends MES add/remove/suspend/resume commands, and marks hung user queues during MES detect/reset.

Important APIs and functions: `mes_userq_mqd_create()` allocates an MQD BO, copies and validates user MQD inputs for compute, graphics, or SDMA queues, calls the hardware MQD initializer, allocates process/gang context space, and creates a WPTR mapping. `mes_userq_map()` fills `mes_add_queue_input` with process VA range, PASID, queue type, MQD address, wptr address, doorbell, page-table base, process/gang context addresses, and priority. `mes_userq_unmap()` sends `mes_remove_queue_input`. `mes_userq_detect_and_reset()` calls common MES hung-queue detection/reset and marks matching `amdgpu_usermode_queue` objects hung. `mes_userq_preempt()` and `mes_userq_restore()` suspend/resume a gang through MES. `userq_mes_funcs` exports the backend.

Control flow: queue creation validates user ABI first, then creates kernel-owned GPU objects. For compute queues it validates EOP VA; for GFX it obtains shadow/CSA sizes and validates shadow and CSA VAs; for SDMA it validates CSA VA. Mapping is serialized by `amdgpu_mes_lock()`, then MES firmware owns scheduling. Preempt allocates a writeback fence, sends `suspend_gang`, waits up to 2100 ms for the fence value, and frees the writeback slot. Restore refuses hung queues and resumes only preempted queues.

State and persistence behavior: persistent per-queue state includes `queue->mqd`, `queue->fw_obj`, `queue->wptr_obj`, `queue->userq_prop`, `queue->doorbell_index`, state flags, and fence-driver GPU addresses. `mes_userq_create_wptr_mapping()` stores a BO reference in `wptr_obj->obj`, pins it in GTT, binds it to GART, and records `wptr_obj.gpu_addr`. MES firmware persists process/gang context in the allocated context BO.

Dependencies and integration points: depends on DRM exec locking, AMDGPU VM mappings, BO reservation/pinning/GART binding, userqueue object helpers, userqueue fence driver, `adev->mqds[queue_type]`, GFX shadow-info callbacks, MES function table, xarray `adev->userq_doorbell_xa`, DRM wedge notification, and PASID/page-table state from `queue->vm`.

Risks and edge cases: WPTR mapping rejects BOs larger than one page and pins instead of using an eviction fence, which is called out as TODO. If `amdgpu_ttm_alloc_gart()` fails after pinning, the failure path unrefs the BO but does not visibly unpin it in this function. `memdup_user()` failures are collapsed to `-ENOMEM` instead of preserving `PTR_ERR()`. Hung queue detection uses a fixed local `db_array[8]` and depends on the MES-reported array size. Preempt uses a busy microsecond loop and must not be called from an inappropriate context.

Test signals: create/map/unmap for compute, graphics, and SDMA user queues; invalid MQD size and invalid VA rejection; WPTR BO mapping, pinning, and GART address correctness; priority conversion; suspend fence completion and timeout; restore refusal for hung queues; detect/reset marking only matching doorbells and queue types; forced userqueue fence completion and DRM wedged event on detected hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_userqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_userqueue.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_userqueue.h

Purpose: declares the MES-backed userqueue function table.

Important APIs: includes `amdgpu_userq.h` and exports `extern const struct amdgpu_userq_funcs userq_mes_funcs`.

Control flow and state: no logic or state. The exported table is implemented in `mes_userqueue.c` and selected by userqueue manager setup when MES is the backend.

Dependencies and integration points: requires common userqueue type definitions. The function table provides MQD create/destroy, map/unmap, detect/reset, preempt, and restore hooks to generic userqueue code.

Risks and test signals: risks are declaration/implementation drift or backend selection without MES support. Compile/link and successful user queue lifecycle through `userq_mes_funcs` validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_userqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c

Purpose: implements the MES 11.0 AMDGPU IP block, including firmware loading, MES scheduler and optional KIQ pipes, scheduler packet submission, hardware queue add/remove/reset, legacy queue mapping, gang suspend/resume, hung queue detection, scheduler resource setup, and ring/MQD initialization.

Important APIs and functions: `mes_v11_0_submit_pkt_and_poll_completion()` writes a scheduler API packet plus a query-status packet to the MES ring, uses writeback memory for API completion, and polls the ring fence and API fence. `mes_v11_0_add_hw_queue()`, `remove_hw_queue()`, `map_legacy_queue()`, `unmap_legacy_queue()`, `suspend_gang()`, `resume_gang()`, `reset_hw_queue()`, and `detect_and_reset_hung_queues()` implement `amdgpu_mes_funcs`. `mes_v11_0_load_microcode()`, `mes_v11_0_enable()`, `mes_v11_0_queue_init()`, and `mes_v11_0_hw_init()` own firmware and hardware bring-up. `mes_v11_0_ip_block` exports the IP callbacks.

Control flow: early init sets hung-queue array metadata and loads MES microcode metadata for enabled pipes. Software init assigns MES callbacks, initializes common MES state, allocates EOP buffers, MQD BOs/backups, optional KIQ ring, scheduler ring, and the resource_1 BO. Hardware init loads direct firmware if needed, enables MES pipes, initializes the scheduler ring through KIQ mapping, sends `SET_HW_RSRC`, optionally sends `SET_HW_RSRC_1` for firmware rev >= 0x52, queries scheduler status, updates enforce-isolation config, then marks the MES ring ready and KIQ ring not ready for driver use.

State and persistence behavior: persistent state is in `adev->mes` firmware pointers, ucode/data BOs, EOP BOs, MQD BOs, scheduler context buffers, query-status fences, resource_1 buffer, event log, ring read/write pointers, and version fields. Hardware state is in CP_MES control/cache/program-counter registers, HQD/MQD registers, RLC scheduler selection, doorbell controls, and queue reset registers. `enable_legacy_queue_map` is enabled only for scheduler firmware rev >= 0x47.

Dependencies and integration points: depends on GC 11 register headers, `v11_compute_mqd`, `mes_v11_api_def` packet layouts, common MES initialization/finalization, KIQ packet functions, SOC21 GRBM selection, GFX RLC safe mode, SRBM/GRBM mutexes, ring/fence/writeback helpers, firmware loading, and AMDGPU isolation policy. Queue type and priority conversion bridge AMDGPU enums to MES API enums.

Risks and edge cases: packet submission uses polling with long timeouts and can halt forever when `halt_if_hws_hang` is set. Queue reset via MMIO must correctly enter/exit RLC safe mode and restore GRBM selection. Firmware-version gates change wptr address selection, remove-after-reset support, legacy mapping, and resource_1 behavior. `mes_v11_0_hw_fini()` is a no-op, so shutdown is mostly handled by KIQ fini or later teardown. `mes_v11_0_mqd_sw_init()` returns `-ENOMEM` if backup allocation fails after creating the MQD BO, relying on outer fini for cleanup.

Test signals: firmware load for each declared GC 11.x MES image, direct and non-direct load paths, scheduler and KIQ version reads, scheduler ring packet completion, add/remove user and KFD queues, legacy queue map/unmap, gang suspend/resume fences, MMIO reset for GFX/compute/SDMA queues, hung queue detect/reset doorbell array contents, enforce-isolation update, SR-IOV timeout behavior, and suspend/resume without leaving KIQ and MES readiness inconsistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.h

Purpose: declares the MES 11.0 IP block descriptor for AMDGPU IP discovery.

Important APIs: exports `extern const struct amdgpu_ip_block_version mes_v11_0_ip_block`.

Control flow and state: no executable logic or storage. The implementation’s `amd_ip_funcs` table is reached through this exported descriptor.

Dependencies and integration points: requires the AMDGPU IP block version type to be visible to includers. ASIC setup code uses the symbol to register MES v11.0 lifecycle callbacks.

Risks and test signals: declaration drift would fail link. Runtime validation is MES v11.0 early/sw/hw init being invoked through the IP block table and the scheduler becoming ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.c

Purpose: implements the MES 12.0 AMDGPU IP block for GC 12 hardware. It extends the MES 11 pattern with pipe-selectable packet submission, optional unified MES mode, unmapped-doorbell handling, aggregated doorbells, MES-driven PASID TLB invalidation, updated resource packets, and GC 12 queue reset mechanics.

Important APIs and functions: `mes_v12_0_submit_pkt_and_poll_completion()` is the pipe-aware scheduler packet submission helper. `mes_v12_0_add_hw_queue()`, `remove_hw_queue()`, `map_legacy_queue()`, `unmap_legacy_queue()`, `suspend_gang()`, `resume_gang()`, `reset_hw_queue()`, `invalidate_tlbs_pasid()`, and `detect_and_reset_hung_queues()` populate `mes_v12_0_funcs`. `gfx_v12_0_request_gfx_index_mutex()` arbitrates GFX index mutex access for GFX queue reset. `mes_v12_0_set_hw_resources()`, `set_hw_resources_1()`, `init_aggregated_doorbell()`, and `enable_unmapped_doorbell_handling()` program scheduler resources. `mes_v12_0_ip_block` exports IP callbacks.

Control flow: early init loads microcode metadata for both MES pipes and records hung-queue array layout. Software init enables legacy queue map, sizes event logs differently for unified MES, initializes common MES state, allocates EOP/MQD resources for both pipes, creates either a legacy KIQ ring or MES pipe rings, and allocates `resource_1` for MES-managed rings. KIQ hardware init selects the RLC scheduler queue, loads firmware or programs start addresses, enables MES, initializes the KIQ pipe, optionally sends KIQ resources for unified MES, then calls scheduler hardware init. Scheduler hardware init enables unmapped-doorbell handling, initializes the scheduler queue, sends hardware resources, optionally sends resource_1 for firmware rev >= 0x4b, programs aggregated doorbells, queries status, updates isolation, and marks MES ready.

State and persistence behavior: persistent state includes per-pipe MES rings, ring locks, firmware objects, data firmware objects, EOP BOs, MQD BOs/backups, resource_1 buffers, event log regions, scheduler/KIQ version fields, aggregated doorbell offsets, and hung-queue buffer addresses. Hardware state includes CP_MES control/program-counter/cache registers, HQD/MQD registers, RLC scheduler mapping, CP_UNMAPPED_DOORBELL, CP_MES_DOORBELL_CONTROL1-5, and queue reset registers. In unified MES mode, both pipes can be MES rings rather than one external GFX KIQ ring.

Dependencies and integration points: depends on GC 12 register headers, `v12_compute_mqd`, `mes_v12_api_def` packet layouts, common MES helpers, GFX v12 support, SOC21 GRBM selection, ring/fence/writeback helpers, firmware loader modes including direct and RLC backdoor auto, VM hub identifiers, and AMDGPU KIQ packet functions. The TLB invalidation API converts AMDGPU GFXHUB/MMHUB IDs into MES hub IDs and submits on KIQ pipe.

Risks and edge cases: `add_hw_queue()` duplicates the KFD queue-size assignment block, harmless but suspicious. `mes_v12_0_mqd_sw_init()` warns but does not fail if MQD backup allocation fails, unlike v11. Packet completion treats only the low 32 bits of the status writeback as success and leaves high bits as debug detail. Several resource_1 calls ignore return values in KIQ unified mode and for scheduler rev >= 0x4b. Unmapped doorbell handling changes `PROC_LSB` and may affect KFD doorbell interpretation. `hw_fini()` remains a no-op.

Test signals: boot GC 12 hardware in direct and RLC-backdoor firmware modes, with and without unified MES; verify both pipe versions, scheduler query completion, aggregated doorbell interrupts, unmapped doorbell behavior, queue add/remove/reset for GFX/compute/SDMA/MES queue types, legacy queue map/unmap pipe selection, PASID TLB invalidation for GFXHUB and MMHUB0 with invalid-hub rejection, hung queue detect/reset buffer format, suspend/resume readiness, and isolation limit-single-process updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.h

Purpose: declares the MES 12.0 IP block descriptor for AMDGPU IP discovery and binding.

Important APIs: exports `extern const struct amdgpu_ip_block_version mes_v12_0_ip_block`.

Control flow and state: no executable control flow or runtime state. It exposes the implementation’s IP block version object to ASIC setup code.

Dependencies and integration points: requires AMDGPU IP block type declarations from the includer context. Selected GC 12 ASIC tables use this symbol to install MES v12.0 early, software, hardware, suspend, and resume callbacks.

Risks and test signals: risks are limited to symbol/type mismatch. Compile/link coverage and successful MES v12.0 IP lifecycle invocation validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.h -->
