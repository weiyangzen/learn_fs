<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/cmdline.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/lib/cmdline.c

**Purpose:** Provides generic firmware command-line and environment parsing for non-ARC MIPS bootloaders.

**Important APIs/types/functions:** Globals `fw_argc`, `_fw_argv`, and `_fw_envp` store validated boot data. `fw_init_cmdline()` builds `arcs_cmdline`. `fw_getcmdline()` returns it. `fw_getenv()` supports YAMON name/value pairs and U-Boot name=value strings. `fw_getenvl()` parses an environment variable as `unsigned long`.

**Control flow:** Initialization validates argument and environment pointers against CKSEG0 expectations, then concatenates argv entries 1..argc-1. Environment lookup detects format from the first entry and scans by one or two slots.

**State, dependencies, integration:** Mutates boot command-line globals and relies on `fw_arg0..fw_arg2`. Used by generic board fixups, YAMON DT helpers, and Realtek initrd fixups.

**Risks and test signals:** Pointer validation is heuristic and assumes bootloader conventions. Test U-Boot and YAMON env formats, invalid pointers, large command lines, and numeric conversion failure returning zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/cmdline.c -->
