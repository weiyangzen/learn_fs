<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.h

Purpose: small header for stdio console support.

Important APIs/types/functions: declares `save_console_flags()`.

Control flow: no executable flow exists in this header. In the researched subset the declaration is not implemented or used by `stdio_console.c`, suggesting it is legacy or used by other UML files outside this work item.

State and persistence: no state is defined.

Dependencies and integration points: guarded by `__STDIO_CONSOLE_H`. It can be included by code that wants to preserve console flags across UML startup.

Risks: stale declarations can mislead maintainers. Before removal, search the whole UML tree for users because this subset may not contain all call sites.

Test signals: full UML build with warnings enabled and tree-wide symbol search for `save_console_flags`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.h -->
