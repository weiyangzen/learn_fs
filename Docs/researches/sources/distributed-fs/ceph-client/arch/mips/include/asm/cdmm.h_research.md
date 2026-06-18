<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cdmm.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cdmm.h

**Purpose:** Defines the MIPS Common Device Memory Map bus and driver interfaces.

**Important APIs/types/functions:** `struct mips_cdmm_device`, `struct mips_cdmm_driver`, `mips_cdmm_phys_base()`, `mips_cdmm_bustype`, `mips_cdmm_early_probe()`, driver register/unregister helpers, `module_mips_cdmm_driver`, `builtin_mips_cdmm_driver`, and optional early FDC console setup.

**Control flow:** Driver core matches CDMM devices by ID tables and calls probe/remove/shutdown/CPU hotplug callbacks.

**State, dependencies, integration:** Integrates CPU-local CDMM devices with Linux driver model and CPU hotplug. Used by EJTAG FDC early console and other CDMM devices.

**Risks and test signals:** CDMM base must be 32 KiB aligned and platform-reserved; CPU-local hotplug callbacks must quiesce pinned work. Test early probe, module and builtin registration, CPU up/down callbacks, and early FDC console config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cdmm.h -->
