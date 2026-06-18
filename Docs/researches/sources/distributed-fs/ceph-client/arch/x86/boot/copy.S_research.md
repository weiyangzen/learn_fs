# sources/distributed-fs/ceph-client/arch/x86/boot/copy.S

Purpose: provides 16-bit setup-code memory copy and fill routines plus segment-aware copies to/from `%fs`.

Important APIs and state: defines `memcpy`, `memset`, `copy_from_fs`, and `copy_to_fs` as 16-bit callable routines using `retl`. They operate on registers following the setup-code convention rather than normal C ABI details.

Control flow: `memcpy` copies dwords then bytes using `rep movsl/movsb`; `memset` expands a byte to a 32-bit pattern and stores dwords then bytes. `copy_from_fs` temporarily loads `%fs` into `%ds`; `copy_to_fs` temporarily loads `%fs` into `%es`, then delegates to `memcpy`.

Dependencies and integration: used by real-mode boot C code for BIOS data areas and video memory access through `set_fs()`, `rdfs*`, and screen save/restore logic.

Risks and test signals: segment register save/restore mistakes corrupt later BIOS calls or screen memory. Test by booting through video mode selection, EDD/BIOS probing, and screen restore paths that exercise `%fs` copies.
