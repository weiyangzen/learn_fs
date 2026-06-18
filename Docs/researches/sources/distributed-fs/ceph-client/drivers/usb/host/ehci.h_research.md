# sources/distributed-fs/ceph-client/drivers/usb/host/ehci.h

## Purpose
Central private header for the Linux EHCI host-controller implementation. It defines the EHCI controller state object, DMA descriptor layouts, queue/schedule metadata, endian accessors, timer events, quirk flags, TT bandwidth structures, and exported interfaces used by bus glue and shared EHCI source files.

## Important APIs, types, and functions
Core types include `struct ehci_hcd`, `struct ehci_qtd`, `struct ehci_qh_hw`, `struct ehci_qh`, `struct ehci_iso_stream`, `struct ehci_itd`, `struct ehci_sitd`, `struct ehci_fstn`, `struct ehci_tt`, and `struct ehci_driver_overrides`. Important enums/macros cover root-hub state, hrtimer events, qTD/QH token bits, periodic type tags, descriptor endian conversions, root-hub TT helpers, Freescale/ChipIdea errata predicates, and logging wrappers. Export declarations include `ehci_init_driver()`, `ehci_setup()`, `ehci_reset()`, `ehci_suspend()`, `ehci_resume()`, `ehci_hub_control()`, and related helpers.

## Control flow
The header itself has no runtime control path, but its structures drive all EHCI paths. Bus glue allocates `struct ehci_hcd` inside `usb_hcd`, sets caps/register pointers and quirks, and calls shared setup. Queue code manipulates qTD/QH fields defined here. Scheduler code manipulates iTD/siTD/FSTN/TT structures. Timer code uses the event enum and `struct ehci_hcd` fields to coordinate deferred work.

## State and persistence behavior
`struct ehci_hcd` is the persistent per-controller state for schedule lists, DMA pools, root-hub port bitmaps, timer state, quirk flags, bandwidth accounting, and private bus-glue storage. Hardware-visible descriptor structs are DMA-backed and must match EHCI-specified alignment and endian rules.

## Dependencies and integration points
Includes EHCI register definitions from `linux/usb/ehci_def.h` and integrates with USB HCD core, DMA pool users, platform/PCI glue, root-hub code, queue/scheduler/timer/sysfs/debug files, and architecture-specific endian IO helpers.

## Risks and edge cases
Descriptor layout, alignment, bit definitions, and endian conversions are ABI-critical for hardware DMA. `struct ehci_hcd` private storage must remain last. Timer enum order must match arrays in `ehci-timer.c`. Quirk flags are shared across many bus drivers and core paths, so adding or repurposing flags can change broad behavior.

## Test signals
Builds across little-endian and big-endian MMIO/descriptor configs, sparse endian checks, all bus glue drivers, async and periodic transfer tests, suspend/resume, root-hub TT behavior, quirk-specific hardware, and structure-size/alignment checks are the best signals.
