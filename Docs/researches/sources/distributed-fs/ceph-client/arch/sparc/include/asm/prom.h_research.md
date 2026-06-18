# sources/distributed-fs/ceph-client/arch/sparc/include/asm/prom.h

Purpose: OpenPROM/OpenFirmware device-tree integration header for SPARC, declaring property mutation, integer property lookup, PROM tree build, CPU mask population, IO unmap, and IRQ translation setup.

Important APIs/types/functions: types `of_irq_controller`, `device_node`, `resource`; functions/helpers `of_set_property`, `of_getintprop_default`, `of_find_in_proplist`, `prom_build_devicetree`, `of_populate_present_mask`, `of_fill_in_cpu_data`, `of_iounmap`, `irq_trans_init`; macros/constants `_SPARC_PROM_H`, `of_compat_cmp`, `of_prop_cmp`, `of_node_cmp`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_PROM_H`, `__KERNEL__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into locking paths rather than through standalone functions.

State and persistence behavior: Persistent state lives in OF device nodes/properties, present CPU masks, IRQ domains/controllers, and PROM-created resource mappings.

Dependencies and integration points: Includes/dependencies: `linux/of.h`, `linux/types.h`, `linux/of_pdt.h`, `linux/proc_fs.h`, `linux/mutex.h`, `linux/atomic.h`, `linux/irqdomain.h`, `linux/spinlock.h`. Integration points include locking; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Boot device-tree population, property update locking, CPU enumeration, PROM IO mapping teardown, and IRQ domain translation are the relevant signals.
