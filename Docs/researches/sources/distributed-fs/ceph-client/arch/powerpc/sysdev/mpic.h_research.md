<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.h

Purpose: Declares internal MPIC adjunct interfaces for MSI and Freescale error-interrupt support.

Important APIs/types/functions: Declares `mpic_msi_reserve_hwirq()`, `mpic_msi_init_allocator()`, `mpic_u3msi_init()`, `mpic_pasemi_msi_init()`, core chip helpers `mpic_set_irq_type()`, `mpic_set_vector()`, `mpic_set_affinity()`, `mpic_reset_core()`, and FSL error helpers `mpic_map_error_int()`, `mpic_err_int_init()`, `mpic_setup_error_int()`, with stubs under disabled configs.

Control flow: Compile-time conditionals select real declarations or no-op/error-returning static inlines.

State and persistence: No state, but function declarations operate on persistent `struct mpic` state, MSI bitmaps, and FSL error vector arrays.

Dependencies and integration points: Included by `mpic.c`, `mpic_msi.c`, `mpic_u3msi.c`, and FSL error interrupt implementations.

Risks: Stub return values such as `-1` for unsupported MSI paths drive fallback behavior, so callers must handle them. FSL helper availability depends on `CONFIG_FSL_SOC`.

Test signals: Build coverage across `CONFIG_PCI_MSI`, `CONFIG_PPC_PASEMI`, and `CONFIG_FSL_SOC`.

Source read size: 60 lines, 1637 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.h -->
