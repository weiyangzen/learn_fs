# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-hcd.h

## Purpose
`fotg210-hcd.h` defines the EHCI-style host-side data structures, register layout, bit fields, byte-order helpers, and inline accessors used by `fotg210-hcd.c`. It is the hardware contract for the host controller side of the Faraday FOTG210 block.

## Important APIs, Types, and Functions
Key exported types are `struct fotg210_hcd`, `struct fotg210_caps`, `struct fotg210_regs`, `struct fotg210_qtd`, `struct fotg210_qh_hw`, `struct fotg210_qh`, `union fotg210_shadow`, `struct fotg210_iso_stream`, `struct fotg210_iso_sched`, `struct fotg210_itd`, and `struct fotg210_fstn`. The root-hub state machine is encoded in `enum fotg210_rh_state`; hrtimer work items are encoded in `enum fotg210_hrtimer_event`. Conversion helpers `hcd_to_fotg210()` and `fotg210_to_hcd()` bridge usbcore `struct usb_hcd` and the private HCD object.

Register definitions cover capability registers (`HC_LENGTH`, `HC_VERSION`, `HCS_N_PORTS`, `HCC_CANPARK`, `HCC_PGM_FRAMELISTLEN`), operational registers (`CMD_RUN`, `CMD_RESET`, `CMD_ASE`, `CMD_PSE`, `STS_*`, `PORT_*`), OTG registers (`OTGCSR_*`, `OTGISR_OVC`), and global interrupt mask bits. Descriptor helpers include `QTD_NEXT()`, `QH_NEXT()`, `FOTG210_LIST_END()`, QTD status bits, QH type tags, periodic link tags, and endian conversion helpers `cpu_to_hc32()`, `hc32_to_cpu()`, and `hc32_to_cpup()`.

## Control Flow
This header does not run independently, but its layout controls every host path. Probe maps MMIO into `fotg210_caps` and then computes `fotg210_regs`. Enqueue paths allocate `fotg210_qtd`, `fotg210_qh_hw`, and `fotg210_itd` objects whose first fields match the hardware descriptor formats. Completion paths interpret the bit fields here to translate hardware status into Linux URB status. Periodic scheduling updates both the hardware frame list and the parallel `union fotg210_shadow` table using the same link type tags.

## State and Persistence Behavior
`struct fotg210_hcd` is the central volatile state container. Its `lock` protects schedule lists, endpoint private pointers, hardware descriptor fields, and MMIO updates. The state includes root-hub lifecycle, hrtimer event masks/timeouts, async and interrupt unlink queues, periodic frame-list state, port suspend/resume/reset bitmaps, DMA pools, the cached command register, and statistics. No state persists across driver removal; the durable ABI is the MMIO/descriptor layout encoded by this header.

## Dependencies and Integration Points
The header depends on Linux USB HCD types, EHCI debug-port types, DMA address types, hrtimers, clocks, spinlocks, and the shared `struct fotg210` wrapper. It integrates with usbcore through `struct usb_hcd`, `struct usb_device`, `struct usb_host_endpoint`, URB endpoint private storage, and USB port status constants. It assumes little-endian MMIO and descriptors through fixed `readl()`/`writel()` and `cpu_to_le32()` helpers, while retaining EHCI-derived big-endian comments for non-FOTG variants.

## Risks
The descriptor structures are hardware-visible and alignment-sensitive. Changes to field order, packing, link tags, or endian helpers can corrupt DMA. The file has comments inherited from broader EHCI code about big-endian and companion-controller support, but this FOTG210 variant hardcodes little-endian behavior and a single root port. `FOTG210_MAX_ROOT_PORTS` limits bitmap use to one port; adding multi-port hardware would require coordinated changes in root-hub code. Timer enum order must remain synchronized with `event_delays_ns[]` and `event_handlers[]` in the C file.

## Test Signals
Compile testing with sparse/endian checks is useful because `__hc32` and hardware descriptors are central. Runtime validation should exercise all descriptor types: QTD/QH control and bulk, interrupt QH periodic entries, ITD ISO entries, and root-hub port status paths. Debugfs register and schedule dumps should show sane decoded status bits and link tags. Any change to this header should be paired with DMA alignment checks, USB enumeration, transfer stress, and unload/reload tests.
