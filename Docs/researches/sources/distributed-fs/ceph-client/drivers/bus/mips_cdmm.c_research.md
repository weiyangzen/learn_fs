# sources/distributed-fs/ceph-client/drivers/bus/mips_cdmm.c

## Purpose

`mips_cdmm.c` implements the MIPS Common Device Memory Map bus. CDMM exposes per-CPU in-core devices through a common MMIO region. This driver registers the `cdmm` bus, discovers CDMM device register blocks on each CPU, creates `struct mips_cdmm_device` instances, routes driver callbacks to the CPU owning each device, supports early probing for boot-time users, and coordinates CPU hotplug notifications.

## Important APIs, Types, And Functions

- Bus registration: exported `mips_cdmm_bustype`, `mips_cdmm_driver_register()`, and `mips_cdmm_driver_unregister()`.
- Early access: exported `mips_cdmm_early_probe()`.
- Per-CPU setup/discovery: `mips_cdmm_get_bus()`, `mips_cdmm_cur_base()`, weak `mips_cdmm_phys_base()`, `mips_cdmm_setup()`, `mips_cdmm_bus_discover()`, `mips_cdmm_cpu_online()`, and `mips_cdmm_cpu_down_prep()`.
- Callback routing: `BUILD_PERCPU_HELPER()` wraps probe/remove/shutdown through `work_on_cpu()`, and `BUILD_PERDEV_HELPER()` calls driver `cpu_up`/`cpu_down` callbacks for devices on a CPU.
- Data state: `struct mips_cdmm_bus` records physical base, mapped regs, DRB count, reserved block count, discovery status, and offline flag.

## Control Flow

At `subsys_initcall`, the driver registers the bus and a dynamic CPU hotplug state. On CPU online, it gets or allocates that CPU's bus record, configures the CDMM base if needed, marks it online, and either discovers devices or notifies existing drivers via `cpu_up`. Discovery scans device register blocks, decodes ACSR type/size/revision fields, creates one device per nonzero type, assigns a CPU device parent, resource range, bus, unique id, and name, then registers it with the driver core.

Driver probe/remove/shutdown callbacks must execute on the CPU that owns the CDMM device, so driver-core callbacks are wrappers that call `work_on_cpu(cdev->cpu, ...)`. CPU down first calls interested drivers' `cpu_down` callbacks through `bus_for_each_dev()`, then marks the per-CPU bus offline so future users revalidate or reconfigure CDMM.

`mips_cdmm_early_probe()` can be called before normal discovery, provided migration is prevented. It sets up the current CPU's CDMM region and scans for a requested device type, returning an MMIO pointer or an IOMEM error pointer.

## State And Persistence Behavior

CPU0 uses static `mips_cdmm_boot_bus`; other CPUs lazily allocate per-CPU `struct mips_cdmm_bus` pointers. `mips_cdmm_default_base` caches the first successful physical base for other CPUs. Device ids come from an atomic counter. CDMM enablement is stored in CP0 `cdmmbase`; `mips_cdmm_setup()` may inherit bootloader state, use DT/platform override, or copy the cached default.

## Dependencies And Integration Points

The driver depends on MIPS-specific CP0 register helpers, hazards, `cpu_has_cdmm`, `asm/cdmm.h`, device tree address parsing for `mti,mips-cdmm`, Linux CPU hotplug, per-CPU storage, work-on-CPU, and driver core bus APIs. Client CDMM drivers provide `struct mips_cdmm_driver` id tables and optional CPU hotplug callbacks.

## Risks

Callers of setup/early probe must prevent CPU migration; otherwise the per-CPU bus state and CP0 register state can mismatch. A missing physical base is memoized as sentinel `1` after logging once, so later setup returns `-ENOMEM`. Device discovery assumes ACSR size fields advance correctly; malformed hardware can affect scan progress. Probe/remove wrappers rely on `work_on_cpu()` availability during hotplug-sensitive windows.

## Test Signals

Signals include `cdmm%u discovery` logs, sysfs attributes for cpu/type/revision/modalias/resource, modalias `mipscdmm:tXX`, driver probe callbacks running on the owning CPU, CPU online/offline callbacks firing, early probe returning valid MMIO for known devices, and graceful behavior when no CDMM base is provided.
