<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-init.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-init.c

### Purpose
`malta-init.c` performs early Malta PROM/platform initialization. It detects the system controller, maps controller registers, configures PCI byte swapping and IO bases, installs NMI/EJTAG vectors, initializes firmware command line and memory, sets console defaults, and chooses SMP operations.

### Important APIs, Types, And Functions
`prom_init()` is the main platform entry. `console_config()` parses `modetty0` and appends early console/console arguments when absent. `mips_nmi_setup()` and `mips_ejtag_setup()` copy exception vectors. `mips_cpc_default_phys_base()` returns the CPC base. Globals include revision IDs and controller base addresses.

### Control Flow
Early boot maps Bonito to identify emulation boards, resolves `mips_revision_sconid`, then switches over GT64120, Bonito, SOCit/ROCit, or SOCitSC controllers. It configures PCI swaps, DMA mappings, retry policy, IO port base, and then registers board exception setup callbacks. Finally it initializes firmware command line, memory, serial console, CPC probing, and SMP ops in CPS/vSMP/UP priority order.

### State, Persistence, And Dependencies
Persistent state includes mapped controller bases, revision globals, firmware command line, IO port base, installed exception vectors, and selected SMP ops. Dependencies include YAMON/fw helpers, board revision registers, controller register macros, PCI constants, cache flush, and CPS support.

### Integration Points
This is the earliest Malta platform setup used by later memory, interrupt, PCI, and time code. `malta-dtshim.c`, `malta-int.c`, and `malta-setup.c` depend on the detected system controller state.

### Risks
Wrong system-controller detection leads to wrong register mappings and IO base. Console string appends directly into firmware command line storage. PCI byte-lane swap settings differ by endianness and controller. The default unknown-controller path intentionally spins forever.

### Test Signals
Boot Malta variants across controller IDs and endian modes, verify serial console defaults, PCI enumeration, NMI/EJTAG vectors, and SMP startup mode selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-init.c -->
