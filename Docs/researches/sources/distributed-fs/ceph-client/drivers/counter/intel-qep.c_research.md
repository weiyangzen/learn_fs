# sources/distributed-fs/ceph-client/drivers/counter/intel-qep.c

Purpose: PCI driver for Intel Quadrature Encoder Peripheral devices, exposing a single X4 quadrature count with phase A/B/index signals and several configuration extensions.

Important APIs/types/functions: `struct intel_qep` stores MMIO base, device, mutex, enabled flag, and suspend context registers. Hardware helpers are `intel_qep_readl()`, `intel_qep_writel()`, and `intel_qep_init()`. Counter callbacks include count read, fixed function/action reads, ceiling, enable, spike filter length in nanoseconds, and preset-enable.

Control flow: PCI probe enables the device, maps BAR0, initializes registers with the peripheral disabled, fills Generic Counter structures, sets up runtime PM, and registers with `devm_counter_add()`. Configuration writes that alter `QEPCON`, `QEPFLT`, or `QEPMAX` take the mutex and reject changes while enabled. Enable writes manage `QEPCON_EN` and an extra runtime-PM reference to keep hardware powered while counting. Suspend saves key registers; resume restores them with enable cleared first, then restores the previous enable state.

State and persistence: live state is in MMIO registers plus cached `enabled`; suspend context caches `qepcon`, `qepflt`, and `qepmax`. Configuration is volatile across driver reload but restored across PM suspend/resume.

Dependencies and integration: uses PCI managed resource helpers, runtime PM, Generic Counter API, and PCI IDs for Intel EHL devices. No event interrupts are exposed; it is primarily polling/sysfs configuration.

Risks: several `pm_runtime_get_sync()` return values are ignored, so runtime-PM failures may produce stale MMIO access. Configuration is disabled while counting, so userspace must order enable off before setting ceiling/filter/preset behavior. Spike-filter conversion has clock-period assumptions fixed at 10 ns.

Test signals: PCI probe/remove, sysfs count and ceiling reads, attempts to change ceiling/filter/preset-enable while enabled return `-EBUSY`, 32-bit ceiling range validation, enable toggling balances runtime PM, and suspend/resume preserves filter/max/control state.
