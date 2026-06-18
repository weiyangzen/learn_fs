# sources/distributed-fs/ceph-client/drivers/usb/host/ohci.h

## Purpose

`ohci.h` is the shared OHCI core contract. It defines hardware descriptor layouts, register layouts, bit masks, private HCD state, endian conversion helpers, root-hub register access helpers, quirk flags, and exported symbols used by bus glue drivers.

## Important APIs, Types, and Functions

Key types are `struct ed`, `struct td`, `struct ohci_hcca`, `struct ohci_regs`, `struct urb_priv`, `enum ohci_rh_state`, `struct ohci_hcd`, and `struct ohci_driver_overrides`. Important helpers include `hcd_to_ohci()`, `ohci_to_hcd()`, `_ohci_readl()`, `_ohci_writel()`, `cpu_to_hc16/32()`, `hc16/32_to_cpu()`, `ohci_frame_no()`, `ohci_hwPSW()`, `periodic_reinit()`, and root-hub readers. Exported declarations include `ohci_init_driver()`, `ohci_restart()`, `ohci_setup()`, `ohci_suspend()`, `ohci_resume()`, `ohci_hub_control()`, and `ohci_hub_status_data()`.

## Control Flow

The header has no standalone runtime path, but its inline accessors are executed throughout the OHCI core. Descriptor endian helpers mediate every CPU/hardware ED and TD field. Register helpers select little-endian or big-endian MMIO based on Kconfig and quirk flags. `periodic_reinit()` reprograms frame interval and periodic start after reset/resume.

## State and Persistence Behavior

The header defines all important runtime state but stores none by itself. `struct ohci_hcd` persists for the HCD lifetime and contains hardware mappings, DMA memory, schedules, quirk flags, PM state, watchdog state, debugfs, and platform private extension storage.

## Dependencies and Integration Points

It depends on Linux USB HCD, endian helpers, MMIO accessors, DMA types, list heads, timers, work structs, and debugfs types supplied by including C files. It is included by core and bus glue files, making it the ABI-like internal interface for all OHCI variants.

## Risks and Test Signals

Risks include endian-helper regressions, incorrect descriptor alignment or masks, root-hub bit definition errors, quirk flag collisions, frame-number handling on big-endian hosts, and structure layout changes affecting every bus glue driver. Test signals include build coverage across little-endian, big-endian, and mixed-endian configs; sparse/endian warnings; USB enumeration on multiple buses; isochronous PSW handling; and root-hub port status correctness.
