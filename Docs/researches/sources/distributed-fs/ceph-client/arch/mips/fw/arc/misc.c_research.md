<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/misc.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/misc.c

**Purpose:** Supplies miscellaneous ARC PROM service wrappers for interactive mode and display status.

**Important APIs/types/functions:** `ArcEnterInteractiveMode()` disables board cache and local IRQs, calls firmware `imode`, and is marked `__noreturn`. `ArcGetDisplayStatus()` calls `GetDisplayStatus` for a file ID.

**Control flow:** Interactive mode intentionally never returns to the kernel. Display status is a direct firmware query.

**State, dependencies, integration:** Uses board-cache control, IRQ disabling, ARC call macros, and ARC display types. It supports reboot/debug paths and firmware console/display users.

**Risks and test signals:** Calling interactive mode after PROM resources are invalid is unsafe. Test that IRQ/cache disabling happens before firmware entry and that display status calls use valid file handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/misc.c -->
