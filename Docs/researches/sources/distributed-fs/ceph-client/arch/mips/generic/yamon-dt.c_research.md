<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/yamon-dt.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/yamon-dt.c

**Purpose:** Converts YAMON bootloader command-line, memory, and serial environment into FDT properties for legacy boards.

**Important APIs/types/functions:** `yamon_dt_append_cmdline()` writes `/chosen/bootargs`. `yamon_dt_append_memory()` creates/updates `/memory` `reg` and `linux,usable-memory`. `yamon_dt_serial_config()` writes `/chosen/stdout-path`. Helper `gen_fdt_mem_array()` maps memory regions and discard gaps.

**Control flow:** Memory fixup reads `ememsize` or `memsize`, defaults to 32 MiB, applies command-line override, creates memory arrays with at most two entries, and writes big-endian cells. Serial fixup parses `yamontty` and `modettyN`, normalizes baud/parity/stop/flow, and writes a serial path.

**State, dependencies, integration:** Depends on generic firmware environment access, `arcs_cmdline`, libfdt mutation, and `struct yamon_mem_region` board tables.

**Risks and test signals:** Limited memory entry count can truncate region descriptions; parser accepts malformed serial modes by falling back. Test both env variable names, command-line memory override, region discard behavior, missing chosen/memory nodes, and serial mode variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/yamon-dt.c -->
