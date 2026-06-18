<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/init.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/init.c

**Purpose:** Performs ARC PROM library initialization for MIPS platforms.

**Important APIs/types/functions:** `prom_init()` validates the ARC system parameter block magic, stores `romvec`, initializes the command line, identifies the architecture, logs firmware version/revision, and calls `prom_meminit()`. `romvec` and optional `o32_stk` are exported state.

**Control flow:** Boot enters `prom_init()`, pulls `PROMBLOCK` and `ROMVECTOR`, hard-loops on invalid magic, then runs ordered setup before generic memory setup.

**State, dependencies, integration:** Initializes global firmware dispatch state consumed by `ARC_CALL*` users. It depends on boot arguments `fw_arg0/fw_arg1`, ARC command-line parsing, platform identification, and memory descriptor import.

**Risks and test signals:** Bad PROM magic leaves the system spinning before panic infrastructure may work. Test valid/invalid magic, 32-bit ARC with 64-bit kernels, and that memory descriptors become available before `memblock` setup completes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/init.c -->
