# Research: subset-b-001255

Grouped research for DMA drivers under `sources/distributed-fs/ceph-client/drivers/dma`. Each section preserves the exact source path expected by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsldma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/fsldma.c

## Purpose

`fsldma.c` is the dmaengine driver for Freescale/NXP Elo, EloPlus, and Elo3 DMA controllers found on MPC83xx/MPC85xx-family platforms. It exposes memory-copy and limited slave-DMA services through `struct dma_device`, discovers channels from OpenFirmware child nodes, and supports both per-controller and per-channel interrupts.

## Important APIs, Types, And Functions

The driver centers on `struct fsldma_device`, `struct fsldma_chan`, and `struct fsl_desc_sw` from `fsldma.h`. Register helpers (`set_sr`, `get_mr`, `set_cdar`, `set_bcr`) hide endian-aware MMIO. Descriptor helpers build 32-byte aligned link descriptors and insert 83xx/85xx-specific snoop and next-link bits. Public integration includes `fsl_dma_external_start()` and the dmaengine callbacks `fsl_dma_prep_memcpy`, `fsl_dma_tx_submit`, `fsl_dma_memcpy_issue_pending`, `fsl_tx_status`, `fsl_dma_device_config`, and `fsl_dma_device_terminate_all`.

## Control Flow

`fsldma_of_probe()` allocates the controller, maps global registers, reads the DMA address width from OF match data, initializes dmaengine capabilities, probes compatible child channels, requests interrupts, and registers the dmaengine device. Clients allocate a channel descriptor pool, prepare memcpy transactions as chained link descriptors, submit them to `ld_pending`, and start them from `issue_pending`. IRQs clear status, log transfer/programming errors, then schedule a tasklet. The tasklet marks the channel idle, completes running descriptors up to the hardware current descriptor, invokes callbacks, frees acked descriptors, and starts the next pending chain.

## State And Persistence Behavior

Runtime state is entirely in MMIO registers, DMA pools, linked descriptor queues, cookies, and tasklet state. The driver keeps separate pending, running, and completed descriptor lists under `desc_lock`. PM suspend only succeeds for idle channels, saves `MR`, marks channels suspended, and resume restores safe mode bits while clearing start/abort/control bits.

## Dependencies And Integration Points

Dependencies include dmaengine, async_tx, OF address/IRQ parsing, platform driver registration, DMA pools, and the endian helpers in `fsldma.h`. OF compatibles distinguish controller address width and child-channel IP/endian features. `linux/fsldma.h` consumers may toggle external start behavior.

## Risks And Edge Cases

Channel IDs are derived from resource offsets and must match hardware layout. Halt waits only about 1 ms before warning. 83xx and 85xx share bit positions with different meanings, so feature masks are safety-critical. `device_config` assumes burst byte count is a power-of-two-friendly request count and can hit `BUG_ON(size > 1024)`. Suspend fails if any channel is active.

## Test Signals

Useful signals are successful OF probe logs per channel, dmaengine registration, `dmatest` memcpy over lengths above `FSL_DMA_BCR_MAX_CNT`, interrupt completion without stuck running descriptors, terminate-all freeing all queues, external-start users resuming correctly, and suspend/resume while idle plus rejection while active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsldma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsldma.h -->
# sources/distributed-fs/ceph-client/drivers/dma/fsldma.h

## Purpose

`fsldma.h` defines the private register layout, descriptor format, state structures, feature bits, and endian conversion helpers used by the Freescale Elo DMA driver.

## Important APIs, Types, And Functions

Important definitions include `struct fsl_dma_ld_hw` for hardware link descriptors, `struct fsl_desc_sw` for software descriptors plus `dma_async_tx_descriptor`, `struct fsldma_chan_regs` for per-channel MMIO, `struct fsldma_device`, and `struct fsldma_chan`. Feature bits encode controller family (`FSL_DMA_IP_85XX`, `FSL_DMA_IP_83XX`), endian mode, and external pause/start state. Inline 64-bit accessors provide PPC 32-bit split reads/writes, while `FSL_DMA_IN`, `FSL_DMA_OUT`, `DMA_TO_CPU`, and `CPU_TO_DMA` centralize endian handling.

## Control Flow

The header has no independent runtime flow. It supplies the constants and access helpers called by `fsldma.c` during descriptor preparation, channel probing, interrupt handling, and power management.

## State And Persistence Behavior

Structures model volatile driver state only. Hardware state is represented by MMIO register definitions and descriptor fields. Under `CONFIG_PM`, `fsldma_chan_regs_save` stores the mode register and `fsldma_pm_state` gates submissions during suspend.

## Dependencies And Integration Points

It depends on Linux device, DMA pool, dmaengine, list, spinlock, tasklet, PPC I/O, ARM/ARM64 I/O, and endian conversion APIs. The hardware descriptor alignment and `FSL_DMA_BCR_MAX_CNT` constrain how the C file builds transfer chains.

## Risks And Edge Cases

Endian abstraction is critical because the same driver supports big-endian 85xx and little-endian 83xx. Incorrect descriptor alignment or next-link masking can break DMA fetching. `FSL_DMA_SNEN`, `FSL_DMA_EOL`, and snoop bits overlap descriptor addresses, so callers must preserve alignment.

## Test Signals

Compile coverage on PPC and ARM/ARM64 configurations, sparse/endian checking of `__bitwise` descriptor fields, successful descriptor DMA on both endian modes, and PM builds with `CONFIG_PM` enabled are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsldma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hisi_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/hisi_dma.c

## Purpose

`hisi_dma.c` is the PCI dmaengine driver for HiSilicon Kunpeng HIP08/HIP09 DMA endpoints. It exposes memory-to-memory copy channels, each backed by a hardware queue pair with a submission queue, completion queue, MSI vector, and revision-specific register layout.

## Important APIs, Types, And Functions

Core types are `hisi_dma_dev`, `hisi_dma_chan`, `hisi_dma_desc`, `hisi_dma_sqe`, and `hisi_dma_cqe`. Revision helpers choose queue base, MSI count, channel count, and register layout from PCI revision. `hisi_dma_init_dma_dev()` wires dmaengine operations. `hisi_dma_prep_dma_memcpy()` creates a virtual-DMA descriptor, `hisi_dma_start_transfer()` copies it into the SQ and advances the tail pointer, and `hisi_dma_irq()` advances the CQ head and completes the descriptor.

## Control Flow

Probe enables the PCI function, maps BAR 2, sets a 64-bit DMA mask, allocates the flexible `hisi_dma_dev`, allocates MSI vectors, initializes dmaengine state, sets HIP08 RC mode where needed, performs HIP09 port setup, allocates coherent SQ/CQ rings for each channel, requests one IRQ per channel, enables all queue pairs, registers cleanup with devm, registers the dmaengine device, and creates debugfs files. Channel issue-pending starts one outstanding descriptor per queue; completion interrupts launch the next queued descriptor.

## State And Persistence Behavior

SQ/CQ rings are coherent DMA memory. Per-channel state tracks tail/head indices, current descriptor, queue number, and status. Hardware state is reset by pausing, disabling, masking IRQs, polling FSM state out of `RUN`, asserting queue reset, zeroing queue pointers, and optionally re-enabling/unmasking.

## Dependencies And Integration Points

It depends on PCI/MSI, `virt-dma`, dmaengine MEMCPY, coherent DMA memory, relaxed MMIO, bitfield helpers, polling helpers, and optional debugfs register dumps. It integrates with Huawei PCI ID `0xa122` and separates HIP08/HIP09 behavior by revision.

## Risks And Edge Cases

Unsupported revisions are rejected. HIP08 and HIP09 register layouts differ substantially, so wrong revision detection corrupts setup. IRQ handling logs errors but does not complete failed descriptors with an error callback. The driver queues only one active descriptor per channel despite deep hardware rings. Reset polling timeouts warn and continue.

## Test Signals

Signals include PCI probe on HIP08B and HIP09A+, correct MSI count allocation, successful `dmatest` MEMCPY, CQ head/tail movement, debugfs register readability, queue reset without timeout warnings, and unload paths disabling all queue pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hisi_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/hsu/Kconfig

## Purpose

This Kconfig fragment declares the Intel High Speed UART DMA core and PCI glue symbols.

## Important APIs, Types, And Functions

`CONFIG_HSU_DMA` is a tristate core symbol that selects `DMA_ENGINE` and `DMA_VIRTUAL_CHANNELS`. `CONFIG_HSU_DMA_PCI` is a tristate bus glue symbol depending on `HSU_DMA && PCI`.

## Control Flow

There is no runtime control flow. Kconfig dependency resolution decides whether `hsu.o` and `pci.o` are eligible to build.

## State And Persistence Behavior

The only persistent effect is kernel configuration state. Enabling the PCI symbol requires the core symbol, which ensures exported core helpers exist for the PCI module.

## Dependencies And Integration Points

It integrates with the surrounding DMA Kconfig tree and the Makefile in the same directory. The core selects virtual DMA channels because `hsu.c` uses `virt-dma`.

## Risks And Edge Cases

The core symbol has no prompt here, so it is intended to be selected by another platform option or dependency path. Misconfigured builds can include the core without bus glue or omit PCI probing entirely.

## Test Signals

Build matrix checks should verify `HSU_DMA=m/y`, `HSU_DMA_PCI=m/y`, and disabled PCI cases, confirming symbol dependencies produce `hsu_dma.o` and `hsu_dma_pci.o` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/hsu/Makefile

## Purpose

The Makefile maps HSU DMA configuration symbols to build artifacts.

## Important APIs, Types, And Functions

`obj-$(CONFIG_HSU_DMA) += hsu_dma.o` builds the core from `hsu.o`. `obj-$(CONFIG_HSU_DMA_PCI) += hsu_dma_pci.o` builds the PCI wrapper from `pci.o`.

## Control Flow

There is no runtime flow. Kbuild composes the objects based on Kconfig results.

## State And Persistence Behavior

The Makefile produces either built-in or module objects depending on tristate values. It does not generate runtime state.

## Dependencies And Integration Points

It depends on the Kconfig symbols in `hsu/Kconfig` and Kbuild object aggregation. The split lets non-PCI integration reuse the HSU core exports.

## Risks And Edge Cases

If future bus glue is added, it should depend on the exported core API and avoid folding bus-specific code into `hsu_dma.o`. Object names must continue to match module aliases and exported symbols.

## Test Signals

Useful checks are `make drivers/dma/hsu/` under module and built-in configurations and verifying `modinfo hsu_dma_pci` reports the PCI driver metadata from `pci.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/hsu.c -->
# sources/distributed-fs/ceph-client/drivers/dma/hsu/hsu.c

## Purpose

`hsu.c` is the core dmaengine implementation for Intel High Speed UART DMA. It serves UART-oriented slave scatter-gather transfers using small per-channel hardware descriptor slots and `virt-dma` software queuing.

## Important APIs, Types, And Functions

Key operations include `hsu_dma_probe()` and `hsu_dma_remove()` for bus glue, exported IRQ helpers `hsu_dma_get_status()` and `hsu_dma_do_irq()`, and dmaengine callbacks `hsu_dma_prep_slave_sg`, `hsu_dma_issue_pending`, `hsu_dma_tx_status`, `hsu_dma_slave_config`, pause/resume, terminate, and synchronize. `hsu_dma_chan_start()` programs up to four hardware descriptors, burst/min-transfer registers, descriptor interrupts, and timeout workaround bits.

## Control Flow

Probe calculates channel count from MMIO length and offset, creates one `virt_dma_chan` per 0x40-byte channel, assigns even channels to TX (`DMA_MEM_TO_DEV`) and odd channels to RX (`DMA_DEV_TO_MEM`), then registers a private slave dmaengine device. Clients prepare SG descriptors, issue pending work, and the core starts the first queued descriptor. IRQ glue first calls `hsu_dma_get_status()` to read-clear channel status and identify timeout-only events, then calls `hsu_dma_do_irq()` for channel errors or descriptor completion. Completion either starts the next hardware batch for the same SG list, completes the cookie, or starts the next queued virtual descriptor.

## State And Persistence Behavior

State lives in `struct hsu_dma_desc` (`sg`, `nents`, `length`, `active`, `status`) and `struct hsu_dma_chan` (`config`, fixed direction, active descriptor). MMIO channel state is reset by clearing channel control and descriptor control. No disk persistence exists.

## Dependencies And Integration Points

It depends on dmaengine slave SG support, `virt-dma`, scatterlists, per-channel MMIO from `hsu.h`, and exported `linux/dma/hsu.h` glue structures. PCI glue in `pci.c` supplies the chip descriptor and interrupt dispatch.

## Risks And Edge Cases

Only four descriptors can be programmed at a time; residue and active accounting must stay consistent across batches. Status read has hardware errata semantics and must be read-cleared even for timeout cases. Pause simply disables the channel and resume re-enables it, so clients must tolerate device-side FIFO state. Segment length is capped by `HSU_CH_DxTSR_MASK`.

## Test Signals

Test with UART TX/RX DMA under load, SG lists longer than four entries, timeout interrupt paths, pause/resume, terminate-all, residue reporting, and shared interrupt configurations used by Intel mobile SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/hsu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/hsu.h -->
# sources/distributed-fs/ceph-client/drivers/dma/hsu/hsu.h

## Purpose

`hsu.h` is the private header for the High Speed UART DMA core. It defines channel registers, descriptor/control/status bits, private descriptor/channel/controller structures, and MMIO access helpers.

## Important APIs, Types, And Functions

Important constants include `HSU_CH_SR`, `HSU_CH_CR`, `HSU_CH_DCR`, buffer/min-transfer registers, four descriptor address/size slots, `HSU_DMA_CHAN_NR_DESC`, and `HSU_DMA_CHAN_LENGTH`. Types include `hsu_dma_sg`, `hsu_dma_desc`, `hsu_dma_chan`, and `hsu_dma`. Inline helpers convert from dmaengine/virt-dma containers and read/write per-channel registers.

## Control Flow

The header has no independent flow. `hsu.c` uses it when programming descriptors, reading status, computing residue, and registering channels.

## State And Persistence Behavior

It models volatile driver state: an active virtual descriptor, per-channel direction/configuration, and controller channel array. Hardware status bits describe descriptor timeout, descriptor done, current descriptor, and channel error events.

## Dependencies And Integration Points

It includes `linux/dma/hsu.h` for the public chip descriptor, `virt-dma`, Linux I/O helpers, and bit macros. Bus glue must fill `struct hsu_dma_chip` from the public header and call the exported core functions.

## Risks And Edge Cases

Register bit definitions encode HSU errata-sensitive behavior used by `hsu.c`. The four-slot descriptor limit and 16-bit transfer-size mask require callers to segment transfers correctly. Direction is fixed per channel by convention rather than negotiated dynamically.

## Test Signals

Build coverage with `CONFIG_HSU_DMA`, sparse/container checks, and runtime validation that programmed descriptor registers match the SG list are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/hsu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/pci.c -->
# sources/distributed-fs/ceph-client/drivers/dma/hsu/pci.c

## Purpose

`pci.c` is PCI glue for the Intel HSU DMA core. It maps the PCI BAR, allocates the interrupt vector, initializes `struct hsu_dma_chip`, calls the core probe, and dispatches interrupts to core helpers.

## Important APIs, Types, And Functions

Key functions are `hsu_pci_probe()`, `hsu_pci_irq()`, and the devm cleanup wrapper `hsu_pci_dma_remove()`. It recognizes Intel Medfield and Merrifield/Tangier device IDs, uses `HSU_PCI_CHAN_OFFSET` to locate channel windows, and reads `HSU_PCI_DMAISR` to find interrupting channels.

## Control Flow

Probe enables the PCI device, maps BAR 0, sets bus mastering and MWI, configures a 32-bit coherent DMA mask, allocates one IRQ vector, fills chip fields, calls `hsu_dma_probe()`, registers devm cleanup, requests the IRQ, and disables the IRQ for Merrifield-style shared UART handling. The IRQ handler iterates set bits in DMAISR, read-clears per-channel status through `hsu_dma_get_status()`, and delegates non-timeout events to `hsu_dma_do_irq()`.

## State And Persistence Behavior

State is the devm-managed chip object, mapped BAR, PCI IRQ vector, and core `chip->hsu` pointer. There is no suspend/resume logic in this file.

## Dependencies And Integration Points

It depends on PCI managed enable/iomap, DMA mask setup, IRQ vectors, `hsu.h`, and the core exports. It integrates with UART interrupt sharing on Tangier/Anniedale by disabling its own IRQ path.

## Risks And Edge Cases

On MRFLD devices the IRQ is deliberately disabled, so UART-side code must service DMA status. A wrong BAR length or offset changes detected channel count in the core. The IRQ handler treats timeout-only status as handled without calling completion.

## Test Signals

Validate probe on both PCI IDs, BAR mapping, one IRQ vector allocation, core channel count, normal IRQ completion on MFLD, disabled IRQ behavior on MRFLD, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/hsu/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idma64.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idma64.c

## Purpose

`idma64.c` is the platform driver and dmaengine core for Intel integrated DMA 64-bit controllers, typically LPSS-attached. It provides private slave SG channels for peripheral DMA using linked-list hardware descriptors.

## Important APIs, Types, And Functions

The driver uses `struct idma64`, `idma64_chan`, `idma64_desc`, `idma64_hw_desc`, and `idma64_chip` from `idma64.h`. Hardware lifecycle helpers include `idma64_off`, `idma64_on`, `idma64_chan_init`, `idma64_chan_start`, and `idma64_chan_irq`. Dmaengine operations include `idma64_prep_slave_sg`, `idma64_issue_pending`, `idma64_tx_status`, `idma64_slave_config`, pause/resume, terminate, synchronize, and resource allocation.

## Control Flow

Platform probe gets IRQ and MMIO, coerces the parent device to 64-bit DMA, and calls `idma64_probe()`. The core powers the controller off, requests the shared IRQ, creates two virt-dma channels, and registers a private slave dmaengine device. Preparing SG allocates one coherent hardware LLI per SG element from a DMA pool, fills descriptors in reverse so LLP pointers chain forward, and enables interrupt on the last block. Submit and issue-pending move a virtual descriptor to active state, initialize channel registers, point LLP at the first LLI, and enable the channel. IRQ completion clears error/xfer status, updates bytes transferred, completes the cookie, starts the next descriptor, or stops on error.

## State And Persistence Behavior

State lives in virt-dma queues, the active descriptor pointer, DMA pool LLIs, copied slave config, and controller enable/interrupt masks. Suspend powers the controller off; resume powers it on. Channel initialization re-enables the controller because suspend loses context.

## Dependencies And Integration Points

It depends on platform devices named `LPSS_IDMA64_DRIVER_NAME`, dmaengine slave SG, `virt-dma`, DMA pools, 64-bit lo-hi MMIO helpers, and parent-device DMA masks. Peripheral drivers consume channels through dmaengine.

## Risks And Edge Cases

Only two channels are supported. Burst configuration converts maxburst to log2 form in-place. Residue calculation depends on LLP and CTL_HI matching current hardware progress. Terminate drains FIFO with a bounded wait. Shared IRQs can arrive while the controller is powered off and are filtered by all-ones status.

## Test Signals

Signals include LPSS platform probe, `dmaengine` slave transfers in both directions, SG chains with multiple entries, residue during active transfers, pause/resume, terminate-all, system suspend/resume, and no stale tasklets on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idma64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idma64.h -->
# sources/distributed-fs/ceph-client/drivers/dma/idma64.h

## Purpose

`idma64.h` defines the private register map, bitfields, linked-list descriptor structures, channel/controller objects, and MMIO helpers for Intel integrated DMA 64-bit.

## Important APIs, Types, And Functions

Important definitions include channel offsets (`SAR`, `DAR`, `LLP`, `CTL`, `CFG`), interrupt register macros (`RAW`, `STATUS`, `MASK`, `CLEAR`), common registers (`CFG`, `CH_EN`), `struct idma64_lli`, `struct idma64_hw_desc`, `struct idma64_desc`, `struct idma64_chan`, `struct idma64`, and `struct idma64_chip`. Inline helpers wrap per-channel and global 32/64-bit MMIO and container conversions.

## Control Flow

No standalone flow exists. `idma64.c` uses the definitions to allocate LLIs, program CFG/CTL/LLP registers, mask or clear interrupts, and expose the platform chip representation.

## State And Persistence Behavior

The header models transient kernel and hardware state. LLIs are DMA-visible and hold source, destination, LLP, control, and status words. `idma64_chip` bridges platform resources to the core.

## Dependencies And Integration Points

It depends on Linux I/O, spinlock/types, non-atomic lo-hi 64-bit accessors, and `virt-dma`. `linux/dma/idma64.h` supplies public platform naming such as `LPSS_IDMA64_DRIVER_NAME`.

## Risks And Edge Cases

The hardware uses bit-encoded transfer widths and burst sizes, so callers must pass values already converted to expected encodings. LLP chain control bits must be disabled on the final descriptor. Non-atomic 64-bit MMIO ordering must match hardware expectations.

## Test Signals

Compile coverage, sparse checks for MMIO helper use, successful chained SG DMA, and residue values matching descriptor progress validate this header’s contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idma64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/Makefile

## Purpose

The IDXD Makefile composes the Intel DSA/IAA bus module, main accelerator driver, optional perfmon object, and compatibility driver.

## Important APIs, Types, And Functions

It sets `DEFAULT_SYMBOL_NAMESPACE` to `IDXD`, builds `idxd_bus.o` from `bus.o`, builds `idxd.o` from `init.o irq.o device.o sysfs.o submit.o dma.o cdev.o debugfs.o defaults.o`, conditionally adds `perfmon.o`, and builds `idxd_compat.o` from `compat.o`.

## Control Flow

There is no runtime flow. Kbuild controls which modules are compiled from `CONFIG_INTEL_IDXD_BUS`, `CONFIG_INTEL_IDXD`, `CONFIG_INTEL_IDXD_PERFMON`, and `CONFIG_INTEL_IDXD_COMPAT`.

## State And Persistence Behavior

The build namespace affects symbol export/import behavior for IDXD internals. Object aggregation decides module boundaries and initialization order at load time.

## Dependencies And Integration Points

The main module depends on the bus module type and shares namespaced symbols with dmaengine/user/compat subdrivers. Perfmon is optional and folded into the main module when enabled.

## Risks And Edge Cases

Adding a new source file without updating `idxd-y` can silently omit functionality. Namespace changes must stay aligned with `EXPORT_SYMBOL_NS_GPL` and `MODULE_IMPORT_NS`.

## Test Signals

Build tests should cover bus-only, main IDXD, perfmon-enabled, and compat-enabled configurations, plus `modpost` namespace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/bus.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/bus.c

## Purpose

`bus.c` defines and registers the internal `dsa` bus used by IDXD devices, work queues, engines, groups, cdevs, and subdrivers.

## Important APIs, Types, And Functions

It exports `__idxd_driver_register()`, `idxd_driver_unregister()`, and `dsa_bus_type`. Match logic compares an `idxd_dev` type against the driver’s accepted type array. Probe/remove convert `struct device_driver` back to `struct idxd_device_driver` and call type-specific callbacks.

## Control Flow

Module init registers `dsa_bus_type`. IDXD subdrivers call `idxd_driver_register()`, which fills driver name, bus, owner, and module name before registering. During device binding, `idxd_config_bus_match()` checks type compatibility, then `idxd_config_bus_probe()` invokes the subdriver’s probe. Removal calls the subdriver’s remove.

## State And Persistence Behavior

The persistent runtime state is the global registered bus type and registered device drivers. Devices on the bus carry their type in embedded `struct idxd_dev`.

## Dependencies And Integration Points

It depends on the Linux driver core and `idxd.h` container helpers. `init.c`, `device.c`, `dma.c`, `cdev.c`, and `compat.c` all register or create objects on this bus.

## Risks And Edge Cases

Drivers with a missing type array are rejected. The uevent currently emits a modalias with type `0`, not the actual device type, so automatic module matching relies on broader behavior. Type arrays must end with `IDXD_DEV_NONE`.

## Test Signals

Signals include `/sys/bus/dsa` existence, subdriver registration, successful binding of IDXD devices and WQs to `idxd`, `dmaengine`, or `user`, and clean bus unregister at module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/cdev.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/cdev.c

## Purpose

`cdev.c` implements the IDXD user work-queue character device path. It exposes user-submission portals, binds user address spaces with SVA/PASID, tracks per-open contexts, handles user descriptor submission, and reports completion-record fault counters.

## Important APIs, Types, And Functions

Core types are `idxd_cdev_context` and `idxd_user_context`. File operations are `idxd_cdev_open`, `release`, `mmap`, `write`, and `poll`. WQ device integration uses `idxd_user_drv_probe/remove`, `idxd_wq_add_cdev`, and `idxd_wq_del_cdev`. `idxd_copy_cr()` lets event-log fault work copy completion records back into a user mm.

## Control Flow

The user subdriver only probes WQs whose driver name matches and whose device has user PASID/SVA enabled. It creates a cdev and a per-WQ workqueue. Open rejects busy dedicated WQs, binds the current mm with `iommu_sva_bind_device()`, records the PASID in `wq->upasid_xa`, optionally writes the PASID into a dedicated WQ, creates a `fileN` device, and increments the WQ client count. `mmap` maps the limited portal page after security checks. `write` copies one or more user descriptors, validates unsafe batch use and completion alignment, then submits via `iosubmit_cmds512` for dedicated WQs or ENQCMDS for shared WQs.

## State And Persistence Behavior

State includes global major/minor IDAs, per-open PASID/mm/task/file device, per-context counters, WQ xarray entries, and the cdev object. Release unregisters the file device; final device release drains PASID or WQ work, unbinds SVA, removes xarray state, frees the context, and decrements WQ clients.

## Dependencies And Integration Points

It depends on char devices, sysfs device attributes, IOMMU SVA, xarray, user copy, polling, capability checks, IDXD event log handling, and portal submission helpers.

## Risks And Edge Cases

User submission is security-sensitive. Unsafe devices require `CAP_SYS_RAWIO` for mmap, DSA v1 batch descriptors can be rejected, completion records must be aligned, and operations are tied to the opening mm. Dedicated WQs allow only one opener. Completion-record fault copying temporarily adopts the user mm in kernel-thread context.

## Test Signals

Signals include cdev node creation, open/mmap/write from a valid SVA process, rejection without SVA, CAP_SYS_RAWIO enforcement on unsafe devices, PASID xarray cleanup on close, poll wakeups on software errors, and CR fault counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/cdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/compat.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/compat.c

## Purpose

`compat.c` provides a legacy-compatible `dsa` driver facade with custom bind/unbind attributes that redirect devices to the real IDXD, dmaengine, or user subdrivers.

## Important APIs, Types, And Functions

Important pieces are `bind_store`, `unbind_store`, the `DRIVER_ATTR_IGNORE_LOCKDEP` attributes, `dsa_drv_compat_groups`, and exported `struct idxd_device_driver dsa_drv`.

## Control Flow

The compat driver itself matches no device types. Users write a dsa-bus device name to `bind`; the code finds the device, rejects already-bound devices or writes to non-compat drivers, chooses an alternate driver based on device type and WQ type, and attaches that driver. `unbind` finds a device by name and detaches its current driver.

## State And Persistence Behavior

Runtime state is driver-core binding state. The compat module adds writable driver attributes while suppressing default bind attrs.

## Dependencies And Integration Points

It depends on the IDXD bus, driver core attach/detach helpers, and device type helpers from `idxd.h`. It imports the `IDXD` namespace.

## Risks And Edge Cases

The code references `device_driver_detach()` as extern, reflecting compatibility pressure with driver-core internals. Bind dispatch depends on WQ type already being set correctly. Failed `driver_find()` or attach returns are passed back to sysfs users.

## Test Signals

Test by writing IDXD device and WQ names to `/sys/bus/dsa/drivers/dsa/bind`, verifying the actual target driver binds, and using unbind to detach without lockdep warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/debugfs.c

## Purpose

`debugfs.c` adds IDXD debugfs support, primarily an event-log dump for devices that allocate an EVL.

## Important APIs, Types, And Functions

Key functions are `idxd_init_debugfs()`, `idxd_remove_debugfs()`, `idxd_device_init_debugfs()`, `idxd_device_remove_debugfs()`, `debugfs_evl_show()`, and `dump_event_entry()`. The file uses `DEFINE_SHOW_ATTRIBUTE(debugfs_evl)`.

## Control Flow

Global init creates `/sys/kernel/debug/idxd` when debugfs is initialized. Per-device init creates a directory named after the config device and, if `idxd->evl` exists, creates an `event_log` file. Reading that file locks the event log, reads hardware head/tail status, walks entries in ring order, and prints decoded fields plus raw u64 words for valid entries.

## State And Persistence Behavior

Debugfs dentries are stored in `idxd->dbgfs_dir` and `idxd->dbgfs_evl_file`. EVL state is not owned here; it is read under `evl->lock` from coherent memory and hardware status registers.

## Dependencies And Integration Points

It depends on debugfs, seq_file, PCI/MMIO helpers, IDXD register definitions, and event-log layout from the uapi headers. `init.c` calls global setup/removal and per-device setup; `device.c` owns EVL allocation.

## Risks And Edge Cases

The file tolerates missing debugfs and missing EVL. Pointer arithmetic assumes the event-log allocation and entry size match hardware capability. Output is diagnostic only and should not be used as synchronization for recovery.

## Test Signals

Signals include debugfs directory creation, `event_log` presence only for EVL-capable devices, successful reads under load, decoded head/tail values matching hardware, and clean recursive removal on device/module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/defaults.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/defaults.c

## Purpose

`defaults.c` provides default configuration for configurable Intel IAA/IAX devices so they can expose a kernel crypto work queue without manual sysfs setup.

## Important APIs, Types, And Functions

The single exported routine is `idxd_load_iaa_device_defaults(struct idxd_device *idxd)`. It updates WQ 0, group 0, and engine 0 defaults.

## Control Flow

If the device is not configurable, the function exits successfully. Otherwise it requires WQ 0 to be disabled, marks it dedicated, assigns the full WQ size, sets priority 10, sets type kernel, attaches it to group 0, names it `iaa_crypto`, sets `driver_name` to `crypto`, and assigns engine 0 to group 0.

## State And Persistence Behavior

It mutates in-memory configuration shadow state only. The actual hardware configuration is later written by `idxd_device_config()` during binding/enabling.

## Dependencies And Integration Points

It is referenced in the IAX entry of `idxd_driver_data` in `init.c`. The crypto driver can then bind by matching `driver_name`.

## Risks And Edge Cases

Only WQ 0 and engine 0 are configured. If WQ 0 is already enabled, it returns `-EPERM`. The defaults assume a valid group 0 and engine 0 exist.

## Test Signals

Probe an IAA device and verify sysfs shows WQ 0 as dedicated kernel `iaa_crypto`, group/engine counts incremented, and crypto binding can enable the WQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/defaults.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/device.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/device.c

## Purpose

`device.c` is the IDXD control-plane implementation. It manages device commands, WQ enable/disable, descriptor resources, portal mapping, PASID programming, group/WQ/engine configuration writes, event-log setup, interrupt handle management, and binding support for the internal `idxd` driver.

## Important APIs, Types, And Functions

Important exported functions include `idxd_wq_alloc_resources`, `idxd_wq_free_resources`, `idxd_wq_enable`, `idxd_wq_disable`, `idxd_wq_drain`, `idxd_wq_reset`, `idxd_wq_map_portal`, `idxd_wq_set_pasid`, `idxd_wq_quiesce`, `idxd_device_init_reset`, `idxd_device_enable`, `idxd_device_disable`, `idxd_device_config`, `idxd_wq_request_irq`, `idxd_drv_enable_wq`, `idxd_drv_disable_wq`, and `idxd_device_drv_probe/remove`. `idxd_cmd_exec()` serializes hardware commands through `cmd_lock`, `cmd_waitq`, and an interrupt-driven completion.

## Control Flow

The device driver probe requires the accelerator to be disabled, writes configuration, re-enables user interrupts for saved PASID, sets up EVL, enables the device, and registers an empty dmaengine device. WQ subdrivers call `idxd_drv_enable_wq()`, which validates state, group, name, shared-WQ support, PASID setup, writes config tables, enables the WQ, maps the portal, requests IRQ/int handles, allocates kernel descriptor/completion resources, and initializes a percpu ref. Disable reverses this with portal unmap, drain, IRQ free, WQ reset, resource free, and percpu-ref exit.

## State And Persistence Behavior

State includes WQ shadow config, group config, engine membership, `wq_enable_map`, coherent completion records, software descriptors, sbitmap descriptor IDs, EVL memory/bitmap, IRQ permission entries, int handles, PASID fields, device state, and command status. No disk persistence exists, but state may be saved/restored around FLR by `init.c`.

## Dependencies And Integration Points

It depends on IDXD registers/uapi, PCI IRQ vectors, dmaengine descriptor completion, IOMMU PASID semantics, devm portal mapping, per-cpu refs, debug/perf/event-log consumers, and subdrivers in `dma.c` and `cdev.c`.

## Risks And Edge Cases

Command execution depends on misc interrupt completion. WQ disable must drain translations before config changes. Shared WQs require ENQCMD and PASID support. Dedicated kernel WQ PASID privilege is rejected if PCI PASID lacks privileged mode. Freeing IRQs flushes pending descriptors to avoid callbacks into unloaded code. EVL free must disable hardware before freeing coherent memory.

## Test Signals

Signals include sysfs-driven device and WQ enable/disable, command status reporting, portal mapping, MSI-X WQ interrupt setup, dmaengine and user WQ binding, PASID enable/disable, EVL allocation/debugfs dump, WQ drain/reset, and error paths that unwind resources without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/dma.c

## Purpose

`dma.c` exposes IDXD work queues as Linux dmaengine channels for kernel clients, supporting interrupt descriptors and DSA memmove when the hardware operation capability allows it.

## Important APIs, Types, And Functions

Key functions are `idxd_register_dma_device`, `idxd_unregister_dma_device`, `idxd_register_dma_channel`, `idxd_unregister_dma_channel`, `idxd_dmaengine_drv_probe/remove`, `idxd_dma_submit_memcpy`, `idxd_dma_prep_interrupt`, `idxd_dma_tx_submit`, and `idxd_dma_complete_txd`. `struct idxd_dma_dev` wraps `struct dma_device`; `struct idxd_dma_chan` maps a dmaengine channel back to an IDXD WQ.

## Control Flow

Device probe in `device.c` registers a dmaengine device with no channels. When the dmaengine subdriver binds a kernel WQ, it enables the WQ through `idxd_drv_enable_wq()`, allocates a channel, initializes every preallocated WQ descriptor’s `dma_async_tx_descriptor`, registers the channel, and holds a WQ device reference. Preparing a transfer allocates an IDXD descriptor from the WQ pool, fills a DSA NOOP or MEMMOVE hardware descriptor with completion address and flags, and returns the tx descriptor. `tx_submit` assigns a cookie and immediately submits to the portal; `issue_pending` is intentionally empty.

## State And Persistence Behavior

State lives in the dmaengine device, per-WQ channel object, preallocated descriptors, cookies, and completion records. `tx_status` returns `DMA_OUT_OF_ORDER` because the hardware can complete out of order. Terminate flushes WQ descriptors; synchronize drains the WQ.

## Dependencies And Integration Points

It depends on dmaengine core, internal submit/allocation functions, DSA uapi opcodes, IDXD WQ state, and the IDXD bus. Completion is called from IRQ paths via the driver callback registered in `idxd_dmaengine_drv`.

## Risks And Edge Cases

`tx_submit` can fail after cookie assignment and returns a negative error. `idxd_dma_complete_txd()` may resubmit on invalid interrupt handles. Memcpy length is rejected above device max. No residue is reported because completion order is not ordered.

## Test Signals

Validate WQ binding to `dmaengine`, channel registration, `dmatest` MEMCPY, DMA_INTERRUPT descriptors, out-of-order status behavior, invalid interrupt-handle recovery, terminate flush, synchronize drain, and clean unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/idxd.h -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/idxd.h

## Purpose

`idxd.h` is the central private interface for the Intel DSA/IAA driver stack. It defines device model types, WQ/group/engine/device state, event-log state, descriptors, helper predicates, portal addressing, registration helpers, and cross-file prototypes.

## Important APIs, Types, And Functions

Major types include `idxd_dev`, `idxd_device_driver`, `idxd_irq_entry`, `idxd_group`, `idxd_wq`, `idxd_engine`, `idxd_hw`, `idxd_device`, `idxd_saved_states`, `idxd_desc`, `idxd_dma_dev`, `idxd_cdev`, `idxd_pmu`, and `idxd_evl`. Inline helpers classify device/WQ types, compute portal offsets, rotate portal addresses, manage simple WQ client counts, handle max batch/SGL constraints, and dispatch descriptor completion to the bound subdriver.

## Control Flow

The header coordinates control flow across files rather than running it itself. `bus.c` uses driver registration macros, `init.c` allocates objects and registers PCI devices, `device.c` implements control operations, `dma.c` and `cdev.c` bind WQs, and IRQ/submit/sysfs files use the shared prototypes.

## State And Persistence Behavior

It models all volatile IDXD state: hardware capability shadows, device state flags, command status, WQ config shadows, PASID/SVA state, descriptor pools, completion records, event logs, saved FLR state, and debugfs/perf pointers. It defines no persistent storage.

## Dependencies And Integration Points

Dependencies span dmaengine, PCI, IOMMU, cdev, perf, xarray, wait queues, percpu refs, crypto, uapi IDXD structures, and `registers.h`. It exports the `dsa_bus_type` and internal namespace prototypes used by all IDXD modules.

## Risks And Edge Cases

Because this header is shared widely, layout or helper changes affect sysfs, DMA, cdev, IRQ, and recovery paths. `idxd_wq_portal_addr()` intentionally uses non-atomic portal offset rotation. WQ refcount helpers are simple counters protected by caller locking. IAA disables batch size regardless of hardware field.

## Test Signals

Signals include full IDXD build coverage with dmaengine, cdev, compat, perfmon, and SVA options; module namespace checks; successful device/WQ binding; and FLR recovery using `idxd_saved_states`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/idxd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/init.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/init.c

## Purpose

`init.c` is the PCI and module lifecycle for Intel IDXD accelerators, covering DSA and IAA/IAX enumeration, capability discovery, object graph allocation, SVA/PASID setup, interrupt setup, sysfs/debugfs/perf registration, FLR recovery, shutdown, and module init/exit.

## Important APIs, Types, And Functions

Important routines include `idxd_setup_interrupts`, `idxd_setup_wqs`, `idxd_setup_engines`, `idxd_setup_groups`, `idxd_setup_internals`, `idxd_read_caps`, `idxd_alloc`, `idxd_enable_system_pasid`, `idxd_probe`, `idxd_device_config_save/restore`, `idxd_reset_prepare/done`, `idxd_pci_probe_alloc`, `idxd_wqs_quiesce`, `idxd_shutdown`, `idxd_remove`, and `idxd_init_module`. It defines module parameters `sva` and `tc_override`, global `support_enqcmd`, and PCI ID tables for DSA/IAA devices.

## Control Flow

Module init checks CPU MOVDIR64B and ENQCMD support, registers internal IDXD subdrivers, allocates cdev majors, initializes debugfs, and registers the PCI driver. PCI probe enables the function, allocates an `idxd_device`, maps MMIO, sets DMA masks, resets hardware, optionally enables a system PASID, reads capabilities and table offsets, allocates WQs/engines/groups/EVL/workqueues, loads read-only config if needed, sets up MSI-X, initializes perfmon, optionally loads IAA defaults, registers dsa-bus devices, and creates debugfs.

## State And Persistence Behavior

State includes the allocated `idxd_device`, config devices for WQs/engines/groups, capability shadows, SVA/PASID flags, MSI-X entries, EVL cache, IDA IDs, and saved state for reset recovery. FLR prepare snapshots device/group/engine/WQ configuration and PCI state; reset-done restores PCI state, re-probes hardware without reallocating, restores config, rebinds the device driver, and attempts to rebind previously enabled user WQs.

## Dependencies And Integration Points

It depends on PCI, MSI-X, IOMMU PASID APIs, CPU feature flags, workqueues, dmaengine, IDXD bus/subdrivers, sysfs registration, debugfs, perfmon, cdev majors, and IAA defaults.

## Risks And Edge Cases

No MOVDIR64B prevents module load. ENQCMD absence disables shared WQ support but still loads. SVA can be disabled by module parameter. FLR recovery currently only re-enables user WQs, not kernel WQs. Cleanup ordering is delicate because config-device release frees IDXD memory after driver unbind.

## Test Signals

Signals include probe on DSA and IAA PCI IDs, CPU feature gating, SVA on/off behavior, MSI-X vector setup, sysfs device tree creation, IAA default WQ configuration, debugfs/perf setup, shutdown disable, remove cleanup, and PCI FLR recovery with user WQ rebind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/init.c -->
