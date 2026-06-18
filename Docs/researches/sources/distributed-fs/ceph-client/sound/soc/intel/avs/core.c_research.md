<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/core.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/core.c

Purpose: main Intel AVS PCI/HDA driver: probes the controller, initializes HDA/extended links, IRQs, codecs, firmware, boards, runtime/system PM, and platform descriptors.

Important APIs, types, and functions: PCI driver `avs_pci_driver`; probe/remove/shutdown; bus/chip helpers; IRQ handlers for HDA streams and DSP IPC; codec probing; async `avs_hda_probe_work()`; PM helpers; platform `avs_spec` descriptors and PCI ID table. Also exports HDA power/clock/L1SEN helpers used by loader code.

Control flow: PCI probe honors `snd_intel_dsp_driver_probe()`, enables PCI, allocates `avs_dev`, initializes HDA extended bus and IPC, maps BAR0 and DSP BAR4, parses capabilities, configures DMA, initializes streams, requests two shared IRQ handlers on one vector, initializes i915 audio component, and schedules probe work. Probe work powers display, initializes the HDA chip, probes codecs, powers down links, enables processing-pipe capability and interrupts, initializes debugfs, first-boots firmware, obtains NHLT, registers all boards, and enables autosuspend. IRQ top half masks global interrupts and wakes a thread; stream thread handles HDA stream/RIRB events, while DSP thread dispatches platform IPC interrupt handling. Remove reverses board/debugfs/NHLT/CLDMA/streams/codecs/links/firmware/IRQ/mapping state.

State and persistence: `struct avs_dev` owns bus, IPC, firmware cache, module info, component/path lists, PM counters, trace state, and work item. Runtime PM transitions may either full-suspend DSP or enter a standby path when low-power paths are active. PCI config power/clock gating masks are module parameters.

Dependencies and integration points: integrates PCI, HDA codec core, HDA extended bus, i915 display audio, ACPI NHLT, debugfs, firmware loader, board selection, PCM components, DSP ops from platform files, and sysfs attributes. PCI ID descriptors choose firmware version minimums, SRAM/HIPC register layouts, boot masks, and attributes such as CLDMA/IMR/ACE/ALTHDA.

Risks: probe is split between PCI probe and async work, so remove/shutdown must cancel work and tolerate partial initialization. Two `pci_request_irq()` calls share the same vector with different dev_ids; cleanup must match both. PM paths rely on firmware IPC unless recovery has blocked IPC. Platform descriptors must stay aligned with firmware locations and register layouts. Error unwinding differs before and after scheduled work.

Test signals: successful firmware boot, HDA codec enumeration, board cards appearing, runtime suspend/resume cycles, shared IRQ handling without lost stream periods or IPC timeouts, and removal after deferred probe without leaks or use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/core.c -->
