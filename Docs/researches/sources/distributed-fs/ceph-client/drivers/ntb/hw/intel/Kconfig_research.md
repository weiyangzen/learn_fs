# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/Kconfig

Purpose: Adds the `NTB_INTEL` kernel configuration option for Intel Non-Transparent Bridge hardware support.

Important APIs, types, and functions: Declares `config NTB_INTEL` as a tristate named "Intel Non-Transparent Bridge support". It depends on `X86_64` and its help text identifies capable Intel Xeon and Atom hardware.

Control flow: There is no runtime control flow. Build-time selection controls whether the Intel NTB hardware module can be built in, built as a module, or omitted.

State and persistence behavior: The chosen Kconfig value persists in the kernel `.config` and drives Makefile expansion through `CONFIG_NTB_INTEL`.

Dependencies and integration points: It integrates with the NTB hardware driver subtree and `drivers/ntb/hw/intel/Makefile`, which builds `ntb_hw_intel.o` from gen1/gen3/gen4 objects when enabled. The `X86_64` dependency prevents this hardware driver from being offered on unsupported architectures.

Risks and edge cases: There are no explicit dependencies on `PCI`, `NTB`, or `DEBUG_FS`; those are likely provided by parent menus or broader NTB infrastructure. If this Kconfig is reused outside its original tree context, missing parent dependencies could cause invalid build exposure.

Test signals: Kconfig tests include `allmodconfig`/`allyesconfig` on x86_64, checking `CONFIG_NTB_INTEL=m/y` builds the composite object, and non-x86_64 config checks showing the option is hidden.
