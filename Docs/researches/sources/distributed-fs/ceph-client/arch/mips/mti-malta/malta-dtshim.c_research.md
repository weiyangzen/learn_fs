<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-dtshim.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-dtshim.c

### Purpose
`malta-dtshim.c` mutates firmware or built-in Malta device trees at boot to add memory nodes and adjust interrupt topology when a GIC is absent.

### Important APIs, Types, And Functions
`malta_dt_shim()` is the public entry. `append_memory()` reads firmware memory size, command-line overrides, memory-map version, and writes `/memory` `reg` plus `linux,usable-memory`. `remove_gic()` detects CM/ROCit GIC presence, nops the GIC node when absent, and redirects the i8259 interrupt parent. `gen_fdt_mem_array()` creates v1/v2 Malta memory ranges.

### Control Flow
The shim validates and opens the FDT into a 16 KiB aligned buffer, checks root compatibility for `mti,malta`, appends memory only if no memory node exists, removes or enables GIC handling as needed, packs the FDT, and returns either the modified buffer or original FDT for non-Malta compatibles.

### State, Persistence, And Dependencies
Persistent state is the modified flattened device tree handed to `__dt_setup_arch()`, plus global `physical_memsize`. Dependencies include libfdt, firmware environment access, ARC command line, ROCit/MSC registers, CM probing, and Malta revision macros.

### Integration Points
`malta-setup.c` calls this from `plat_mem_setup()`. The output affects memblock setup, interrupt controller probing, GIC timer availability, and i8259 routing.

### Risks
The fixed 16 KiB FDT buffer must be large enough after edits. Big-endian Malta subtracts a page for a SOC-it DMA quirk. Memory map v2 discards the IO-obscured 256 MiB window. If GIC detection is wrong, interrupt routing in the DT will not match hardware.

### Test Signals
Boot Malta with GT64120, Bonito, SOCit, and ROCit controllers; with and without CM/GIC; with `memsize=` and `ememsize=` env/cmdline overrides; and validate `/proc/device-tree` memory and interrupt-parent properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-dtshim.c -->
