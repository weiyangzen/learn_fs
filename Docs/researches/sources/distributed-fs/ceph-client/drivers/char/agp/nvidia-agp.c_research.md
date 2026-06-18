# sources/distributed-fs/ceph-client/drivers/char/agp/nvidia-agp.c

## Purpose

`nvidia-agp.c` is the AGPGART bridge driver for NVIDIA nForce and nForce2 chipsets. It handles NVIDIA-specific aperture setup, AMD K7 IORR programming, ATTBASE directory programming, aperture MMIO mapping for TLB flushes, and adjusted insertion/removal for apertures below 64 MB.

## Important APIs, Types, And Functions

- `nvidia_private` stores secondary PCI functions, mapped aperture pointer, active entry count, page offset, and write-buffer control mask.
- `nvidia_fetch_size()`, `nvidia_configure()`, `nvidia_cleanup()`, and `nvidia_tlbflush()` implement chipset hooks.
- `nvidia_init_iorr()` programs AMD K7 IORR MSRs for the AGP aperture.
- `nvidia_insert_memory()` and `nvidia_remove_memory()` override generic GATT operations to account for NVIDIA page offset/active entries.
- `agp_nvidia_probe()`, `agp_nvidia_remove()`, `agp_nvidia_resume()`, and the PCI driver/table provide module integration.

## Control Flow

Probe locates required companion PCI functions `(0,1)`, `(0,2)`, and `(30,0)`, validates AGP capability, sets a chipset-specific write-buffer-control mask, allocates a bridge, and registers it. Configure writes APSIZE, aperture base/limit into multiple functions, programs CPU IORR, computes active entries and offset for sub-64 MB apertures, writes up to eight ATTBASE directory pointers, enables GART/GTLB control, and maps the aperture. Insert checks type and bounds against active entries minus reserved memory, verifies scratch/empty GATT slots at the NVIDIA offset, writes masked page entries, and flushes.

## State And Persistence Behavior

The driver persists companion PCI device references until module cleanup, writes NVIDIA GART state into PCI config registers, maps 33 pages of the aperture for flush reads, and stores GATT offsets in `nvidia_private`. It relies on generic AGP bridge state and allocated GATT pages. Cleanup disables GART/GTLB, unmaps aperture space, restores previous APSIZE, and reinitializes IORR for the previous aperture.

## Dependencies And Integration Points

Dependencies include x86 MSR access, PCI config/resource APIs, `agp.h`, generic AGP allocation/GATT helpers, and the global `agp_memory_reserved`. The file integrates with the AGP core through `nvidia_driver` callbacks and with CPU memory type/range behavior through AMD K7 IORR registers.

## Risks And Edge Cases

Missing companion functions abort probe. IORR programming is CPU-specific and can fail if no free IORR exists. Sub-64 MB apertures require special `pg_offset`; generic insertion would map the wrong GATT area. TLB flush waits up to three seconds on write-buffer-control bits and then uses repeated aperture reads, so hardware hangs or bad aperture mappings are visible. Error paths in probe can leave acquired companion device refs until module cleanup rather than immediate release.

## Test Signals

Test by probing nForce/nForce2 hardware, validating all companion functions are found, aperture base/limit registers match BAR resources, IORR setup succeeds, and 32 MB aperture insertion targets the correct offset. Exercise bind/unbind under load and watch for TLB flush timeout logs. Suspend/resume should re-run configuration without stale mappings.
