# Research Group: subset-b-003780

This grouped report covers the Xe driver source files assigned to `subset-b-003780`. Each file section is marker-delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hwmon.c

## Purpose
`xe_hwmon.c` implements the Xe DRM driver's Linux hwmon interface for discrete GPUs. It exposes package/card power limits, power averaging windows, energy counters, temperatures, voltage, current limits, and fan speed through `devm_hwmon_device_register_with_info()`. It is disabled for integrated GPUs and SR-IOV VFs.

## Important APIs, Types, And Functions
- Internal state is held in `struct xe_hwmon`, including the registered hwmon device, `struct xe_device *`, `hwmon_lock`, power/energy/time unit shifts, accumulated energy state, cached fan counters, boot power limits, and thermal metadata.
- Register abstraction is centralized in `xe_hwmon_get_reg()`, which maps logical sensor registers to platform-specific MMIO registers for PVC, DG2, and Battlemage.
- Power limit handling is split between MMIO RAPL registers and PCode mailbox paths: `xe_hwmon_pcode_read_power_limit()`, `xe_hwmon_pcode_rmw_power_limit()`, `xe_hwmon_power_max_read()`, and `xe_hwmon_power_max_write()`.
- Energy accounting uses `xe_hwmon_energy_get()` to accumulate 32-bit hardware counters into a long-lived software total and avoid short hardware counter wrap intervals.
- Temperature handling uses direct MMIO for package/VRAM channels, PCode thermal data for MCTRL/PCIe, and dynamic per-channel VRAM labels.
- `xe_hwmon_read()`, `xe_hwmon_write()`, `xe_hwmon_is_visible()`, and `xe_hwmon_read_label()` are the hwmon callbacks.
- `xe_hwmon_register()` is the public registration entry point.

## Control Flow
Registration checks `IS_DGFX()` and excludes `IS_SRIOV_VF()`, allocates managed state, initializes the mutex, assigns `xe->hwmon`, preloads sensor metadata with `xe_hwmon_get_preregistration_info()`, then registers the hwmon chip. Visibility callbacks perform capability probing so unsupported attributes do not appear in sysfs. Runtime reads and writes enter through the hwmon core, take a runtime-PM guard, dispatch by sensor type, and often take `hwmon_lock` around MMIO/PCode update sequences.

## State And Persistence
The driver persists unit scaling read at registration, boot-time PL1/PL2 defaults for mailbox-backed power limits, accumulated energy deltas, and previous fan pulse counters. Energy and fan values are derived from monotonic deltas, so reset/reprobe resets their software baselines. Power-limit writes persist in hardware or firmware state until reset or later firmware/driver writes. Managed allocations and the hwmon device are cleaned up by device-managed lifetime.

## Dependencies And Integration Points
This file depends on hwmon/sysfs, Xe MMIO, PCode mailbox APIs, PM runtime guards, PMT telemetry for Battlemage energy, VSEC/PMT register definitions, and platform capability flags in `xe->info`. It integrates with the Xe probe path through `xe_hwmon_register()` and exposes user-facing sysfs ABI via Linux hwmon.

## Risks
Power-limit paths are hardware- and firmware-sensitive: unit conversion, clamping, and mailbox failure handling can expose incorrect sysfs values or reject writes. Energy accumulation depends on reads happening often enough and on correct initial baseline capture. Visibility checks may have side effects such as reading sensors and filling VRAM labels. Fan RPM is time-delta based and returns `-EAGAIN` for zero elapsed time. PCode mailbox limits are clamped to boot defaults, which protects hardware but may surprise users.

## Test Signals
Useful tests include hwmon sysfs presence/absence on dGPU, iGPU, and VF; power limit read/write/disable attempts; mailbox failure paths; 32-bit energy wrap behavior; dynamic VRAM channel visibility; fan RPM consecutive reads; and runtime PM coverage around all callbacks. The PMT telemetry import should be verified on Battlemage energy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hwmon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hwmon.h

## Purpose
`xe_hwmon.h` declares the Xe hwmon registration interface and provides a no-op stub when hwmon support is unavailable.

## Important APIs, Types, And Functions
- Forward-declares `struct xe_device`.
- Exposes `int xe_hwmon_register(struct xe_device *xe)` when `CONFIG_HWMON` is reachable.
- Provides an inline `xe_hwmon_register()` returning 0 when hwmon is not built or not reachable.

## Control Flow
The header lets probe code call `xe_hwmon_register()` unconditionally. Build-time configuration selects either the real implementation in `xe_hwmon.c` or the stub.

## State And Persistence
The header owns no runtime state. It controls whether any hwmon state can be allocated by the implementation.

## Dependencies And Integration Points
It depends only on Linux types and is consumed by Xe device initialization code. It is the ABI boundary between generic Xe setup and optional hwmon support.

## Risks
The main risk is build-configuration drift: callers must not assume `xe->hwmon` exists after a successful stub call. The trailing semicolon after the inline stub is harmless but stylistically unusual.

## Test Signals
Build coverage should include `CONFIG_HWMON=y/m` and disabled configurations, verifying callers link and treat registration success as optional capability rather than proof of device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_i2c.c

## Purpose
`xe_i2c.c` discovers and registers an MMIO-backed Synopsys DesignWare I2C host controller embedded in Xe devices, then creates an I2C client for the attached Add-In Management Controller. It also bridges Xe top-level interrupts to a Linux IRQ domain used by the I2C adapter.

## Important APIs, Types, And Functions
- `xe_i2c_probe()` is the public probe entry point.
- `xe_i2c_present()` validates the endpoint cookie and confirms controller availability.
- `xe_i2c_register_adapter()` creates a software fwnode and platform device named `i2c_designware`.
- `xe_i2c_notifier()` captures the DesignWare adapter once the platform device is added, then schedules `xe_i2c_client_work()` to instantiate the `"amc"` client.
- `xe_i2c_create_irq()`, `xe_i2c_irq_postinstall()`, `xe_i2c_irq_reset()`, and `xe_i2c_irq_handler()` create and operate the pseudo IRQ used by the adapter.
- `xe_i2c_pm_suspend()` and `xe_i2c_pm_resume()` directly manipulate the embedded PCI PM registers.
- `xe_i2c_read()` and `xe_i2c_write()` provide a regmap-backed MMIO access layer.

## Control Flow
Probe exits early when the platform lacks I2C, is an SR-IOV VF, or endpoint cookie validation fails. On success it allocates `struct xe_i2c`, stores it in `xe->i2c`, resumes the embedded device to D0, creates a regmap, registers an I2C bus notifier, optionally creates an IRQ domain/mapping, registers the DesignWare platform device, enables IRQ forwarding, and installs managed cleanup. Adapter creation deliberately avoids `platform_device_register_full()` so the notifier has a valid `pdev` handle early.

## State And Persistence
State persists in `xe->i2c`: endpoint data, platform device/fwnode, adapter pointer, I2C clients, notifier, work item, IRQ domain, adapter IRQ, DRM device, and MMIO pointer. Cleanup unregisters client devices, bus notifier, platform device, fwnode, and IRQ domain. The embedded controller's PM state is written directly by suspend/resume helpers.

## Dependencies And Integration Points
The file integrates with Linux I2C, platform devices, fwnodes, irqdomain, regmap, PCI PM definitions, Xe MMIO, Xe SR-IOV checks, and survivability mode. The global Xe IRQ handler calls `xe_i2c_irq_handler()`, `xe_i2c_irq_reset()`, and `xe_i2c_irq_postinstall()`.

## Risks
The notifier/workqueue sequence depends on adapter discovery ordering. The work item is scheduled when the adapter appears, but removal does not explicitly flush it, so lifetime assumptions rely on managed remove ordering and adapter/device teardown. IRQ forwarding deasserts/reasserts INTx bits after the nested handler; incorrect ordering could lose edge-like events. Survivability mode disables IRQ creation, so adapter behavior must remain correct without IRQs.

## Test Signals
Exercise endpoint absent/present paths, SR-IOV VF exclusion, adapter registration/unregistration, client instantiation, IRQ forwarding under repeated interrupts, D3hot/D0 transitions, and survivability boot mode. Dynamic debug around PMCSR and adapter events is useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_i2c.h

## Purpose
`xe_i2c.h` defines the Xe I2C endpoint data, runtime state, capability bits, public I2C lifecycle APIs, and no-op stubs when `CONFIG_I2C` is disabled.

## Important APIs, Types, And Functions
- `XE_I2C_MAX_CLIENTS` is 3, matching the endpoint address array.
- `XE_I2C_EP_COOKIE_DEVICE` validates firmware-provided endpoint data.
- `XE_I2C_EP_CAP_IRQ` indicates adapter IRQ support.
- `struct xe_i2c_endpoint` stores cookie, capabilities, and client addresses.
- `struct xe_i2c` stores platform/fwnode, adapter/client objects, notifier/work, IRQ domain, endpoint, parent device, and MMIO pointer.
- Public functions cover probe, presence checks, IRQ handling/reset/postinstall, and PM suspend/resume.

## Control Flow
Callers include this header to interact with optional I2C support. When I2C is disabled, every exported operation compiles to a no-op or `false`/0 result, allowing the main driver and IRQ paths to remain unconditional.

## State And Persistence
The header defines, but does not allocate, `struct xe_i2c` state. The implementation stores the state in `xe->i2c` after endpoint validation.

## Dependencies And Integration Points
The header depends on Linux notifier, workqueue, bits, and type definitions. It bridges Xe device code, IRQ code, PM code, and the I2C implementation.

## Risks
Because the stubs silently succeed, callers must use `xe_i2c_present()` rather than assuming `xe_i2c_probe()` created hardware state. The endpoint layout is ABI-like with firmware/MMIO producer expectations, so packing or field changes would be high risk.

## Test Signals
Build with and without `CONFIG_I2C`; check that global IRQ and PM paths still compile and that runtime behavior cleanly skips I2C when `xe->i2c` is unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_irq.c

## Purpose
`xe_irq.c` owns Xe interrupt initialization, installation, suspend/resume, reset, top-level dispatch, engine interrupt enabling, and MSI-X vector management. It routes display, GT engine, GuC, GSC proxy, PXP, I2C, MERT, hardware error, and memory-backed interrupt events.

## Important APIs, Types, And Functions
- Public API: `xe_irq_init()`, `xe_irq_install()`, `xe_irq_suspend()`, `xe_irq_resume()`, `xe_irq_enable_hwe()`, `xe_irq_msix_request_irq()`, and `xe_irq_msix_free_irq()`.
- Legacy and tiled top-level handlers are `xelp_irq_handler()` and `dg1_irq_handler()`.
- VF memory-backed path uses `vf_mem_irq_handler()` and `xe_memirq_handler()`.
- GT dispatch is centralized in `gt_irq_handler()`, which reads `GT_INTR_DW`, resolves identity with `gt_engine_identity()`, chooses primary/media GT with `pick_engine_gt()`, and calls engine or subsystem handlers.
- Reset/postinstall functions mask/unmask register blocks, display, I2C, GU misc, and memory IRQ state.
- MSI-X support uses an xarray to track static and dynamic vectors and installs a GuC2Host vector plus a default HWE vector.

## Control Flow
`xe_irq_init()` initializes locking and probes MSI-X capability. `xe_irq_install()` resets hardware state, allocates MSI or MSI-X vectors, requests IRQs, enables the atomic IRQ gate, postinstalls masks/enables, and registers managed uninstall. Runtime IRQ handlers first check `xe->irq.enabled`, disable/ack master state, dispatch GT and platform-specific subevents, re-enable master interrupts, and perform display re-enable using GU misc ack data. Suspend clears `enabled`, synchronizes all active vectors, and resets interrupts; resume resets, postinstalls, and re-enables HWE interrupts for each GT.

## State And Persistence
Persistent state lives under `xe->irq`: spinlock, enabled atomic, MSI-X vector count, and xarray vector allocations. Hardware interrupt masks and enable registers are reset and reprogrammed across install, suspend, resume, and uninstall. MSI-X dynamic vector allocations persist until explicitly freed or global uninstall.

## Dependencies And Integration Points
This file integrates with PCI MSI/MSI-X APIs, Xe display IRQ code, GT/HWE IRQ handling, GuC, GSC proxy, PXP, hardware error handling, I2C, MERT, SR-IOV detection, memory IRQ support, and tile/GT topology helpers. It also relies on register definitions in `regs/xe_irq_regs.h`.

## Risks
Interrupt ordering is delicate: master disable/ack, lower-level ack, display re-enable, and IIR clearing must avoid lost or relatched interrupts. `identity[32]` is reused per bank, so bank-local bit handling must remain consistent. MSI-X vector xarray teardown uses `xa_for_each()` while freeing entries, which depends on xarray iteration semantics. VF paths require memory IRQ support on newer graphics versions. Top-level DPC containment handling returns early when MMIO reads all ones.

## Test Signals
Coverage should include MSI and MSI-X install/uninstall, dynamic MSI-X request/free, suspend/resume IRQ quiescing, VF memory IRQ delivery, display and GU misc events, I2C/MERT interrupt forwarding, media-vs-primary GT routing, PXP/GSC/HECI routing, and DPC containment reads. Interrupt storm and missed-interrupt tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_irq.h

## Purpose
`xe_irq.h` declares the public interrupt-management interface for Xe and defines the default MSI-X vector index used by the driver.

## Important APIs, Types, And Functions
- `XE_IRQ_DEFAULT_MSIX` is 1, paired with static GuC2Host vector 0 in the implementation.
- Declares init/install/suspend/resume lifecycle functions.
- Declares `xe_irq_enable_hwe()` for per-GT engine interrupt programming.
- Declares dynamic MSI-X request/free helpers for other Xe subsystems.

## Control Flow
Subsystems include this header to interact with IRQ setup or allocate dedicated MSI-X vectors. The implementation decides whether MSI, MSI-X, or memory-backed interrupt handling is active.

## State And Persistence
The header owns no state; it exposes operations over `xe->irq` and hardware masks managed by `xe_irq.c`.

## Dependencies And Integration Points
Depends on Linux interrupt types and forward-declares Xe core structures. It is used by driver probe, PM, GT setup, and subsystems needing MSI-X vectors.

## Risks
Callers using dynamic MSI-X helpers must obey vector lifetime and free allocated vectors. The static default vector constant must stay synchronized with the implementation's `enum xe_irq_msix_static`.

## Test Signals
Build/link tests plus runtime checks for MSI-X dynamic allocation/free and correct default vector reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw.c

## Purpose
`xe_late_bind_fw.c` loads optional late-binding firmware blobs, currently fan-control firmware, and pushes them to a MEI/GSC late-bind component when available.

## Important APIs, Types, And Functions
- Public functions: `xe_late_bind_init()`, `xe_late_bind_fw_load()`, and `xe_late_bind_wait_for_worker_completion()`.
- Firmware parsing uses `parse_lb_layout()` for FPT layout and `parse_cpd_header()` for CPD/manifest version extraction.
- `__xe_late_bind_fw_init()` validates hardware need, builds the `xe/<name>_8086_<device>_<subvendor>_<subdevice>.bin` path, requests firmware, validates size/layout, stores payload, and initializes work.
- `xe_late_bind_work()` waits for component binding, retries `push_payload()` on `-EBUSY`, logs component status codes, and drops failed payloads to prevent repeated attempts.
- Component integration uses `component_add_typed()`, bind/unbind callbacks, and managed remove.

## Control Flow
Initialization exits when the platform lacks late-bind support or required MEI components are disabled. Otherwise it registers a typed component, installs managed cleanup, creates an ordered workqueue, initializes each firmware slot, and queues any available payloads. Work can be queued before component binding; it waits up to 20 seconds for component ops, then retries payload push for up to 6 seconds on busy. Runtime PM is held while queued work is pending.

## State And Persistence
`struct xe_late_bind` tracks component ops/device, firmware slots, ordered workqueue, component-added flag, and a `disable` flag used to suppress reloads during PM flows. Firmware payloads are DRM-managed allocations; failed upload frees and nulls the payload so it will not be retried. Successful payloads remain available for future reload unless freed by device teardown.

## Dependencies And Integration Points
The file depends on Linux component framework, firmware loader, MEI late-bind component interfaces, GSC firmware layout ABI types, Xe PCode fan-count query, Xe PM runtime, and PCI IDs. It is tied to fan-control hwmon/firmware support through PCode-reported fan count.

## Risks
`parse_lb_layout()` returns without releasing firmware on parse failure in `__xe_late_bind_fw_init()`, which is a leak risk unless ownership is otherwise handled. Component binding races are handled by polling, but long waits during workqueue execution can delay ordered work. Positive MEI status codes and negative errno values share the same logging path. Missing firmware is non-fatal, which is intentional but can hide deployment errors unless debug logs are enabled.

## Test Signals
Test missing firmware, oversized firmware, bad FPT/CPD layouts, missing manifest entries, no-fan platforms, late component bind/unbind, busy retry behavior, runtime PM reference balance, and PM reload disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw.h

## Purpose
`xe_late_bind_fw.h` exposes the minimal late-bind firmware lifecycle API to the rest of the Xe driver.

## Important APIs, Types, And Functions
- Forward-declares `struct xe_late_bind`.
- Declares initialization, load/reload, and worker-flush helpers.

## Control Flow
Callers initialize late-bind support through `xe_late_bind_init()`, may request payload load with `xe_late_bind_fw_load()`, and can synchronize pending work with `xe_late_bind_wait_for_worker_completion()`.

## State And Persistence
The header owns no state; it operates on `struct xe_late_bind` defined in the types header.

## Dependencies And Integration Points
It depends only on Linux types and is included by Xe device/PM paths that coordinate late-bind firmware.

## Risks
Callers need to understand that `xe_late_bind_fw_load()` can queue async work and success does not mean the firmware has already reached MEI. The flush helper must be used before component teardown or other operations that invalidate payload/component state.

## Test Signals
Build coverage and PM/component teardown tests that call the flush path before removing the component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw_types.h

## Purpose
`xe_late_bind_fw_types.h` defines data structures and constants used by late-bind firmware loading and MEI component communication.

## Important APIs, Types, And Functions
- `XE_LB_MAX_PAYLOAD_SIZE` limits payloads to 4 KiB.
- `enum xe_late_bind_fw_id` currently contains `XE_LB_FW_FAN_CONTROL`.
- `struct xe_late_bind_fw` stores blob path, type, flags, payload pointer/size, work item, and parsed GSC firmware version.
- `struct xe_late_bind_component` stores MEI device and operation callbacks.
- `struct xe_late_bind` stores component state, per-ID firmware slots, workqueue, component flag, and reload-disable flag.

## Control Flow
The implementation fills each firmware slot during init, queues its `work_struct` during load, and uses the component fields once bind callbacks populate them.

## State And Persistence
Firmware payload and component pointers persist across initialization and reloads. The `disable` boolean provides coarse persistence of PM flow state so reloads can be suppressed.

## Dependencies And Integration Points
The header depends on workqueues, Linux device/path types, and Xe firmware ABI definitions for `struct gsc_version`. It is embedded in `struct xe_device`.

## Risks
The payload pointer is `const u8 *` but points to driver-allocated mutable memory. Future firmware IDs require synchronized updates to enum, arrays in the C file, and initialization loops.

## Test Signals
Compile-time and runtime tests should add coverage when new firmware IDs are introduced, verifying array indexing and work item initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt.c

## Purpose
`xe_lmtt.c` manages Local Memory Translation Tables for SR-IOV PF operation. LMTT maps VF-visible local-memory offsets to PF VRAM backing pages, sets the root directory in hardware, and invalidates GT/MERT TLBs when mappings change.

## Important APIs, Types, And Functions
- Public API: `xe_lmtt_init()`, `xe_lmtt_init_hw()`, `xe_lmtt_invalidate_hw()`, `xe_lmtt_prepare_pages()`, `xe_lmtt_populate_pages()`, `xe_lmtt_drop_pages()`, `xe_lmtt_estimate_pt_size()`, and `xe_lmtt_page_size()`.
- Variant selection uses `lmtt_2l_ops` or `lmtt_ml_ops` based on graphics version.
- `lmtt_pt_alloc()` creates VRAM-backed, 64K-capable page table BOs and stores child pointers in flexible arrays.
- `lmtt_alloc_range()` and `__lmtt_alloc_range()` recursively allocate VF page-table hierarchy.
- `lmtt_insert_bo()` walks a VRAM BO resource cursor and writes leaf PTEs.
- `lmtt_setup_dir_ptr()` programs LMEM/MERT directory pointer registers.

## Control Flow
PF initialization selects ops, allocates a root page directory, and registers managed cleanup. Hardware initialization programs the directory pointer after reset. VF setup calls `xe_lmtt_prepare_pages()` for the supported range, then `xe_lmtt_populate_pages()` for BO backstore. VF teardown calls `xe_lmtt_drop_pages()`, invalidates the PDE, invalidates GT TLBs, and recursively frees child page tables. Explicit hardware invalidation also triggers MERT invalidation on capable root tiles.

## State And Persistence
`struct xe_lmtt` stores root PD and ops. Each `struct xe_lmtt_pt` owns a pinned mapped VRAM BO plus child pointers. LMTT page-table contents persist in VRAM across normal operation and are re-registered after resets by `xe_lmtt_init_hw()`. Managed cleanup asserts all VF child entries are dropped before freeing the root.

## Dependencies And Integration Points
The file depends on Xe BO creation/mapping, tile/GT topology, SR-IOV PF checks, TLB invalidation fences, MERT invalidation, MMIO LMEM config registers, resource cursors, and the common `xe_map` memory access wrappers. It includes KUnit tests when built with `CONFIG_DRM_XE_KUNIT_TEST`.

## Risks
Recursive allocation error handling can leave partially populated child structures if a deeper allocation fails after PDE writes; callers need robust teardown on failure. Index assertions use `<=` in places where `<` may be expected. Mapping insertion assumes prepared leaf tables already exist. The `vram_offset` adjustment is marked `XXX`, signaling hardware address interpretation risk. Missing invalidations can expose stale VF translations.

## Test Signals
KUnit should cover 2L and ML page sizes, PTE encoding/indexing, range allocation/drop, PT size estimates, invalidation calls, partial allocation failures, and BO population over fragmented VRAM resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt.h

## Purpose
`xe_lmtt.h` declares the SR-IOV PF Local Memory Translation Table API and provides minimal stubs when PCI IOV is disabled.

## Important APIs, Types, And Functions
- Declares software init, hardware init, hardware invalidation, VF page preparation/population/drop, PT-size estimate, and page-size query functions.
- Stubs only `xe_lmtt_init()` and `xe_lmtt_init_hw()` when `CONFIG_PCI_IOV` is disabled.

## Control Flow
PF setup and reset code call into this API when LMTT is supported. Build configuration either links the real implementation or compiles no-op initialization.

## State And Persistence
No state is owned by the header. It exposes operations over `struct xe_lmtt`, which stores root page directory and ops.

## Dependencies And Integration Points
It forward-declares `struct xe_bo`, `struct xe_lmtt`, and `struct xe_lmtt_ops`, and is used by SR-IOV provisioning code.

## Risks
Only two functions are stubbed for non-IOV builds; callers of other LMTT functions must be compiled out under the same config. Public functions assume PF-only usage and initialized ops/root where applicable.

## Test Signals
Build configurations with and without `CONFIG_PCI_IOV`, plus PF flows that call init, reset-time hardware init, map/unmap, and invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_2l.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_2l.c

## Purpose
`xe_lmtt_2l.c` implements the two-level LMTT variant for older SR-IOV-capable platforms, mapping one root PDE per VF to a per-VF leaf table of 2 MiB local-memory PTEs.

## Important APIs, Types, And Functions
- Exports `const struct xe_lmtt_ops lmtt_2l_ops`.
- Root level is 1; leaf level is 0.
- PDE/PTE storage uses 32-bit entries.
- HAW is 37 bits with `CONFIG_DRM_XE_LMTT_2L_128GB`, otherwise 35 bits.
- Helpers provide entry counts, entry sizes, address shifts, PTE indexes, and PTE/PDE encoding with `FIELD_PREP()`.

## Control Flow
The common LMTT manager calls these ops to allocate table sizes, select indexes for guest local-memory offsets, and encode either leaf LMEM page entries or directory pointers. Leaf granularity is always 2 MiB; PDE pointers require 64 KiB alignment.

## State And Persistence
The file is stateless except for exported function-table data. Encoded PTE/PDE values persist in VRAM BOs allocated by `xe_lmtt.c`.

## Dependencies And Integration Points
It depends on bitfield/log2 helpers, Xe warning macros, and `xe_lmtt_types.h`. It is selected by `xe_lmtt.c` when the device does not require multi-level LMTT.

## Risks
Compile-time checks validate expected table sizes for configured HAW, but runtime misuse with unaligned offsets only warns and still returns encoded values. HAW configuration changes alter leaf table size and should be validated against hardware/firmware expectations.

## Test Signals
KUnit should verify HAW-dependent entry counts, 2 MiB leaf page size, 64 KiB PDE alignment checks, index wrapping, and encoding fields for representative offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_2l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_ml.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_ml.c

## Purpose
`xe_lmtt_ml.c` implements the multi-level LMTT variant for newer platforms with 48-bit local-memory host and guest address width.

## Important APIs, Types, And Functions
- Exports `const struct xe_lmtt_ops lmtt_ml_ops`.
- Root level is 2, intermediate level is 1, leaf level is 0.
- PDEs are 64-bit, leaf PTEs are 32-bit.
- Level-1 spans 32 GiB chunks; leaf entries map 2 MiB pages.
- Encoding validates 64 KiB directory-pointer alignment and 2 MiB LMEM page alignment.

## Control Flow
The common LMTT manager recurses through levels 2 and 1 using this ops table, then writes level-0 PTEs for VRAM backstore. Indexing uses guest address bits shifted by either 35 or 21 bits depending on level.

## State And Persistence
The file owns no mutable state. It supplies static ops used to encode persistent table BO contents.

## Dependencies And Integration Points
It integrates with `xe_lmtt.c` via `struct xe_lmtt_ops` and relies on bitfield/log2/sizes helpers plus `XE_WARN_ON()`.

## Risks
48-bit field fitting is easy to break if hardware field definitions change. Level numbering is implementation-specific and must remain consistent with common recursive allocation. Alignment violations warn rather than fail.

## Test Signals
Verify root/intermediate/leaf entry counts, level shifts, index calculations across 32 GiB boundaries, and PTE/PDE field encoding for high offsets up to 48-bit limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_ml.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_types.h

## Purpose
`xe_lmtt_types.h` defines the shared data model and ops interface for Local Memory Translation Tables.

## Important APIs, Types, And Functions
- `LMTT_PTE_INVALID` is the zero invalid entry value.
- `struct xe_lmtt` contains the root directory pointer and selected ops table.
- `struct xe_lmtt_pt` models a page table level, its backing BO, and child pointers.
- `struct xe_lmtt_ops` abstracts variant-specific root level, entry count, entry size, shift, index, and encoding.
- Externs expose `lmtt_2l_ops` and `lmtt_ml_ops`.

## Control Flow
`xe_lmtt.c` uses these structures to select a variant and perform common recursive allocation/population/drop while delegating layout math to ops.

## State And Persistence
`struct xe_lmtt` and child PT structures persist for the PF lifetime. The header itself owns no storage.

## Dependencies And Integration Points
Depends on Linux types and forward declarations for Xe BOs. It is the contract between common LMTT manager and layout-specific source files.

## Risks
The flexible array in `struct xe_lmtt_pt` exists only when allocation used the correct entry count. Ops must remain internally consistent: wrong level counts or shifts corrupt common allocation logic.

## Test Signals
Compile-time and KUnit tests that instantiate both ops tables and validate recursive allocation assumptions against the type layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc.c

## Purpose
`xe_lrc.c` implements Logical Ring Context creation, layout, register image initialization, ring writes, seqno fences, memory-backed interrupt register patching, context-restore workaround batches, default LRC dumping/lookup, hang snapshots, and context timestamp accounting.

## Important APIs, Types, And Functions
- Public creation/lifetime: `xe_lrc_create()`, `xe_lrc_destroy()`, `xe_lrc_get()`/`put()` in the header.
- Size/layout helpers: `xe_gt_lrc_hang_replay_size()`, `xe_gt_lrc_size()`, `xe_lrc_reg_size()`, `xe_lrc_engine_state_size()`, offsets, and GGTT/map helpers.
- Context initialization: `empty_lrc_data()`, `set_offsets()`, `set_context_control()`, `set_memory_based_intr()`, `xe_lrc_ctx_init()`, and `xe_lrc_init()`.
- Ring and descriptor helpers: `xe_lrc_write_ring()`, `xe_lrc_set_ring_head/tail()`, `xe_lrc_ring_head/tail/space()`, and `xe_lrc_descriptor()`.
- Fence/seqno helpers: `xe_lrc_alloc_seqno_fence()`, `xe_lrc_init_seqno_fence()`, `xe_lrc_seqno()`, and start-seqno equivalents.
- Workaround/indirect context setup: `setup_wa_bb()`, `setup_indirect_ctx()`, `xe_lrc_setup_wa_bb_with_scratch()`.
- Debug/recovery: `xe_lrc_dump_default()`, `xe_lrc_lookup_default_reg_value()`, `xe_lrc_snapshot_capture()`, delayed capture/print/free.
- Utilization: `xe_lrc_timestamp()` and `xe_lrc_update_timestamp()`.

## Control Flow
Creation allocates `struct xe_lrc`, calculates BO size from ring, PPHWSP, context image, optional indirect context/ring-state pages, and WA BB, then creates a GGTT-pinned context BO plus a system seqno BO. `xe_lrc_ctx_init()` copies default or replay state, writes VM PDP/ASID, programs memory IRQ pointers and MSI-X vector data, initializes ring registers, descriptor fields, arbitration, seqno memory, WA BB, and optional indirect context. Runtime ring writes update the software tail and wrap around the mapped ring. Snapshot capture grabs stable scalar state immediately and defers BO copy to a sleepable path.

## State And Persistence
The LRC BO contains ring, PPHWSP, context image, optional indirect pages, and WA BB. `seqno_bo` stores GPU-written sequence numbers in system memory. `struct xe_lrc` stores descriptor, ring tail shadow, fence context, replay size, flags, and cached timestamp. BOs are pinned/mapped until refcounted destruction. Context images are persistent GPU-visible state that may be copied from defaults, replay buffers, or updated after GGTT address changes.

## Dependencies And Integration Points
The file integrates with hardware engine metadata, GT default LRC storage, VM page-table descriptors, BO/GGTT allocation, memory IRQ pointers, MSI-X vectors, ring operation workarounds, configfs test batch injection, DRM client BO accounting, hw fences, tracepoints, and Xe map wrappers. It uses generated register layout constants and MI/GFXPIPE/GFX_STATE instruction definitions.

## Risks
The file is sensitive to platform register layout tables and engine-class variants. Indirect context and indirect ring-state offsets depend on BO size and flags. Workaround batch generation must never overflow 4 KiB WA BB or indirect context limits. Configfs-injected batches intentionally taint the kernel and can submit arbitrary context-restore commands. Timestamp accounting is explicitly racy for active contexts and requires read-again logic. Memory IRQ pointers must be repatched if BO GGTT addresses change.

## Test Signals
Tests should cover LRC sizing by platform/class, context creation with VM/user/PXP/runalone flags, ring wrap writes, seqno fence initialization, WA BB scratch path for iomem/non-iomem maps, indirect context setup, memory IRQ pointer patching, MSI-X vector programming, default LRC register lookup, snapshot delayed capture, and timestamp update on active/inactive contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc.h

## Purpose
`xe_lrc.h` declares the Logical Ring Context public API, creation flags, snapshot structure, fixed PPHWSP scratch offsets, WA BB size, and inline refcount/ring-size helpers.

## Important APIs, Types, And Functions
- `struct xe_lrc_snapshot` captures context descriptor, ring pointers, seqnos, timestamps, and optional copied HW context data.
- Creation flags include runalone, PXP, user context, and disabling a state-cache performance fix.
- Declares lifecycle, ring, descriptor, seqno, GGTT-address, context-register, memory IRQ update, default dump/lookup, HWE state emission, priority, snapshot, scratch, and timestamp APIs.
- `xe_lrc_ring_size()` currently returns 16 KiB.

## Control Flow
Execution queue and GT code use this API to allocate contexts, write rings, create fences, dump/debug contexts, and update utilization. Refcount helpers wrap `kref`.

## State And Persistence
The header defines snapshot persistence fields and exposes operations over the LRC state defined in `xe_lrc_types.h`.

## Dependencies And Integration Points
It includes `xe_lrc_types.h` and forward-declares Xe execution, GT, VM, HWE, DRM printer, and BB structures. It is a central contract for scheduler, exec queue, debug, and reset/recovery code.

## Risks
API breadth means changes to LRC layout or flags can ripple widely. Snapshot structures carry BO references and must be freed with the matching helper. Callers must respect ring-space and register-index conventions.

## Test Signals
Build coverage for all users, refcount lifetime tests, snapshot allocation/free paths, and ABI-like validation of creation flags and fixed offsets used by other modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc_types.h

## Purpose
`xe_lrc_types.h` defines the core `struct xe_lrc` storage used by logical ring contexts.

## Important APIs, Types, And Functions
- `struct xe_lrc` stores the context/ring BO, seqno BO, size, replay size, owning GT, flags, refcount, ring state, descriptor, hardware fence context, and cached timestamp.
- Flags indicate indirect context and indirect ring-state page usage.
- Forward-declares `struct xe_lrc_snapshot`.

## Control Flow
The implementation allocates and initializes this structure in `xe_lrc_create()`, while users interact through the public API and refcount helpers.

## State And Persistence
This is persistent per-context state. The ring tail is driver-owned shadow state; seqno memory is GPU-written and CPU-read; descriptor and flags define GPU execution context identity and layout.

## Dependencies And Integration Points
Depends on Linux kref and Xe hardware fence types. It is used by scheduler, execution queues, fencing, and debug/recovery paths.

## Risks
The structure binds memory objects and fence context lifetime. Any direct mutation outside LRC helpers risks desynchronizing software tail, descriptor bits, or timestamp state from hardware-visible memory.

## Test Signals
Lifetime/refcount tests and creation/destruction tests should verify BOs, fence context, and cached fields are initialized and released in the right order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_macros.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_macros.h

## Purpose
`xe_macros.h` provides small common macros used by Xe code for warnings and ioctl argument debug logging.

## Important APIs, Types, And Functions
- `XE_WARN_ON` aliases the kernel `WARN_ON`.
- `XE_IOCTL_DBG(xe, cond)` evaluates a condition, logs a DRM debug message with file, line, and expression text when true, and returns the boolean result.

## Control Flow
Callers use `XE_IOCTL_DBG()` in validation paths where a failed condition should be logged but handled by caller logic rather than necessarily warning.

## State And Persistence
No persistent state. The macro can emit debug log records.

## Dependencies And Integration Points
Depends on Linux bug helpers and assumes the passed Xe object has a `drm` member suitable for `drm_dbg()`. Used across driver validation code.

## Risks
The macro evaluates `cond` once, which is good, but still should not be used with side-effect-heavy expressions if logging behavior changes control clarity. It embeds `__FILE__`/`__LINE__`, which can be noisy in tests.

## Test Signals
Compile use sites and verify debug builds produce useful messages without changing validation return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_map.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_map.h

## Purpose
`xe_map.h` wraps `iosys_map` memory access so Xe can assert device memory accessibility before touching shared system or VRAM mappings.

## Important APIs, Types, And Functions
- Copy helpers: `xe_map_memcpy_to()`, `xe_map_memcpy_from()`, and `xe_map_memset()`.
- 32-bit helpers: `xe_map_read32()` and `xe_map_write32()`, with iomem-aware readl/writel handling.
- Typed macros: `xe_map_rd()`, `xe_map_wr()`, `xe_map_rd_field()`, and `xe_map_wr_field()`.

## Control Flow
Every helper first calls `xe_device_assert_mem_access(xe)` and then delegates to iosys-map operations. This centralizes runtime-PM/D3Cold safety checks.

## State And Persistence
The header owns no state but controls access to persistent GPU-visible BO contents. Writes through these helpers may update context images, page tables, memory IRQ pages, and other device-shared memory.

## Dependencies And Integration Points
Depends on `iosys-map` and Xe device definitions. It is used by LRC, LMTT, memory pools, memory IRQ, and other BO-backed state managers.

## Risks
Bypassing these helpers can miss memory-access assertions. The `xe_map_read32/write32` helpers are marked FIXME and may eventually be removed, so new code should prefer typed iosys wrappers through this layer.

## Test Signals
Runtime-PM tests should assert that memory access during disallowed states is caught. Iomem and system-memory BO mappings need both read/write coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool.c

## Purpose
`xe_mem_pool.c` implements a DRM MM suballocation pool backed by one pinned, CPU-mapped Xe BO, with optional shadow BO support for staged/atomic updates.

## Important APIs, Types, And Functions
- `struct xe_mem_pool` contains a `drm_mm`, active BO, optional shadow BO, swap mutex, CPU pointer, and iomem flag.
- `xe_mem_pool_init()` creates the backing BO, optional CPU shadow memory for iomem mappings, optional shadow BO, initializes `drm_mm`, and registers managed teardown.
- Shadow helpers: `xe_mem_pool_sync()`, `xe_mem_pool_swap_shadow_locked()`, and `xe_mem_pool_sync_shadow_locked()`.
- Address/data helpers: `xe_mem_pool_gpu_addr()`, `xe_mem_pool_cpu_addr()`, `xe_mem_pool_bo_flush_write()`, `xe_mem_pool_bo_sync_read()`, and `xe_mem_pool_node_cpu_addr()`.
- Node lifecycle: `xe_mem_pool_alloc_node()`, `xe_mem_pool_insert_node()`, and `xe_mem_pool_free_node()`.
- `xe_mem_pool_dump()` dumps allocator state.

## Control Flow
Initialization allocates a managed BO of `size`, reserves `guard` bytes at the end by giving `drm_mm` only `size - guard`, and optionally creates a shadow BO protected by `swap_guard`. Clients allocate nodes, write through CPU addresses, flush/sync for iomem-backed BOs, and free nodes when done. Shadow users must hold the swap guard while syncing or swapping.

## State And Persistence
The pool persists until DRM-managed cleanup. The active BO and optional shadow BO are pinned and mapped. For iomem BO mappings, `pool->cpu_addr` points to separate kernel memory and explicit flush/readback copies synchronize with the BO. `drm_mm` state tracks active suballocations.

## Dependencies And Integration Points
Depends on Xe BO creation/mapping, tile/device helpers, `xe_map`, DRM MM, managed DRM cleanup, and MI command headers. It is intended for Xe subsystems needing persistent GPU-addressable suballocations.

## Risks
`xe_mem_pool_insert_node()` uses raw `drm_mm_insert_node()` without internal locking, so callers must serialize allocations if needed. Shadow swap changes `pool->bo`, so clients caching GPU addresses must refresh after swaps. For iomem mappings, forgetting flush/sync leaves CPU and GPU views stale. `xe_mem_pool_free_node()` assumes the node was inserted before remove.

## Test Signals
Test pool size/guard handling, allocation/free fragmentation, iomem flush/readback, shadow initialization/sync/swap under lockdep, GPU address changes after swap, and dump output for allocator state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool.h

## Purpose
`xe_mem_pool.h` declares the memory-pool API for BO-backed suballocation and optional shadow synchronization.

## Important APIs, Types, And Functions
- Declares pool initialization, full sync, shadow swap, per-node shadow sync, GPU/CPU address accessors, swap guard accessor, flush/readback helpers, node allocation/insertion/free, node CPU address, and dump.
- Includes `xe_mem_pool_types.h` for node and flag definitions.

## Control Flow
Clients create a pool, allocate/insert nodes, access node memory by CPU pointer or GPU address offset, optionally flush/sync for iomem, and free nodes.

## State And Persistence
The header owns no state but exposes functions over `struct xe_mem_pool` and `struct xe_mem_pool_node` state allocated by the implementation.

## Dependencies And Integration Points
Depends on Linux sizes/types, DRM MM, DRM printer, and Xe tile forward declarations. It is used by subsystems needing compact GPU-visible allocation arenas.

## Risks
The API does not expose internal locking for `drm_mm`; callers must establish allocation serialization. Shadow operations require respecting the returned mutex.

## Test Signals
Compile users and verify allocation, address, shadow, and dump APIs across regular and iomem-backed BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool_types.h

## Purpose
`xe_mem_pool_types.h` defines the public node type and initialization flag for Xe memory pools.

## Important APIs, Types, And Functions
- `XE_MEM_POOL_BO_FLAG_INIT_SHADOW_COPY` requests shadow BO setup.
- `struct xe_mem_pool_node` wraps a `struct drm_mm_node` used for suballocation.

## Control Flow
Clients allocate nodes through the implementation and pass the flag at pool initialization when they need shadow-copy behavior.

## State And Persistence
Each node persists while inserted in a pool and is freed by `xe_mem_pool_free_node()`. The header owns no storage.

## Dependencies And Integration Points
Depends on DRM MM. Used by pool clients and `xe_mem_pool.c`.

## Risks
A node must not be freed before removal from `drm_mm`, and the type does not track insertion state itself.

## Test Signals
Node allocation/free tests and misuse detection around double free or freeing uninserted nodes where debug config can catch it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq.c

## Purpose
`xe_memirq.c` implements memory-based interrupt reporting for Xe, a scalable alternative to MMIO interrupt status registers used especially by SR-IOV and MSI-X flows.

## Important APIs, Types, And Functions
- `xe_memirq_init()` allocates and initializes the memory IRQ BO and enables the mask.
- Pointer helpers return GGTT addresses for source, status, and enable-mask pages: `xe_memirq_source_ptr()`, `xe_memirq_status_ptr()`, and `xe_memirq_enable_ptr()`.
- `xe_memirq_init_guc()` programs GuC self-config keys with memory IRQ source/status addresses.
- Reset/postinstall toggle interrupt processing through `xe_memirq_reset()` and `xe_memirq_postinstall()`.
- Dispatch helpers check source/status bytes and call HWE or GuC handlers.
- Public handlers are `xe_memirq_hwe_handler()` and `xe_memirq_handler()`.
- `xe_memirq_guc_sw_int_0_irq_pending()` peeks at GuC software interrupt state without clearing it.

## Control Flow
Initialization exits when the device does not use memory IRQs. Otherwise it allocates a system, GGTT-pinned, uncached BO sized either one page or one page per engine instance for MSI-X, clears it, maps source/status/mask iosys offsets, and enables all mask bits. Handlers check source bytes, then corresponding status vectors, clear consumed bytes, and invoke engine or GuC handlers. MSI-X per-HWE flow can call `xe_memirq_hwe_handler()` directly for each engine.

## State And Persistence
`struct xe_memirq` stores the BO, iosys maps, and enabled flag. Hardware writes 0xff bytes into source/status memory; software clears them after dispatch. The mask page persists in the BO and is toggled on reset/postinstall. For MSI-X, page layout is duplicated per engine instance to distinguish engines reporting to instance zero.

## Dependencies And Integration Points
Depends on Xe BO creation, GGTT addresses, GT/HWE iteration, GuC self-config, GuC IRQ handling, tile/device helpers, memory IRQ capability checks, and register bit definitions. LRC code programs these GGTT pointers into context images.

## Risks
Unexpected status byte values are rate-limited errors but still treated as received. Correct source/status offsets are crucial; MSI-X instance remapping changes pointer semantics. `GUC_INTR_SW_INT_0` has special no-clear-then-clear ordering to avoid VF recovery races. BO must be UC and system memory to match hardware requirements.

## Test Signals
Test BO size/layout for MSI-X and non-MSI-X, GuC self-config values, source/status dispatch and clearing, SW_INT_0 pending behavior, reset/postinstall mask changes, and VF memory IRQ interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq.h

## Purpose
`xe_memirq.h` declares the memory-based interrupt public API used by IRQ, LRC, GuC, and HWE code.

## Important APIs, Types, And Functions
- Declares init, source/status/enable pointer getters, reset/postinstall, HWE and global handlers, GuC setup, and SW_INT_0 pending query.

## Control Flow
Initialization allocates memory IRQ pages before LRC or GuC programming. LRC code queries GGTT pointers, IRQ code toggles/dispatches handlers, and recovery code can query SW_INT_0 pending state.

## State And Persistence
The header owns no state; it operates on `struct xe_memirq` defined in the types header.

## Dependencies And Integration Points
Forward-declares GuC, hardware engine, and memirq structures. It is the contract between memory IRQ implementation and the rest of Xe interrupt/context setup.

## Risks
Callers must only use pointer getters after successful `xe_memirq_init()` and when the device actually uses memory IRQs. Dispatch helpers assume the BO and maps are valid.

## Test Signals
Build/link tests and runtime assertions around pointer use before/after init, reset, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq_types.h

## Purpose
`xe_memirq_types.h` defines the memory IRQ page-layout offsets and the runtime storage object for memory-based interrupts.

## Important APIs, Types, And Functions
- `XE_MEMIRQ_STATUS_OFFSET(inst)` defines status report page offset.
- `XE_MEMIRQ_SOURCE_OFFSET(inst)` defines source report page offset.
- `XE_MEMIRQ_ENABLE_OFFSET` defines interrupt mask offset.
- `struct xe_memirq` stores the BO, source/status/mask iosys maps, and enabled flag.

## Control Flow
The implementation uses the offsets to allocate and index page-like regions inside a single BO. LRC/GuC programming consumes the derived GGTT addresses.

## State And Persistence
The struct persists per tile. Hardware and software share the BO contents; software owns the `enabled` flag and map metadata.

## Dependencies And Integration Points
Depends on `iosys-map` and forward-declares `struct xe_bo`. Used by tile state, IRQ code, memirq implementation, and LRC context setup.

## Risks
Offsets are ABI-like hardware contract values. Changing them without matching hardware programming would break interrupt delivery. The enabled flag is separate from hardware mask contents, so both must remain synchronized.

## Test Signals
Static layout assertions, pointer calculation tests, and dispatch tests validating source/status/mask offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mert.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mert.c

## Purpose
`xe_mert.c` manages MERT-specific state, LMTT invalidation, and MERT interrupt handling for SR-IOV-capable devices with a standalone MERT block.

## Important APIs, Types, And Functions
- `xe_mert_init_early()` initializes spinlock and completion state on the root tile.
- `xe_mert_invalidate_lmtt()` triggers MERT LMTT invalidation and waits up to `HZ / 4`.
- `mert_handle_cat_error()` decodes CAT error register state and handles unmapped GGTT or LMTT faults.
- `xe_mert_irq_handler()` processes MERT interrupts, CAT errors, and invalidation completion.

## Control Flow
Early init prepares synchronization. LMTT invalidation takes the lock, triggers the descriptor if not already active, reinitializes completion, writes the valid bit, then waits for completion. The IRQ handler runs on root tile SOC memory interrupt, handles CAT errors, then checks whether the hardware cleared the valid bit and completes waiters.

## State And Persistence
`struct xe_mert` stores a spinlock, `tlb_inv_triggered`, and a completion. Trigger state persists between invalidate request and interrupt completion. CAT errors can wedge the device on severe faults.

## Dependencies And Integration Points
Integrates with Xe MMIO, root tile state, SR-IOV logging, device wedging, MERT registers, IRQ dispatch in `xe_irq.c`, and LMTT invalidation in `xe_lmtt.c`.

## Risks
Invalidation depends on receiving the MERT interrupt before timeout. Severe CAT error handling wedges the device, while LMTT faults are only debug-logged with a TODO for malicious VF tracking. Concurrent invalidation callers share one trigger/completion and rely on lock-protected state.

## Test Signals
Test successful invalidation completion, timeout path, concurrent callers, CAT error decoding, wedging on unmapped GGTT/unexpected codes, and IRQ path integration from master interrupt bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mert.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mert.h

## Purpose
`xe_mert.h` defines MERT state and declares the MERT lifecycle/IRQ APIs, with IRQ no-op support when PCI IOV is disabled.

## Important APIs, Types, And Functions
- `struct xe_mert` contains the spinlock, invalidation-triggered flag, and completion.
- Declares early init, LMTT invalidation, and IRQ handler under `CONFIG_PCI_IOV`.
- Provides a no-op `xe_mert_irq_handler()` stub for non-IOV builds.

## Control Flow
Root tile initialization sets up the structure, LMTT code calls invalidation, and IRQ code calls the handler on relevant master interrupt bits.

## State And Persistence
The state lives in the root tile for the device lifetime. The header owns no storage by itself.

## Dependencies And Integration Points
Depends on Linux completion/spinlock/types and forward-declares `struct xe_device`. It links MERT into SR-IOV, LMTT, and IRQ paths.

## Risks
Only the IRQ handler is stubbed for non-IOV builds; callers of init/invalidate must be compiled under the same feature guard. The structure is synchronization-sensitive and must be initialized before invalidation or IRQ handling.

## Test Signals
Build both PCI IOV and non-IOV configurations; runtime test init-before-use and invalidation timeout/completion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mert.h -->
