# sources/distributed-fs/ceph-client/sound/hda/controllers/intel.c

## Purpose
`intel.c` is the primary PCI HD-audio controller driver for Intel HDA and many compatible PCI controllers from AMD/ATI, NVIDIA, VIA, Creative, C-Media, Zhaoxin, Loongson, Glenfly, VMware, and generic class-code devices. It binds PCI IDs to `azx` driver capability flags, initializes PCI/MMIO/DMA/IRQ/streams, probes codecs, integrates optional i915/DRM display power, handles runtime/system PM, and applies many platform workarounds.

## Important APIs, Types, and Functions
The private state is `struct hda_intel` from `intel.h`, embedding `struct azx` plus delayed probe, pending IRQ work, power-save list linkage, VGA switcheroo flags, runtime-PM flags, i915 power requirements, and retry state.

Critical functions include `azx_probe()`, `azx_create()`, `azx_probe_continue()`, `azx_first_init()`, `azx_free()`, `azx_remove()`, `azx_shutdown()`, `azx_init_pci()`, `hda_intel_init_chip()`, `azx_acquire_irq()`, `check_position_fix()`, `assign_position_fix()`, `check_probe_mask()`, `check_msi()`, `azx_check_snoop_available()`, `set_default_power_save()`, `azx_runtime_suspend/resume/idle()`, `azx_suspend/resume()`, and optional vga_switcheroo helpers.

## Control Flow
PCI probe first checks PCI/DMI denylists and whether another Intel DSP driver should own the device. It allocates an ALSA card, creates the `azx` bus, optionally initializes i915/audio-component integration, registers vga_switcheroo, and schedules delayed probe unless the bound GPU is off.

`azx_probe_continue()` enables display power, runs first hardware initialization, probes codecs, optionally loads patch firmware through `snd_hda_load_patch()`, configures codecs with retry support for flagged devices, registers the card, enables runtime PM/autosuspend, adds the card to the power-save list, and completes `probe_wait`.

## State and Persistence Behavior
Runtime state spans module parameters, the global `probed_devs` bitmap, global `card_list`, PCI drvdata, `azx` stream/bus fields, i915 display-power refcounts, work items, and codec/cache state. Power-save parameter writes iterate active cards and update codec power-save timeouts. Runtime suspend stops streams/chip, enables WAKEEN bits, and display power is requested during resume/reset. `probe_retry` can keep requeueing delayed work up to 60 times.

## Dependencies and Integration Points
The driver depends on PCI, ALSA core, HDA core/controller helpers, `snd-intel-dsp-config`, runtime PM, DMI quirks, optional firmware loader, optional input beep, optional i915 component APIs, vga_switcheroo, Apple gmux, tracepoints in `intel_trace.h`, and a very large PCI ID table.

## Risks
The driver has high quirk density: wrong caps can break MSI, snoop/cacheability, DMA addressing, position reporting, stream tags, i915 binding, or codec probing. Asynchronous probe and vga_switcheroo require careful completion and teardown handling. Position IRQ workarounds depend on wall clock, LPIB/POSBUF/FIFO behavior, and `bdl_pos_adj`. Runtime PM can break HDMI ELD notifications or click/pop on denied platforms. The PCI ID table is broad, so generic matches must stay below more specific entries.

## Test Signals
Test representative Intel PCH/SKL/HDMI, AMD, NVIDIA, VIA, Loongson, and generic devices; MSI fallback via `disable_msi_reset_irq()`, codec probe masks, DSP-driver handoff, patch loading, i915 binding/display power, vga_switcheroo off/on transitions, suspend/resume/runtime PM, DMA pointer modes, delayed IRQ work, and power-save denylist behavior. Tracepoints should emit suspend/resume/runtime events with the expected card index.
