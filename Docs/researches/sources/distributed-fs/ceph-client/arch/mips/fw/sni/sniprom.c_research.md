<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/sni/sniprom.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/sni/sniprom.c

**Purpose:** Implements PROM access, memory detection, command-line construction, and system type reporting for big-endian SNI RM machines.

**Important APIs/types/functions:** Firmware entry macros map calls at `PROM_VEC`. `prom_putchar()`, `prom_getenv()`, and `prom_get_hwconf()` wrap PROM services. `sni_mem_init()` imports memory banks. `prom_init()` initializes memory and command line. `get_system_type()` returns `system_type`.

**Control flow:** On 64-bit kernels, PROM calls route through `call_o32` with a static O32 stack. Memory init reads IDPROM size and PROM bank layout, adjusts PCI tower windows, and adds banks to memblock. Command-line init copies argv entries from CKSEG0 addresses.

**State, dependencies, integration:** Uses firmware vectors at physical ROM, IDPROM constants, memblock, boot args, and optional O32 bridge. It supplies platform-specific `prom_init`.

**Risks and test signals:** Some PROM functions are version-dependent, and memory bank fixups are board-type specific. Test old/new PROM versions, PCI tower base adjustment, 64-bit O32 calls, `hwconf == 0xffffffff`, and command-line copy bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/sni/sniprom.c -->
