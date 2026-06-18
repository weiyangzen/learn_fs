# Research Report: subset-b-001268

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/xilinx_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/xilinx/xilinx_dma.c

## Purpose

This file is the Linux DMAengine platform driver for several Xilinx soft DMA IP blocks: AXI DMA, AXI CDMA, AXI VDMA, and AXI MCDMA. It binds OF compatibles `xlnx,axi-dma-1.00.a`, `xlnx,axi-cdma-1.00.a`, `xlnx,axi-vdma-1.00.a`, and `xlnx,axi-mcdma-1.00.a`, exposes DMAengine channels, translates DT DMA phandles, allocates hardware descriptors, and drives transfers through memory-mapped control/status registers.

## Important APIs, Types, and Functions

Core state is split across `struct xilinx_dma_device`, which owns the mapped register base, clocks, DMAengine `dma_device`, channel array, address width, and IP-specific config, and `struct xilinx_dma_chan`, which owns per-channel register offsets, descriptor queues, DMA direction, IRQ, tasklet, state flags, transfer callbacks, and VDMA configuration. Hardware descriptor layouts are represented by `xilinx_vdma_desc_hw`, `xilinx_axidma_desc_hw`, `xilinx_aximcdma_desc_hw`, and `xilinx_cdma_desc_hw`, wrapped in per-segment structures that carry list nodes and DMA addresses.

The DMAengine entry points are wired in `xilinx_dma_probe()`: `device_alloc_chan_resources`, `device_free_chan_resources`, `device_terminate_all`, `device_synchronize`, `device_tx_status`, `device_issue_pending`, and `device_config` are shared, while prep callbacks differ by IP. AXI DMA supports `device_prep_slave_sg`, `device_prep_peripheral_dma_vec`, and `device_prep_dma_cyclic`; CDMA supports `device_prep_dma_memcpy`; VDMA supports `device_prep_interleaved_dma`; MCDMA supports `xilinx_mcdma_prep_slave_sg()`. The VDMA runtime control API `xilinx_vdma_channel_set_config()` is exported for consumers that need parking, genlock, frame count, delay, fsync source, reset, or vertical flip control.

Transfer control is abstracted by per-channel function pointers. `xilinx_vdma_start_transfer()`, `xilinx_dma_start_transfer()`, `xilinx_cdma_start_transfer()`, and `xilinx_mcdma_start_transfer()` each program the descriptor registers required by their IP, set interrupt coalescing/delay fields, run the channel, and move queued descriptors to `active_list`. Stop behavior uses either `xilinx_dma_stop_transfer()` or CDMA's idle wait in `xilinx_cdma_stop_transfer()`.

## Control Flow

Probe selects an IP config from the OF match data, enables the correct clock set, maps registers, reads DT properties such as address width, SG length width, VDMA frame stores, flush-on-fsync mode, and AXI-stream metadata support, configures the DMA mask, fills DMAengine capability bits, probes child channel nodes, registers the DMAengine device, and registers an OF DMA controller translator. Channel probing reads direction-specific compatible strings, data width, DRE presence, IRQ delay, genlock, vertical flip support, and IRQ lines, then chooses start/stop callbacks and resets the channel.

Client flow follows normal DMAengine ordering. Prep functions allocate a software transaction descriptor, fill one or more hardware segments, and return `dma_async_tx_descriptor`. `xilinx_dma_tx_submit()` assigns a cookie, chains the descriptor into `pending_list`, and marks cyclic state when needed. `xilinx_dma_issue_pending()` calls the selected start routine under the channel spinlock. Interrupt handlers acknowledge status, flag unrecoverable errors, complete active descriptors into `done_list`, restart pending work when possible, and schedule a tasklet. The tasklet calls `xilinx_dma_chan_desc_cleanup()`, invokes callbacks outside the spinlock, runs dependencies, and frees or recycles descriptor storage.

## State and Persistence

The driver keeps all state in RAM and hardware registers; there is no on-disk persistence. Queue state is held in `pending_list`, `active_list`, `done_list`, and `free_seg_list`, protected by `chan->lock`. AXI DMA and MCDMA preallocate coherent descriptor rings and recycle segments through `free_seg_list`; VDMA and CDMA allocate descriptors from DMA pools. Flags such as `idle`, `err`, `cyclic`, `terminating`, `desc_pendingcount`, and `desc_submitcount` model hardware progress and cleanup decisions. Register state is restored through reset/start paths rather than saved persistently.

## Dependencies and Integration Points

The file depends on DMAengine core APIs, OF DMA registration, Linux platform driver probing, IRQ handling, tasklets, DMA pools/coherent allocation, clock framework, and 64-bit MMIO helpers. DT bindings are critical: channel compatibles decide direction and register offsets, `xlnx,datawidth` and `xlnx,include-dre` determine alignment constraints, `xlnx,addrwidth` controls DMA mask and 64-bit descriptor programming, and VDMA-specific `xlnx,num-fstores` is mandatory. The driver integrates with async_tx callbacks, DMA metadata support through descriptor APP words when `xlnx,axistream-connected` is set, and external VDMA users via `xilinx_vdma_channel_set_config()`.

## Risks and Edge Cases

Descriptor ownership is sensitive: AXI DMA/MCDMA recycle preallocated descriptors while VDMA/CDMA free pool allocations, so wrong IP type checks would corrupt memory. Several paths rely on hardware status bits and timeout loops; a stuck reset or halt leaves `chan->err` set and may require system-level recovery. Cyclic AXI DMA has special handling that moves done descriptors back to active and uses a synthetic tail descriptor, which is a high-risk area for regressions. MCDMA interrupt demultiplexing uses SER masks and channel IDs, so off-by-one handling or DT channel numbering errors can route completions to the wrong channel. VDMA has additional risks around frame store counts, parking, genlock, vertical flip, and flush-on-fsync recoverable error masking.

## Test Signals

Useful validation signals include successful probe messages for each IP type, DT probe failures for missing mandatory properties, DMAengine memcpy tests for CDMA, cyclic audio-style tests for AXI DMA, VDMA interleaved frame transfer tests, MCDMA multichannel SG tests, IRQ completion counts, callback residue values, and forced error/status-bit tests that exercise reset and termination. Static checks should cover lock ordering around callbacks, descriptor list transitions, DMA mask/address width handling, and cleanup paths after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/xilinx_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/xilinx_dpdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/xilinx/xilinx_dpdma.c

## Purpose

This file implements the DMAengine driver for the Xilinx ZynqMP DisplayPort DMA (DPDMA) controller. It is a memory-to-device engine used by the display pipeline, supports six hardware channels, cyclic and interleaved transfers, grouped video-channel triggering, debugfs test hooks, and virtual-DMA based descriptor lifecycle management.

## Important APIs, Types, and Functions

`struct xilinx_dpdma_device` owns the DMAengine device, register base, shared IRQ, AXI clock, channel pointers, and extended-address flag. `struct xilinx_dpdma_chan` embeds `virt_dma_chan`, owns per-channel registers, running/first-frame/video-group flags, a stop wait queue, descriptor pool, error tasklet, and two hardware-facing descriptor pointers: `desc.pending` and `desc.active`. `struct xilinx_dpdma_hw_desc` mirrors the 256-byte-aligned hardware descriptor format, while `xilinx_dpdma_sw_desc` and `xilinx_dpdma_tx_desc` wrap hardware descriptors and virt-dma transactions.

The main DMAengine callbacks are `xilinx_dpdma_alloc_chan_resources()`, `xilinx_dpdma_free_chan_resources()`, `xilinx_dpdma_prep_dma_cyclic()`, `xilinx_dpdma_prep_interleaved_dma()`, `xilinx_dpdma_issue_pending()`, `xilinx_dpdma_config()`, pause/resume, terminate, and synchronize. `xilinx_dpdma_irq_handler()` services shared controller interrupts, while `xilinx_dpdma_chan_vsync_irq()`, `xilinx_dpdma_chan_done_irq()`, and `xilinx_dpdma_chan_err_task()` manage normal frame switching, callbacks, and error recovery.

## Control Flow

Probe allocates the device, gets the `axi_clk`, maps registers, initializes hardware by disabling interrupts and channels, requests the shared IRQ, sets DMAengine capabilities (`DMA_SLAVE`, `DMA_PRIVATE`, `DMA_CYCLIC`, `DMA_INTERLEAVE`, `DMA_REPEAT`, `DMA_LOAD_EOT`), initializes six virtual channels, enables the AXI clock, registers the DMAengine device and OF DMA controller, enables interrupts, and creates a debugfs testcase file.

Prep paths build cyclic or repeating interleaved descriptors. Cyclic preparation splits the buffer into periods, validates 256-byte alignment, links descriptors in a ring, sets complete interrupts and last-of-frame, and returns a virt-dma prepared transaction. Interleaved preparation validates MEM_TO_DEV, repeat/load-EOT flags, alignment, line size, and stride, then builds a single self-linked descriptor suitable for display refresh.

`xilinx_dpdma_issue_pending()` moves virt-dma issued descriptors into hardware scheduling via `xilinx_dpdma_chan_queue_transfer()`. Queueing enables the channel if stopped, removes the next virt descriptor, stamps descriptor IDs from the cookie, writes the descriptor start address, and triggers either the individual channel or a ready video group. VSYNC then verifies the pending descriptor ID has become active, completes the previous active descriptor, promotes pending to active, and queues another transfer. Descriptor-done IRQs invoke cyclic callbacks for the current active descriptor.

## State and Persistence

The driver stores transient state only. `running`, `first_frame`, `video_group`, `desc.pending`, and `desc.active` describe hardware scheduling. The virt-dma queue owns submitted-but-not-hardware-pending descriptors. Hardware descriptor pools are allocated per channel and freed with channel resources. Stop synchronization uses `wait_to_stop` and the NO_OSTAND interrupt or a polling fallback in error-task context. Debugfs state is global (`dpdma_debugfs`) and tracks one active test request and descriptor-done count.

## Dependencies and Integration Points

The driver depends on DMAengine, virt-dma, OF DMA, debugfs, wait queues, tasklets, DMA pools, and `dt-bindings/dma/xlnx-zynqmp-dpdma.h` channel IDs. It is tightly integrated with the DRM/display pipeline through `DMA_MEM_TO_DEV` transfers and the custom `struct xilinx_dpdma_peripheral_config` carried in `dma_slave_config.peripheral_config` to mark grouped video channels. OF translation exposes hardware channels by `dma_spec->args[0]`.

## Risks and Edge Cases

Correct operation depends on VSYNC ordering. If a retrigger races with VSYNC, the driver leaves the pending descriptor in place and retries on the next frame; changes in this area can cause frame drops or stale descriptors. The terminate path pauses channels and frees only descriptors that hardware cannot touch; pending and active descriptors are completed or freed later by synchronize. Video group stopping clears `video_group` flags while pausing running grouped channels, so mixed grouped and ungrouped usage needs care. Error handling disables channel interrupts, waits for outstanding transactions, disables the channel, may reschedule an errored active descriptor, and then re-enables interrupts; repeated errors can loop without higher-level throttling.

## Test Signals

Relevant tests include display pipeline bring-up with all six channels, cyclic callback cadence, interleaved repeat/load-EOT operation, grouped RGB/video-channel triggering, terminate/synchronize behavior while frames are outstanding, NO_OSTAND timeout paths, and injected descriptor/AXI/global error interrupts. The debugfs `testcase` file exposes a descriptor-done IRQ count test for a selected channel when debugfs is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/xilinx_dpdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/zynqmp_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/xilinx/zynqmp_dma.c

## Purpose

This file implements the DMAengine memcpy driver for Xilinx ZynqMP DMA and AMD Versal Gen 2 DMA-compatible hardware. It exposes one DMA_MEMCPY channel per platform device, manages source and destination linked-list descriptors, handles interrupts and runtime power management, and registers an OF DMA controller.

## Important APIs, Types, and Functions

`struct zynqmp_dma_device` owns the DMAengine device, channel pointer, and main/APB clocks. `struct zynqmp_dma_chan` owns mapped registers, descriptor lists, a coherent low-level descriptor pool, software descriptor pool, IRQ, tasklet, idle/error flags, bus width, burst lengths, descriptor size, and an optional IRQ offset for Versal Gen 2. `struct zynqmp_dma_desc_sw` represents a submitted transaction and may link additional child descriptors through `tx_list`; each software descriptor points to paired source and destination `struct zynqmp_dma_desc_ll` hardware descriptors.

The DMAengine operations are `zynqmp_dma_prep_memcpy()`, `zynqmp_dma_tx_submit()`, `zynqmp_dma_issue_pending()`, `zynqmp_dma_alloc_chan_resources()`, `zynqmp_dma_free_chan_resources()`, `zynqmp_dma_device_terminate_all()`, `zynqmp_dma_synchronize()`, `dma_cookie_status`, and `zynqmp_dma_device_config()` for burst lengths. PM hooks use runtime suspend/resume to gate `clk_main` and `clk_apb`.

## Control Flow

Probe sets a 44-bit DMA mask, declares `DMA_MEMCPY`, initializes DMAengine callbacks, gets clocks, enables runtime PM, probes the channel, registers with DMAengine, registers OF DMA translation, and drops the runtime PM reference for autosuspend. Channel probe maps registers, validates `xlnx,bus-width` as 64 or 128 bits, reads optional match data for the IRQ register offset, detects `dma-coherent`, initializes lists and cookies, initializes hardware registers, requests the IRQ, and records descriptor size.

Resource allocation resumes the device, allocates `ZYNQMP_DMA_NUM_DESCS` software descriptors, initializes their async descriptors and free list, and allocates a coherent pool sized for paired source/destination low-level descriptors. `zynqmp_dma_prep_memcpy()` checks descriptor availability, chunks transfers by `ZYNQMP_DMA_MAX_TRANS_LEN`, obtains descriptors from the free list, programs linked-list source/destination descriptors, chains children into the first descriptor's `tx_list`, marks the final descriptor as end-of-descriptor, and returns the first async descriptor.

Submit assigns a cookie and, if a pending transaction already exists, patches the previous tail descriptor's next pointers to the new descriptor while clearing STOP bits. Issue pending starts the transfer only if idle: it programs SG mode and burst attributes, splices all pending descriptors into active, writes source/destination descriptor start addresses, enables interrupts, clears the byte counter, and enables the channel. IRQ handling acknowledges status, schedules the tasklet for done/error interrupts, sets `idle` on DONE, and clears overflow accounting. The tasklet resets on errors or completes as many descriptors as the destination accounting register reports, invokes callbacks, frees descriptors, and starts the next pending transfer when idle.

## State and Persistence

State is volatile and stored in lists plus hardware registers. `pending_list`, `active_list`, `done_list`, and `free_list` are protected by `chan->lock`. `desc_free_cnt` reserves descriptor capacity during prep. Hardware descriptor memory is coherent and reused between transfers. Runtime PM state gates clocks across allocation/free and probe/remove. There is no persistent configuration beyond DT properties and DMA slave burst settings.

## Dependencies and Integration Points

The driver depends on DMAengine, OF DMA, platform resources, PM runtime, clock framework, coherent DMA allocation, tasklets, and 64-bit MMIO write helpers. DT properties include `xlnx,bus-width`, optional `dma-coherent`, and compatible data for the Versal Gen 2 IRQ offset (`amd,versal2-dma-1.0`). Consumers get the single channel through OF translation regardless of DMA spec contents.

## Risks and Edge Cases

Descriptor accounting is critical: `zynqmp_dma_prep_memcpy()` decrements `desc_free_cnt` before all descriptors are obtained, and error paths must not leak reservations. `zynqmp_dma_get_descriptor()` assumes the free list is non-empty after the prior count check. Chaining new submissions onto pending tails mutates hardware descriptor STOP bits, so list/tail selection must stay consistent with child descriptors. Error IRQ handling resets the channel and frees all descriptors, which can surprise clients if partial completion expectations are wrong. Runtime PM error handling in allocation and probe has potential leak points if allocation fails after `pm_runtime_resume_and_get()`.

## Test Signals

Useful validation includes DMAengine memcpy tests across sizes below, equal to, and above `ZYNQMP_DMA_MAX_TRANS_LEN`; concurrent submissions that extend an existing pending chain; invalid/missing `xlnx,bus-width`; coherent versus noncoherent DT operation; runtime suspend/resume cycles; forced AXI/APB/overflow interrupts; and remove/shutdown while idle or after active transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/zynqmp_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dpll/Kconfig

## Purpose

This Kconfig fragment declares the generic DPLL subsystem configuration menu. It defines the base `CONFIG_DPLL` symbol, the optional debug-oriented `CONFIG_DPLL_REFCNT_TRACKER`, and includes vendor-specific DPLL driver configuration from `drivers/dpll/zl3073x/Kconfig`.

## Important Symbols

`config DPLL` is a bool with no prompt in this file, intended to be selected by DPLL providers or users rather than directly exposed. `config DPLL_REFCNT_TRACKER` is user-visible, depends on `DEBUG_KERNEL`, `STACKTRACE_SUPPORT`, and `DPLL`, and selects `REF_TRACKER`. Its help text documents debugfs paths under `/sys/kernel/debug/ref_tracker/dpll_device_*` and `/sys/kernel/debug/ref_tracker/dpll_pin_*`.

## Control Flow and Integration

The file opens a `menu "DPLL device support"`, defines the generic symbols, sources the ZL3073x child Kconfig, and closes the menu. Build behavior is consumed by the DPLL Makefile: `CONFIG_DPLL` controls compilation of the generic DPLL core/netlink objects, while `CONFIG_DPLL_REFCNT_TRACKER` controls conditional ref tracker calls in `dpll_core.c`.

## State and Persistence

Kconfig selections persist in the kernel build configuration, not at runtime. Enabling the tracker changes runtime behavior by allocating/freeing ref-tracker records for DPLL devices and pins, but the Kconfig file itself has no runtime state.

## Risks and Test Signals

The base symbol being promptless means driver Kconfig files must select or depend on it correctly; otherwise DPLL providers can fail to link or omit the core. The tracker option depends on debug facilities and should be tested by building with and without `CONFIG_DPLL_REFCNT_TRACKER`, checking that DPLL core references to ref tracking compile away cleanly when disabled and expose debugfs leak data when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dpll/Makefile

## Purpose

This Makefile builds the generic DPLL subsystem objects and descends into the ZL3073x provider directory when enabled. It is the build glue connecting `CONFIG_DPLL` to the DPLL core, generated netlink family, and netlink operation implementation.

## Important Targets

`obj-$(CONFIG_DPLL) += dpll.o` builds the composite DPLL module/built-in object. `dpll-y` includes `dpll_core.o`, `dpll_netlink.o`, and `dpll_nl.o`; the last file is typically generated from the DPLL generic-netlink spec. `obj-$(CONFIG_ZL3073X) += zl3073x/` includes the vendor provider subtree independently of the core object's internal source list.

## Control Flow and Integration

When `CONFIG_DPLL=y`, kbuild links the three generic objects into `dpll.o`. `dpll_core.o` provides kernel registration and object lifetime APIs, `dpll_netlink.o` provides user-space netlink operations and notifications, and `dpll_nl.o` supplies generic-netlink family definitions. Provider drivers rely on the exported symbols from the composite object.

## State, Risks, and Test Signals

The Makefile has no runtime state. Build risks are mostly dependency-related: generated `dpll_nl.o` must be available in the kernel build, and provider configs should ensure the generic core is built before provider code references exported DPLL symbols. Test signals are successful `CONFIG_DPLL=y/m` builds, successful builds with `CONFIG_ZL3073X`, and modpost verification of exported DPLL symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_core.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/dpll_core.c

## Purpose

This file implements the kernel-space core of the DPLL subsystem. It manages DPLL device and pin object identity, reference counting, registration with user-visible state, pin-to-DPLL and pin-to-parent relationships, notifier fanout, optional reference tracking, netdevice pin association, and generic-netlink family initialization.

## Important APIs, Types, and Functions

Global state consists of `dpll_lock`, `dpll_device_xa`, `dpll_pin_xa`, a raw notifier chain, an IDA for dynamically assigned pin indexes, and cyclic xarray allocation cursors. Internal registration records (`dpll_device_registration` and `dpll_pin_registration`) attach provider ops and private data to devices and references. Public exported APIs include `dpll_device_get/put/register/unregister`, `dpll_pin_get/put/register/unregister`, `dpll_pin_on_pin_register/unregister`, `dpll_pin_ref_sync_pair_add`, `dpll_pin_fwnode_set`, `fwnode_dpll_pin_find`, netdevice pin set/clear helpers, and DPLL notifier registration.

The core lookup helpers `dpll_priv()`, `dpll_device_ops()`, `dpll_pin_on_dpll_priv()`, `dpll_pin_on_pin_priv()`, and `dpll_pin_ops()` are used heavily by `dpll_netlink.c` to route user-space operations to the provider callbacks associated with a given DPLL or pin reference.

## Control Flow

`dpll_device_get()` and `dpll_pin_get()` search global xarrays for an existing object matching `(clock_id, index, module)`, increment its tracked refcount if found, or allocate a new object with a unique subsystem ID. Device registration validates required ops (`mode_get`, `lock_status_get`) and type range, adds a registration record, marks the object as `DPLL_REGISTERED` only for the first registration, and emits create notification. Unregistration removes the matching registration, drops the held reference, sends delete notification, and clears the registered mark when no registrations remain.

Pin allocation duplicates provider properties, including labels and supported frequency arrays, initializes xarrays for DPLL refs, parent refs, and reference-sync pins, and allocates a global pin ID. `dpll_pin_register()` validates required pin ops, enforces matching module/clock identity with the DPLL, adds reciprocal references between the DPLL and pin, marks the pin registered, and emits a create notification. `dpll_pin_on_pin_register()` supports child pins under mux parent pins by adding a parent reference and registering the child against every DPLL connected to the parent. Unregister paths delete notifications, remove reciprocal references, clear registration marks when no DPLL refs remain, and drop reference counts.

Reference-sync pairs are kept in each pin's `ref_sync_pins` xarray. Adding a pair inserts the sync pin and emits a change notification; unregistering a pin scans all pins and removes references to the departing pin. Module initialization registers the DPLL generic-netlink family at `subsys_initcall` time; exit unregisters it and destroys the mutex.

## State and Persistence

All subsystem state is volatile kernel memory. Device and pin identities live in global xarrays and are guarded by `dpll_lock`. Object lifetime uses refcounts plus optional `ref_tracker` allocations when `CONFIG_DPLL_REFCNT_TRACKER` is enabled. Pins use RCU freeing (`kfree_rcu`) after final put, while devices are freed directly after xarray removal and registration-list checks. Registration marks in the xarrays distinguish allocated objects from user-visible registered objects. No state survives reboot or module unload.

## Dependencies and Integration Points

The file depends on Linux xarray, IDA, refcount, optional ref_tracker, notifier chains, firmware-node references, rtnetlink for assigning `dev->dpll_pin`, and the generated DPLL generic-netlink family. It integrates with public provider APIs in `include/linux/dpll.h` and with `dpll_netlink.c`, which assumes these helpers run under the DPLL core's object model. Provider drivers supply `dpll_device_ops`, `dpll_pin_ops`, private pointers, and stable clock/index identities.

## Risks and Edge Cases

The code relies on strict lock discipline: most object graph mutations require `dpll_lock`, while netdevice assignment uses RTNL. Registration records can stack multiple providers/owners on one object, but helper functions return the first registration, so multi-registration semantics must stay intentional. `dpll_pin_on_pin_unregister()` iterates `pin->dpll_refs` while unregistering entries, a pattern that should be reviewed carefully for xarray iteration safety. Unregistering a directly registered pin warns if it still has parent refs, preventing removal while child topology remains. Dynamic pin indexes are mapped above `INT_MAX`, and explicit provider indexes above `INT_MAX` are rejected; tests should cover both paths.

## Test Signals

Useful tests include provider get/register/unregister/put sequences, duplicate registration returning `-EEXIST`, invalid ops/type/property validation, dynamic pin index allocation and free, pin-on-DPLL and pin-on-pin topologies, reference-sync add and cleanup on pin unregister, fwnode lookup with refcounting, notifier delivery for create/delete/change, ref-tracker leak reports when enabled, and generic-netlink registration/unregistration during module init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_core.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/dpll_core.h

## Purpose

This private header defines the internal DPLL core object model shared by `dpll_core.c` and the DPLL netlink implementation. It exposes internal structs for devices, pins, and references, declares global xarrays and the global mutex, and provides helper prototypes used to retrieve provider ops/private data and send notifications.

## Important Types and APIs

`struct dpll_device` stores the subsystem ID, provider index, clock ID, owning module, DPLL type, pin reference xarray, refcount/ref-tracker state, and registration list. `struct dpll_pin` stores subsystem and provider indexes, clock ID, module, optional firmware node, xarrays for DPLL refs, parent refs, and reference-sync pins, copied pin properties, refcount/ref-tracker state, and an RCU head. `struct dpll_pin_ref` is a tagged reference to either a DPLL or parent pin with a registration list and refcount.

The header defines `DPLL_REGISTERED` as `XA_MARK_1`, the mark used in global xarrays to distinguish registered objects from merely allocated objects. It declares helper functions such as `dpll_priv()`, `dpll_pin_on_dpll_priv()`, `dpll_pin_on_pin_priv()`, `dpll_device_ops()`, `dpll_device_get_by_id()`, `dpll_pin_ops()`, `dpll_xa_ref_dpll_first()`, `dpll_device_notify()`, and `dpll_pin_notify()`.

## Control Flow and Integration

Netlink code includes this header to traverse registered DPLL objects, resolve references, and call provider callbacks with the right private pointers. Core code owns the backing storage and enforces locking; users of this header are expected to respect `dpll_lock` when walking or mutating xarrays and registration lists. The public API surface remains in `include/linux/dpll.h`; this header intentionally exposes implementation details only within the DPLL subsystem.

## State and Persistence

The structs describe in-memory kernel state only. Refcounts and ref-tracker directories are per object. Xarrays store relationship state: devices to pins, pins to DPLLs, pins to parent pins, and pins to reference-sync peers. Firmware-node handles are retained by the core and released during final pin teardown.

## Risks and Test Signals

Because this header exposes concrete struct layouts to internal users, changes require coordinated updates in `dpll_core.c` and `dpll_netlink.c`. Risks include accessing registration lists without holding `dpll_lock`, assuming a `dpll_pin_ref` union member without knowing which xarray supplied it, and using helpers after an object's registered mark was cleared. Compile tests for `CONFIG_DPLL` plus functional netlink/provider tests are the primary signals that the internal contract remains valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_core.h -->
