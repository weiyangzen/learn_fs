# subset-b-001344 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_sdma_pkt_open.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_sdma_pkt_open.h

## Purpose
`iceland_sdma_pkt_open.h` is a generated-style packet layout header for Iceland SDMA command streams. It exposes opcode/sub-opcode constants and bitfield packing macros used by SDMA ring emitters to build 32-bit packet DWORDs without open-coded masks and shifts.

## Important APIs, Types, And Macros
The file has no C functions or types. Its API is the macro set: top-level `SDMA_OP_*` values for NOP, COPY, WRITE, INDIRECT, FENCE, TRAP, SEM, POLL_REGMEM, COND_EXE, ATOMIC, CONST_FILL, GEN_PTEPDE, TIMESTAMP, SRBM_WRITE, and PRE_EXE; sub-op values for timestamp, copy, and write; and per-packet macros such as `SDMA_PKT_COPY_LINEAR_HEADER_OP(x)`, `SDMA_PKT_COPY_TILED_DW_5_ARRAY_MODE(x)`, `SDMA_PKT_FENCE_DATA_DATA(x)`, and `SDMA_PKT_POLL_REGMEM_DW5_RETRY_COUNT(x)`. Packet sections cover linear copy, broadcast linear copy, linear sub-window copy, tiled copy, linear-to-tiled broadcast, tiled-to-tiled copy, tiled sub-window copy, structured copy, untiled/tiled/incremental writes, indirect buffers, semaphores, fences, SRBM writes, pre-execute, conditional execute, constant fill, poll reg/mem, timestamp set/get/global get, trap, and NOP.

## Control Flow
There is no runtime control flow. Including code composes packet DWORDs by ORing opcode/sub-opcode macros with field macros, then emits those values into an SDMA command buffer in hardware-defined DWORD order.

## State And Persistence
The header owns no persistent state. Its constants define a stable userspace/kernel command ABI for this SDMA generation; mistakes persist indirectly as malformed command buffers submitted to hardware.

## Dependencies And Integration Points
The header is self-contained except for consumers that understand the SDMA packet ABI. It integrates with amdgpu SDMA ring construction code and with GPU firmware/hardware packet parsers. The include guard is `__ICELAND_SDMA_PKT_OPEN_H_`.

## Risks
The macros do not validate value ranges beyond masking, so oversized inputs silently truncate. Several fields share DWORDs, making incorrect OR composition easy. Packet layout drift against hardware documentation would cause GPU hangs or data corruption. There is also a duplicated `SDMA_PKT_COPY_BROADCAST_LINEAR_SRC_ADDR_LO_src_addr_31_0_shift` macro definition, apparently benign but a signal that generated-header hygiene matters.

## Test Signals
Useful signals are SDMA ring selftests, copy/fill/fence tests, GPUVM memory movement tests, command submission stress, and compile coverage for all consumers. Static checks should watch duplicate macro definitions and verify packet emitted DWORD counts against the packet specification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_sdma_pkt_open.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c

## Purpose
`ih_v6_0.c` implements the amdgpu Interrupt Handler IP block for IH version 6.0. It allocates and programs interrupt rings, enables/disables hardware interrupt delivery, services write/read pointer synchronization, and wires the block into the generic `amd_ip_funcs` lifecycle.

## Important APIs, Types, And Functions
The exported object is `ih_v6_0_ip_block`. Important internal functions include `ih_v6_0_init_register_offset`, `ih_v6_0_toggle_ring_interrupts`, `ih_v6_0_enable_ring`, `ih_v6_0_irq_init`, `ih_v6_0_irq_disable`, `ih_v6_0_get_wptr`, `ih_v6_0_set_rptr`, `ih_v6_0_self_irq`, and clock/power-gating helpers. It installs `amdgpu_ih_funcs` with `get_wptr`, common IV decoders, and `set_rptr`.

## Control Flow
Early init installs IH and self-IRQ callbacks. Software init registers self interrupt source `SOC21_IH_CLIENTID_IH`, allocates ring0, optionally ring1 on dGPU, then allocates a software IH ring and calls `amdgpu_irq_init`. Hardware init disables rings, lets NBIO configure IH, optionally enables GPA addressing when firmware loading bypasses PSP, programs ring bases/control/doorbells, configures storm/flood handling and ring1 redirection, enables PCI bus mastering, enables interrupts, and enables forced write-pointer updates for self interrupts. Suspend/resume call hardware fini/init.

## State And Persistence
State is kept in `adev->irq.ih`, `adev->irq.ih1`, and `adev->irq.ih_soft`: ring sizes, GPU addresses, CPU writeback/readback pointers, doorbell indices, enabled flags, read pointers, and overflow flags. Register programming persists until reset or hardware fini. Disabling resets hardware rptr/wptr to zero and clears software `enabled`/`rptr`.

## Dependencies And Integration Points
The file depends on `amdgpu.h`, `amdgpu_ih.h`, OSSSYS 6.0 register headers, SOC15 accessors, PSP indirect register programming for SR-IOV VF, NBIO IH hooks, PCI core, delayed work for ring1, and amdgpu IRQ registration. It integrates with PSP firmware loading mode and with MSI doorbell behavior.

## Risks
Interrupt loss or storms can occur if doorbell indices, writeback addresses, or storm registers are wrong. Overflow recovery skips to `wptr + 32`, which may lose vectors but lets parsing catch up. SR-IOV indirect paths return timeouts on PSP programming failure. `wait_for_idle` is a TODO returning `-ETIMEDOUT`, so callers must not treat idle wait as implemented. Big-endian rptr writeback is called out as unchecked.

## Test Signals
Signals include boot/resume interrupt delivery, ring0/ring1 IRQ processing, self-interrupt write-pointer update work, SR-IOV VF operation, MSI/non-MSI doorbell rearm behavior, interrupt storm tests, overflow injection, and clock/power-gating transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_0.h

## Purpose
`ih_v6_0.h` is the public declaration point for the IH v6.0 amdgpu IP block.

## Important APIs, Types, And Functions
It declares `extern const struct amdgpu_ip_block_version ih_v6_0_ip_block;`. The type itself is defined by the amdgpu IP framework and instantiated in `ih_v6_0.c`.

## Control Flow
There is no control flow in the header. Consumers include it so board/IP discovery code can reference the v6.0 IH block and register its lifecycle callbacks.

## State And Persistence
The header owns no state. The declared object represents static driver metadata for IH major 6 minor 0 revision 0.

## Dependencies And Integration Points
The header assumes `struct amdgpu_ip_block_version` is visible or forward-resolvable at include sites. It integrates `ih_v6_0.c` with amdgpu IP block tables.

## Risks
Risk is limited to declaration drift: if the implementation symbol name or IP block version changes without updating this header, build or link failures follow.

## Test Signals
Build coverage is the main test signal. Runtime coverage comes indirectly from devices selecting `ih_v6_0_ip_block`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_1.c

## Purpose
`ih_v6_1.c` implements the IH block for OSSSYS/IH 6.1-era hardware. It mirrors the v6.0 lifecycle while using 6.1 register definitions, a larger primary ring, early IRQ domain setup, and slightly different overflow/toggle behavior.

## Important APIs, Types, And Functions
The exported object is `ih_v6_1_ip_block`. Core functions are `ih_v6_1_init_register_offset`, `force_update_wptr_for_self_int`, `ih_v6_1_toggle_ring_interrupts`, `ih_v6_1_enable_ring`, `ih_v6_1_irq_init`, `ih_v6_1_get_wptr`, `ih_v6_1_set_rptr`, `ih_v6_1_self_irq`, lifecycle callbacks, and clock/memory power-gating helpers.

## Control Flow
Early init first calls `amdgpu_irq_add_domain`, then installs IH and self-IRQ callbacks. Software init registers the self IRQ, initializes ring0 at 256 KiB, initializes ring1 for dGPU, sets doorbells, maps register offsets, creates a PAGE_SIZE software IH ring, and calls `amdgpu_irq_init`. Hardware init disables rings, performs NBIO control, optionally enables GPA addressing, programs ring registers and doorbells, configures storm/flood handling and dGPU ring1 routing, enables bus mastering and interrupts, and turns on forced self-interrupt wptr updates.

## State And Persistence
Runtime state lives in `adev->irq` rings and hardware IH registers. Doorbell indices are based on `adev->doorbell_index.ih`. The file persists clockgating and SRAM powergating state in OSSSYS registers. Unlike v6.0, ring toggle enable does not perform the explicit overflow-clear pulse sequence, and init does not reset the per-ring `overflow` flag in the same loop.

## Dependencies And Integration Points
Dependencies include OSSSYS 6.1 offset/mask headers, SOC15 accessors, PSP indirect programming for SR-IOV, NBIO IH configuration hooks, PCI, amdgpu IRQ domains and source registration, and the generic IV decode helpers.

## Risks
The `ih_v6_1_ip_block` metadata sets `.major = 6`, `.minor = 0`, `.rev = 0` despite the v6.1 filename and functions, which may be intentional compatibility or a version-label risk. Overflow handling still advances rptr by 32 and can lose vectors under pressure. PAGE_SIZE software ring sizing should be validated against interrupt burst behavior. TODO idle/reset callbacks remain placeholders.

## Test Signals
Test signals include probe on IH 6.1 hardware, IRQ domain registration, ring0/ring1 interrupt delivery, software ring pressure, resume after suspend, SR-IOV VF PSP indirect register programming, interrupt storm throttling, and clock/power-gating toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_1.h

## Purpose
`ih_v6_1.h` declares the amdgpu IH v6.1 IP block object for consumers that build IP version tables.

## Important APIs, Types, And Functions
The only API is `extern const struct amdgpu_ip_block_version ih_v6_1_ip_block;`.

## Control Flow
There is no runtime control flow. Inclusion enables static registration of the implementation in `ih_v6_1.c`.

## State And Persistence
The header owns no mutable state. It exposes a const IP block descriptor.

## Dependencies And Integration Points
It depends on include sites knowing `struct amdgpu_ip_block_version` and integrates with the amdgpu IP discovery/initialization framework.

## Risks
Declaration/definition mismatch would surface as compile or link failures. The header does not itself reveal the implementation's version metadata, so version-label mistakes must be caught in C-file review or runtime selection tests.

## Test Signals
Build coverage and device-selection coverage for `ih_v6_1_ip_block` are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v7_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v7_0.c

## Purpose
`ih_v7_0.c` implements the IH block for OSSSYS/IH 7.0 and includes special handling for IP version 7.1.0. It manages interrupt rings, self-interrupt routing, storm control, retry CAM setup, and clock/SRAM power behavior.

## Important APIs, Types, And Functions
The exported object is `ih_v7_0_ip_block`. Important functions include `ih_v7_0_init_register_offset`, `ih_v7_0_toggle_ring_interrupts`, `ih_v7_0_enable_ring`, `ih_v7_0_setup_retry_doorbell`, `ih_v7_0_irq_init`, `ih_v7_0_get_wptr`, `ih_v7_0_set_rptr`, `ih_v7_0_self_irq`, lifecycle callbacks, and gating helpers. It defines local v7.1 register offsets for ring1 client config and `IH_CHICKEN`.

## Control Flow
Software init registers the IH self IRQ, allocates a 256 KiB primary ring, optional dGPU ring1, register offsets, and a software ring sized as `IH_SW_RING_SIZE` for OSSSYS 7.1.0 or PAGE_SIZE otherwise. Hardware init disables rings, runs NBIO control, chooses normal or v7.1 register addresses for GPA and ring1 routing, programs ring bases and controls, configures storm/flood throttling, then for v7.1.0 allocates a retry CAM doorbell at `(ih + 2) << 1`, enables `IH_RETRY_INT_CAM_CNTL`, marks `adev->irq.retry_cam_enabled`, and finally enables interrupts and forced self wptr updates.

## State And Persistence
State spans `adev->irq.ih`, `ih1`, `ih_soft`, `retry_cam_doorbell_index`, and `retry_cam_enabled`, plus persistent register state until reset/fini. `get_wptr` clears overflow and moves rptr to `wptr + 32` on overflow. `set_rptr` writes CPU rptr memory and doorbells, with SR-IOV rearm retries when doorbell writes are lost.

## Dependencies And Integration Points
Dependencies include OSSSYS 7.0 register headers, SOC15 register access, `amdgpu_ip_version`, PSP indirect paths, NBIO hooks, PCI bus mastering, IRQ registration, self-IRQ work scheduling, and generic IV decoders. v7.1 behavior integrates with retry interrupt CAM hardware.

## Risks
The hard-coded v7.1 register offsets are local to this file and must remain synchronized with register headers/specs. Retry CAM enablement adds state not disabled explicitly in `irq_disable`. Wrong software ring sizing for v7.1 may affect retry/self interrupt workloads. Placeholder idle/reset callbacks remain. Overflow recovery loses entries under pressure.

## Test Signals
Probe both OSSSYS 7.0 and 7.1.0 paths, including dGPU ring1 routing, retry CAM doorbell programming, SR-IOV rearm, storm/flood behavior, suspend/resume, software ring sizing, and interrupt overflow injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v7_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v7_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v7_0.h

## Purpose
`ih_v7_0.h` declares the IH v7.0 amdgpu IP block object.

## Important APIs, Types, And Functions
It exposes `extern const struct amdgpu_ip_block_version ih_v7_0_ip_block;`.

## Control Flow
The header has no control flow. It supports inclusion by IP block tables or device-family initialization code.

## State And Persistence
No state is owned here. The const descriptor is defined in `ih_v7_0.c`.

## Dependencies And Integration Points
Consumers must have the amdgpu IP block type in scope. The declaration links IH v7.0 support into the broader IP framework.

## Risks
Risk is limited to stale symbol declarations or missing implementation linkage.

## Test Signals
Build/link coverage and runtime selection of IH v7.0 hardware are sufficient signals for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v7_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c

## Purpose
`imu_v11_0.c` implements GFX11 IMU firmware handling and IMU-programmed RLC RAM setup. It requests the correct IMU firmware, optionally stages it for PSP loading, directly uploads IRAM/DRAM when needed, starts the IMU, and writes generation-specific golden register sequences into IMU RLC RAM.

## Important APIs, Types, And Functions
The exported API is `gfx_v11_0_imu_funcs`. Key functions are `imu_v11_0_init_microcode`, `imu_v11_0_load_microcode`, `imu_v11_0_wait_for_reset_status`, `imu_v11_0_setup`, `imu_v11_0_start`, `program_imu_rlc_ram`, and `imu_v11_0_program_rlc_ram`. Static tables `imu_rlc_ram_golden_11` and `imu_rlc_ram_golden_11_0_2` hold register/data/address-mask triples via `IMU_RLC_RAM_GOLDEN_VALUE`.

## Control Flow
Init decodes the GC IP version into a firmware prefix, chooses kicker or normal firmware, requests it as required, parses `imu_firmware_header_v1_0`, and either records IMU I/D firmware entries for PSP loading or stores the firmware version for direct loading. Direct load writes IRAM then DRAM data from the firmware blob into `GFX_IMU_*_RAM_*` registers. Setup opens C2P message access and sets debug/scratch bits. Start clears `GFX_IMU_CORE_CTRL.CRESET`, asks DPM to power up GFX by IMU on APUs, then polls reset status until low five bits are set. RLC RAM programming selects tables by GC IP version, delegates 11.0.3 to `imu_v11_0_3_program_rlc_ram`, terminates the RAM list, and marks RAM valid.

## State And Persistence
State is held in `adev->gfx.imu_fw`, `adev->gfx.imu_fw_version`, `adev->firmware.ucode[]`, `adev->firmware.fw_size`, `adev->gfx.imu.mode`, and hardware IMU/RLC RAM registers. Dynamic values patch AGP and VRAM location entries from `adev->gmc`.

## Dependencies And Integration Points
Dependencies include Linux firmware loading, `amdgpu_ucode_*`, `amdgpu_is_kicker_fw`, PSP firmware loading structures, GC 11.0 register headers, DPM GFX power-up, and the companion 11.0.3 table file. It integrates with the `amdgpu_imu_funcs` call sites in the GFX bring-up path.

## Risks
Firmware prefix or kicker selection errors fail probe. PSP size accounting must match firmware sections. Polling uses `adev->usec_timeout`; too short a timeout causes false failures. Unsupported GC versions hit `BUG()`. Golden table values are hardware-sensitive and can corrupt early graphics setup if stale. Firmware version assignment is commented out for one path, so direct load relies on version being set only outside PSP cases.

## Test Signals
Signals include firmware request success for all listed GC 11.x IMU binaries, direct-load register traces, PSP load-table sizing, IMU reset completion, APU DPM interaction, RLC RAM valid bit, and boot tests across 11.0.0, 11.0.2, and 11.0.3 ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.h

## Purpose
`imu_v11_0.h` declares the GFX11 IMU function table for the amdgpu GFX/IMU initialization path.

## Important APIs, Types, And Functions
It declares `extern const struct amdgpu_imu_funcs gfx_v11_0_imu_funcs;`.

## Control Flow
No control flow is present. Consumers include this header to assign the v11 IMU callbacks.

## State And Persistence
No state is owned here; mutable firmware and hardware state lives in `imu_v11_0.c` and `amdgpu_device`.

## Dependencies And Integration Points
The header assumes `struct amdgpu_imu_funcs` is available at inclusion sites. It integrates v11 IMU support with the amdgpu GFX IP setup code.

## Risks
Stale extern declarations result in build/link errors. Behavioral risk is in the implementation rather than this declaration.

## Test Signals
Build coverage and runtime callback-table selection for GFX11 devices cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c

## Purpose
`imu_v11_0_3.c` provides the GC 11.0.3-specific IMU RLC RAM golden register sequence used by the generic v11 IMU implementation.

## Important APIs, Types, And Functions
The exported function is `imu_v11_0_3_program_rlc_ram(struct amdgpu_device *adev)`. Internally, `imu_rlc_ram_golden_11_0_3` stores register settings and `program_rlc_ram_register_setting` writes each entry through `GFX_IMU_RLC_RAM_ADDR_HIGH`, `ADDR_LOW`, and `DATA`.

## Control Flow
The public function calls the helper with the static table. The helper computes the register address from `adev->reg_offset` plus entry register and address mask, patches AGP and framebuffer location registers from `adev->gmc`, writes each tuple into IMU RLC RAM, and appends a zero-address/data terminator.

## State And Persistence
Persistent effects are the written IMU RLC RAM contents. The source table is immutable. Runtime values depend on `adev->gmc.vram_start` and `adev->gmc.vram_end` for framebuffer aperture entries.

## Dependencies And Integration Points
It depends on `amdgpu.h`, `amdgpu_imu.h`, its header, and GC 11.0.3 register definitions. It is called from `imu_v11_0_program_rlc_ram` when `amdgpu_ip_version(... GC_HWIP ...)` is 11.0.3.

## Risks
The table is ASIC-specific and includes per-shader-array and harvest/steering settings; incorrect entries can break graphics initialization. The address mask is ORed into the computed register, so malformed masks can redirect writes. There is no validation of table size beyond `ARRAY_SIZE`.

## Test Signals
Boot and graphics workload tests on GC 11.0.3 hardware, RLC RAM dump comparison, VRAM aperture correctness, and regression against harvest configurations are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.h

## Purpose
`imu_v11_0_3.h` exposes the GC 11.0.3-specific RLC RAM programming helper to the broader v11 IMU implementation.

## Important APIs, Types, And Functions
It declares `void imu_v11_0_3_program_rlc_ram(struct amdgpu_device *adev);`.

## Control Flow
There is no header control flow. `imu_v11_0.c` calls the declared function from its GC IP version switch.

## State And Persistence
The header owns no state. The implementation writes persistent IMU RLC RAM contents.

## Dependencies And Integration Points
The declaration requires `struct amdgpu_device` to be visible or forward-declared by include context. It integrates the 11.0.3 table module with `imu_v11_0.c`.

## Risks
Declaration drift causes build failures. Missing include context for `struct amdgpu_device` can also fail compilation.

## Test Signals
Build coverage and execution of the 11.0.3 branch in `imu_v11_0_program_rlc_ram` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.c

## Purpose
`imu_v12_0.c` implements GFX12.0 IMU firmware loading, IMU startup, and RLC RAM programming. It keeps the v11 firmware flow but adds GFX12 transfer-RAM addressing, GRBM index remapping, and MMHUB-derived GFXHUB aperture settings.

## Important APIs, Types, And Functions
The exported object is `gfx_v12_0_imu_funcs`. Key functions are `imu_v12_0_init_microcode`, `imu_v12_0_load_microcode`, `imu_v12_0_wait_for_reset_status`, `imu_v12_0_setup`, `imu_v12_0_start`, `program_imu_rlc_ram_old`, `imu_v12_0_grbm_gfx_index_remap`, `imu_v12_init_gfxhub_settings`, `program_imu_rlc_ram`, and `imu_v12_0_program_rlc_ram`. `TRANSFER_RAM_MASK` is `0x001c0000`.

## Control Flow
Init requests normal or kicker GFX12.0 IMU firmware, stores the firmware version, and for PSP loading records IMU I/D entries plus aligned firmware sizes. Direct load writes firmware IRAM and DRAM arrays to IMU RAM registers. Setup opens C2P message access and, in debug mode, sets C2PMSG and scratch bits. Start releases IMU reset and optionally invokes APU DPM power-up, then polls reset status. RLC programming selects IP 12.0.0/12.0.1, currently falls back to `program_imu_rlc_ram_old` because `r` remains `-EINVAL`, writes a terminator, and marks RAM valid. The newer `program_imu_rlc_ram` path supports triplet arrays, MMHUB value substitution, and GRBM index remapping.

## State And Persistence
State includes firmware pointers/version, PSP firmware table accounting, IMU C2P/scratch/core registers, and IMU RLC RAM. Aperture values may be sourced live from MMHUB registers rather than static table data.

## Dependencies And Integration Points
Dependencies include firmware APIs, amdgpu ucode helpers, `amdgpu_is_kicker_fw`, PSP firmware loading, DPM APU hooks, GC 12.0 register headers, MMHUB 4.1 register headers, and `amdgpu_imu_funcs` users in GFX bring-up.

## Risks
The new triplet programming path is effectively disabled by `r = -EINVAL`, so intended data-driven programming may be incomplete or future-facing. `BUG()` handles unsupported versions. MMHUB/GFX register mapping must remain exact. GRBM remapping is bit-sensitive and can mis-target per-instance writes. Firmware load failure blocks initialization.

## Test Signals
Signals include firmware availability for `gc_12_0_0_imu.bin`, `gc_12_0_1_imu.bin`, and kicker firmware; direct and PSP load paths; reset polling; RLC RAM valid bit; MMHUB aperture consistency; and boot/display/compute workloads on 12.0.0 and 12.0.1 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.h

## Purpose
`imu_v12_0.h` declares the GFX12.0 IMU callback table.

## Important APIs, Types, And Functions
It exposes `extern const struct amdgpu_imu_funcs gfx_v12_0_imu_funcs;`.

## Control Flow
No runtime control flow is present. Include sites use the extern to select v12.0 IMU operations.

## State And Persistence
No state is owned by the header. Firmware and hardware state are managed by `imu_v12_0.c`.

## Dependencies And Integration Points
It depends on include context for `struct amdgpu_imu_funcs` and integrates with GFX IP initialization.

## Risks
The header risk is limited to stale declaration or missing include context.

## Test Signals
Build coverage and runtime selection on GFX12.0 devices are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_1.c

## Purpose
`imu_v12_1.c` implements the newer GFX12.1 IMU firmware path, with emphasis on per-XCC firmware loading and compute partition switching rather than local start/setup/RLC RAM programming.

## Important APIs, Types, And Functions
The exported object is `gfx_v12_1_imu_funcs`. Important functions are `imu_v12_1_init_microcode`, `imu_v12_1_xcc_load_microcode`, `imu_v12_1_load_microcode`, `imu_v12_1_switch_compute_partition`, and `imu_v12_1_init_mcm_addr_lut`. It declares firmware `amdgpu/gc_12_1_0_imu.bin`.

## Control Flow
Init decodes the GC IP version into a short prefix, requests the required IMU firmware, stores the firmware version, and for PSP loading records IMU I/D firmware entries and aligned sizes. `load_microcode` rejects missing firmware, computes `NUM_XCC(adev->gfx.xcc_mask)`, and uploads the same firmware IRAM/DRAM image to each XCC instance via `GET_INST(GC, xcc_id)`. Compute partition switching calls `psp_spatial_partition` when PSP functions are present, using total XCC count divided by XCCs per XCP, then records `adev->gfx.num_xcc_per_xcp`.

## State And Persistence
State includes `adev->gfx.imu_fw`, `adev->gfx.imu_fw_version`, PSP firmware entries, per-XCC IMU RAM contents, and `adev->gfx.num_xcc_per_xcp`. `init_mcm_addr_lut` is a placeholder and persists nothing.

## Dependencies And Integration Points
Dependencies include Linux firmware loading, amdgpu ucode helpers, GC 12.1 register headers, MMHUB 4.2 headers, XCC macros, PSP spatial partitioning, and the `amdgpu_imu_funcs` interface. The file includes DPM headers but does not currently start or power up IMU directly.

## Risks
`ucode_prefix[15]` is smaller than older IMU files and depends on decoded names fitting. Per-XCC loops assume XCC IDs are dense from zero to `NUM_XCC(mask)-1`; sparse masks would need scrutiny. Partition switching divides by `num_xccs_per_xcp` without a local zero guard. TODO comments indicate incomplete ASP/interface and MCM LUT handling.

## Test Signals
Firmware request success, per-XCC IMU RAM upload traces, multi-XCC hardware boot, PSP spatial partition return codes, invalid partition parameter tests, and compute partition mode transitions are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_1.h

## Purpose
`imu_v12_1.h` declares the GFX12.1 IMU callback table.

## Important APIs, Types, And Functions
It exposes `extern const struct amdgpu_imu_funcs gfx_v12_1_imu_funcs;`.

## Control Flow
The header has no control flow. It lets device/GFX initialization select the v12.1 IMU implementation.

## State And Persistence
No state is owned here; per-XCC firmware and partition state are owned by the implementation and `amdgpu_device`.

## Dependencies And Integration Points
It depends on include context for `struct amdgpu_imu_funcs` and integrates with amdgpu GFX setup code.

## Risks
Risk is declaration drift or missing implementation linkage.

## Test Signals
Compile/link coverage and runtime callback-table selection on GFX12.1 hardware cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_0.c

## Purpose
`isp_v4_1_0.c` initializes and tears down ISP 4.1.0 support by presenting ISP capture, I2C, and GPIO/pinctrl blocks as MFD child devices with memory and IRQ resources derived from the amdgpu device.

## Important APIs, Types, And Functions
The exported function is `isp_v4_1_0_set_isp_funcs`, which installs `isp_v4_1_0_funcs`. Internal functions are `isp_v4_1_0_hw_init` and `isp_v4_1_0_hw_fini`. `isp_4_1_0_int_srcid` maps eight ISP ringbuffer write-pointer source IDs to Linux IRQ resources.

## Control Flow
Hardware init validates `adev->rmmio_size`, allocates three `mfd_cell` entries, a combined resource array for capture MMIO plus IRQs, platform data, a one-resource I2C MMIO array, and a one-resource GPIO MMIO array. It fills platform data with `adev`, ASIC type, and base RMMIO size; maps the main ISP register window, PHY0 window, eight IRQ mappings, the I2C0 window, and sensor GPIO window; then calls `mfd_add_hotplug_devices`. On allocation or MFD failure it frees allocated pieces and returns the error. Hardware fini removes child devices and frees all stored allocations.

## State And Persistence
State is stored in `struct amdgpu_isp`: `isp_cell`, `isp_res`, `isp_pdata`, `isp_i2c_res`, and `isp_gpio_res`. Child MFD devices persist after init until `mfd_remove_devices` in fini.

## Dependencies And Integration Points
Dependencies include `amdgpu.h`, `isp_v4_1_0.h`, `amdgpu_isp`, Linux MFD helpers, IRQ source mapping, DRM logging, and platform child drivers named `amd_isp_capture`, `amd_isp_i2c_designware`, and `amdisp-pinctrl`.

## Risks
The RMMIO size check compares against `0x5289`, which is smaller than the largest offsets used (`0x66700` plus size) if interpreted as absolute range, so resource validity depends on the meaning of `rmmio_size` and `rmmio_base`. Failure cleanup frees memory but does not null pointers, so repeated fini after failed init would be risky if callers do not respect return status. IRQ mapping failures are not checked for invalid mappings.

## Test Signals
Probe/remove tests, MFD child creation, resource ranges in sysfs, IRQ mapping delivery for all eight source IDs, I2C and GPIO child-driver binding, hotplug removal, and allocation-failure injection are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_0.h

## Purpose
`isp_v4_1_0.h` defines ISP 4.1.0 resource counts and MMIO offsets, imports ISP interrupt source IDs, and declares the function-table installer.

## Important APIs, Types, And Functions
Macros include `MAX_ISP410_MEM_RES`, `MAX_ISP410_SENSOR_RES`, `MAX_ISP410_INT_SRC`, `ISP410_PHY0_OFFSET/SIZE`, `ISP410_I2C0_OFFSET/SIZE`, and `ISP410_GPIO_SENSOR_OFFSET/SIZE`. The exported function declaration is `void isp_v4_1_0_set_isp_funcs(struct amdgpu_isp *isp);`.

## Control Flow
There is no control flow. The implementation consumes these constants when building MFD resources.

## State And Persistence
No state is owned here. Constants define persistent driver assumptions about ISP register layout and interrupt count.

## Dependencies And Integration Points
It includes `amdgpu_isp.h` and `ivsrcid/isp/irqsrcs_isp_4_1.h`. It integrates the ISP 4.1.0 implementation with amdgpu ISP setup and with platform child drivers that receive the resource windows.

## Risks
Incorrect offsets or sizes will expose wrong MMIO ranges to child devices. `MAX_ISP410_SENSOR_RES` is defined but not used in the companion implementation, so future sensor-resource changes need review. Header constants must stay synchronized with ASIC documentation.

## Test Signals
Build coverage, resource range inspection, child driver binding, and IRQ source validation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_0.h -->
