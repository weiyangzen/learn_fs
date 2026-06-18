# sources/distributed-fs/ceph-client/drivers/cache/hisi_soc_hha.c

## Purpose
`hisi_soc_hha.c` exposes HiSilicon Hydra Home Agent cache clean-invalidate support through the generic cache coherency operations framework.

## Important APIs, Types, And Functions
`struct hisi_soc_hha` embeds `struct cache_coherency_ops_inst` first, plus a mutex and MMIO base. `hisi_soc_hha_wbinv()` starts a range clean-invalidate operation, `hisi_soc_hha_done()` waits for completion, and `hisi_soc_hha_probe()` allocates/registers an operation instance for ACPI ID `HISI0511`.

## Control Flow
Probe allocates the coherency instance, maps the HHA MMIO resource, initializes the mutex, and registers with `cache_coherency_ops_instance_register()`. `wbinv` rejects zero sizes, aligns the address and top to 128-byte granules, waits for any previous operation to finish, writes start and length registers, programs clean-invalidate range mode, and returns immediately after starting. `done` locks the same instance and polls until the enable bit clears or times out.

## State And Persistence
Each platform device has its own registered coherency instance and MMIO mapping. Hardware state is an in-flight range maintenance operation. The mutex serializes overlapping commands per HHA instance.

## Dependencies And Integration Points
The file imports the `CACHE_COHERENCY` namespace and depends on ACPI platform enumeration, MMIO resources, `readl_poll_timeout_atomic()`, and the generic `cache_coherency_ops` API used by hotplug-like cache maintenance flows.

## Risks And Edge Cases
The driver intentionally does not filter physical addresses to the HHA responsible for a line; every instance may receive the operation and hardware must report success if not responsible. Polling is atomic and bounded to 50 ms. Size is programmed as inclusive `size - 1`, so alignment and underflow handling are critical. Remove must unregister before unmapping to avoid callbacks into freed MMIO.

## Test Signals
Test ACPI probe/remove, multi-HHA systems, zero-size rejection, unaligned ranges, concurrent `wbinv` calls, timeout on a forced busy bit, and full hotplug/cache-maintenance users that call both start and done.
