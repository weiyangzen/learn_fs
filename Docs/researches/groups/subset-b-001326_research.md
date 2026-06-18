# Research: subset-b-001326

Grouped research for AMDGPU CIK AtomBIOS encoder, I2C, interrupt handler, SDMA, packet definition, and clear-state data sources. Each file section preserves the original source path for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_encoders.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_encoders.c

Purpose: implements the legacy AtomBIOS-backed display encoder control layer for AMDGPU. It translates DRM encoder/connector state into AtomBIOS command-table calls for DAC, DVO, DIG encoder, UNIPHY/LVTMA transmitter, external encoder, eDP panel power, CRTC source selection, BIOS scratch registers, load detection, and LVDS/DIG private-data allocation.

Important APIs and functions: backlight helpers read/write `mmBIOS_SCRATCH_2`, expose Linux `backlight_ops`, and register/unregister native or ACPI backlight devices. `amdgpu_atombios_encoder_mode_fixup()` updates active-device routing, CRTC timing invariants, panel scaling, and DP link configuration. `amdgpu_atombios_encoder_get_encoder_mode()` maps connector type, DP bridge presence, HDMI audio policy, DP sink type, and analog/digital routing to Atom encoder modes. `amdgpu_atombios_encoder_setup_dig_encoder()`, `amdgpu_atombios_encoder_setup_dig_transmitter()`, `amdgpu_atombios_encoder_setup_external_encoder()`, `amdgpu_atombios_encoder_setup_dac()`, and `amdgpu_atombios_encoder_setup_dvo()` are command-table marshalling functions with version-specific parameter unions. `amdgpu_atombios_encoder_dpms()` drives the high-level enable/disable paths. `amdgpu_atombios_encoder_get_lcd_info()` parses Atom LVDS data and optional LCD records, including fake EDID and panel-size patches.

Control flow: display enable for a DIG encoder runs through `dpms(ON)` -> `setup_dig(ATOM_ENABLE)`: choose DP panel mode, set up internal DIG encoder, set up panel mode, initialize external encoder if present, power on eDP panel, enable transmitter, run DP link training and DP video-on, restore LCD backlight, then enable the external encoder. Disable reverses that sequence with DP video-off, external encoder disable, LCD backlight off, DP sink D3, transmitter disable, and eDP panel power-off. CRTC routing is programmed separately through `SelectCRTC_Source`, with per-table-version fields for CRTC id, encode mode, destination bpc, and internal encoder id.

State and persistence: persistent state is mostly hardware/firmware state: BIOS scratch registers 0, 2, 3, and 6, display connector status bits, backlight level, HPD/eDP state, transmitter/encoder programmed state, and `amdgpu_encoder_atom_dig` fields such as `dig_encoder`, `linkb`, `panel_mode`, `coherent_mode`, `backlight_level`, and `bl_dev`. Fake EDID parsed from Atom tables may be stored in `adev->mode_info.bios_hardcoded_edid`.

Dependencies and integration points: depends on DRM connector/encoder/CRTC objects, AMDGPU connector helpers, AtomBIOS parser and command execution (`amdgpu_atom_parse_cmd_header`, `amdgpu_atom_execute_table`, data-table parsing), DP helpers from `atombios_dp.h`, ACPI video backlight policy, Linux backlight core, and register definitions from BIOS/DCE/BIF headers. It integrates with display mode-setting, DP link training, connector detection, external DP bridge setup, and BIOS scratch-register conventions used by firmware and boot/display handoff.

Risks: AtomBIOS table version handling is broad and fragile; unknown versions log errors and may leave hardware partly configured. The file contains suspicious source artifacts in this tree, including a duplicated `amdgpu_atombios_encoder_setup_dig_encoder` signature line and an extra-looking brace near backlight finalization, which are compile-risk signals. Several branches assume connector private data exists when connector lookup succeeds. Hardware sequencing is order-sensitive for eDP power, DP training, backlight, and external encoder actions. Scratch-register updates are read-modify-write operations that can race with other firmware/users if not serialized by the surrounding display stack. Bad LCD record parsing aborts only the local loop and trusts firmware-provided lengths.

Test signals: build coverage should catch syntax drift and union/table-version mismatches. Runtime signals include successful module load, DRM hotplug and connector detection, DP/eDP link training, brightness changes via `/sys/class/backlight`, HDMI/DVI/DP mode validation, suspend/resume display restoration, and dmesg absence of `Unknown table version`, `Bad LCD record`, or backlight registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_encoders.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_encoders.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_encoders.h

Purpose: declares the AtomBIOS encoder API used by AMDGPU display code. It is the public header for the legacy AtomBIOS display-encoder implementation in `atombios_encoders.c`.

Important APIs and types: exposes backlight accessors and lifecycle (`get_backlight_level_from_reg`, `set_backlight_level_to_reg`, `get_backlight_level`, `set_backlight_level`, `init_backlight`, `fini_backlight`), encoder classification and mode helpers (`is_digital`, `mode_fixup`, `get_encoder_mode`), DIG/DAC/display sequencing (`setup_dig_encoder`, `setup_dig_transmitter`, `set_edp_panel_power`, `dpms`, `set_crtc_source`, `init_dig`), detection and scratch state (`dac_detect`, `dig_detect`, `setup_ext_encoder_ddc`, `set_bios_scratch_regs`), and private-data constructors (`get_lcd_info`, `get_dig_info`). The key return types are DRM connector status and `struct amdgpu_encoder_atom_dig *`.

Control flow: this header does not implement control flow, but its declarations define the display stack call graph: connector/encoder setup code obtains DIG/LCD private data, mode-setting calls fixup and CRTC-source programming, DPMS calls the AtomBIOS encoder/transmitter sequence, connector detection calls DAC/DIG detect, and driver teardown calls backlight finalization.

State and persistence: declared functions mutate hardware registers, AtomBIOS scratch registers, backlight devices, connector detect state, and `amdgpu_encoder_atom_dig` private state. The header itself is stateless.

Dependencies and integration points: consumers must already know DRM and AMDGPU core types (`struct drm_encoder`, `struct drm_connector`, `struct drm_display_mode`, `struct amdgpu_device`, `struct amdgpu_encoder`, and `struct amdgpu_encoder_atom_dig`). It integrates the AtomBIOS display path with the rest of AMDGPU mode-setting and connector setup.

Risks: the header relies on prior type declarations from including translation units rather than including all defining headers itself. Prototype drift against `atombios_encoders.c` would break display builds. The API surface exposes many low-level sequencing operations, so callers must preserve ordering and valid encoder/connector associations.

Test signals: compile all AMDGPU display objects that include this header. Link success confirms implementation/prototype alignment. Runtime display tests exercise the declared entry points indirectly through mode set, DPMS, hotplug detection, and backlight lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_encoders.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_i2c.c

Purpose: provides a hardware-assisted I2C adapter implementation that executes AtomBIOS `ProcessI2cChannelTransaction` command-table calls. It lets AMDGPU perform DDC/AUX-adjacent legacy I2C transactions through BIOS-described I2C lines.

Important APIs and functions: `amdgpu_atombios_i2c_xfer()` is the Linux I2C adapter transfer callback. `amdgpu_atombios_i2c_func()` advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`. `amdgpu_atombios_i2c_channel_trans()` is a direct one-byte channel transaction helper. The internal `amdgpu_atombios_i2c_process_i2c_ch()` serializes a single AtomBIOS transaction and copies read data from Atom scratch space.

Control flow: `xfer()` handles zero-length bus probes as a write transaction, then iterates each `i2c_msg`. It chunks reads to `ATOM_MAX_HW_I2C_READ` and writes to `ATOM_MAX_HW_I2C_WRITE`, calls the internal transaction helper, and returns either the number of messages or the first error. The helper locks the channel mutex, prepares `PROCESS_I2C_CHANNEL_TRANSACTION_PS_ALLOCATION`, encodes register index/write payload for write transactions, sets I2C speed, slave address, byte count, and line number, executes the Atom table, checks BIOS status, copies swapped read bytes from Atom scratch, and unlocks.

State and persistence: there is no persistent file-local state. Runtime state includes the per-channel mutex, `chan->rec.i2c_id`, AtomBIOS scratch buffer contents, and the hardware I2C transaction state. Error status is returned as `-EINVAL` for invalid write lengths/buffers and `-EIO` for BIOS transaction failure.

Dependencies and integration points: depends on Linux I2C adapter/message APIs, DRM/AMDGPU device conversion, AtomBIOS command table indexes, `amdgpu_atom_execute_table`, and `amdgpu_atombios_copy_swap`. It integrates with connector probing and EDID/DDC paths that bind AMDGPU I2C channels to adapters.

Risks: write transactions are limited to three bytes because of the AtomBIOS helper, not necessarily hardware. The direct `amdgpu_atombios_i2c_channel_trans()` does not lock the channel mutex and uses the caller-provided slave address directly rather than left-shifting like the adapter path, so callers must match BIOS expectations. The transaction helper assumes Atom scratch is valid and large enough for the read. Chunking makes long writes multiple independent transactions, which may not match devices requiring combined transfers.

Test signals: EDID reads over DDC, monitor hotplug probing, I2C bus probe behavior, and dmesg absence of `hw_i2c error` or "tried to write too many bytes" messages. Compile should verify AtomBIOS parameter struct compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_i2c.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_i2c.h

Purpose: declares the AtomBIOS-backed I2C transfer interface for AMDGPU.

Important APIs: `amdgpu_atombios_i2c_xfer()` is the adapter transfer callback; `amdgpu_atombios_i2c_func()` returns I2C capability flags; `amdgpu_atombios_i2c_channel_trans()` exposes a direct one-byte transaction helper over a selected AtomBIOS line.

Control flow: no implementation is present, but the declarations are used by AMDGPU I2C adapter setup and low-level display/firmware helpers that need AtomBIOS I2C transactions.

State and persistence: the header is stateless. Declared functions operate on `struct i2c_adapter`, `struct i2c_msg`, and `struct amdgpu_device` state and affect hardware I2C transactions.

Dependencies and integration points: relies on Linux I2C types and AMDGPU device types being visible to includers. It connects AMDGPU display probing code with the implementation in `atombios_i2c.c`.

Risks: prototype drift would break adapter registration. The direct helper signature uses raw byte arguments, making address/offset interpretation a caller responsibility.

Test signals: build users of AtomBIOS I2C adapter setup; runtime EDID/DDC reads verify the declared transfer path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c

Purpose: implements the common ASIC support for CIK-generation AMD GPUs/APUs. It provides register accessors, golden register programming, BIOS reads, reset selection/execution, UVD/VCE clock programming, PCIe link/ASPM tuning, allowed register reads, HDP coherency hooks, video capability reporting, common IP block lifecycle, and ASIC-specific IP block assembly.

Important APIs and functions: `cik_set_ip_blocks()` is the public entry used to assemble the IP block list for Bonaire, Hawaii, Kaveri, Kabini, and Mullins. `cik_srbm_select()` selects indexed ME/pipe/queue/VMID register instances. `cik_common_early_init()` installs indirect register accessors and `cik_asic_funcs`. `cik_common_hw_init()` programs golden registers and PCIe behavior. ASIC functions include BIOS read helpers, `cik_read_register()`, reset methods, xclk/config-memsize queries, UVD/VCE clock setters, HDP flush/invalidate, PCIe usage/replay counters, BACO support, and video codec query.

Control flow: early init wires register accessor function pointers for SMC, PCIe, UVD context, and DIDT spaces, installs ASIC function callbacks, reads revision id, and sets clock/power-gating flags plus external revision id by ASIC type. Hardware init applies per-chip golden register arrays under the GRBM index mutex, then enables PCIe gen2/gen3 and ASPM. Reset selection honors the module reset method, falls back to BACO for supported dGPU ASICs, otherwise PCI config reset, while APUs skip full reset. IP block setup adds common, GMC, IH, GFX, SDMA, SMU, display, UVD, and VCE blocks with display variants selected from virtual display, DC support, or DCE generation.

State and persistence: mutates `adev` function tables, `cg_flags`, `pg_flags`, `rev_id`, `external_rev_id`, `has_hw_reset`, and hardware registers. Golden register arrays encode persistent bring-up policy but are static const data. BIOS reads temporarily change BUS/VGA/ROM control registers and restore them. Reset code updates AtomBIOS engine-hung scratch state. PCIe usage samples counters over a one-second window.

Dependencies and integration points: tightly depends on AMDGPU core, AtomBIOS, GMC/GFX/IH/SDMA/DCE/UVD/VCE/SMU IP block definitions, Linux PCIe helpers, register headers for CIK subblocks, display manager/vkms selection, and KFD-facing common hardware setup. It provides the common foundation used by the IP block framework before later blocks initialize.

Risks: this file is hardware-sequencing sensitive; incorrect golden registers, register masks, or PCIe/ASPM programming can hang devices. The source tree contains suspicious duplicate text in `cik_set_uvd_clock()` and `cik_get_pcie_usage()` that is a compile-risk signal. Reset flow differs between APUs and dGPUs and depends on BACO support. Allowed-register reads must remain constrained to avoid unsafe arbitrary MMIO exposure. PCIe link training loops and ASPM tweaks depend on root-port capabilities and device quirks.

Test signals: compile, CIK dGPU/APU module load, IP block init ordering in dmesg, successful firmware/display/GFX initialization, GPU reset tests, suspend/resume, PCIe speed reporting, video codec query ioctls, UVD/VCE clock changes under decode/encode workloads, and absence of timeout or link training failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.h

Purpose: small public header for CIK common support shared by AMDGPU CIK IP blocks.

Important APIs and constants: defines `CIK_FLUSH_GPU_TLB_NUM_WREG` as the number of register writes needed for a CIK GPU TLB flush sequence. Declares `cik_srbm_select()` for selecting ME/pipe/queue/VMID indexed register instances, `cik_set_ip_blocks()` for adding ASIC-specific IP blocks to an AMDGPU device, and `legacy_doorbell_index_init()` for legacy doorbell setup.

Control flow: the header has no implementation. Its declarations support the startup path where common CIK code installs IP blocks and other blocks, especially SDMA/GFX, select indexed registers during initialization or command emission.

State and persistence: stateless header. Declared functions mutate hardware register selection, device IP block lists, and doorbell-index layout.

Dependencies and integration points: depends on `struct amdgpu_device` and fixed-width AMDGPU integer types from including context. Used by `cik.c`, `cik_sdma.c`, and other CIK-generation blocks.

Risks: the TLB flush constant must stay aligned with the actual GMC flush emission sequence used by SDMA ring sizing. Prototype drift can break cross-IP initialization. `cik_srbm_select()` users must restore default selection after indexed access.

Test signals: CIK build coverage, VM flush ring emission sizing tests, and runtime validation of IP block addition and indexed register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.c

Purpose: implements the CIK interrupt handler (IH) IP block. CIK writes interrupt vectors into a GPU-accessible ring buffer; this file initializes that ring, enables/disables hardware interrupt delivery, decodes 128-bit interrupt vectors, handles ring pointer management and overflow, and exposes IH lifecycle callbacks to the AMDGPU IP framework.

Important APIs and functions: `cik_ih_irq_init()` programs IH registers, ring base, ring size, writeback pointer address, MSI-dependent control bits, and enables interrupts. `cik_ih_get_wptr()` reads the write pointer from writeback memory and handles overflow. `cik_ih_decode_iv()` decodes source id, source data, ring id, VMID, and PASID from the current ring entry and advances rptr by 16 bytes. `cik_ih_set_rptr()` writes the hardware read pointer. IP callbacks include early/sw/hw init/fini, suspend/resume, idle wait, soft reset, and no-op gating hooks. `cik_ih_ip_block` exports this as an IH block version 2.0.

Control flow: early init adds the IRQ domain and installs IH function pointers. SW init allocates the hardware IH ring and software IH ring, then initializes AMDGPU IRQ infrastructure. HW init disables interrupts, programs ring and interrupt control registers, sets writeback, clears pointers, enables PCI bus mastering, enables interrupts, and marks the software IH ring enabled if allocated. Interrupt processing elsewhere calls the function table to get wptr, decode entries until rptr catches wptr, and commit rptr.

State and persistence: mutates `adev->irq.ih` and `adev->irq.ih_soft` ring fields (`enabled`, `rptr`, writeback pointers), hardware IH registers, and IRQ domain/core state. Overflow handling intentionally advances `ih->rptr` to a recent vector boundary and clears the hardware overflow flag.

Dependencies and integration points: depends on AMDGPU IRQ and IH core helpers, Linux PCI bus mastering, BIF/OSS register definitions, writeback memory, and the AMDGPU IP block framework. SDMA/GFX/display interrupt sources are decoded through this common vector path and dispatched by AMDGPU IRQ code.

Risks: IH pointer units are bytes while ring array indexing is dwords, so off-by-unit errors are dangerous. Overflow recovery drops old vectors by moving rptr, which can lose fence/hotplug/error events. Writeback pointer memory must be coherent and correctly addressed. Soft reset only toggles IH if SRBM reports busy. MSI-dependent `RPTR_REARM` behavior must match interrupt mode.

Test signals: IRQ domain initialization, module load without IH timeout, interrupt storm/overflow logging, fence completion from SDMA/GFX interrupts, hotplug interrupt delivery, suspend/resume IRQ recovery, and successful soft reset under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.h

Purpose: exports the CIK interrupt handler IP block descriptor.

Important API: declares `extern const struct amdgpu_ip_block_version cik_ih_ip_block`, used by CIK common setup to add the IH block to the device IP block list.

Control flow: no implementation. `cik_set_ip_blocks()` consumes this symbol during ASIC-specific IP block assembly, after common/GMC and before GFX/SDMA blocks.

State and persistence: stateless header; the referenced block owns IH ring and IRQ state when initialized.

Dependencies and integration points: requires the AMDGPU IP block type definition from includers. Integrates `cik_ih.c` with `cik.c`.

Risks: if the symbol declaration drifts from the definition, CIK IP block registration fails at build/link time. Ordering remains a caller responsibility.

Test signals: link success and runtime IP block list containing the IH block for supported CIK ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.c

Purpose: implements the CIK system DMA (SDMA) IP block. CIK has two asynchronous DMA engines used for graphics and compute copies, VM page-table updates, fences, traps, and buffer fill/copy acceleration. This file loads SDMA firmware, initializes rings, emits SDMA packets, handles SDMA interrupts, and provides IP/ring/buffer/VM function tables.

Important APIs and functions: firmware lifecycle is handled by `cik_sdma_init_microcode()`, `cik_sdma_load_microcode()`, and `cik_sdma_free_microcode()`. Ring pointer and packet methods include `get_rptr`, `get_wptr`, `set_wptr`, `emit_ib`, `emit_fence`, `emit_hdp_flush`, `emit_pipeline_sync`, `emit_vm_flush`, `emit_wreg`, `insert_nop`, and `pad_ib`. Hardware setup flows through `cik_sdma_start()`, `cik_sdma_gfx_resume()`, `cik_sdma_enable()`, `cik_ctx_switch_enable()`, and soft reset. Test paths are `cik_sdma_ring_test_ring()` and `cik_sdma_ring_test_ib()`. VM helpers emit copy/write/generate-PTE packets. IRQ handlers process trap fence interrupts and illegal instruction faults. Buffer functions expose copy/fill acceleration to memory management.

Control flow: early init sets `adev->sdma.num_instances` to two, loads required firmware names by ASIC type, installs function tables, and registers VM PTE schedulers. SW init registers legacy IRQ ids for traps and illegal instructions and initializes one ring per SDMA instance. HW init loads microcode after halting engines, enables context switching, programs each gfx ring buffer and writeback pointer, enables RB/IB, unhalts engines, and tests rings. Suspend/hw fini disables context switch and halts engines; resume soft-resets then restarts.

State and persistence: mutates `adev->sdma.instance[]` firmware pointers, firmware/feature versions, burst-NOP capability, ring names and pointers, trap/illegal IRQ source function tables, memory-manager buffer function pointers, clock-gating registers, SDMA microcode memory, and hardware ring registers. Ring packet emission persists command streams in ring/IB memory until consumed by hardware.

Dependencies and integration points: depends on AMDGPU firmware/ucode helpers, ring scheduler/fence/IB helpers, VM/GMC TLB flush emission, AMDGPU IRQ, SDMA packet definitions from `cikd.h`, common SRBM selection from `cik.h`, memory manager buffer callbacks, and CIK register headers. It integrates with IP block init, VM updates, TTM buffer moves, fence processing, and IH decoded interrupt vectors.

Risks: firmware is required; missing or wrong `*_sdma*.bin` stops init. Ring alignment and packet sizes must match SDMA hardware format. This tree contains suspicious duplicated text (`WARN_ONCE(1,` and duplicate `case AMDGPU_SDMA_IRQ_INSTANCE0`) that is a compile-risk signal. RLC compute SDMA queues are marked TODO, so only gfx queues are fully managed. Illegal instruction handling indexes by `entry->ring_id` and assumes a valid instance. Clock-gating writes are low-level and ASIC-flag dependent. Soft reset unconditionally halts both SDMA engines before toggling SRBM reset bits.

Test signals: firmware request logs, ring test and IB test success, fence completion through SDMA trap IRQs, VM page table updates under GPUVM workloads, buffer copy/fill acceleration under TTM moves, suspend/resume restart, clock-gating transitions, and no `Illegal instruction in SDMA command stream` or SDMA timeout messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.h

Purpose: exports the CIK SDMA IP block descriptor.

Important API: declares `extern const struct amdgpu_ip_block_version cik_sdma_ip_block`, used by CIK common setup to register the SDMA block for each supported CIK ASIC.

Control flow: no implementation. `cik_set_ip_blocks()` consumes this symbol after selecting the appropriate GFX block and before SMU/display/video blocks.

State and persistence: stateless header; the referenced block owns firmware, rings, interrupts, VM PTE callbacks, and buffer-function state when initialized.

Dependencies and integration points: requires AMDGPU IP block type definitions from includers. Integrates `cik_sdma.c` with ASIC IP block assembly in `cik.c`.

Risks: declaration/definition drift breaks link. IP block ordering must ensure common/GMC/IH prerequisites are available before SDMA initialization and interrupt use.

Test signals: build/link success and runtime IP block list showing SDMA block for Bonaire/Hawaii/Kaveri/Kabini/Mullins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cikd.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cikd.h

Purpose: defines CIK-generation register offsets, packet constructors, command opcodes, bit masks, display offsets, memory-type constants, SDMA packet fields, VCE command ids, and raster/backend mapping masks shared by CIK AMDGPU blocks.

Important APIs and definitions: memory type masks for `MC_SEQ_MISC0`, display CRTC/HPD/audio endpoint offsets, SRBM selector field helpers, PM4 packet helpers (`PACKET0`, `PACKET2`, `PACKET3`, `PACKET3_COMPUTE`), a large set of `PACKET3_*` opcode ids and field helpers, SDMA instance offsets and `SDMA_PACKET()`, SDMA opcodes/subopcodes for NOP/COPY/WRITE/IB/FENCE/TRAP/SEMAPHORE/POLL/COND_EXEC/FILL/PTE/TIMESTAMP/SRBM_WRITE, VCE command ids, LDS/private base helpers, KFD SDMA queue offset, and raster-config field masks.

Control flow: no executable control flow. The macros are consumed by ring emitters and register programming code to generate correct command stream words and MMIO offsets. `cik_sdma.c` uses SDMA definitions extensively; GFX and VM paths use PM4 packet definitions; `cik.c` and display code use register offsets and masks.

State and persistence: stateless compile-time definitions. The values encode hardware ABI contracts; changing them changes command streams and MMIO programming.

Dependencies and integration points: included by CIK common, IH, SDMA, GFX, and related blocks. It bridges generated/ASIC register headers and driver code that needs hand-authored packet/register constants.

Risks: any incorrect opcode, shift, mask, or offset can corrupt command streams, hang rings, or program the wrong register. Some macros assume a `REG_SET` helper exists from other headers. The file uses a broad include guard name `CIK_H`, which can conflict conceptually with `cik.h`'s `__CIK_H__` but not textually. Because these are raw hardware constants, review should compare against ASIC documentation or known-good upstream headers.

Test signals: compile of all CIK ring emitters, packet decoder tests where available, SDMA/GFX ring tests, VM flush behavior, VCE command submission, display register programming, and hardware smoke tests under graphics/compute/video workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cikd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_ci.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_ci.h

Purpose: contains the CIK/CI clear-state context-register payload used to initialize or reset graphics pipeline context state. It is data-only: arrays of register default values grouped into extents, plus a section table exported as `ci_cs_data`.

Important APIs and data: defines seven `ci_SECT_CONTEXT_def_*` arrays of unsigned register values. `ci_SECT_CONTEXT_defs[]` maps those arrays to context register start indexes and register counts, for example start `0x0000a000` count 212 and later context-register ranges. `ci_cs_data[]` maps the context extent list to `SECT_CONTEXT` using structures from `clearstate_defs.h`.

Control flow: no executable code. Consumers iterate `ci_cs_data`, then each `cs_extent_def`, and write or packetize the values into the corresponding context register ranges. Holes in the arrays are represented as zero-valued entries with comments naming them as holes.

State and persistence: static const data only. When consumed, it affects GPU graphics context state such as DB/PA/CB/VGT/SPI/SX registers, scissor defaults, viewport z ranges, shader masks, coherency bases, and other context registers.

Dependencies and integration points: depends on `struct cs_extent_def`, `struct cs_section_def`, and `enum section_id` from `clearstate_defs.h`. It integrates with the GFX clear-state or command preamble path for CIK-class GPUs.

Risks: the data must exactly match CIK context-register layout. A wrong register count, start offset, or default value can cause rendering corruption or GPU hangs. Because the arrays contain many holes and magic defaults, manual edits are high risk. Comments are descriptive but not enforced; consumers rely on extent counts.

Test signals: compile consumers that include this header, command submission using clear-state preambles, graphics rendering correctness, GPU reset/recovery, and comparison against known-good upstream clear-state tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_ci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_defs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_defs.h

Purpose: defines the small schema used by clear-state data headers to describe groups of register defaults.

Important APIs and types: `enum section_id` identifies section categories: `SECT_NONE`, `SECT_CONTEXT`, `SECT_CLEAR`, and `SECT_CTRLCONST`. `struct cs_extent_def` points to an extent array and records the starting register index plus register count. `struct cs_section_def` maps an extent list to a section id.

Control flow: no executable logic. Clear-state consumers interpret these structures to know which register section a table belongs to and how to walk its extents.

State and persistence: stateless definitions. The data structures describe persistent static clear-state tables such as `clearstate_ci.h`.

Dependencies and integration points: used by ASIC-specific clear-state headers and graphics command/preamble code. It is intentionally generic enough to represent context, clear, and control-constant sections.

Risks: there is no length field on `cs_section_def` and no explicit sentinel shown in this header, so consumers must know table sizes from surrounding declarations or conventions. `extent` points to raw unsigned int arrays, so type safety is limited. Field semantics must remain stable for all clear-state data headers.

Test signals: compile graphics consumers, static validation that extent counts match array lengths, and runtime clear-state command submission/rendering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_defs.h -->
