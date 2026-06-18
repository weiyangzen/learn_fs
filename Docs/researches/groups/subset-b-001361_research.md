# Research: subset-b-001361

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.c

Purpose: Southern Islands common ASIC support for amdgpu. It provides per-chip register programming tables, ASIC callback wiring, BIOS/register helpers, reset plumbing, PCIe link management, UVD/VCE clock programming, and the IP block list for Tahiti, Pitcairn, Verde, Oland, and Hainan.

Important APIs, types, and functions: the file defines large golden-register and clock-gating init arrays, video codec capability tables, `si_asic_funcs`, `si_common_ip_block`, and exported `si_set_ip_blocks()`. Key helpers include indirect register accessors for PCIe/SMC/UVD context, `si_read_register()`, BIOS read fallbacks, `si_asic_reset()`, `si_set_uvd_clocks()`, `si_set_vce_clocks()`, `si_common_early_init()`, `si_init_golden_registers()`, `si_pcie_gen3_enable()`, and `si_program_aspm()`.

Control flow: early init installs indirect register functions, assigns `adev->asic_funcs`, reads revision straps, and chooses clock/power-gating flags by ASIC. Hardware init fixes PCIe max read request size, applies chip-specific golden register sequences, retrains PCIe Gen2/Gen3 when allowed, and configures ASPM. Reset either uses normal PCI reset or the legacy PCI config reset path that bypasses clocks, powers down SPLL, clears bus mastering, resets, and waits for `CONFIG_MEMSIZE` to return. Media clock setters bypass clocks, calculate PLL dividers, program PLL registers, wait for control acks, and switch sources back to PLL output.

State and persistence: persistent state is hardware register state, PCI config state, programmed ring/IP ordering, and fields stored on `adev` such as `cg_flags`, `pg_flags`, revision IDs, callback tables, and reset status. There is no filesystem persistence. Several helpers temporarily save display/VGA/ROM registers and restore them after BIOS reads.

Dependencies and integration points: integrates with amdgpu core IP block management, gmc/gfx/sdma/smu/dce/uvd/vce blocks, DC or VKMS display selection, AtomBIOS, PCIe capability helpers, DRM logging, and generated SI register headers. The allowed-register table gates debugfs/ioctl-style register reads.

Risks and test signals: PLL programming and PCIe retraining rely on timeouts and exact register masks; failures surface as boot hangs, reset failures, media clock timeouts, or bad link speed. `BUG()` is used for impossible ASIC cases. Test signals include SI board probe, suspend/resume, GPU reset recovery, UVD/VCE playback/encode clocks, PCIe link speed/lane reporting, BIOS read paths, and ring/IB tests after `si_set_ip_blocks()` ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.h

Purpose: public Southern Islands common header shared by SI-era amdgpu blocks.

Important APIs, types, and functions: declares `SI_FLUSH_GPU_TLB_NUM_WREG`, `si_srbm_select()`, and `si_set_ip_blocks()`. The TLB flush constant is consumed by SDMA ring sizing; the function declarations connect common SI selection and device IP registration to other IP files.

Control flow: this header has no runtime flow. It enables compile-time linkage so GFX/GMC/SDMA/common code can call SRBM selection and top-level IP block registration.

State and persistence: no state is stored here; the declared functions mutate `amdgpu_device` hardware and software state in their implementations.

Dependencies and integration points: depends on `struct amdgpu_device` and basic fixed-width types being visible through including translation units. It is included by SI common and SDMA code.

Risks and test signals: risks are limited to ABI drift between declarations and definitions. Build coverage catches signature mismatches; runtime test signals come from successful SI IP block registration and VM flush ring sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_dma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_dma.c

Purpose: Southern Islands SDMA engine implementation. It initializes two DMA rings, emits SDMA packets for IBs, fences, VM updates, TLB flushes, buffer copy/fill, trap interrupts, and clock/power gating.

Important APIs, types, and functions: exports `si_dma_ip_block` and defines `sdma_offsets`, `si_dma_ring_funcs`, `si_dma_vm_pte_funcs`, `si_dma_buffer_funcs`, and trap IRQ callbacks. Key functions are `si_dma_start()/stop()`, ring pointer accessors, `si_dma_ring_emit_ib()`, `si_dma_ring_emit_fence()`, `si_dma_ring_test_ring()`, `si_dma_ring_test_ib()`, VM PTE writers, `si_dma_ring_emit_vm_flush()`, and lifecycle hooks `early_init`, `sw_init`, `hw_init`, `suspend`, and `resume`.

Control flow: early init sets two SDMA instances and installs ring, buffer, VM PTE, and IRQ function tables. Software init registers legacy IRQ IDs 224 and 244 and creates `sdma0`/`sdma1` rings. Hardware init programs ring buffer control, read-pointer writeback, base addresses, IB control, disables context-empty interrupts, enables rings, then runs ring tests. Command emission writes packet dwords directly into ring or IB buffers; VM updates are chunked to hardware packet limits.

State and persistence: persistent state lives in SDMA registers, ring BOs, writeback slots, `adev->sdma`, IRQ source tables, and memory-manager buffer callback pointers. Fence packets persist sequence values into GPU-visible memory. No disk state exists.

Dependencies and integration points: integrates with amdgpu ring scheduling, fences, IRQ core, VM/GMC TLB flush helpers, writeback memory, IB allocation/scheduling, and TTM buffer moves through `adev->mman.buffer_funcs`.

Risks and test signals: packet alignment is subtle: IB packets must start on an 8-DW boundary and IBs are padded to 8 DW. The ring supports only 40-bit-ish address high fields (`& 0xff`) and advertises no 64-bit pointers. Soft reset is not implemented. Test signals include ring and IB self-tests writing `0xDEADBEEF`, trap IRQ fence processing on both instances, VM update correctness, suspend/resume ring restart, and buffer copy/fill validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_dma.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_dma.h

Purpose: SI SDMA block declaration header.

Important APIs, types, and functions: declares `extern const struct amdgpu_ip_block_version si_dma_ip_block`, the IP block descriptor consumed by `si_set_ip_blocks()`.

Control flow: no runtime flow in the header. The descriptor points amdgpu core at the SDMA lifecycle callbacks in `si_dma.c`.

State and persistence: no state is stored in the header; runtime state is in `adev->sdma`, rings, writeback memory, and SDMA registers.

Dependencies and integration points: included by `si.c` to add the SDMA block to the device IP list and by any SI code needing the descriptor.

Risks and test signals: build errors catch declaration drift. Runtime signal is that SI devices register and initialize `AMD_IP_BLOCK_TYPE_SDMA` successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_enums.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_enums.h

Purpose: small SI-era macro header for priority, RLC power/clock status, and RLC state-table offsets.

Important APIs, types, and functions: defines masks such as `PRIORITY_MARK_MASK`, `PRIORITY_OFF`, `GFX_POWER_STATUS`, `RLC_BUSY_STATUS`, `RLC_PUD/PDD/TTPD/MSD` fields, and RLC save/restore offsets.

Control flow: no runtime flow. Consumers compose or test bitfields against SI hardware registers or RLC memory layouts.

State and persistence: no software state. The macros describe encoded hardware state and firmware table offsets.

Dependencies and integration points: included by SI common/GFX-related code alongside generated GFX and OSS register headers.

Risks and test signals: incorrect masks would cause invalid RLC power sequencing or status interpretation. Test signals are clock/power-gating stability, RLC save/restore behavior, and clean GPU reset/resume on SI parts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_enums.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_ih.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_ih.c

Purpose: Southern Islands interrupt handler ring IP block. It programs the IH ring, decodes 16-byte legacy interrupt vectors, tracks read/write pointers, handles overflow, and exposes the IH lifecycle to amdgpu core.

Important APIs, types, and functions: exports `si_ih_ip_block` and installs `si_ih_funcs` with `get_wptr`, `decode_iv`, and `set_rptr`. Main functions include `si_ih_irq_init()`, `si_ih_enable_interrupts()`, `si_ih_disable_interrupts()`, `si_ih_get_wptr()`, `si_ih_decode_iv()`, `si_ih_soft_reset()`, and IP callbacks for early/sw/hw init and suspend/resume.

Control flow: software init allocates the hardware IH ring and soft IH ring, then initializes amdgpu IRQ support. Hardware init disables interrupts, programs dummy page, IH base, writeback address, ring size, read/write pointers, MSI rearm behavior, enables bus mastering, and enables interrupts. During interrupt processing, `get_wptr` reads writeback memory and recovers from overflow by advancing `rptr`; `decode_iv` maps four dwords into legacy client/source/ring/vmid fields and advances by 16 bytes.

State and persistence: state is in `adev->irq.ih`, `adev->irq.ih_soft`, IH ring BO memory, writeback memory, and IH/MMIO registers. No disk state exists.

Dependencies and integration points: depends on PCI bus mastering, amdgpu IRQ core, `amdgpu_ih_ring_init`, generated OSS register definitions, and SDMA/GFX clients that emit legacy IRQ source IDs.

Risks and test signals: overflow handling drops entries by moving `rptr` near `wptr`; repeated overflow means interrupt consumers are too slow. `set_rptr` always writes hardware `IH_RB_RPTR`, so callers must avoid using it for soft ring semantics unless core guards that path. Test signals include MSI/non-MSI interrupt delivery, SDMA trap IRQs, ring overflow warning behavior, suspend/resume interrupt recovery, and idle/soft-reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_ih.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_ih.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_ih.h

Purpose: SI interrupt handler block declaration header.

Important APIs, types, and functions: declares `extern const struct amdgpu_ip_block_version si_ih_ip_block`.

Control flow: no header runtime flow. The descriptor lets SI common add IH to the amdgpu IP block list.

State and persistence: no state here; `si_ih.c` owns IH ring and interrupt state through `adev->irq`.

Dependencies and integration points: included by `si.c` and any SI code that needs the IH IP descriptor.

Risks and test signals: build linkage is the main risk. Runtime signal is successful IRQ setup and interrupt vector decoding on SI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_ih.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sid.h

Purpose: Southern Islands hardware definition header. It collects non-generated register offsets, bit masks, packet encoders, display constants, DMA packet formats, memory-controller fields, interrupt-ring fields, and media PLL definitions used by SI-era drivers.

Important APIs, types, and functions: key macros include `SI_MAX_CTLACKS_ASSERTION_WAIT`, UPLL/VCEPLL register fields, VM invalidate registers, IH control registers, PM4 `PACKET0/PACKET3` encoders, SDMA `DMA_PACKET/DMA_IB_PACKET/DMA_PTE_PDE_PACKET`, SDMA packet opcodes, CRTC/HPD/audio offsets, graphics format constants, PCIe indirect index/data registers, and memory type masks.

Control flow: no executable flow. The macro encoders directly shape command processor and SDMA command streams and register programming sequences in SI common, GFX, DCE, GMC, VCE, UVD, and SDMA code.

State and persistence: no state is stored. The constants describe hardware register state and command packet layouts.

Dependencies and integration points: included by `si.c`, `si_dma.c`, `si_ih.c`, and other SI IP files. It bridges hand-maintained SI definitions with generated block-specific headers.

Risks and test signals: incorrect bit shifts or packet formats cause hard-to-debug GPU hangs, invalid display programming, broken DMA copies, or failed PLL changes. Test signals include command submission, SDMA packet execution, display modeset, IH interrupt delivery, UVD/VCE clock changes, memory-controller setup, and VM invalidate success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sienna_cichlid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sienna_cichlid.c

Purpose: reset-control implementation for Sienna Cichlid mode2 resets. It registers a reset handler that suspends graphics/SDMA state, asks DPM/SMU to perform a mode2 reset, restores GFXHUB and selected IP blocks, resumes RAS/IRQ state, and reruns IB tests.

Important APIs, types, and functions: exported `sienna_cichlid_reset_init()` and `sienna_cichlid_reset_fini()` allocate/free `adev->reset_cntl`. Static handler functions implement reset-handler callbacks: default selection, handler lookup, prepare hardware context, perform reset, restore hardware context, async reset work, and direct `do_reset`.

Control flow: handler lookup honors an explicit reset method, otherwise selects mode2 only when `amdgpu_reset_method` requests it. Preparation ungates PG/CG and suspends GFX and SDMA blocks in reverse order for non-SRIOV. Reset clears PCI bus mastering and calls `amdgpu_dpm_mode2_reset()`. Restore starts PSP RLC autoload, restores and reenables GFXHUB GART, resumes IH, then GFX/SDMA, runs late init, regates PG/CG, registers the GPU instance, resumes RAS/IRQ reset helpers, and runs IB ring tests.

State and persistence: state is in `adev->reset_cntl`, reset work item, active reset method, IP block status flags, GFXHUB saved registers, and hardware reset side effects. No persistent storage exists.

Dependencies and integration points: depends on amdgpu reset framework, DPM mode2 reset, PSP RLC autoload, GFXHUB callbacks, IP block suspend/resume, RAS, IRQ reset helpers, PCI bus-mastering control, and IB ring tests.

Risks and test signals: mode2 support is gated by a disabled firmware-version block and currently by module reset method, so default behavior is conservative. Restore ordering is critical: GFXHUB and IH must come back before GFX/SDMA work. Test signals are successful mode2 reset recovery, no GART faults after restore, RAS resume, IRQ reenablement, and passing IB ring tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sienna_cichlid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sienna_cichlid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sienna_cichlid.h

Purpose: Sienna Cichlid reset-control public header.

Important APIs, types, and functions: includes `amdgpu.h` and declares `sienna_cichlid_reset_init()` and `sienna_cichlid_reset_fini()`.

Control flow: no runtime flow. Callers use init/fini during ASIC setup and teardown to install or remove the mode2 reset controller.

State and persistence: no state in the header; implementation allocates `adev->reset_cntl`.

Dependencies and integration points: integrates the ASIC reset implementation with common amdgpu device setup code.

Risks and test signals: declaration drift would fail builds. Runtime signal is that reset control is installed for Sienna Cichlid and released without leaking or leaving stale `adev->reset_cntl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sienna_cichlid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v11_0_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v11_0_i2c.c

Purpose: Linux I2C adapter implementation for the SMU v11 SMUIO DesignWare-style I2C controller, primarily for RAS/FRU EEPROM access shared with firmware.

Important APIs, types, and functions: exported `smu_v11_0_i2c_control_init()` registers the adapter and `smu_v11_0_i2c_control_fini()` clears bus pointers. Static helpers manage clock gating, enable/disable, status clearing, controller configuration, clock timing, target address, TX/RX polling, transmit/receive, abort, activity detection, bus lock/unlock, I2C transfer, and functionality reporting. The file defines custom error bits such as `I2C_SW_TIMEOUT`, `I2C_ABORT`, and restart flag `I2C_X_RESTART`.

Control flow: adapter transfers call `smu_v11_0_i2c_xfer()`, which initializes the controller, tracks address/direction changes to emit restart, marks the final message with STOP, dispatches reads or writes, then finalizes the controller. Lock ops serialize through `smu_i2c->mutex` and ask SMU firmware for bus ownership via `amdgpu_dpm_smu_i2c_bus_access()`. Init disables clock gating, aborts if activity is stuck, disables the IP, configures master fast-mode capability, and writes fixed timing values.

State and persistence: state is in SMUIO I2C registers, the `amdgpu_smu_i2c_bus` adapter/mutex/port fields, and `adev->pm` bus pointers and `bus_locked` flag. EEPROM contents are external to the driver; the driver itself stores no persistent data.

Dependencies and integration points: depends on Linux I2C core, amdgpu DPM/SMU arbitration, SMUIO v11 register headers, DRM logging, PCI device parentage, and HWMON-class adapter consumers.

Risks and test signals: fixed clock programming assumes a 100 MHz reference and effectively standard-speed timing despite fast-mode configuration. Clock gating is deliberately not restored because it can break later SMU bus use. `trylock_bus` always warns/fails, so atomic I2C users are unsupported. Test signals include EEPROM reads/writes, repeated-message restart/STOP behavior, timeout/NAK reporting, bus lock/unlock balance, and recovery after a stuck controller activity bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v11_0_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v11_0_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v11_0_i2c.h

Purpose: public declaration header for SMU v11 SMUIO I2C adapter setup.

Important APIs, types, and functions: forward-declares `struct amdgpu_device` and declares `smu_v11_0_i2c_control_init()` plus `smu_v11_0_i2c_control_fini()`.

Control flow: no runtime flow in the header. Callers initialize the adapter during device setup and clear it during teardown.

State and persistence: no header state; implementation mutates `adev->pm.smu_i2c`, RAS/FRU bus pointers, and hardware registers.

Dependencies and integration points: depends only on Linux types and amdgpu device ownership. It exposes the I2C bridge to SMU/DPM and RAS EEPROM code.

Risks and test signals: build linkage catches signature drift. Runtime signal is creation and teardown of the "AMDGPU SMU 0" I2C adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v11_0_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v13_0_10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v13_0_10.c

Purpose: reset-control implementation for SMU v13.0.10 mode2 reset flows. It is similar to Sienna Cichlid but includes MES in suspend/restore and reloads IMU firmware after reset.

Important APIs, types, and functions: exported `smu_v13_0_10_reset_init()` and `smu_v13_0_10_reset_fini()` manage `adev->reset_cntl`. Static callbacks implement default mode2 decision, reset-handler lookup, IP suspend, hardware-context prepare/restore, actual mode2 reset, async reset work, and reset-handler table setup.

Control flow: mode2 is default when PM firmware version is at least `0x00502005`, the device is not SRIOV VF, and `amdgpu_asic_reset_method()` resolves to mode2. Preparation ungates PG/CG and suspends GFX, SDMA, and MES in reverse order. Restore collects IMU I/D firmware entries, reloads them through PSP, starts RLC autoload, enables DPM GFX features, resumes GFX/MES/SDMA blocks, runs late init, restores PG/CG gating, resumes RAS/IRQ helpers, and validates with IB ring tests.

State and persistence: state is reset-control allocation, active reset method, work item, IP status flags, firmware table entries, and hardware state restored by PSP/DPM/IP callbacks. No filesystem persistence exists.

Dependencies and integration points: integrates amdgpu reset framework, DPM mode2 reset and GFX feature enablement, PSP firmware loading/RLC autoload, RAS, IRQ GPU reset resume helper, MES/GFX/SDMA IP blocks, and IB tests.

Risks and test signals: only two IMU firmware slots are reserved, so firmware enumeration assumptions matter. Firmware-version gating and ASIC reset method must agree or no handler is selected. Test signals are mode2 reset on supported firmware, IMU reload success, MES/GFX/SDMA resume, late init state, RAS/IRQ recovery, and passing IB tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v13_0_10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v13_0_10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v13_0_10.h

Purpose: public header for SMU v13.0.10 reset-control installation.

Important APIs, types, and functions: includes `amdgpu.h` and declares `smu_v13_0_10_reset_init()` and `smu_v13_0_10_reset_fini()`.

Control flow: no runtime flow. The declarations are used by ASIC setup/teardown to install or remove the mode2 reset controller.

State and persistence: no header state; implementation allocates and stores `adev->reset_cntl`.

Dependencies and integration points: connects SMU v13.0.10 ASIC code to the common reset framework.

Risks and test signals: build coverage catches declaration mismatch. Runtime signal is reset controller installation and cleanup on supported ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smu_v13_0_10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0.c

Purpose: SMUIO v11 function table for ROM register offsets and ROM memory clock-gating control.

Important APIs, types, and functions: defines `smuio_v11_0_funcs` with `get_rom_index_offset`, `get_rom_data_offset`, `update_rom_clock_gating`, and `get_clock_gating_state`. Helpers use SMUIO 11.0.0 generated offsets and masks.

Control flow: ROM offset helpers return SOC15 register offsets. Clock-gating update exits for APUs or unsupported `AMD_CG_SUPPORT_ROM_MGCG`; otherwise it clears soft override bits to enable gating or sets them to disable gating. State query reads the same register and reports ROM MGCG when override0 is clear.

State and persistence: state is the `mmCGTT_ROM_CLK_CTRL0` hardware register and feature flags in `adev->cg_flags`. No software persistence exists.

Dependencies and integration points: consumed through `adev->smuio.funcs` by ROM/VBIOS access and clock-gating reporting code. Depends on SOC15 access macros and generated SMUIO register headers.

Risks and test signals: APU paths must avoid unavailable registers. State reporting checks only override0, while update controls override0 and override1. Test signals are VBIOS ROM access offsets, clock-gating debug flags, and no register faults on APUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0.h

Purpose: SMUIO v11 function-table declaration header.

Important APIs, types, and functions: includes `soc15_common.h` and declares `extern const struct amdgpu_smuio_funcs smuio_v11_0_funcs`.

Control flow: no runtime flow. The descriptor is selected by SOC/IP discovery code to install version-specific SMUIO operations.

State and persistence: no state in the header; implementation reads/writes SMUIO registers.

Dependencies and integration points: exposes SMUIO v11 operations to amdgpu common SOC15 code.

Risks and test signals: build linkage catches mismatch. Runtime signal is correct ROM offset and ROM clock-gating behavior when the v11 table is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.c

Purpose: SMUIO v11.0.6 variant operations for ROM offsets and ROM clock gating.

Important APIs, types, and functions: defines `smuio_v11_0_6_funcs` with ROM index/data offset callbacks, clock-gating update, and state query using v11.0.6 generated headers.

Control flow: offset helpers return SOC15 offsets. Clock-gating update skips APUs, clears soft override bits only when enabling and ROM MGCG is supported, and otherwise sets overrides. Query reports ROM MGCG when override0 is clear.

State and persistence: state is hardware register `mmCGTT_ROM_CLK_CTRL0`; software input state is `adev->flags` and `adev->cg_flags`.

Dependencies and integration points: selected by versioned SMUIO setup for ASICs with SMUIO 11.0.6 and used by VBIOS/ROM and CG reporting paths.

Risks and test signals: unlike v11.0, unsupported enable requests explicitly force overrides, which is safer but should match power expectations. Test signals are ROM read offsets, CG flag reporting, and APU register avoidance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.h

Purpose: declaration header for SMUIO v11.0.6 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v11_0_6_funcs`.

Control flow: no runtime flow; version selection code uses the descriptor.

State and persistence: no header state.

Dependencies and integration points: integrates the v11.0.6 SMUIO table with SOC15 common code.

Risks and test signals: build linkage and correct version-table selection are the main checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0.c

Purpose: SMUIO v13.0 operations for ROM offsets, ROM clock gating, topology identity, host-GPU XGMI detection, and package type.

Important APIs, types, and functions: defines `smuio_v13_0_funcs` with ROM index/data callbacks, die/socket ID accessors, `is_host_gpu_xgmi_supported`, ROM clock-gating update/query, and `get_pkg_type`.

Control flow: ROM and CG operations mirror newer SMUIO register names. Identity helpers read `regSMUIO_MCM_CONFIG` and extract `DIE_ID`, `SOCKET_ID`, `TOPOLOGY_ID`, or package-related encodings. Host-GPU XGMI is inferred from topology bit 0; package type maps topology values `0x4` and `0xC` to CEM and defaults to OAM.

State and persistence: state is hardware SMUIO MCM configuration and ROM clock-control registers. No persistent software state exists.

Dependencies and integration points: feeds multi-die/socket topology, XGMI decisions, VBIOS ROM access, and CG reporting through the generic `amdgpu_smuio_funcs` interface.

Risks and test signals: package mapping defaults to OAM for all unrecognized topology values, which can hide future encodings. Host-GPU XGMI detection uses a local mask against extracted topology. Test signals include topology reporting, package classification on CEM/OAM systems, ROM access, and CG state reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0.h

Purpose: declaration header for SMUIO v13.0 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v13_0_funcs`.

Control flow: no runtime flow; selected by versioned SOC setup.

State and persistence: no header state.

Dependencies and integration points: exposes v13.0 SMUIO callbacks to amdgpu SOC15 code.

Risks and test signals: correct version selection and successful topology/ROM callback use validate this header link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_3.c

Purpose: SMUIO v13.0.3 topology helper table focused on die ID, socket ID, and package type.

Important APIs, types, and functions: defines `smuio_v13_0_3_funcs` with `get_die_id`, `get_socket_id`, and `get_pkg_type`. Package type uses local `PKG_TYPE_MASK`.

Control flow: each helper reads `regSMUIO_MCM_CONFIG`; die/socket helpers extract fields directly. Package helper extracts `PKG_TYPE`, masks low bits, and maps `0` to CEM, `1` to OAM, `2` to APU, otherwise unknown.

State and persistence: state is the hardware MCM config register. No software persistence.

Dependencies and integration points: used by amdgpu topology/package code through `amdgpu_smuio_funcs` for ASICs with this SMUIO revision.

Risks and test signals: reserved package encodings deliberately become unknown. Test signals are correct die/socket ID reporting and package classification across CEM/OAM/APU devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_3.h

Purpose: declaration header for SMUIO v13.0.3 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v13_0_3_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: makes the v13.0.3 topology callback table available to SOC setup.

Risks and test signals: build linkage plus correct die/socket/package callback dispatch validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_6.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_6.c

Purpose: minimal SMUIO v13.0.6 ROM offset operation table.

Important APIs, types, and functions: defines `smuio_v13_0_6_funcs` with `get_rom_index_offset` and `get_rom_data_offset`.

Control flow: helpers return SOC15 offsets for `regROM_INDEX` and `regROM_DATA` using v13.0.6 generated headers.

State and persistence: no mutable software state; returned offsets point to hardware ROM index/data registers.

Dependencies and integration points: used by ROM/VBIOS access code through the generic SMUIO function table for matching ASICs.

Risks and test signals: this variant lacks CG/topology callbacks, so callers must tolerate NULL operations. Test signals are successful VBIOS ROM reads on v13.0.6 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_6.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_6.h

Purpose: declaration header for SMUIO v13.0.6 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v13_0_6_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: exposes minimal ROM callbacks to SOC setup.

Risks and test signals: correct descriptor selection and ROM callback use validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v14_0_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v14_0_2.c

Purpose: SMUIO v14.0.2 operations for ROM offsets and a coherent 64-bit GPU clock counter read.

Important APIs, types, and functions: defines `smuio_v14_0_2_funcs` with ROM index/data callbacks and `get_gpu_clock_counter`.

Control flow: ROM helpers return SOC15 offsets. Clock-counter helper disables preemption, reads upper, lower, then upper again from golden TSC registers, rereads lower if upper changed, reenables preemption, and combines high/low into a 64-bit value.

State and persistence: state is hardware ROM and golden TSC counter registers. No software persistence.

Dependencies and integration points: used by timing/profiling code and ROM access paths through `amdgpu_smuio_funcs`; depends on v14.0.2 generated SMUIO headers and Linux preemption control.

Risks and test signals: the double-read handles rollover but only if registers behave as expected. Preemption is disabled briefly, so the path should stay fast. Test signals are monotonic clock counter reads, rollover behavior, and successful ROM offset use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v14_0_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v14_0_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v14_0_2.h

Purpose: declaration header for SMUIO v14.0.2 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v14_0_2_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: exposes v14.0.2 ROM and clock-counter callbacks.

Risks and test signals: build linkage and correct clock-counter dispatch validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v14_0_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_0.c

Purpose: SMUIO v15.0.0 operation table exposing only the GPU golden TSC clock counter.

Important APIs, types, and functions: defines `smuio_v15_0_0_funcs` with `get_gpu_clock_counter`.

Control flow: the counter read disables preemption, reads upper/lower/upper, rereads lower on upper rollover, reenables preemption, and returns a combined 64-bit counter.

State and persistence: state is the hardware golden TSC counter registers; no software state persists.

Dependencies and integration points: used by generic amdgpu timing paths through `amdgpu_smuio_funcs`; depends on SMUIO 15.0.0 generated register headers and preemption control.

Risks and test signals: no ROM/topology callbacks are provided, so callers must handle NULL operations. Test signals are monotonic counter reads and correct version dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_0.h

Purpose: declaration header for SMUIO v15.0.0 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v15_0_0_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: exposes the v15.0.0 clock-counter callback table.

Risks and test signals: build linkage and monotonic counter callback dispatch validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_8.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_8.c

Purpose: SMUIO v15.0.8 operations for ROM offsets, GPU clock counter, topology IDs, host-GPU XGMI detection, package type, and placeholder ROM clock-gating support.

Important APIs, types, and functions: defines `smuio_v15_0_8_funcs` with ROM callbacks, `get_gpu_clock_counter`, `get_die_id`, `get_socket_id`, `is_host_gpu_xgmi_supported`, `update_rom_clock_gating`, `get_clock_gating_state`, and `get_pkg_type`. Ethernet-switch and custom-HBM helpers are present but compiled out.

Control flow: ROM helpers return SOC15 offsets; ROM CG update is a no-op. Clock counter uses the upper/lower/upper rollover-safe read. Die/socket/XGMI/package helpers read `regSMUIO_MCM_CONFIG`; XGMI tests topology bit 0 and package type maps bits `0xC` to BB or CEM, otherwise unknown.

State and persistence: state is SMUIO register contents. No persistent software state exists.

Dependencies and integration points: feeds ROM access, timing, topology, and package decisions through `amdgpu_smuio_funcs` for v15.0.8 devices.

Risks and test signals: ROM CG state query reads `regCGTT_ROM_CLK_CTRL0` while update does nothing, which can produce read-only reporting semantics. Package mapping ignores lower package bits except `0xC` mask. Test signals are ROM reads, monotonic counter reads, die/socket reporting, XGMI topology detection, and package classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_8.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_8.h

Purpose: declaration header for SMUIO v15.0.8 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v15_0_8_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: exposes v15.0.8 SMUIO callbacks to SOC setup.

Risks and test signals: build linkage and correct dispatch of ROM, clock, and topology callbacks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v9_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v9_0.c

Purpose: SMUIO v9 operation table for ROM index/data offsets and ROM clock-gating control.

Important APIs, types, and functions: defines `smuio_v9_0_funcs` with ROM offset callbacks, `update_rom_clock_gating`, and `get_clock_gating_state`.

Control flow: ROM helpers return SOC15 offsets for `mmROM_INDEX` and `mmROM_DATA`. Clock-gating update skips APUs, clears ROM soft overrides when enabling supported MGCG, and sets overrides otherwise. Query reads override0 to report ROM MGCG.

State and persistence: state is hardware `mmCGTT_ROM_CLK_CTRL0` and software feature flags in `adev`; no persistent storage.

Dependencies and integration points: used by generic ROM/VBIOS and CG reporting paths for SMUIO v9 ASICs.

Risks and test signals: APU register avoidance is required. Query only checks one override bit. Test signals are VBIOS access, CG flag reporting, and safe operation on APU/discrete variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v9_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v9_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v9_0.h

Purpose: declaration header for SMUIO v9 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v9_0_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: exposes v9 ROM/clock-gating callbacks to SOC15 common code.

Risks and test signals: build linkage and successful version-specific ROM/CG callback dispatch validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v9_0.h -->
