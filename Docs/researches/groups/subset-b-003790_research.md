# Research Group subset-b-003790

Source-tree-aligned grouped research for subset B work item `subset-b-003790`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-prv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-prv.h

## Purpose

`ipu-prv.h` is the private coordination header for the i.MX IPUv3 core driver. It centralizes common-register offsets, IDMAC register helpers, module enable bits, core-private state, and init/exit declarations for the IPU sub-blocks used by capture, display, image conversion, and prefetch/render helpers.

## Important APIs, Types, And Functions

Important definitions include `IPU_CM_*_REG_OFS`, `IPU_CONF`, flow-control register bit masks, IDMAC channel register macros, `IPU_NUM_IRQS`, `enum ipu_modules`, `struct ipuv3_channel`, and `struct ipu_soc`. Inline helpers `ipu_idmac_read()` and `ipu_idmac_write()` wrap IDMAC MMIO. The header declares module lifecycle functions such as `ipu_csi_init()`, `ipu_vdi_init()`, `ipu_smfc_init()`, `ipu_dp_init()`, `ipu_dc_init()`, `ipu_cpmem_init()`, `ipu_pre_*()`, and `ipu_prg_lookup_by_phandle()`.

## Control Flow

The header has no executable flow, but it defines the call graph used by IPU core probe and teardown: the core allocates `struct ipu_soc`, maps common and IDMAC registers, then initializes sub-block private objects that store back-pointers in `ipu_soc`. Consumer drivers later use exported public APIs to acquire channels or submodules whose private implementations rely on these declarations and register definitions.

## State And Persistence Behavior

Persistent state is represented by `struct ipu_soc`: device identity, type, common locks, channel list, common/IDMAC MMIO windows, IRQ domain, clock, use count, and pointers to submodule-private state. Hardware state persists in IPU common, flow, interrupt, buffer-ready/current-buffer, and IDMAC registers until changed by submodule code or reset.

## Dependencies And Integration Points

It depends on Linux device, clock, platform, MMIO, list, mutex/spinlock, and `video/imx-ipu-v3.h` public definitions. It integrates IPU internals with DRM, V4L2, capture, display, image conversion, PRE/PRG, and platform-driver submodules through shared private prototypes.

## Risks And Test Signals

Risks include register-offset drift across IPU revisions, shared bit definitions being used by multiple submodules with different locking expectations, unchecked macro arguments for channel register selection, and private struct changes breaking out-of-file users. Test signals are full IPUv3 build coverage, probe/remove on supported i.MX variants, IDMAC channel allocation, interrupt routing, and capture/display pipelines that exercise CSI, SMFC, VDI, IC, DP/DC/DI/DMFC, PRE, and PRG paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-prv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-smfc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-smfc.c

## Purpose

`ipu-smfc.c` implements the Sensor Multi-FIFO Controller helper for IPUv3. It configures SMFC channel-to-CSI/MIPI mapping, burst size, FIFO watermarks, module gating, and channel ownership for four SMFC channels feeding capture paths.

## Important APIs, Types, And Functions

Private state is split between `struct ipu_smfc_priv`, which owns the MMIO base, spinlock, IPU pointer, channel array, and module `use_count`, and `struct ipu_smfc`, which tracks a channel number and `inuse` flag. Exported functions are `ipu_smfc_set_burstsize()`, `ipu_smfc_map_channel()`, `ipu_smfc_set_watermark()`, `ipu_smfc_enable()`, `ipu_smfc_disable()`, `ipu_smfc_get()`, and `ipu_smfc_put()`. Lifecycle is `ipu_smfc_init()` and empty `ipu_smfc_exit()`.

## Control Flow

Initialization allocates `ipu_smfc_priv`, stores it in `ipu->smfc_priv`, maps the SMFC register page, initializes the lock, and pre-populates four channel descriptors. Clients call `ipu_smfc_get()` to reserve a channel, configure mapping, burst, and watermarks under the shared spinlock, then call `ipu_smfc_enable()`. The first enable turns on `IPU_CONF_SMFC_EN`; later enables only increment the count. Disable decrements and turns the module off when the count reaches zero.

## State And Persistence Behavior

Software state persists in the devm-managed `ipu_smfc_priv` and per-channel `inuse` flags. `use_count` tracks active users but is not tied to channel ownership. Hardware state persists in `SMFC_MAP`, `SMFC_WMC`, and `SMFC_BS` until reprogrammed. The mapped MMIO region is devm-managed; `ipu_smfc_exit()` performs no explicit cleanup.

## Dependencies And Integration Points

It depends on `ipu-prv.h`, `ipu_module_enable()`, `ipu_module_disable()`, Linux MMIO, export symbols, and spinlocks. Capture drivers integrate through the exported SMFC API to connect CSI/MIPI inputs to IDMAC capture channels.

## Risks And Test Signals

Risks include accepting unchecked burst, watermark, CSI, and MIPI field values, a disable-underflow path that clamps after temporarily going negative, no validation that an enabled channel was reserved, and empty explicit teardown. Test by reserving all four channels, checking `-EBUSY` and `-EINVAL` paths, programming each register field, running concurrent get/put/configure calls, and verifying SMFC module enable/disable balance across multiple capture streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-smfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-vdi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-vdi.c

## Purpose

`ipu-vdi.c` implements the IPUv3 Video De-Interlacer helper. It programs VDI frame size, chroma format, motion mode, field order, FIFO burst/watermark defaults, module gating, and lookup for capture/display pipelines that need deinterlacing.

## Important APIs, Types, And Functions

`struct ipu_vdi` stores the VDI MMIO base, module enable mask, spinlock, use count, and parent `ipu_soc`. Exported APIs are `ipu_vdi_set_field_order()`, `ipu_vdi_set_motion()`, `ipu_vdi_setup()`, `ipu_vdi_enable()`, `ipu_vdi_disable()`, `ipu_vdi_get()`, and `ipu_vdi_put()`. Internal helpers `ipu_vdi_read()` and `ipu_vdi_write()` wrap register access to `VDI_FSIZE` and `VDI_C`.

## Control Flow

Initialization allocates the VDI object, installs it in `ipu->vdi_priv`, maps a page at the supplied base, records the module bit, and initializes the spinlock. Setup writes `(yres - 1, xres - 1)` into `VDI_FSIZE`, derives 4:2:2 versus 4:2:0 mode from the media bus code, and applies burst and watermark defaults. Field-order and motion setters update only their fields. Enable/disable gate the IPU module around a reference count.

## State And Persistence Behavior

Persistent software state is the devm-managed `ipu_vdi` object and its `use_count`. `ipu_vdi_get()` simply returns the singleton; `ipu_vdi_put()` is a no-op. Hardware state in `VDI_C` and `VDI_FSIZE` persists across users until explicitly changed or reset.

## Dependencies And Integration Points

It depends on Linux MMIO/spinlocks, V4L2 field and standard constants, media bus format constants from public IPU headers, and `ipu_module_enable()/disable()`. It integrates with deinterlacing paths that configure VDI before feeding the IC or display/capture flow.

## Risks And Test Signals

Risks include singleton access with no ownership tracking, no validation for zero or overflowing dimensions, `VDI_C` setup using OR without clearing prior chroma/burst bits, field-order fallback based on `V4L2_STD_525_60`, and no explicit teardown. Test with 4:2:2 and 4:2:0 inputs, all V4L2 field orders, low/medium/high motion settings, repeated setup changes, enable/disable nesting, and deinterlaced capture output validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-vdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/Kconfig

## Purpose

`Kconfig` declares the `NOVA_CORE` kernel configuration option for the Rust Nova Core NVIDIA GPU driver. It controls whether the core GSP-based driver is built and advertises the driver as work in progress.

## Important APIs, Types, And Functions

The single symbol is `config NOVA_CORE`, a tristate named "Nova Core GPU driver". It depends on `64BIT`, `PCI`, and `RUST`, selects `AUXILIARY_BUS` and `RUST_FW_LOADER_ABSTRACTIONS`, defaults to `n`, and documents the module name `nova_core`.

## Control Flow

There is no runtime flow. At configuration time, selecting `NOVA_CORE=y` or `m` allows the Makefile to build `nova_core.o`; dependency and select clauses ensure PCI, Rust, auxiliary device registration, and firmware-loader abstractions are available.

## State And Persistence Behavior

The file stores no runtime state. Its persistent effect is the generated kernel config symbol, which controls compilation and module availability.

## Dependencies And Integration Points

It integrates with the kernel Kconfig system, Rust-for-Linux support, PCI driver infrastructure, auxiliary bus, and firmware loading. The help text scopes support to NVIDIA GPUs based on GSP, Turing and later.

## Risks And Test Signals

Risks include missing dependencies for Rust DMA/PCI/debugfs features elsewhere in the module, selecting firmware abstractions while leaving other required Rust symbols implicit, and users enabling a non-functional work-in-progress driver. Test signals are `allmodconfig`/targeted Rust kernel builds, `modinfo nova_core`, dependency resolution with `CONFIG_RUST=n`, and module load attempts on supported NVIDIA PCI display devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/Makefile

## Purpose

`Makefile` connects the `CONFIG_NOVA_CORE` Kconfig symbol to the built kernel object for the Nova Core Rust GPU driver.

## Important APIs, Types, And Functions

The only build rule is `obj-$(CONFIG_NOVA_CORE) += nova_core.o`, under GPL-2.0 SPDX metadata.

## Control Flow

There is no program flow. During kbuild evaluation, `nova_core.o` is added to the object list when `NOVA_CORE` is enabled as built-in or module.

## State And Persistence Behavior

No runtime state is stored. The persistent build outcome is the presence or absence of the `nova_core` module or built-in object.

## Dependencies And Integration Points

It integrates with kbuild's Rust object handling and the `Kconfig` symbol in the same directory. The crate/module source composition is expected to be described by Rust module files and higher-level build metadata.

## Risks And Test Signals

Risks are mainly build-system drift: object name mismatch with module declarations, missing generated binding inputs, or absent inclusion from a parent Makefile. Test by building with `CONFIG_NOVA_CORE=m` and `y`, confirming `nova_core.o` is produced, and checking that disabling the symbol omits it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/bitfield.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/bitfield.rs

## Purpose

`bitfield.rs` defines the `bitfield!` macro used by Nova register and ABI wrappers to create transparent integer newtypes with typed accessors, builder-style setters, `Debug`, and `Default` implementations.

## Important APIs, Types, And Functions

The macro accepts `vis struct Name(storage) { hi:lo field as type [=> Into] [?=> TryInto]; }`. It generates `#[repr(transparent)]` structs, `From<Name> for storage`, field constants for masks/shifts/ranges, getters, `set_` setters, `Debug`, and default initialization through field defaults. It uses `kernel::bits::genmask_u8/u16/u32/u64`, `kernel::build_assert!`, and `kernel::macros::paste!`.

## Control Flow

Expansion dispatches from the public rule into core struct definition, field collection, bounds checks, accessor generation, then debug/default generation. Getter flow masks and shifts the stored integer, then optionally casts, converts with `From`, or converts with `TryFrom`. Setter flow converts the typed value into the primitive field type, shifts, masks, clears the old field, and writes the new field bits.

## State And Persistence Behavior

Generated bitfield values are copyable transparent wrappers around integer storage. Setters are pure value transformers that return updated `Self`; no external state is persisted. Generated default values depend on each field's `Default` conversion path rather than raw zero alone.

## Dependencies And Integration Points

It is foundational for `regs.rs`, GSP ABI wrappers, and hardware register programming across Nova. It depends on Rust macro expansion, kernel formatting, kernel bit helpers, build-time assertions, and typed conversion traits.

## Risks And Test Signals

Risks include unchecked values being silently masked in setters, bool fields requiring one-bit ranges, storage sizes outside 1/2/4/8 bytes causing build errors, default generation failing for fields whose converted type lacks `Default`, and try-getters surfacing hardware-reserved values. Test with compile-fail coverage for invalid ranges, runtime/unit checks for masks and shifts, debug output, default values, and register wrapper build coverage across all generated bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/bitfield.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/driver.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/driver.rs

## Purpose

`driver.rs` implements the PCI-facing Nova Core driver entry point. It matches NVIDIA display PCI devices, enables BAR0/MMIO and DMA, constructs the GPU runtime, and registers a `nova-drm` auxiliary device.

## Important APIs, Types, And Functions

Important items are `struct NovaCore`, `type Bar0 = pci::Bar<SZ_16M>`, `PCI_TABLE`, `BAR0_SIZE`, `GPU_DMA_BITS`, `AUXILIARY_ID_COUNTER`, and the `pci::Driver` implementation. `probe()` performs initialization through a pinned initializer; `unbind()` delegates cleanup to `Gpu::unbind()`.

## Control Flow

Probe logs, enables PCI memory decoding, marks the device bus-master capable, sets a 47-bit DMA mask, maps BAR0 as a devres-backed region, constructs `Gpu::new()`, and registers an auxiliary device named `nova-drm` with a monotonically allocated ID. Unbind obtains the pinned object from PCI core and invokes `gpu.unbind()` for GPU-level teardown.

## State And Persistence Behavior

`NovaCore` owns a pinned `Gpu` and the devres auxiliary registration. The auxiliary ID counter is global atomic state and does not recycle IDs. BAR0 is held behind an `Arc<Devres<Bar0>>`; device and DMA state persists until unbind/devres cleanup.

## Dependencies And Integration Points

It depends on Rust PCI abstractions, DMA mask APIs, auxiliary bus registration, devres, atomics, and `Gpu`. The PCI ID table matches NVIDIA VGA and 3D display class devices and exposes module metadata through `MODULE_PCI_TABLE`.

## Risks And Test Signals

Risks include broad class/vendor matching before chipset filtering, fixed 16 MiB BAR0 assumption, fixed 47-bit DMA mask, non-recycled auxiliary IDs, and cleanup depending on `Gpu::unbind()` plus devres ordering. Test signals are probe on supported and unsupported NVIDIA GPUs, failure unwinds for BAR/DMA/aux registration, auxiliary device creation, unbind/remove, and DMA mask behavior on constrained systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon.rs

## Purpose

`falcon.rs` provides common support for NVIDIA Falcon microcontrollers used by GSP and SEC2. It abstracts engine register bases, firmware load descriptors, PIO and DMA loading, BROM parameter programming, reset, boot, mailbox access, and chipset-specific HAL selection.

## Important APIs, Types, And Functions

Core types are `Falcon<E>`, `FalconEngine`, `FalconFirmware`, `FalconDmaLoadable`, `FalconPioLoadable`, `FalconDmaLoadTarget`, `FalconBromParams`, `FalconMem`, `PFalconBase`, `PFalcon2Base`, and PIO target adapters. Important methods are `new()`, `reset()`, `dma_reset()`, `pio_load()`, `load()`, `boot()`, `start()`, `wait_till_halted()`, mailbox helpers, `signature_reg_fuse_version()`, `is_riscv_active()`, and `write_os_version()`.

## Control Flow

`Falcon::new()` selects a HAL for the chipset. Reset delegates engine reset, core selection, and memory scrubbing to the HAL, then writes revision metadata from `NV_PMC_BOOT_0`. PIO load writes IMEM/DMEM via port 0 and programs BROM registers. DMA load creates a coherent padded firmware object, configures FBIF to coherent physical sysmem, copies secure IMEM and DMEM in 256-byte chunks through Falcon DMA registers, programs BROM, and sets the boot vector. `load()` chooses PIO or DMA based on HAL.

## State And Persistence Behavior

Software state is a boxed Falcon HAL and device reference. Firmware objects and coherent DMA buffers are temporary during load except where wrappers keep them alive. Hardware state persists in Falcon DMA, IMEM/DMEM, BROM, boot vector, CPU control, mailbox, OS, FBIF, and reset registers.

## Dependencies And Integration Points

It depends on `falcon::hal`, engine marker modules, `regs`, BAR0 IO, coherent DMA allocation, polling, safe numeric conversions, and chipset definitions. It is used by GPU boot to control GSP and SEC2, and by firmware wrappers that implement `FalconFirmware`.

## Risks And Test Signals

Risks include strict 4-byte and 256-byte alignment requirements, DMA address width limits, timeout sensitivity, firmware descriptor bounds errors, boot-vector differences between PIO and DMA paths, and HAL-specific BROM programming. Test by loading SEC2 and GSP firmwares on Turing, GA100, GA10x, and Ada, exercising both PIO and DMA paths, injecting malformed descriptor sizes, validating mailbox exit codes, and checking reset/boot timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/gsp.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/gsp.rs

## Purpose

`falcon/gsp.rs` defines the Falcon engine marker for the GPU System Processor and adds GSP-specific Falcon helper methods.

## Important APIs, Types, And Functions

`struct Gsp(())` implements `RegisterBase<PFalconBase>` at `0x00110000`, `RegisterBase<PFalcon2Base>` at `0x00111000`, and `FalconEngine`. `Falcon<Gsp>::clear_swgen0_intr()` clears SWGEN0 in the Falcon IRQ clear register. `Falcon<Gsp>::check_reload_completed()` polls `NV_PGC6_BSI_SECURE_SCRATCH_14` for the boot-stage handoff bit.

## Control Flow

The type itself is uninstantiable and only supplies compile-time register base selection. During GPU initialization, `Gpu::new()` creates a `Falcon<Gsp>` and clears SWGEN0 so queue messages can signal the CPU. Reload completion, when used, polls until the secure scratch handoff appears or the caller-provided timeout expires.

## State And Persistence Behavior

No Rust state is stored in this file. Hardware effects persist in GSP Falcon IRQ status clear and secure scratch registers. The register bases shape all generic Falcon register accesses for the GSP engine.

## Dependencies And Integration Points

It depends on generic Falcon support, register-base traits, BAR0 IO, polling, and GSP-specific registers. It integrates with `gpu.rs`, GSP boot sequencing, and firmware loading paths that target `FalconFirmware<Target = Gsp>`.

## Risks And Test Signals

Risks include incorrect base addresses, SWGEN0 clearing at the wrong time, and reload polling returning only `true` on success with timeout propagated as an error. Test by confirming GSP Falcon register accesses hit the expected MMIO range, queue interrupts are delivered after boot, and reload handoff polling behaves on resume/reload scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/gsp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal.rs

## Purpose

`falcon/hal.rs` defines the Falcon hardware abstraction layer and dispatches chipset families to Turing or GA102-style implementations.

## Important APIs, Types, And Functions

`LoadMethod` selects `Pio` or `Dma`. `FalconHal<E>` defines `select_core()`, `signature_reg_fuse_version()`, `program_brom()`, `is_riscv_active()`, `reset_wait_mem_scrubbing()`, `reset_eng()`, and `load_method()`. `falcon_hal()` returns a boxed trait object for Turing, GA10x/Ada, or `ENOTSUPP`.

## Control Flow

`Falcon::new()` calls `falcon_hal(chipset)`. The dispatcher maps TU102/TU104/TU106/TU116/TU117 to `tu102::Tu102`, and GA102/GA103/GA104/GA106/GA107/AD102/AD103/AD104/AD106/AD107 to `ga102::Ga102`; other chipsets fail.

## State And Persistence Behavior

The selected HAL is heap allocated and stored in each `Falcon<E>`. It stores no dynamic hardware state by itself, but it controls persistent Falcon reset, BROM, RISC-V selection, and load method behavior.

## Dependencies And Integration Points

It depends on `Chipset`, BAR0 IO, generic Falcon types, and architecture-specific HAL modules. It is the boundary between common Falcon loading code and chipset-specific register semantics.

## Risks And Test Signals

Risks include missing GA100 dispatch despite other files supporting GA100 framebuffer behavior, chipset family changes requiring explicit updates, and object allocation failure during probe. Test with each listed chipset ID, unsupported chipset rejection, PIO load on Turing, DMA load on GA102/Ada, and reset/RISC-V status behavior behind the trait interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal/ga102.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal/ga102.rs

## Purpose

`falcon/hal/ga102.rs` implements Falcon HAL behavior for GA102-class Ampere and Ada chips, including Peregrine core selection, BROM setup, fuse-version lookup, reset sequencing, and DMA load selection.

## Important APIs, Types, And Functions

Important helpers are `select_core_ga102()`, `signature_reg_fuse_version_ga102()`, and `program_brom_ga102()`. `struct Ga102<E>` implements `FalconHal<E>` with `LoadMethod::Dma`, RISC-V active checks via `NV_PRISCV_RISCV_CPUCTL`, scrubbing polling through `NV_PFALCON_FALCON_HWCFG2`, and engine reset through `NV_PFALCON_FALCON_ENGINE::reset_engine()`.

## Control Flow

Core selection checks `NV_PRISCV_RISCV_BCR_CTRL`; if the Falcon core is not selected, it writes `core_select = Falcon` and waits up to 10 ms for `valid`. Fuse lookup maps engine masks to SEC2, NVDEC, or GSP fuse-version arrays, validates `ucode_id` 1..16, and returns the highest set-bit index. BROM programming writes parameter address, engine mask, ucode ID, and RSA3K algorithm. Reset tolerates a short `reset_ready` timeout, resets the engine, then waits for memory scrubbing.

## State And Persistence Behavior

No software state beyond phantom typing. Hardware state persists in Peregrine core-select, BROM parameter registers, MOD_SEL, Falcon reset/scrub registers, and fuse-read-derived signature decisions.

## Dependencies And Integration Points

It depends on `regs`, BAR0 IO, polling, Falcon generic types, `PeregrineCoreSelect`, `FalconModSelAlgo`, and engine-specific register bases. It is selected for GA10x and Ada by `falcon_hal()`.

## Risks And Test Signals

Risks include engine mask assumptions, off-by-one fuse index selection, unsupported engine masks, using RSA3K unconditionally, tolerated reset-ready timeout masking hardware faults, and no GA100 coverage. Test by booting SEC2/GSP on GA10x/Ada, checking signature choice against fuses, invalid descriptor rejection, reset/scrub timeouts, and RISC-V/Falcon core switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal/ga102.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal/tu102.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal/tu102.rs

## Purpose

`falcon/hal/tu102.rs` implements the Turing Falcon HAL, using PIO firmware loading and older reset/scrubbing/status registers.

## Important APIs, Types, And Functions

`struct Tu102<E>` implements `FalconHal<E>`. It returns no-op BROM programming and signature fuse version `0`, checks RISC-V activity via `NV_PRISCV_RISCV_CORE_SWITCH_RISCV_STATUS`, waits for memory scrubbing via `NV_PFALCON_FALCON_DMACTL`, resets through `NV_PFALCON_FALCON_ENGINE::reset_engine()`, and reports `LoadMethod::Pio`.

## Control Flow

Common Falcon code delegates reset to this HAL, which resets the engine and polls scrubbing completion for up to 10 ms. PIO is selected for firmware load because pre-GA102 hardware exposes CPU PIO memory ports. BROM/signature hooks are effectively bypassed for this generation in current implementation.

## State And Persistence Behavior

The HAL stores only phantom type state. Hardware state affected by this file is limited to reset and scrubbing-related Falcon registers; load and boot state is handled by common Falcon PIO helpers.

## Dependencies And Integration Points

It depends on generic Falcon support, BAR0 IO, polling, and Turing/Peregrine status registers. It is selected for TU102/TU104/TU106/TU116/TU117.

## Risks And Test Signals

Risks include returning fuse version `0` for all signatures, no BROM parameter programming, PIO-only assumptions, and scrubbing timeout sensitivity. Test by loading Booter/FWSEC on Turing, validating signature selection fallback to last signature, checking PIO memory writes, and verifying reset completion on all Turing variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal/tu102.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/sec2.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/sec2.rs

## Purpose

`falcon/sec2.rs` defines the Falcon engine marker for the SEC2 security processor, which Nova uses to run Booter firmware during GSP startup.

## Important APIs, Types, And Functions

`struct Sec2(())` implements `RegisterBase<PFalconBase>` at `0x00840000`, `RegisterBase<PFalcon2Base>` at `0x00841000`, and `FalconEngine`.

## Control Flow

The file has no runtime code beyond trait-associated constants. Generic `Falcon<Sec2>` methods use these base addresses for reset, firmware load, mailbox, and boot operations.

## State And Persistence Behavior

No software state is stored. The marker controls which SEC2 hardware registers are accessed, and any persistent hardware state is managed by generic Falcon routines.

## Dependencies And Integration Points

It depends on register-base traits and generic Falcon engine markers. It integrates with `BooterFirmware`, `Gpu`, and GSP boot code through `Falcon<Sec2>`.

## Risks And Test Signals

Risks are limited but severe if register bases are wrong. Test by resetting SEC2, loading booter firmware, receiving expected mailbox status, and confirming no GSP/Falcon register range is accidentally addressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/sec2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb.rs

## Purpose

`fb.rs` manages framebuffer-related state needed before and during GSP boot: the sysmem flush page required for GPU-initiated memory barriers, printable framebuffer ranges, and the VRAM layout carved into VGA workspace, FRTS, bootloader, GSP image, WPR2 heap, WPR2, and non-WPR heap.

## Important APIs, Types, And Functions

Important types are `SysmemFlush`, `FbRange`, and `FbLayout`. `SysmemFlush::register()` allocates a coherent page and writes its DMA address through the FB HAL; `unregister()` clears it if still active. `FbLayout::new()` computes all firmware boot memory ranges using chipset HALs, `GspFirmware` sizes, `LibosParams`, and alignment helpers.

## Control Flow

GPU initialization registers the sysmem flush page before Falcon reset. GSP boot loads firmware, then calls `FbLayout::new()`. Layout begins with total VRAM, determines VGA workspace from display fuse and workspace register, reserves FRTS below it, places bootloader and firmware image below FRTS with 4K/64K alignment, computes WPR2 heap with 1 MiB alignment, then reserves WPR2 metadata and a 1 MiB non-WPR heap.

## State And Persistence Behavior

`SysmemFlush` owns a coherent page and records chipset/device for unregister. The GPU may use the registered DMA address until cleared. `FbLayout` is an in-memory plan used to create WPR metadata and validate FWSEC results; hardware WPR registers later persist the protected region.

## Dependencies And Integration Points

It depends on FB HALs, BAR0 IO, coherent DMA, pointer alignment helpers, `GspFirmware`, `LibosParams`, and GSP WPR metadata. It integrates with `Gpu::new()` and `gsp/boot.rs`.

## Risks And Test Signals

Risks include underflow on small or unusual VRAM sizes, display workspace fallback mismatches, alignment holes, WPR2 overlap, stale sysmem flush page if unregister ordering fails, and chipset-specific VRAM size errors. Test with Turing/GA100/GA10x/Ada VRAM sizes, display-disabled chips, FWSEC WPR2 address verification, sysmembar-dependent Falcon reset, and unbind cleanup warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal.rs

## Purpose

`fb/hal.rs` defines the framebuffer HAL trait and chipset dispatcher for sysmem flush page registers, display support detection, and VRAM size queries.

## Important APIs, Types, And Functions

`FbHal` exposes `read_sysmem_flush_page()`, `write_sysmem_flush_page()`, `supports_display()`, and `vidmem_size()`. `fb_hal(chipset)` returns a static HAL for Turing, GA100, or GA102/Ada families.

## Control Flow

Callers select the HAL through `fb_hal()`, then invoke trait methods when registering the sysmem flush page or computing `FbLayout`. Dispatch maps Turing chips to `tu102`, GA100 to `ga100`, and GA10x/Ada chips to `ga102`.

## State And Persistence Behavior

The dispatcher returns static trait-object references with no per-device state. Hardware state persists in registers written through concrete HALs.

## Dependencies And Integration Points

It depends on `Chipset`, BAR0 IO, and concrete HAL modules. It integrates with `SysmemFlush` and framebuffer layout computation.

## Risks And Test Signals

Risks include chipset dispatch drift, trait methods whose register formats differ by generation, and default assumptions for future GPUs. Test by querying HAL behavior for every `Chipset::ALL` variant, registering/unregistering sysmem flush pages, and comparing reported VRAM size/display status with hardware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal/ga100.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal/ga100.rs

## Purpose

`fb/hal/ga100.rs` implements framebuffer HAL behavior for GA100, combining GA100 sysmem flush high-address handling and display fuse checks with GP102-style VRAM size reporting.

## Important APIs, Types, And Functions

Helpers are `read_sysmem_flush_page_ga100()`, `write_sysmem_flush_page_ga100()`, and `display_enabled_ga100()`. `Ga100` implements `FbHal`; `GA100_HAL` exposes it as a static trait object. `FLUSH_SYSMEM_ADDR_SHIFT_HI` defines the high-register shift at bit 40.

## Control Flow

Read combines low `adr_39_08` and high `adr_63_40` fields. Write programs the high register first using bounded shifting/casting, then low bits. Display support reads the GA100 display-disabled fuse. VRAM size delegates to `tu102::vidmem_size_gp102()`.

## State And Persistence Behavior

No Rust state is stored. Hardware state persists in `NV_PFB_NISO_FLUSH_SYSMEM_ADDR` and `_HI` until overwritten; fuse and memory-size registers are read-only from this driver's perspective.

## Dependencies And Integration Points

It depends on BAR0 IO, bounded numeric conversions, register definitions, `FbHal`, and TU102 helper reuse. It is used by `fb_hal(Chipset::GA100)`.

## Risks And Test Signals

Risks include high/low address write ordering, missing explicit address-width error on writes, reuse of GP102 VRAM size for GA100, and display fuse interpretation. Test with DMA addresses above 40 bits, sysmem flush unregister comparisons, GA100 display-disabled systems, and VRAM size consistency against firmware/PCI resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal/ga100.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal/ga102.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal/ga102.rs

## Purpose

`fb/hal/ga102.rs` implements framebuffer HAL behavior for GA102-family Ampere and Ada GPUs.

## Important APIs, Types, And Functions

`vidmem_size_ga102()` reads `NV_USABLE_FB_SIZE_IN_MB`. `Ga102` implements `FbHal`, reusing GA100 sysmem flush and display-fuse helpers while using GA102-specific VRAM size. `GA102_HAL` exposes the static HAL.

## Control Flow

Calls to read/write sysmem flush and display support delegate to GA100 helpers. VRAM size reads the usable framebuffer size register. The dispatcher selects this HAL for GA102/GA103/GA104/GA106/GA107 and AD102/AD103/AD104/AD106/AD107.

## State And Persistence Behavior

There is no software state. Hardware state persists in the sysmem flush address registers; VRAM size and display fuse are read-only signals for layout decisions.

## Dependencies And Integration Points

It depends on BAR0 IO, register definitions, GA100 helper functions, and `FbHal`. It feeds `SysmemFlush` and `FbLayout`.

## Risks And Test Signals

Risks include assuming Ada uses GA102 sysmem/display register formats, interpreting `NV_USABLE_FB_SIZE_IN_MB` units correctly through register wrapper behavior, and stale reuse if future Ampere/Ada variants differ. Test by comparing framebuffer size to physical VRAM, registering high DMA flush addresses, and booting GSP on each selected chipset family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal/ga102.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal/tu102.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal/tu102.rs

## Purpose

`fb/hal/tu102.rs` implements framebuffer HAL behavior for Turing-class GPUs and provides reusable GM107/GP102-style helpers.

## Important APIs, Types, And Functions

Helpers are `read_sysmem_flush_page_gm107()`, `write_sysmem_flush_page_gm107()`, `display_enabled_gm107()`, and `vidmem_size_gp102()`. `FLUSH_SYSMEM_ADDR_SHIFT` is 8. `Tu102` implements `FbHal`, and `TU102_HAL` is the static instance.

## Control Flow

Read reconstructs the sysmem flush address from `adr_39_08 << 8`. Write validates that `addr >> 8` fits in `u32`, then writes the low register. Display support checks the GM107 display fuse. VRAM size reads `NV_PFB_PRI_MMU_LOCAL_MEMORY_RANGE`.

## State And Persistence Behavior

No software state is stored. The sysmem flush register persists until overwritten; display and VRAM signals are read-only.

## Dependencies And Integration Points

It depends on BAR0 IO, register wrappers, and the FB HAL trait. The helpers are reused by GA100 for VRAM size and by Turing layout code.

## Risks And Test Signals

Risks include rejecting DMA addresses above the 40-bit low-register format, assuming GM107 display fuse semantics on all Turing chips, and VRAM size wrapper correctness. Test sysmem flush registration with low and too-large DMA addresses, display fuse handling, and GSP boot layout on all Turing variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal/tu102.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware.rs

## Purpose

`firmware.rs` provides common firmware parsing, request naming, Falcon descriptor abstractions, signature-patching state, module firmware metadata generation, and temporary ELF section extraction for Nova GSP boot assets.

## Important APIs, Types, And Functions

Important items are `FIRMWARE_VERSION`, `request_firmware()`, `FalconUCodeDescV2`, `FalconUCodeDescV3`, `FalconUCodeDesc`, `FalconUCodeDescriptor`, `FirmwareObject<F, SignedState>`, `FirmwareSignature`, `BinHdr`, `BinFirmware`, `ModInfoBuilder`, and `elf::elf64_section()`. Descriptor methods return IMEM/DMEM load targets and signature metadata.

## Control Flow

Firmware requests build paths like `nvidia/<chip>/gsp/<name>-570.144.bin`. `BinFirmware::new()` validates the common magic and exposes payload ranges. Descriptor implementations normalize V2 and V3 layouts into secure/non-secure IMEM and DMEM load targets. `FirmwareObject<Unsigned>` can patch a selected signature into a bounded offset or explicitly transition to signed without patching. `ModInfoBuilder` emits firmware file names for every supported chipset. The ELF helper walks ELF64 section headers to locate named sections.

## State And Persistence Behavior

Firmware bytes are stored in kernel vectors or coherent allocations owned by higher-level wrappers. The signed/unsigned state is encoded in Rust types and prevents loading unpatched firmware through wrapper APIs. Module firmware metadata persists in the built module.

## Dependencies And Integration Points

It depends on kernel firmware loading, CString formatting, transmute `FromBytes`, Falcon firmware traits, chipset names, and numeric conversion helpers. Submodules `booter`, `fwsec`, `gsp`, and `riscv` build on this common parsing layer.

## Risks And Test Signals

Risks include fixed firmware version, strict binary magic validation but limited semantic header validation, saturating descriptor arithmetic hiding malformed descriptors, temporary ELF parser assumptions, and signature state being module-local rather than globally enforced. Test with present/missing firmware files, malformed binary and ELF headers, V2/V3 descriptors, signature patch bounds, module firmware aliases, and firmware version upgrades.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/booter.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/booter.rs

## Purpose

`firmware/booter.rs` parses, signs, and describes SEC2 Booter firmware images used to load or unload the GSP firmware during startup.

## Important APIs, Types, And Functions

Key types are `BooterFirmware`, `BooterKind`, `HsHeaderV2`, `HsFirmwareV2`, `HsSignatureParams`, `HsLoadHeaderV2`, `HsLoadHeaderV2App`, and `BooterSignature`. `BooterFirmware::new()` requests and parses `booter_load` or `booter_unload`; it implements `FalconDmaLoadable` and `FalconFirmware<Target = Sec2>`.

## Control Flow

`new()` requests the selected firmware, validates the common binary header, reads the HS header, load header, patch location, signature metadata, and app0 load descriptor, then creates a firmware object from the payload. If signatures exist, it queries the SEC2 Falcon HAL for fuse version and selects either the last signature or an indexed signature before patching it. It then derives load targets differently for Turing/GA100 versus GA102+ because the same filenames encode different layouts.

## State And Persistence Behavior

`BooterFirmware` owns a signed firmware byte vector and immutable load/BROM parameters. It persists long enough for SEC2 Falcon loading and boot. Signature patching mutates only the in-memory copy.

## Dependencies And Integration Points

It depends on firmware common parsing, SEC2 Falcon traits, chipset ordering, fuse-version HALs, bounded byte extraction, and kernel firmware loading. GSP boot uses `BooterKind::Loader` with `sec2_falcon.load()` and mailbox arguments pointing to WPR metadata.

## Risks And Test Signals

Risks include division by zero avoided through `checked_div` but nuanced empty-signature behavior, patch signature offset interpretation, chipset-based layout selection without explicit format marker, fuse-version index math, and boot address selection using source offset on GA102+. Test with signed and unsigned Booter images, malformed HS offsets, Turing/GA100 and GA102+ layouts, signature fuse variants, SEC2 boot mailbox success/failure, and missing unloader coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/booter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/fwsec.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/fwsec.rs

## Purpose

`firmware/fwsec.rs` extracts FWSEC firmware from VBIOS, patches its command and signature, and runs it on the GSP Falcon to create the WPR2/FRTS protected region or perform other secure firmware tasks.

## Important APIs, Types, And Functions

Important types are `FwsecFirmware`, `FwsecCommand`, `Bcrt30Rsa3kSignature`, APPIF/DMEM mapper structs, `ReadVbios`, `FrtsRegion`, and `FrtsCmd`. `FirmwareObject<FwsecFirmware, Unsigned>::new_fwsec()` builds and patches the command payload. `FwsecFirmware::new()` selects and patches a signature, and `run()` resets, loads, boots, and checks mailbox status.

## Control Flow

`new_fwsec()` reads the FWSEC descriptor and microcode from VBIOS, finds the APPIF DMEM mapper entry, sets `init_cmd` to FRTS or SB, and writes FRTS command parameters including VBIOS read flags and framebuffer region page numbers. `FwsecFirmware::new()` then checks descriptor signatures; if present, it computes the signature index from firmware signature-version bits and hardware fuse version, fetches the matching VBIOS signature, and patches it. `run()` performs direct Falcon reset/load/boot on chipsets that do not require the bootloader wrapper.

## State And Persistence Behavior

The firmware object owns a signed in-memory FWSEC image and descriptor. Running it mutates hardware by creating WPR2, updating scratch status, and executing secure Falcon code. The firmware bytes must remain valid during load/boot only.

## Dependencies And Integration Points

It depends on VBIOS parsing, Falcon GSP support, firmware descriptor abstractions, signature patching, BAR0 IO, transmute byte views, and `FwsecFirmwareWithBl` for older chipsets. GSP boot invokes it before Booter loads the main GSP image.

## Risks And Test Signals

Risks include APPIF table parsing over packed structs, descriptor offset arithmetic, FRTS address truncation to 4 KiB page units and `u32`, signature bitmask/fuse mismatch, and direct-run use on bootloader-required chipsets. Test with VBIOS FWSEC descriptor variants, signature-count zero/nonzero cases, invalid APPIF entries, FWSEC mailbox nonzero, scratch FRTS error codes, and WPR2 register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/fwsec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/fwsec/bootloader.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/fwsec/bootloader.rs

## Purpose

`firmware/fwsec/bootloader.rs` wraps FWSEC in a PIO-loaded generic bootloader for Turing and GA100, where FWSEC itself cannot be loaded directly.

## Important APIs, Types, And Functions

Important types are `BootloaderDesc`, `BootloaderDmemDescV2`, and `FwsecFirmwareWithBl`. `FwsecFirmwareWithBl::new()` loads `gen_bootloader`, prepares aligned bootloader code, creates a coherent DMA mirror of FWSEC, builds the DMEM descriptor, and implements `FalconFirmware<Target = Gsp>` plus `FalconPioLoadable`. `run()` loads and executes the wrapper.

## Control Flow

`new()` parses the bootloader descriptor from a firmware binary, copies and 256-byte-aligns bootloader code, pads the FWSEC DMA image so source offsets mirror destination offsets, and fills `BootloaderDmemDescV2` with non-secure/secure code offsets, data base/size, DMA context, and entry point. It places bootloader IMEM just below the first 64 KiB. `run()` resets GSP, PIO-loads the bootloader and descriptor, configures FBIF DMA context, boots, and checks mailbox status.

## State And Persistence Behavior

The wrapper owns the coherent FWSEC DMA object, bootloader code vector, and DMEM descriptor; these must remain alive while the bootloader DMA-copies FWSEC. Hardware state persists in GSP Falcon IMEM/DMEM, FBIF transaction config, and mailbox results.

## Dependencies And Integration Points

It depends on FWSEC firmware load parameters, Falcon PIO APIs, coherent DMA, firmware request parsing, chipset firmware naming, FBIF target/mem-type enums, and GSP registers. `gsp/boot.rs` uses it when `Chipset::needs_fwsec_bootloader()` is true.

## Risks And Test Signals

Risks include assuming FWSEC has a non-secure IMEM target, requiring DMEM destination zero, offset mirroring and padding correctness, bootloader load-ceiling underflow, DMA context index validation, and coherent versus non-coherent naming mismatch. Test on Turing and GA100, malformed bootloader headers, nonzero FWSEC DMEM destinations, IMEM size near 64 KiB, mailbox failure, and WPR2 creation after wrapper execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/fwsec/bootloader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/gsp.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/gsp.rs

## Purpose

`firmware/gsp.rs` loads the main GSP firmware ELF, maps it through a three-level radix page table for the GSP bootloader, maps matching signatures, and loads the RISC-V bootloader firmware.

## Important APIs, Types, And Functions

`GspFirmware` owns SG tables for firmware, level2, level1, a coherent level0 table, firmware size, signatures, and `RiscvFirmware` bootloader. `GspFirmware::new()` constructs all pieces. `radix3_dma_handle()` returns the level0 DMA address. `map_into_lvl()` emits little-endian DMA page entries for SG mappings.

## Control Flow

`new()` requests `gsp`, extracts the `.fwimage` ELF section, copies it into a `VVec`, maps it as SG to the device, builds level2 entries pointing to firmware pages, builds level1 entries pointing to level2 pages, and stores the first level1 DMA address in a coherent level0 page. It selects the signature ELF section by architecture/chipset, maps it coherently, requests `bootloader`, and parses it as `RiscvFirmware`.

## State And Persistence Behavior

Pinned `GspFirmware` keeps all mapped SG and coherent objects alive through GSP boot. The GSP boot metadata references the level0 radix table, firmware size, signature DMA address, and bootloader DMA address. Firmware data is read-only from the driver after construction.

## Dependencies And Integration Points

It depends on firmware request helpers, the temporary ELF section parser, DMA SG tables, coherent allocations, `Chipset`/`Architecture`, `RiscvFirmware`, and GSP page constants. `FbLayout` and `GspFwWprMeta` consume its sizes and DMA handles.

## Risks And Test Signals

Risks include ELF section name drift, SG entry page rounding, endian assumptions for page-table entries, firmware/signature architecture mapping, and lifetime requirements for mapped tables. Test by loading all supported chipset firmware variants, verifying radix3 tables with multi-entry SG mappings, missing section failures, bootloader parse failures, and successful Booter consumption of WPR metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/gsp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/riscv.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/riscv.rs

## Purpose

`firmware/riscv.rs` parses firmware binaries designed for NVIDIA RISC-V cores, especially the GSP bootloader used during main GSP startup.

## Important APIs, Types, And Functions

`RmRiscvUCodeDesc` mirrors the RISC-V firmware descriptor. `RiscvFirmware` stores code, data, manifest offsets, application version, and a coherent mapped firmware payload. `RiscvFirmware::new()` parses the common binary header and descriptor, then maps the payload.

## Control Flow

Construction validates the common `BinFirmware`, reads the descriptor at `header_offset`, slices the data payload using `data_offset` and `data_size`, maps it into a coherent device-visible allocation, and exposes monitor code/data/manifest offsets plus app version for boot metadata and Falcon OS version programming.

## State And Persistence Behavior

The coherent firmware payload must remain alive while GSP bootloader DMA references are used. Parsed offsets and `app_version` are immutable state copied from firmware headers.

## Dependencies And Integration Points

It depends on `BinFirmware`, kernel firmware loading, coherent DMA, transmute `FromBytes`, and safe numeric conversions. `GspFirmware` owns a `RiscvFirmware`, and `gsp/boot.rs` writes its app version into the GSP Falcon OS register.

## Risks And Test Signals

Risks include trusting descriptor offsets semantically after bounds checks, coherent allocation size matching payload size, and firmware format changes. Test with valid and malformed bootloader binaries, descriptor offset bounds, payload slicing, app-version propagation, and GSP bootloader load through WPR metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/riscv.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gfw.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gfw.rs

## Purpose

`gfw.rs` waits for GPU firmware/devinit completion after reset before Nova performs deeper GPU initialization.

## Important APIs, Types, And Functions

The single API is `wait_gfw_boot_completion(bar: &Bar0) -> Result`. It polls `NV_PGC6_AON_SECURE_SCRATCH_GROUP_05_PRIV_LEVEL_MASK` and `NV_PGC6_AON_SECURE_SCRATCH_GROUP_05_0_GFW_BOOT`.

## Control Flow

The function polls every millisecond for up to four seconds. Each poll first checks whether FWSEC lowered the scratch register read protection level so the CPU can safely read the GFW boot status, then reads the completion bit. Success maps to `Ok(())`; timeout or IO errors propagate.

## State And Persistence Behavior

No software state is stored. The observed hardware state is secure scratch privilege and completion bits set by firmware/devinit components running before the driver proceeds.

## Dependencies And Integration Points

It depends on BAR0 IO, register wrappers, and polling. `Gpu::new()` calls it immediately after chipset identification and before sysmem flush/Falcon/GSP setup.

## Risks And Test Signals

Risks include hardcoded four-second timeout, privilege-level check behavior differing by GPU or firmware, and limited diagnostics beyond timeout. Test by probing after cold boot and reset, checking timeout behavior on unsupported/failed firmware, and ensuring no later initialization runs before GFW completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gfw.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gpu.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gpu.rs

## Purpose

`gpu.rs` identifies supported NVIDIA GPUs, classifies chipsets and architectures, and constructs the high-level GPU runtime required for GSP boot.

## Important APIs, Types, And Functions

Important types are `Chipset`, `Architecture`, `Revision`, `Spec`, and pinned `Gpu`. `define_chipset!` generates chipset names, `Chipset::arch()`, and `needs_fwsec_bootloader()`. `Spec::new()` reads boot registers and rejects unsupported GPUs. `Gpu::new()` initializes GPU runtime resources; `Gpu::unbind()` unregisters the sysmem flush page.

## Control Flow

`Gpu::new()` reads `NV_PMC_BOOT_0` and `NV_PMC_BOOT_42` through `Spec::new()`, logs chipset details, waits for GFW boot completion, registers the sysmem flush page, constructs GSP and SEC2 Falcon instances, clears GSP SWGEN0, initializes `Gsp`, runs GSP boot with both Falcons, and stores BAR0. Unbind reacquires BAR access and clears the sysmem flush page.

## State And Persistence Behavior

`Gpu` persists chipset spec, shared BAR0 devres, sysmem flush page, Falcon controllers, and GSP runtime. Hardware state includes registered sysmem flush address, Falcon reset/load state, and GSP runtime after boot.

## Dependencies And Integration Points

It depends on PCI device context, BAR0 IO, `gfw`, `fb::SysmemFlush`, `falcon`, `gsp`, and generated register wrappers. It is owned by `NovaCore` in the PCI driver.

## Risks And Test Signals

Risks include chipset enum coverage mismatch with HALs, boot register assumptions for future GPUs, sysmem flush unregister only on PCI unbind, GSP boot errors aborting probe, and pinned initialization ordering. Test supported and unsupported chipsets, GFW timeout, sysmem flush setup/cleanup, GSP boot success, auxiliary registration lifetime, and unbind after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp.rs

## Purpose

`gsp.rs` defines runtime data structures for the GSP manager: page constants, log buffers, command queue, LIBOS memory-region arguments, and RM argument storage.

## Important APIs, Types, And Functions

Important items are `GSP_PAGE_SHIFT`, `GSP_PAGE_SIZE`, `PteArray`, `LogBuffer`, `LogBuffers`, and pinned `Gsp`. `LogBuffer::new()` allocates a coherent log buffer and writes self page-table entries. `Gsp::new()` initializes command queue, RM arguments, LIBOS memory-region array, and debugfs log files.

## Control Flow

Construction allocates three log buffers (`LOGINIT`, `LOGINTR`, `LOGRM`), creates a `Cmdq`, builds padded RM arguments from the command queue, allocates one page of LIBOS memory-region descriptors, initializes entries for logs and RMARGS, then exposes log buffers under the module debugfs root using the PCI device name.

## State And Persistence Behavior

`Gsp` owns coherent LIBOS arguments, coherent RM args, a pinned command queue, and a debugfs scope that owns log buffers. These objects persist for the GPU lifetime and are shared with GSP-RM after boot. Log buffer contents are written by firmware and readable through debugfs.

## Dependencies And Integration Points

It depends on coherent DMA, debugfs, PCI device naming, `Cmdq`, GSP firmware ABI wrappers, and page-table entry helpers. `gsp/boot.rs` consumes this runtime object to pass LIBOS and command queue addresses into firmware.

## Risks And Test Signals

Risks include debugfs root lifetime assumptions, log buffer PTE layout, physical contiguity requirements, fixed log buffer size, and keeping RM/LIBOS arguments alive until initialization completes. Test by constructing GSP runtime, reading debugfs logs, validating LIBOS memory-region IDs and DMA addresses, and booting GSP until init-done.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/boot.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/boot.rs

## Purpose

`gsp/boot.rs` orchestrates the full GSP startup sequence, from VBIOS/FWSEC/WPR2 setup through SEC2 Booter execution, GSP RISC-V activation, sequencer processing, init-done wait, and basic GPU info retrieval.

## Important APIs, Types, And Functions

Methods on `Gsp` are `run_fwsec_frts()` and `boot()`. The flow uses `Vbios`, `GspFirmware`, `FbLayout`, `FwsecFirmware`, `FwsecFirmwareWithBl`, `BooterFirmware`, `GspFwWprMeta`, command helpers `SetSystemInfo`, `SetRegistry`, `wait_gsp_init_done()`, `get_gsp_info()`, and `GspSequencer`.

## Control Flow

`boot()` loads VBIOS and GSP firmware, computes framebuffer layout, runs FWSEC-FRTS to create WPR2, parses SEC2 `booter_load`, creates WPR metadata, queues system-info and registry commands, resets and boots the GSP Falcon with LIBOS DMA address, resets and loads SEC2 Booter with WPR metadata DMA address, checks Booter mailbox, writes bootloader app version, polls for RISC-V active, runs the sequencer, waits for `GspInitDone`, then requests static GPU info.

## State And Persistence Behavior

The method consumes preallocated `Gsp` runtime state and creates temporary firmware/layout/WPR metadata objects. Persistent hardware state includes WPR2 region registers, GSP firmware in protected framebuffer memory, running GSP-RM, command queues, and Falcon OS version. Queued commands persist until GSP processes them.

## Dependencies And Integration Points

It depends on firmware files, VBIOS parsing, framebuffer HAL/layout, GSP and SEC2 Falcons, command queue, sequencer, and register polling. It is called by `Gpu::new()` during PCI probe.

## Risks And Test Signals

Risks include boot ordering sensitivity, WPR2 already existing, FWSEC scratch error handling, Booter mailbox failure, command queue use before GSP is live, RISC-V activation timeout, and temporary object lifetimes during DMA. Test cold boot, reset-required WPR2 condition, missing firmware/VBIOS failures, FWSEC and Booter error codes, sequencer execution, init-done timeout, and GPU name retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/boot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/cmdq.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/cmdq.rs

## Purpose

`gsp/cmdq.rs` implements the shared-memory command and message queues used for CPU-to-GSP RPCs and GSP-to-CPU events.

## Important APIs, Types, And Functions

Key traits are `CommandToGsp` and `MessageFromGsp`; marker `NoReply` represents fire-and-forget commands. Queue structures include `MsgqData`, `Msgq`, `GspMem`, `DmaGspMem`, `GspCommand`, `GspMessage`, `Cmdq`, and `CmdqInner`. Public methods include `Cmdq::new()`, `send_command()`, `send_command_no_wait()`, and `receive_msg()`.

## Control Flow

`DmaGspMem::new()` allocates coherent shared memory, writes self PTEs, and initializes CPU queue headers. Sending locks the queue, optionally splits large commands, waits for writable space, writes a `GspMsgElement`, initializes the typed command and variable payload, checks all bytes were written, computes checksum, advances CPU write pointer, and notifies GSP via `NV_PGSP_QUEUE_HEAD`. Receiving waits for readable GSP data, validates length and checksum, parses the expected typed message, advances CPU read pointer even on mismatch, and returns `ERANGE` for nonmatching functions.

## State And Persistence Behavior

`Cmdq` owns coherent `GspMem`, a mutex-protected sequence counter, and a DMA handle passed to GSP boot arguments. Ring read/write pointers are shared persistent state with explicit CPU/GSP ownership rules and memory fences in `gsp/fw.rs`.

## Dependencies And Integration Points

It depends on coherent DMA, typed GSP ABI wrappers, `SBufferIter`, continuation splitting, BAR0 notification register, polling, mutexes, and DMA read/write macros. `gsp/commands.rs`, `gsp/sequencer.rs`, and boot code use it for all RPCs.

## Risks And Test Signals

Risks include unsafe slice projection over circular buffers, pointer wrap/off-by-one bugs, checksum mismatch, element-count advancement errors, lock scope serializing send/receive, message consumption on unexpected functions, and timeout tuning. Test queue initialization, full/empty ring boundaries, wraparound send/receive, checksum corruption, continuation split commands, unexpected messages, and init-done/GPU-info RPCs on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/cmdq.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/cmdq/continuation.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/cmdq/continuation.rs

## Purpose

`gsp/cmdq/continuation.rs` supports splitting oversized GSP commands into a first truncated command plus continuation-record commands.

## Important APIs, Types, And Functions

Important items are `MAX_CMD_SIZE`, `ContinuationRecords`, `ContinuationRecord`, `SplitState<C>`, and `SplitCommand<C>`. `ContinuationRecord` implements `CommandToGsp` with function `ContinuationRecord` and no reply. `SplitState::new()` decides whether and how to split a command.

## Control Flow

When command size exceeds one queue element, `SplitState::new()` allocates two buffers: the maximum payload fitting beside the original command header and the remaining continuation payload. It asks the original command to write its variable payload across both buffers, then wraps the first part in `SplitCommand` and exposes an iterator over chunks of the rest. `CmdqInner::send_command()` sends the first command followed by each continuation record.

## State And Persistence Behavior

Split payload data is copied into kernel vectors owned by `SplitCommand` and `ContinuationRecords` until sent. No persistent state remains after queue submission, except the queued GSP messages.

## Dependencies And Integration Points

It depends on `CommandToGsp`, `NoReply`, `MsgFunction`, max queue element size, `GspMsgElement`, and `SBufferIter`. It is used internally by `cmdq.rs`.

## Risks And Test Signals

Risks include duplicating payload initialization for split commands, allocation failures for large payloads, boundary errors at exact maximum sizes, and GSP expectations for continuation ordering. KUnit tests cover zero-sized, boundary, one-continuation, and multi-continuation payloads; hardware tests should send a real large registry/control payload and verify GSP accepts it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/cmdq/continuation.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/commands.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/commands.rs

## Purpose

`gsp/commands.rs` defines high-level typed GSP RPC commands and message readers used during early GSP initialization and information retrieval.

## Important APIs, Types, And Functions

Commands include `SetSystemInfo`, `SetRegistry`, and internal `GetGspStaticInfo`. Message/read types include `GspInitDone`, `GetGspStaticInfoReply`, and `GpuNameError`. Public helpers are `wait_gsp_init_done()` and `get_gsp_info()`.

## Control Flow

`SetSystemInfo` initializes a generated `GspSetSystemInfo` from the PCI device. `SetRegistry` builds a packed registry table with three hardcoded keys and a variable payload containing entry records plus NUL-terminated strings. `wait_gsp_init_done()` loops receiving messages until `GspInitDone` arrives, skipping unrelated recognized messages. `get_gsp_info()` sends `GetGspStaticInfo` and parses the reply GPU name.

## State And Persistence Behavior

Commands are temporary typed builders; their serialized bytes persist only in the command queue until consumed by GSP. Registry entries are hardcoded in the command object. The static-info reply stores a copied 64-byte GPU name.

## Dependencies And Integration Points

It depends on generated GSP command bindings, `Cmdq`, `CommandToGsp`, `MessageFromGsp`, `SBufferIter`, PCI device abstractions, and C string/UTF-8 parsing. GSP boot queues system/registry setup before final initialization and reads GPU info after init done.

## Risks And Test Signals

Risks include hardcoded registry policy, payload offset calculations including table size, string termination, ignored extra reply payload, GPU name not NUL-terminated or invalid UTF-8, and skipped unrelated messages hiding important events. Test command serialization sizes, registry payload bytes, init-done wait with interleaved events, static-info reply parsing, and hardware logs showing accepted registry/system info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/commands.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw.rs

## Purpose

`gsp/fw.rs` wraps generated GSP firmware ABI bindings for queue headers, message elements, LIBOS arguments, WPR metadata, heap sizing, sequencer payloads, and function/opcode enums.

## Important APIs, Types, And Functions

Important exports include `GSP_MSG_QUEUE_ELEMENT_SIZE_MAX`, `LibosParams`, `GspFwWprMeta`, `MsgFunction`, `SeqBufOpcode`, sequencer payload wrappers, `SequencerBufferCmd`, `RunCpuSequencer`, `LibosMemoryRegionInitArgument`, `MsgqTxHeader`, `MsgqRxHeader`, `GspMsgElement`, `GspArgumentsCached`, and `GspArgumentsPadded`. The `gsp_mem` submodule provides DMA pointer access and advancement helpers.

## Control Flow

`LibosParams` selects LIBOS2 for pre-GA102 and LIBOS3 for GA102+, then computes WPR heap size from OS carveout, RM base, client allocation, and framebuffer management overhead clamped to allowed bounds. `GspFwWprMeta::new()` fills boot metadata from firmware DMA handles and `FbLayout`. Enums convert raw binding values to typed variants. `SequencerBufferCmd` validates opcode before reading the matching union payload. `GspMsgElement::init()` creates message headers with version, signature, function, length, and element count.

## State And Persistence Behavior

Most wrappers are transparent ABI views over generated C layouts. `GspFwWprMeta`, LIBOS arguments, queue headers, and message elements are serialized into coherent memory consumed by firmware. `gsp_mem` read/write pointer helpers mutate shared queue state with memory fences.

## Dependencies And Integration Points

It depends on generated `r570_144` bindings, `bitfield!`, coherent DMA, alignment helpers, framebuffer layout, GSP firmware objects, command queue constants, and DMA macros. It underpins `gsp.rs`, `gsp/cmdq.rs`, `gsp/commands.rs`, and `gsp/sequencer.rs`.

## Risks And Test Signals

Risks include ABI drift with firmware version 570.144, layout/padding assumptions, union payload safety depending on opcode validation, heap-size clamp choices, pointer fence correctness, message length/element-count overflow, and enum coverage. Test by build-checking bindgen layouts, booting matching firmware, validating WPR metadata values, exercising sequencer opcodes, queue pointer wraparound, and upgrading firmware bindings with compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw.rs -->
