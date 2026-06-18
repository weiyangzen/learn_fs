# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/Makefile

Purpose: Maps pseries Kconfig symbols to object files and applies pseries debug compile flags and sanitizer exclusions.

Important APIs/types/functions: Always-built objects include core pseries LPAR, RTAS, setup, firmware, DLPAR, PCI, EEH, mobility, RNG, platform attributes, and DTL code. Conditional objects include SMP, kexec, energy, CPU/memory hotplug, hypervisor console/server, hcall instrumentation, CMM, HTM dump, IO event IRQs, LPAR config, VIO, IBM eBus, PAPR SCM, VPHN, SVM, fadump, PLPKS, suspend, and VAS.

Control flow: The Makefile has no runtime flow. Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` to decide built-in versus module compilation. `ccflags-$(CONFIG_PPC_PSERIES_DEBUG)` adds `-DDEBUG`; KASAN is disabled for real-mode sensitive `ras.o` and `kexec.o`.

State and persistence: Build output composition is the persistent effect. Objects selected here define which machine initcalls and exported symbols are present in the kernel/module set.

Dependencies and integration points: Integrates the pseries directory with the architecture Kbuild system and Kconfig symbols from `Kconfig`. It is the direct build linkage for the pseries files in this subset.

Risks: Object ordering in `obj-y` can matter for initcall/link ordering and symbol availability. Moving a file between built-in and modular form can change exported symbol requirements. Real-mode code must stay out of sanitizer instrumentation.

Test signals: PPC64 pseries allyesconfig/allmodconfig/defconfig builds, module load tests for optional objects, and link checks when toggling each `CONFIG_*` symbol are useful.

Source read size: 43 lines, 1573 bytes.
