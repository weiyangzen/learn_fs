# sources/distributed-fs/ceph-client/drivers/misc/ocxl/main.c

Purpose: module entry/exit for the generic OpenCAPI driver. It validates that the platform can perform TLB invalidation, initializes the OCXL file layer, and registers the PCI driver.

Important APIs and functions: `init_ocxl()` is the module initializer, `exit_ocxl()` is the exit path, and the file uses the external `ocxl_pci_driver` plus `ocxl_file_init()`/`ocxl_file_exit()` from the OCXL subsystem.

Control flow: initialization fails early with `-EINVAL` if `tlbie_capable` is false. It then initializes file infrastructure and registers the PCI driver; on PCI registration failure it unwinds the file layer. Exit unregisters PCI first, then tears down file state, matching the order that prevents new probes while user-facing device nodes are being removed.

State and persistence: no direct state beyond registered kernel module resources. Runtime state lives in the PCI, file, and link layers.

Dependencies and integration points: depends on `linux/module.h`, `linux/pci.h`, powerpc `asm/mmu.h`, and `ocxl_internal.h`. It is the top-level integration point that makes `pci.c` active.

Risks and test signals: test with unsupported platforms to confirm `tlbie_capable` rejection, simulated `ocxl_file_init()` and `pci_register_driver()` failures for unwind coverage, and module load/unload cycles with no stale device nodes or registered PCI driver.
