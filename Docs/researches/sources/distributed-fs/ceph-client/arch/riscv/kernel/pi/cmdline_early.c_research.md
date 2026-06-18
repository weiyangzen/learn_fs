# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/cmdline_early.c

Purpose: Parses early boot command-line options before normal command-line setup.

Important APIs/types/functions: Defines `early_cmdline`, `get_early_cmdline()`, `set_satp_mode_from_cmdline()`, `set_nokaslr_from_cmdline()`, and matching helpers for `no4lvl`, `no5lvl`, and `nokaslr`.

Control flow: Early code obtains `/chosen/bootargs` from the FDT, copies it into a static buffer, searches for paging mode suppressors or `nokaslr`, and returns SATP mode or KASLR policy decisions to boot setup.

State and persistence: `early_cmdline` is static early storage; decisions persist by influencing page-table mode and KASLR enablement.

Dependencies and integration points: Depends on libfdt-safe early parsing, `pi.h`, FDT physical address from boot, and `head.S`/MM SATP setup.

Risks and test signals: Buffer truncation or parser false positives can select wrong paging mode. Test command lines with `nokaslr`, `no4lvl`, `no5lvl`, long bootargs, missing `/chosen`, and malformed FDTs.
