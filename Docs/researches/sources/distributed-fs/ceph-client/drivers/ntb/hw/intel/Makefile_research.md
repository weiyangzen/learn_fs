# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/Makefile

Purpose: Defines the build composition for the Intel NTB hardware driver.

Important APIs, types, and functions: `obj-$(CONFIG_NTB_INTEL) += ntb_hw_intel.o` emits a single driver object when the Kconfig symbol is enabled. `ntb_hw_intel-y := ntb_hw_gen1.o ntb_hw_gen3.o ntb_hw_gen4.o` links generation-specific implementations into that object.

Control flow: Build-system flow only: Kbuild compiles the three source files and links them as the `ntb_hw_intel` module or built-in object depending on `CONFIG_NTB_INTEL`.

State and persistence behavior: No runtime state. The object list must stay synchronized with headers and PCI dispatch in `ntb_hw_gen1.c`.

Dependencies and integration points: Integrates with the surrounding kernel Kbuild system, `Kconfig`, and the shared module entry in `ntb_hw_gen1.c`, which registers one PCI driver covering gen1, gen3, gen4, gen5, and gen6 IDs.

Risks and edge cases: Adding a new generation header/source without updating this Makefile leaves PCI IDs or prototypes unresolved. Since module metadata lives in gen1, removing gen1 from the composite object would break module registration.

Test signals: `make M=drivers/ntb/hw/intel` or equivalent subtree builds should produce `ntb_hw_intel.o` and include all generation objects; link errors are the primary signal for mismatched object composition.
