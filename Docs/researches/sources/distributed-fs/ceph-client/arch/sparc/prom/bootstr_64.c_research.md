# sources/distributed-fs/ceph-client/arch/sparc/prom/bootstr_64.c

Purpose: retrieves SPARC64 boot arguments from SILO-provided data or IEEE-1275 `/chosen` bootargs.

Important APIs/types/functions: defines `bootstr_info` containing `bootstr_len`, `bootstr_valid`, and a 1024-byte buffer, and exposes `prom_getbootargs()`.

Control flow: if `bootstr_valid` is already set, including via `CONFIG_CMDLINE` or bootloader-filled data, the cached buffer is returned. Otherwise the function reads `/chosen` property `bootargs` through `prom_getstring()`, marks the buffer valid, and returns it.

State and persistence: command line is cached in `bootstr_info`. Placement in `.data` is ABI-visible to the boot loader and must not move to `.bss`.

Dependencies and integration points: depends on `prom_chosen_node`, PROM property access, SILO bootloader expectations, and generic kernel command-line setup.

Risks: moving or reordering `bootstr_info` fields breaks bootloader patching. Long bootargs beyond 1024 bytes are truncated by design.

Test signals: boot with SILO-provided args, `CONFIG_CMDLINE`, and raw PROM `/chosen/bootargs`; verify repeated calls and command-line truncation behavior.
