# sources/distributed-fs/ceph-client/include/linux/export-internal.h

Purpose: internal macros for modpost-generated C files to emit kernel symbol table, CRC, and flag records.

Important APIs/types/functions: relocation-aware `__KSYM_ALIGN`, `__KSYM_REF()`, `__KSYMTAB()`, `KSYM_FUNC()`, `KSYMTAB_FUNC()`, `KSYMTAB_DATA()`, `SYMBOL_CRC()`, and `SYMBOL_FLAGS()`.

Control flow: generated files expand these macros into inline assembly sections: symbol/name/namespace strings, `___ksymtab+name` entries, `___kcrctab+sym` CRCs, and `___kflagstab+sym` flags. PREL32 relocations are used when supported to reduce relocations/size.

State/persistence: export metadata persists in the linked kernel/module image and is used by module loader/modpost.

Dependencies/integration: modpost, linker sections, module loader, genksyms/versioning, architecture relocation support, parisc function descriptors.

Risks/test signals: risks are section syntax incompatibility, wrong relative relocation computation, namespace string mismatch, CRC endian/size issues, and direct inclusion by normal code. Test module symbol resolution, modversions, namespace imports, PREL32 and non-PREL32 architectures, and `readelf` section contents.
