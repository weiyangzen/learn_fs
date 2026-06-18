<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.c

## Purpose

`dev.c` is the Tegra host1x platform driver. It maps SoC resources, selects generation-specific operation tables, configures IOMMU/DMA behavior, initializes channels, contexts, syncpoints, interrupts, debugfs, runtime PM, child devices, virtualization tables, and module bus/driver registration.

## Important APIs, Types, And Functions

- MMIO helpers: `host1x_common_writel()`, hypervisor read/write, sync read/write/readq, and channel read/write.
- Static `host1x_info` tables describe Tegra20 through Tegra234 channel/syncpoint counts, sync register offsets, DMA masks, wide-gather support, hypervisor/common regions, stream-ID protection tables, and PM quirks.
- `host1x_setup_virtualization_tables()` programs SID offset/limit and VM access tables for hypervisor-capable SoCs.
- IOMMU helpers decide when host1x wants an IOMMU, attach a paging domain, initialize IOVA allocation, set the DMA mask, and detach/free on exit.
- `host1x_probe()` is the primary initialization pipeline; `host1x_remove()` tears it down.
- Runtime PM callbacks stop channels/interrupts, save/restore syncpoints, manage reset/clock state, and reprogram virtualization.

## Control Flow

Probe obtains match data, maps either legacy or VM/hypervisor/common register resources, collects named syncpoint IRQs with fallback to IRQ 0, initializes device lists and DMA parameters, calls the generation `init()` function, obtains clock/reset resources, initializes the BO cache and IOMMU, then channels, contexts, syncpoints, interrupts, debugfs, host1x bus registration, and child population. Every failure path unwinds the initialized subset in reverse order.

Runtime suspend stops CDMA on allocated channels, disables syncpoint interrupts, saves syncpoint state, optionally asserts resets, disables the clock, and releases reset controls. Runtime resume reacquires resets, enables the clock, deasserts reset, programs virtualization tables, restores syncpoints, and restarts interrupt hardware.

## State And Persistence Behavior

The `struct host1x` instance persists as platform data. It owns MMIO mappings, IRQ numbers, clocks/resets, IOMMU domain/IOVA allocator, operation-table pointers, syncpoints, channel/context lists, BO cache, debugfs root, and client-device list. Hardware state includes SID protection tables, VM permissions, syncpoint values, threshold interrupts, reset/clock state, and channel registers.

## Dependencies And Integration Points

Depends on Linux platform, OF, runtime PM, reset, clock, DMA/IOMMU/IOVA, tegra OPP, and host1x bus/client infrastructure. It includes generation headers `host1x01` through `host1x08`; child devices populated from DT are typically display, DRM, VIC, NVDEC, NVENC, and media clients.

## Risks And Edge Cases

IOMMU policy is SoC- and firewall-sensitive, especially for 32-bit gather limitations on Tegra124/210. Hypervisor resource names must match DT for newer SoCs. Runtime PM is intentionally forced active because dynamic RPM is not ready. SID table mistakes can break engine memory isolation. Probe unwinding spans many subsystems, so failure injection is valuable. `skip_reset_assert` preserves secure-world access on Tegra186 and must not regress.

## Test Signals

Signals include probe/remove for every compatible, DT resource validation, IOMMU and non-IOMMU boot, large-memory systems requiring 32-bit IOVA for old gathers, runtime suspend/resume, child device population, syncpoint IRQ delivery across multiple IRQ lines, virtualization-table programming on Tegra186/194/234, and module init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.c -->
