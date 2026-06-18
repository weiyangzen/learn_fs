# subset-b-001345 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_1.c

Purpose: implements ISP 4.1.1 hardware glue for amdgpu, including firmware declaration, ACPI platform discovery, MFD child creation, generic PM domain wiring, GPIO lookup tables for the OMNI5C10 camera path, and suspend/resume/fini hooks exposed through `struct isp_funcs`.

Important APIs and functions: `isp_v4_1_1_set_isp_funcs()` installs the static `isp_v4_1_1_funcs`; `isp_v4_1_1_hw_init()` is the main setup path; `isp_v4_1_1_hw_fini()` removes MFD devices and frees allocations; `isp_v4_1_1_hw_suspend()` and `_resume()` force runtime PM on children. PM-domain callbacks `isp_poweron()`, `isp_poweroff()`, and `isp_set_performance_state()` call SMU/DPM helpers to ungate/gate the ISP block and set high ISP XCLK/ICLK.

Control flow and state: init validates MMIO size, locates the ACPI ISP4 device, conditionally installs GPIO lookup tables for HID `OMNI5C10`, initializes `isp->ispgpd`, allocates three `mfd_cell` entries, and creates resources for ISP registers, PHY0, IRQ mappings, I2C, and GPIO. It first hotplugs capture and I2C children, adds MFD children of type `mfd_device` into the PM domain, then hotplugs the pinctrl/GPIO child outside the domain. Persistent driver state lives in `struct amdgpu_isp` allocations (`isp_cell`, `isp_res`, `isp_i2c_res`, `isp_gpio_res`, `isp_pdata`) and the generic PM domain object.

Dependencies and integration: depends on Linux MFD, GPIO lookup, PM runtime/genpd, ACPI camera discovery via `amdgpu_acpi_get_isp4_dev()`, amdgpu IRQ mapping, and SMU DPM power/clock calls. It integrates with child drivers named `amd_isp_capture`, `amd_isp_i2c_designware`, and `amdisp-pinctrl`.

Risks and test signals: init deliberately returns success when no valid ISP platform is detected, so tests should distinguish absent ISP from failed ISP setup. Failure cleanup frees allocations but does not call `pm_genpd_remove()` after `pm_genpd_init()` failure paths that occur later. The GPIO lookup tables are global side effects and are only added, not removed in fini. Test signals include successful ACPI discovery, correct IRQ mappings for all eight WPT sources, MFD child probe ordering, runtime PM suspend/resume of children, high performance state clock programming, and teardown without leaked child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_1.h

Purpose: declares the ISP 4.1.1 hardware interface used by the amdgpu ISP block and centralizes constants for memory resources, interrupt resources, and fixed register offsets.

Important APIs and types: includes `amdgpu_isp.h` and ISP IRQ source IDs, defines `MAX_ISP411_MEM_RES`, `MAX_ISP411_INT_SRC`, PHY/I2C/GPIO offsets and sizes, and declares `isp_v4_1_1_set_isp_funcs(struct amdgpu_isp *isp)`.

Control flow and state: this header has no runtime logic or persistent state. Its constants determine the resource array layout that `isp_v4_1_1.c` fills during hardware init: two memory resources followed by eight IRQ resources.

Dependencies and integration: consumed by the ISP v4.1.1 implementation and by amdgpu ISP initialization code that selects generation-specific function tables. The IRQ include ties the implementation to the ISP 4.1 interrupt source namespace.

Risks and test signals: offset or size drift would expose the wrong MMIO ranges to MFD child drivers. Tests should confirm that resource counts match allocation and loops in `isp_v4_1_1_hw_init()`, and that the declared function setter is linked into the owning amdgpu ISP IP selection path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v1_0.c

Purpose: implements JPEG v1.0 decode ring support for early VCN/JPEG hardware. It provides ring packet emission, a local command-stream parser, IRQ fence processing, software init/fini, and a start routine that programs JRBC ring base registers.

Important APIs and functions: exported generation entry points are `jpeg_v1_0_early_init()`, `jpeg_v1_0_sw_init()`, `jpeg_v1_0_sw_fini()`, and `jpeg_v1_0_start()`. Ring callbacks include get/set read/write pointers, start/end packets, fence and IB emission, VM flush/reg-wait/wreg emission, NOP insertion, and begin-use serialization with VCN v1 rings. `jpeg_v1_dec_ring_parse_cs()` validates user packet streams against the v1 register allowlist.

Control flow and state: early init sets one JPEG instance/ring and installs ring/IRQ funcs. Software init registers VCN client source ID 126, initializes a 512-DW `jpeg_dec` ring on MMHUB0, and records internal/external pitch registers. Start optionally programs the ring buffer in non-DPG mode, initializes `ring->wptr`, and patches ring memory with commands used for later submissions. Runtime progress is tracked by hardware JRBC RPTR/WPTR plus amdgpu fence sequence memory.

Dependencies and integration: depends on `amdgpu_jpeg`, `amdgpu_cs`, VCN v1 helpers, SOC15 register accessors, PACKETJ encoding, MMHUB VM flushing, and amdgpu fence/IRQ infrastructure. Begin-use coordinates with VCN v1 decode/encode rings through `vcn1_jpeg1_workaround`.

Risks and test signals: the parser walks IBs in two-DW packets and rejects unexpected resource bits, condition fields, packet types, or registers, so parser coverage is critical. Fence emission warns on 64-bit fence flags and writes duplicate sequence data through GPCOM. Begin-use waits for all VCN v1 rings, so deadlocks or false non-empty fences can block JPEG. Test signals include ring test, IB test, invalid packet rejection, trap IRQ source 126 fence completion, VM flush waits, and suspend/fini ring cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v1_0.h

Purpose: declares the public JPEG v1.0 entry points and the register allowlist constants used by the v1 command submission parser.

Important APIs and types: declares early/software init/fini and `jpeg_v1_0_start()`. Defines the legal v1 register range plus special LMI BAR, context index/data, and soft-reset registers accepted by `jpeg_v1_dec_ring_parse_cs()`.

Control flow and state: no runtime state. The constants directly shape security validation for user-provided JPEG command streams.

Dependencies and integration: included by `jpeg_v1_0.c` and indirectly tied to PACKETJ parsing macros and SOC15 JPEG register numbering.

Risks and test signals: the parser allowlist is a security boundary; incorrect constants can either reject valid UMD streams or allow writes outside the intended JPEG decode register set. Test with valid decode IBs, soft reset packets, NOPs, and malformed register/type combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.c

Purpose: implements the amdgpu IP block for JPEG v2.0, moving common lifecycle into `amdgpu_jpeg` helpers while providing v2 register programming, power/clock gating, doorbell-based ring operation, reset, IRQ, and reusable packet emission helpers.

Important APIs and functions: the exported `jpeg_v2_0_ip_block` uses `jpeg_v2_0_ip_funcs`. Public packet helpers include `jpeg_v2_0_dec_ring_emit_ib()`, `_emit_fence()`, `_emit_vm_flush()`, `_emit_wreg()`, `_emit_reg_wait()`, `_insert_start()`, `_insert_end()`, and `_nop()`, later reused by v2.5/v3/v4.0/v4.0.5. Lifecycle functions cover early/sw/hw init, fini, suspend/resume, idle wait, clockgating, powergating, and `jpeg_v2_0_ring_reset()`.

Control flow and state: sw init registers the JPEG decode IRQ, initializes shared JPEG firmware state, creates a doorbell-enabled `jpeg_dec` ring, initializes pitch register mappings, register-dump support, and reset-mask sysfs. Start enables DPM JPEG clocks, disables power gating, disables clock gating, sets tiling, JMI, interrupts, ring base/size, and `ring->wptr`. Stop reverses JMI, clock gating, power gating, and DPM. Power state is persisted in `adev->jpeg.cur_state`; ring state lives in `ring->wptr`, doorbell shadow memory, and JRBC registers.

Dependencies and integration: depends on `amdgpu_jpeg`, `amdgpu_pm`, SOC15 register helpers, VCN 2.0 offsets/masks, IRQ source `VCN_2_0__SRCID__JPEG_DECODE`, NBIO doorbell-range programming, reset mask sysfs, and amdgpu scheduler ring callbacks.

Risks and test signals: doorbell programming must match ring index `(vcn_ring0_1 << 1) + 1`; packet helper sizes in `emit_frame_size` and `emit_ib_size` must stay synchronized with emitted DW counts. Reset stops and restarts the whole block. Test signals include register dump init, sysfs reset mask, ring/IB tests, per-queue reset on bare metal, no per-queue reset on SR-IOV VF, powergating transitions, and trap interrupt fence processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.h

Purpose: provides JPEG v2 internal register offsets and declarations for packet emission helpers shared across multiple JPEG generations.

Important APIs and types: declares start/end, fence, IB, reg-wait, VM-flush, wreg, and NOP helper functions plus `jpeg_v2_0_ip_block`. Defines internal offsets for JRBC external register access, GPCOM, LMI BARs, VMID, IB size, RB condition wait, status, pitch, IH control, and `JRBC_DEC_EXTERNAL_REG_WRITE_ADDR`.

Control flow and state: no runtime state. The offsets are encoded into PACKETJ streams by `jpeg_v2_0.c` and reused by later generation ring function tables.

Dependencies and integration: included by JPEG v2.0 and many later JPEG implementations to avoid duplicating packet construction logic where hardware packet format remains compatible.

Risks and test signals: because later generations reuse these declarations, offset mistakes can break multiple IP blocks. Test by comparing emitted packets against hardware docs for each consumer generation and by running ring/IB tests on v2.0, v2.5, v3.0, v4.0, and v4.0.5 variants that reference these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.c

Purpose: implements JPEG v2.5/v2.6 IP blocks, adding up to two hardware instances, harvesting detection, per-instance doorbells, v2.6-specific start/end deepsleep packets, and RAS poison interrupt/status support.

Important APIs and functions: exports `jpeg_v2_5_ip_block` and `jpeg_v2_6_ip_block`. Main lifecycle functions are shared between the two versions. Per-instance helpers start/stop individual JPEG engines, manage clock gating, read/write ring pointers using `ring->me`, and reset a single ring by stopping/starting its instance. RAS helpers query v2.6 JPEG0/JPEG1 poison status and install `adev->jpeg.ras`.

Control flow and state: early init sets two potential instances and reads `mmCC_UVD_HARVESTING` to mark disabled engines in `adev->jpeg.harvest_config`, returning `-ENOENT` if both are harvested. SW init registers decode and poison IRQs per live instance, initializes rings named `jpeg_dec_N`, selects MMHUB based on IP version, and sets doorbell offsets `+ 8 * i`. Start/stop and idle/wait loops skip harvested instances. `cur_state` is block-wide even though operations loop instances.

Dependencies and integration: depends on VCN 2.5 offsets/masks, VCN 2.0 IRQ source IDs, shared v2.0 packet helpers, amdgpu RAS/JPEG helpers, NBIO doorbell ranges, and SOC15 register accessors.

Risks and test signals: global `cur_state` for multiple instances can obscure partial failures. `wait_for_idle()` correctly returns first wait failure; interrupt routing maps IH client VCN/VCN1 to instance 0/1. RAS poison IRQ setup is unconditional in sw init, but hw fini only puts it when RAS is supported. Test signals include harvested-instance skip behavior, two-instance decode interrupts, v2.6 deepsleep start/end packets, ring reset on one instance, RAS poison query, and sysfs reset mask creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.h

Purpose: declares JPEG v2.5/v2.6 IP block exports and the v2.6 RAS poison sub-block identifiers.

Important APIs and types: `enum amdgpu_jpeg_v2_6_sub_block` names JPEG0 and JPEG1 poison status sub-blocks; `jpeg_v2_5_ip_block` and `jpeg_v2_6_ip_block` are exported for IP discovery.

Control flow and state: no runtime logic. The enum bounds drive loops in v2.6 poison-status querying.

Dependencies and integration: consumed by `jpeg_v2_5.c` and by amdgpu IP-version tables that register the correct JPEG block.

Risks and test signals: enum ordering must match the RAS status register switch in the implementation. Test signal is successful poison query coverage for both JPEG sub-blocks and correct IP block selection for Arcturus/Aldebaran-style hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.c

Purpose: implements a single-instance JPEG v3.0 IP block that largely reuses v2.0 packet helpers while adapting power gating, clock gating, harvesting checks, tiling registers, and reset behavior for VCN 3.x hardware.

Important APIs and functions: exports `jpeg_v3_0_ip_block`. Lifecycle functions perform early/sw/hw init, fini, suspend/resume, idle/wait, clockgating, powergating, and ring reset. The ring function table reuses `jpeg_v2_0_dec_ring_*` helpers and `amdgpu_jpeg_dec_parse_cs`.

Control flow and state: early init skips harvesting checks for IP versions 3.1.1/3.1.2 but otherwise returns `-ENOENT` if JPEG is disabled. SW init registers the v2 decode IRQ source, initializes shared JPEG state, creates a doorbell ring, register dump, and reset sysfs. Start enables DPM JPEG, disables static power gating, disables CGC, sets decode and encode GFX10 tiling, enables JMI/interrupts, and programs JRBC ring registers. Stop resets JMI, gates clocks/power, and disables DPM.

Dependencies and integration: depends on VCN 3.0 register headers, shared v2.0 packet functions, amdgpu JPEG helpers, DPM, NBIO doorbell ranges, SOC15 wait/access helpers, and reset mask infrastructure.

Risks and test signals: static power gating relies on PGFSM waits and anti-hang bit sequencing. The generation uses v2 IRQ source IDs despite v3 register headers. Test signals include harvest handling per IP version, ring and IB tests, per-queue reset availability outside SR-IOV, clockgating returning `-EBUSY` when not idle, and successful register dump/sysfs reset mask setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.h

Purpose: declares the JPEG v3.0 IP block version object.

Important APIs and types: exports `jpeg_v3_0_ip_block` for amdgpu IP discovery and registration.

Control flow and state: no runtime behavior or state.

Dependencies and integration: included by IP-version selection code that wires VCN/JPEG 3.x hardware to `jpeg_v3_0.c`.

Risks and test signals: the header is minimal; the key validation is that the right ASIC/IP version selects this block and links the `jpeg_v3_0_ip_funcs` lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0.c

Purpose: implements JPEG v4.0 for a single instance, including normal bare-metal startup, SR-IOV VF startup through MMSCH command tables, RAS poison interrupts/status, reset support, and reused v2 packet emission.

Important APIs and functions: exports `jpeg_v4_0_ip_block`; lifecycle functions cover early/sw/hw init, fini, suspend/resume, clock/power gating, idle/wait, and ring reset. `jpeg_v4_0_start_sriov()` builds an MMSCH v4 init table for VF mode. RAS helpers query JPEG0/JPEG1 poison status.

Control flow and state: sw init registers decode and poison IRQs, initializes shared JPEG state, sets the doorbell differently for SR-IOV VF, initializes the ring, RAS, register dump, and reset sysfs. HW init either sends the MMSCH init table and manually marks the scheduler ready in VF mode, or programs NBIO/VCN doorbells and runs the ring test. Power gating is bypassed for VFs by forcing `cur_state` to ungated. Bare-metal start programs static PG, CGC, tiling, JMI, JRBC interrupt enable, ring base/size, and `ring->wptr`.

Dependencies and integration: depends on VCN 4.0 offsets/masks, `mmsch_v4_0.h`, shared v2.0 packet helpers, amdgpu JPEG/RAS helpers, NBIO doorbell programming, SOC15 register access, and SR-IOV virtualization state.

Risks and test signals: MMSCH init has tight timeout/error handling and depends on the virtual MM table header layout. VF mode skips ring test and manually sets scheduler readiness, so VF coverage must include real command submission. Poison IRQ uses a separate `ras_poison_irq`. Test signals include bare-metal ring/IB tests, VF MMSCH mailbox success, powergating no-op on VF, RAS poison event processing, per-queue reset outside VF, and correct doorbell offset selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0.h

Purpose: declares JPEG v4.0 sub-block IDs used for RAS poison checks and exports the v4.0 IP block object.

Important APIs and types: `enum amdgpu_jpeg_v4_0_sub_block` identifies JPEG0 and JPEG1 RAS status sub-blocks; `jpeg_v4_0_ip_block` exposes the generation implementation.

Control flow and state: no runtime logic. The enum bounds the RAS poison-status loop in `jpeg_v4_0.c`.

Dependencies and integration: consumed by the v4.0 implementation and amdgpu IP discovery tables.

Risks and test signals: enum/register switch alignment is the main risk. Test by injecting or reading poison status for both sub-block values and verifying IP selection for JPEG 4.0.0 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_3.c

Purpose: implements JPEG v4.0.3 for multi-instance, multi-ring hardware. It adds RRMT-aware register normalization, up to eight decode rings per instance, SR-IOV MMSCH setup for multiple rings, custom packet helpers, per-core stall reset, and richer RAS/ACA error reporting.

Important APIs and functions: exports `jpeg_v4_0_3_ip_block` and packet helpers declared in the header: emit IB/fence/VM flush/HDP flush/NOP/start/end/wreg/reg-wait. Lifecycle functions initialize ring funcs, IRQ funcs, RAS funcs, rings, register dumps, sysfs reset masks, power/clock states, and suspend/resume. Reset uses `jpeg_v4_0_3_core_stall_reset()` plus `jpeg_v4_0_3_start_jrbc()` under the paired VCN reset mutex.

Control flow and state: early init sets `num_jpeg_rings` to `AMDGPU_MAX_JPEG_RINGS_4_0_3`. SW init registers one decode IRQ source per ring plus poison IRQs, initializes rings for every `adev->jpeg.num_jpeg_inst`, assigns MMHUB by AID, calculates VF and PF doorbell layouts, and stores per-ring external scratch/pitch offsets. HW init either builds per-instance MMSCH tables for VFs or detects RRMT, programs NBIO/VCN doorbells, and ring-tests every ring. Runtime state spans `ring->me`, `ring->pipe`, `aid_id`, writeback `wptr_offs`, `adev->jpeg.caps`, and block-wide `cur_state`.

Dependencies and integration: depends on VCN 4.0.3 register headers, `mmsch_v4_0_3.h`, SOC15 offset accessors, `node_id_to_phys_map`, amdgpu JPEG/RAS/ACA infrastructure, MMHUB IP versions, and scheduler ring callbacks.

Risks and test signals: `jpeg_v4_0_3_is_idle()` initializes `ret` to false and ANDs into it, so it appears to always return false; clockgating may therefore return `-EBUSY`. `wait_for_idle()` similarly ANDs return codes starting at zero, which can mask failures. Interrupt routing depends on node ID to physical AID mapping and per-source ring mapping. Tests should cover all ring IRQ source IDs, PF and VF doorbell layouts, RRMT and non-RRMT register normalization, per-ring reset under VCN mutex, RAS count/reset paths, ACA bank parsing, and DPG/HDP flush behavior where the JPEG HDP flush is intentionally a no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_3.h

Purpose: declares JPEG v4.0.3 internal packet offsets, RAS sub-block IDs, the IP block export, and packet helper APIs reused by v4.0.3 and newer implementations.

Important APIs and types: defines internal offsets for JRBC external register access, GPCOM, LMI BARs, VMID, IB size, status, scratch/pitch, and MCM addressing. Declares `jpeg_v4_0_3_dec_ring_emit_ib()`, `_emit_fence()`, `_emit_vm_flush()`, `_ring_emit_hdp_flush()`, `_nop()`, `_insert_start()`, `_insert_end()`, `_emit_wreg()`, and `_emit_reg_wait()`.

Control flow and state: no state. The declarations form a shared packet-emission ABI inside the driver; v5.0.0 uses several of these helpers.

Dependencies and integration: included by `jpeg_v4_0_3.c` and `jpeg_v5_0_0.c`, plus generation registration code via `jpeg_v4_0_3_ip_block`.

Risks and test signals: helper declarations make v4.0.3 offset semantics visible to later generations, so changes can regress v5.0.0 packet emission. Validate emitted packet sizes and offsets on v4.0.3 and v5.0.0 rings, especially VM flush/reg-wait normalization and fence DW counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c

Purpose: implements JPEG v4.0.5/v4.0.6 support with one or two instances, optional DPG mode programming, per-instance doorbells, v4 IRQ handling, and reuse of v2 packet helpers.

Important APIs and functions: exports `jpeg_v4_0_5_ip_block`. Early init selects one instance for UVD 4.0.5 and two for 4.0.6. DPG-specific helpers `jpeg_v4_0_5_start_dpg_mode()` and `_stop_dpg_mode()` program JPEG DPG SRAM/registers, while normal start/stop handle static power gating, CGC, JMI, interrupts, and JRBC ring setup. Ring reset restarts the whole JPEG block.

Control flow and state: sw init registers decode and poison source IDs on each live instance, initializes shared JPEG state, creates one doorbell ring per non-harvested instance, sets pitch mappings, register dumps, and reset sysfs. HW init skips ring tests when `AMD_PG_SUPPORT_JPEG_DPG` is set; otherwise it tests each live ring. Start programs NBIO/VCN doorbells for each playback, then chooses DPG or normal register programming. State includes `harvest_config`, per-ring `me`, block-wide `cur_state`, `indirect_sram`, and DPG SRAM current-address pointers.

Dependencies and integration: depends on VCN 4.0.5 register headers, `mmsch_v4_0.h`, amdgpu JPEG helpers, DPM, NBIO doorbells, SOC15 JPEG DPG write macros, PSP SRAM update helper, and shared v2.0 ring packet helpers.

Risks and test signals: poison interrupts are registered against the same IRQ object as decode, so the interrupt handler must distinguish source IDs and call `amdgpu_jpeg_process_poison_irq()`. `wait_for_idle()` returns after the first non-harvested instance, so later instances are not waited on. DPG mode currently skips ring tests, reducing boot-time validation. Test signals include UVD 4.0.5 vs 4.0.6 instance selection, harvested skips, DPG direct and indirect SRAM paths, PSP SRAM update, two-client interrupt routing, poison IRQ processing, and reset under DPG and non-DPG modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.h

Purpose: declares the JPEG v4.0.5 IP block and a single JPEG RAS sub-block enum.

Important APIs and types: `enum amdgpu_jpeg_v4_0_5_sub_block` currently contains only JPEG0 plus a max marker; `jpeg_v4_0_5_ip_block` exposes the implementation.

Control flow and state: no runtime state. The enum is not heavily used in the current v4.0.5 implementation, where poison IRQ processing is delegated to common JPEG handling.

Dependencies and integration: consumed by `jpeg_v4_0_5.c` and amdgpu IP-version selection.

Risks and test signals: the closing include-guard comment says `__JPEG_V4_0_H__`, which is cosmetic but can confuse review. Validate that IP versions 4.0.5 and 4.0.6 select this block and that future RAS code keeps enum bounds aligned with hardware sub-blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_0.c

Purpose: implements JPEG v5.0.0 for a single instance with VCN 5 register names, optional DPG mode, v5 IRQ source handling, v4.0.3 packet helper reuse, and standard amdgpu JPEG lifecycle integration.

Important APIs and functions: exports `jpeg_v5_0_0_ip_block`. Lifecycle functions initialize shared JPEG state, ring, register dump, reset sysfs, doorbell range, power/clock gating, suspend/resume, and reset. DPG helpers `jpeg_engine_5_0_0_dpg_clock_gating_mode()`, `jpeg_v5_0_0_start_dpg_mode()`, and `_stop_dpg_mode()` write SOC24 JPEG DPG registers or indirect SRAM entries.

Control flow and state: sw init registers `VCN_5_0__SRCID__JPEG_DECODE`, creates a doorbell `jpeg_dec` ring, and uses v5 register dump entries. HW init programs the doorbell range, then skips ring test when JPEG DPG is supported because pause-DPG is not implemented. Start enables DPM, chooses DPG or normal mode, configures power/clock gating, tiling, JMI, interrupts, doorbell control, and JRBC ring base/size. Ring funcs use local pointer callbacks but v4.0.3 packet emission for IB/fence/VM flush/reg wait/wreg/start/end/NOP.

Dependencies and integration: depends on VCN 5.0 register headers, v5 IRQ source IDs, `jpeg_v5_0_0.h` SOC24 DPG offsets, v4.0.3 packet helper declarations, amdgpu JPEG/DPM/reset/sysfs helpers, NBIO doorbells, PSP SRAM update helper, and SOC15/SOC24 register macros.

Risks and test signals: DPG start calls `jpeg_v5_0_0_enable_power_gating()` before enabling PG mode, which is generation-specific and should be validated on hardware. Non-DPG `disable_power_gating()` programs DLDO even without checking `AMD_PG_SUPPORT_JPEG`, unlike enable. Ring tests are skipped under DPG. Packet helpers inherited from v4.0.3 must remain compatible with v5 offsets. Test signals include v5 decode IRQ fence completion, DPG direct/indirect SRAM programming, PSP update, skipped ring test coverage through real IB submission, powergating transitions, and reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_0.h

Purpose: declares JPEG v5.0.0 DPG/SOC24 register offsets and exports the v5.0.0 IP block object.

Important APIs and types: defines DPG register offsets for JPEG CGC gate/control, system interrupt enable, no-op, and decode GFX10 address config. Exports `jpeg_v5_0_0_ip_block`.

Control flow and state: no runtime state. Constants are consumed by v5 DPG start code to write directly or to append indirect SRAM commands.

Dependencies and integration: included by `jpeg_v5_0_0.c` and amdgpu IP discovery tables.

Risks and test signals: these hard-coded offsets are critical for DPG mode. Tests should cover direct and indirect DPG register programming and confirm the offsets match VCN 5.0 hardware packet/SRAM expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_0.h -->
