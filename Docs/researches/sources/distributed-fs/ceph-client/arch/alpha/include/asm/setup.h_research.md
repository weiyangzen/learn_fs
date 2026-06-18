<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/setup.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/setup.h

**Purpose:** Defines Alpha boot-time physical layout, kernel start addresses, initial page-table pages, command-line/initrd handoff locations, and bootstrap constants.

**Important APIs/types/functions:** `BOOT_PCB`, `BOOT_ADDR`, `BOOT_SIZE`, `KERNEL_START_PHYS`, `KERNEL_START`, `SWAPPER_PGD`, `INIT_STACK`, `EMPTY_PGT`, `EMPTY_PGE`, `ZERO_PGE`, `START_ADDR`, `PARAM`, `COMMAND_LINE`, `INITRD_START`, and `INITRD_SIZE`.

**Control flow:** Early boot and linker/setup code use fixed offsets from `PAGE_OFFSET + KERNEL_START_PHYS`; after VM init the zero page is reclaimed, so command line and initrd values must be copied out.

**State and persistence behavior:** Defines boot memory contract rather than mutable state. Command line and initrd values originate from the secondary bootstrap loader.

**Dependencies and integration points:** Depends on `uapi/asm/setup.h`, page constants, `CONFIG_ALPHA_LEGACY_START_ADDRESS`, MILO/SRM boot conventions, and early MM setup.

**Risks:** Wrong start address breaks older bootloaders or large systems like Wildfire/Titan/Marvel. Zero-page handoff data must be consumed before reclaim.

**Test signals:** Boot with legacy and modern start-address configs, pass command-line/initrd, and validate early page-table addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/setup.h -->
