
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/Makefile

Purpose: selects PowerNV platform object files and sanitizer exclusions for low-level real-mode code.

Important entries: disables KASAN instrumentation for `idle.o`, `pci-ioda.o`, `pci-ioda-tce.o`, and `setup.o` because real-mode paths and early machine-check handling are unsafe to instrument. Always builds OPAL setup/call/wrapper/core platform files, RTC/NVRAM/LPC/flash/log/dump/sysparam/sensor/message/HMI/power/irq/kmsg/powercap/PSR/sensor-group/ultravisor support. Conditional objects include SMP/subcore, FADump, OPAL core, PCI/IODA, EEH, memory errors, OPAL PRD, IMC, memtrace, VAS, OCXL, XSCOM, and secure variables.

Control flow and state: build-only declarative control. It maps Kconfig symbols to object inclusion and sanitizer behavior.

Dependencies and integration points: depends on symbols from PowerPC and PowerNV Kconfig. It is the link point that ties the source files in this subset into the kernel image.

Risks: enabling KASAN on real-mode code can break runtime behavior. Conditional duplication of `opal-fadump.o` under both `CONFIG_FA_DUMP` and `CONFIG_PRESERVE_FA_DUMP` must remain consistent with the file's compile-time branches. Object ordering matters for some initcall-visible platform symbols.

Test signals: PowerNV allmod/allyes/defconfig builds, KASAN PowerNV builds, and link checks for each conditional feature combination.
