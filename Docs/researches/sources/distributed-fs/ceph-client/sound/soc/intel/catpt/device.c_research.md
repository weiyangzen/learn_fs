<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/device.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/device.c

## Purpose
ACPI platform driver for Intel Low Power AudioDSP on Lynx Point and Wildcat Point platforms. It owns device discovery, MMIO mapping, IRQ registration, runtime/system PM sequencing, board machine registration, and initial assembly of DSP, DMAC, firmware, and ALSA platform components.

## APIs, Types, and Functions
Main entry points are `catpt_acpi_probe()`, `catpt_acpi_remove()`, PM callbacks `catpt_suspend()`, `catpt_resume()`, `catpt_runtime_suspend()`, and `catpt_runtime_resume()`, plus helpers `catpt_do_suspend()`, `catpt_register_board()`, `catpt_probe_components()`, and `catpt_dev_init()`. It defines ACPI machine tables for LPT/WPT, `catpt_spec` descriptors `lpt_desc` and `wpt_desc`, ACPI IDs `INT33C8` and `INT3438`, and registers `catpt_acpi_driver`.

## Control Flow, State, and Persistence
Probe validates that Intel DSP policy selects SST/CATPT, allocates `catpt_dev`, initializes resources from the matched spec, maps LPE and PCI BARs, coerces a 31-bit DMA mask for firmware context storage, allocates a coherent DRAM-sized Dx buffer, gets the IRQ, installs threaded DSP IRQ handlers, powers the DSP, probes DW DMA, boots firmware once, registers the ALSA component, enables autosuspend runtime PM, and then spawns the matching board platform device. Suspend enters firmware Dx D3 over IPC, stalls the DSP, stores firmware memdumps, module states, and stream contexts through DMA, then powers down. Resume powers up, reboots firmware in restore mode, and reapplies cached SSP formats.

## Dependencies and Integration
Depends on ACPI, PCI/platform resources, DMA mapping, IRQs, runtime PM, `snd_intel_acpi_dsp_driver_probe()`, ASoC ACPI machine matching, and all CATPT core subsystems. The registered board uses `mach->mach_params.platform = "catpt-platform"` to bind to the CATPT ALSA component registered by `pcm.c`.

## Risks and Test Signals
Risks include suspend intentionally ignoring `catpt_do_suspend()` failures for system sleep, firmware restore depending on valid Dx context and coherent buffer contents, runtime PM interactions while module unload is in progress, board registration after PM enable, and per-platform offset/mask correctness in `catpt_spec`. Test signals are ACPI probe on `INT33C8`/`INT3438`, successful firmware first boot, child board creation, runtime autosuspend/resume with active and inactive streams, reprogrammed SSP formats after resume, and clean remove after runtime PM disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/device.c -->
