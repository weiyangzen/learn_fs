<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/cmdline.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/cmdline.c

**Purpose:** Builds `arcs_cmdline` from ARC/ARCS firmware argv values while converting selected firmware parameters into Linux kernel arguments.

**Important APIs/types/functions:** `prom_init_cmdline()` is the exported initializer. `move_firmware_args()` moves `OSLoadPartition=` to `root=` and appends `OSLoadOptions=` early. `ignored[]` filters firmware-only keys such as console handles and loader names.

**Control flow:** The code ignores argv[0], first copies converted firmware variables so later explicit arguments can override them, then appends non-ignored argv strings separated by spaces and trims the trailing space.

**State, dependencies, integration:** Mutates global `arcs_cmdline` and uses ARC 32-bit pointer sign extension through `prom_argv()`. It is called from ARC `prom_init()` before generic command-line parsing.

**Risks and test signals:** It uses `strcat()`/`memcpy()` without local bounds checks, relying on boot firmware arguments fitting `COMMAND_LINE_SIZE`. Test with ARC argv containing ignored keys, `OSLoadPartition`, `OSLoadOptions`, empty values, and override ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/cmdline.c -->
