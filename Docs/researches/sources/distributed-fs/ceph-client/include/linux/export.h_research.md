# sources/distributed-fs/ceph-client/include/linux/export.h

Purpose: public source-level macros for exporting kernel symbols to modules.

Important APIs/types/functions: `EXPORT_SYMBOL()`, `EXPORT_SYMBOL_GPL()`, namespace variants, `EXPORT_SYMBOL_FOR_MODULES()`, and internal `__EXPORT_SYMBOL()` variants for assembly, genksyms, GENDWARFKSYMS, and disabled exports.

Control flow: C or assembly files annotate symbols; build macros emit `.export_symbol` records with license, namespace, and symbol reference, or genksyms metadata during symbol version generation. Runtime module loading uses the resulting export tables.

State/persistence: export records persist in kernel/module ELF sections. No runtime mutable state in this header.

Dependencies/integration: compiler addressability, linkage/stringify helpers, genksyms/gendwarfksyms, module loader, namespace enforcement, fixdep rebuild behavior on modversion changes.

Risks/test signals: risks are exporting unintended symbols, namespace/license mismatches, dead-code elimination without `__ADDRESSABLE`, assembly string literal issues, and disabled exports in special build contexts. Test module builds, GPL-only enforcement, namespace import warnings/errors, modversions toggles, and LLVM/GAS assembly handling.
