# sources/distributed-fs/ceph-client/drivers/perf/arm_pmu_platform.c

## Purpose
Device-tree/platform probing helper for ARM CPU PMU drivers. It allocates a common `arm_pmu`, parses PMU IRQ topology and optional interrupt affinity, invokes either OF match init callbacks or CPU-ID probe tables, requests per-CPU IRQs, and registers the PMU with perf.

## Important APIs, Types, And Functions
- `arm_pmu_device_probe()` is the public platform probe helper used by ARMv6, ARMv7, ARMv8, and XScale drivers.
- `pmu_parse_irqs()` supports no-IRQ PMUs, single percpu PPI PMUs, and per-CPU SPI IRQ lists.
- `pmu_parse_irq_affinity()` reads `interrupt-affinity` CPU phandles when present.
- `probe_current_pmu()` reads the current CPU ID and matches `struct pmu_probe_info` entries for non-DT-detailed legacy platforms.
- `armpmu_request_irqs()` and `armpmu_free_irqs()` wrap common IRQ request/free per supported CPU.

## Control Flow
Platform drivers call `arm_pmu_device_probe()` from their `.probe`. The helper allocates and initializes `arm_pmu`, stores the platform device, parses IRQs and supported CPUs, resolves an init function from OF match data or a probe table, applies `secure-reg-access` for 32-bit systems, calls hardware init, requests IRQs for all supported CPUs, and finally calls `armpmu_register()`. Failures unwind IRQs and free the PMU.

## State And Persistence
The helper fills `pmu->supported_cpus`, per-CPU `hw_events->irq`, `pmu->plat_device`, `pmu->secure_access`, and `pmu->pmu.parent`. State is all runtime probe state; no persistent configuration is written.

## Dependencies And Integration Points
It depends on platform IRQ APIs, OF match data, `interrupt-affinity` bindings, `irq_is_percpu_devid()`, common `arm_pmu.c` IRQ registration, and architecture init callbacks from the hardware-specific PMU files.

## Risks
Missing `interrupt-affinity` on SMP triggers fallback to logical CPU order, which is explicitly fragile. Multiple PPIs, mixed PPI/SPI layouts, duplicate CPU IRQ mappings, or invalid phandles fail probe. No-IRQ mode sets `PERF_PMU_CAP_NO_INTERRUPT`, so counting can work but sampling cannot. ARM64 ignores `secure-reg-access`, so firmware relying on that property would not get secure debug access.

## Test Signals
Use DT systems with no IRQ, one PPI, and per-CPU SPI layouts. Check warnings for missing affinity, duplicate IRQs, or mismatched PPIs; verify perf sampling fails cleanly with no IRQ; verify `/sys/.../cpus` matches affinity; and confirm error unwind leaves no requested IRQs after failed probe.
