# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/prom.h

**Purpose:** Declares Alchemy PROM/bootloader argument and environment access helpers.

**Important APIs/types/functions:** Exports `prom_argc`, `prom_argv`, `prom_envp`, `prom_init_cmdline()`, `prom_getenv(char *envname)`, and `prom_get_ethernet_addr(char *ethernet_addr)`.

**Control flow:** Early boot initializes command line state from PROM arguments, queries environment variables, and extracts Ethernet addresses before platform devices are registered.

**State and persistence behavior:** The extern globals hold bootloader-provided argument/environment pointers. Helper implementations may copy boot data into kernel command line and network configuration. No state is defined in the header.

**Dependencies and integration points:** Integrated by Alchemy prom init, board setup, Ethernet platform data, and early kernel command-line construction.

**Risks:** PROM pointers are early-boot data with architecture-specific lifetime/format assumptions. MAC address parsing must handle missing or malformed environment values. Command-line initialization errors can affect rootfs and console selection.

**Test signals:** Boot with multiple bootloaders, verify kernel command line, environment lookup, MAC address extraction, missing variable behavior, and no invalid early pointer dereferences.
