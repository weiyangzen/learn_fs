<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/cmdline.c -->
# sources/distributed-fs/ceph-client/arch/x86/virt/svm/cmdline.c

## Purpose
`cmdline.c` parses the `sev=` kernel command-line options for AMD SEV/SNP host support.

## Important APIs, types, and functions
It defines global `sev_cfg`, `init_sev_config()`, and the `__setup("sev=", ...)` hook. Recognized options are `debug` and `nosnp` outside hypervisor guests.

## Control flow
Boot parsing splits the option string by comma, sets debug mode, or clears SNP CPU/platform capabilities for `nosnp` on bare metal. Unknown or disallowed options log an informational warning.

## State and persistence behavior
Persistent state is `sev_cfg.debug` and CPU/platform capability bits modified during boot.

## Dependencies and integration points
It depends on `asm/sev-common.h`, CPU feature helpers, confidential-computing platform attributes, and command-line setup infrastructure.

## Risks and edge cases
`nosnp` is deliberately ignored under a hypervisor, so deployment assumptions must account for guest context. Unknown tokens are nonfatal.

## Test signals
Signals are boot logs for `sev=debug`, `sev=nosnp`, and unknown options, plus SNP capability visibility after parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/cmdline.c -->
