# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/generic.h

Purpose: Shared constants for MIPS Technologies evaluation boards, including display registers, revision IDs, system-controller IDs, and PCI BIOS setup hook.

Important APIs/types/functions: Defines `ASCII_DISPLAY_WORD_BASE`, `ASCII_DISPLAY_POS_BASE`, `MIPS_REVISION_REG`, many `MIPS_REVISION_CORID_*` values, artificial `CORE_EMUL_*` IDs, `MIPS_REVISION_CORID`, system-controller IDs such as `MIPS_REVISION_SCON_SOCITSC`, negative legacy SCON values, and `MIPS_REVISION_SCONID`. Declares `mips_revision_sconid`. If `CONFIG_PCI` is set, declares `mips_pcibios_init()`, otherwise defines it as a no-op.

Control flow, state, and persistence: `MIPS_REVISION_CORID` and `MIPS_REVISION_SCONID` map and dereference the revision register through `ioremap` macro expressions. Persistent board identity is in hardware revision registers and cached in `mips_revision_sconid`.

Dependencies and integration: Includes address-space, byte-order, and Bonito definitions. It integrates with Malta/SEAD board setup, PCI host selection, and early display/debug output.

Risks and test signals: Macros that call `ioremap` inside expressions can leak mappings or be unsafe if used repeatedly. Test by booting multiple board controller variants and checking revision/controller detection and PCI init selection.
