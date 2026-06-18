# sources/distributed-fs/ceph-client/arch/sh/kernel/sh_ksyms_32.c

Purpose: exports 32-bit SH low-level symbols needed by modules.

Important APIs and control flow: the file exports common memory/string routines, user copy/clear helpers, delay routines, checksumming, page copy, flatmem PFN bounds, and compiler/libgcc arithmetic helper symbols declared through `DECLARE_EXPORT()`.

State, dependencies, and risks: no runtime state beyond the module symbol table. Dependencies are assembly/compiler helper implementations elsewhere and module ABI expectations. Risks include missing exports causing module link failures, over-exporting internal helpers, or config-dependent PFN symbol availability. Test signals are building/loading modules that use memcpy/checksum/delay/division helpers and modpost unresolved-symbol checks.
