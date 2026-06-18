# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/kernel-entry-init.h

**Purpose:** Provides ATH79 assembly macros used at kernel entry before normal C initialization.

**Important APIs/types/functions:** Defines `kernel_entry_setup` and an empty `smp_slave_setup` assembly macro. `kernel_entry_setup` reads CP0 Config, clears `CONF_CM_CMASK`, and sets `CONF_CM_CACHABLE_NONCOHERENT` to force KSEG0 from bootloader-selected write-through/no-write-allocate mode to write-back/write-allocate cacheability.

**Control flow:** This runs at the earliest MIPS kernel entry path. It executes before platform devices or normal memory management, ensuring subsequent KSEG0 accesses use the desired cache algorithm. `smp_slave_setup` is intentionally empty for this platform.

**State and persistence behavior:** It mutates CP0 Config cacheability bits on the boot CPU. That CPU state persists until changed and affects performance and memory behavior for cached kernel segments.

**Dependencies and integration points:** Depends on MIPS assembly symbols `CP0_CONFIG`, `CONF_CM_CMASK`, and `CONF_CM_CACHABLE_NONCOHERENT` from low-level headers. Integrated by MIPS entry assembly for the ATH79 machine.

**Risks:** Incorrect CP0 manipulation can break caching or early boot. The macro assumes the selected cacheability is valid for all ATH79 CPUs and that changing it at this point is safe. Any SMP enablement would need real slave setup.

**Test signals:** Boot with multiple bootloaders, verify no early cache exceptions, compare memory bandwidth/performance before and after entry setup, and run cache coherency and DMA tests after boot.
