<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cop2.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cop2.h

**Purpose:** Abstracts COP2 state handling and CU2 exception notification.

**Important APIs/types/functions:** Defines `cop2_present`, `cop2_lazy_restore`, `cop2_save`, and `cop2_restore` differently for Octeon, Loongson64, or no COP2. Provides `enum cu2_ops`, `register_cu2_notifier`, `cu2_notifier_call_chain`, and `cu2_notifier` helper macro.

**Control flow:** CPU-specific configs select save/restore behavior; CU2 exception code calls notifier chain for interested handlers.

**State, dependencies, integration:** Integrates Octeon COP2 thread state, Loongson lazy handling, and generic notifier infrastructure.

**Risks and test signals:** Missing save/restore corrupts COP2 state across context switches. Test Octeon COP2 workloads, Loongson64 lazy restore, and notifier ordering for CU2 load/store exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cop2.h -->
