<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-realtek.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-realtek.c

**Purpose:** Adds generic Realtek RTL9302 MIPS board FDT fixups, especially initrd location from firmware environment.

**Important APIs/types/functions:** `realtek_add_initrd()` reads `initrd_start` and `initrd_size` via `fw_getenvl()` and writes `/chosen` `linux,initrd-start/end`. `realtek_fixup_fdt()` validates and copies/fixes the FDT. `MIPS_MACHINE(realtek)` matches `realtek,rtl9302-soc`.

**Control flow:** Fixup initializes command line, applies a small list of FDT fixups into a static 16 KiB buffer, and returns the new FDT.

**State, dependencies, integration:** Depends on generic firmware env parsing, libfdt mutation, and generic machine fixup infrastructure.

**Risks and test signals:** The fixed FDT buffer can overflow if source DT grows beyond 16 KiB with fixups. Zero start and size suppress initrd. Test missing `/chosen`, no initrd env, valid initrd env, malformed FDT, and buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-realtek.c -->
