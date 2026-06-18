# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc4xx.h

Purpose: This small header declares the PPC4xx platform reset entry point.

Important APIs/types/functions: `ppc4xx_reset_system(char *cmd)` is declared `__noreturn`, indicating the platform reset path does not return to its caller.

Control flow: Board or architecture restart code passes an optional command string to `ppc4xx_reset_system`, which performs the machine reset in platform implementation code.

State and persistence: The function affects persistent machine state by resetting the system. The header owns no data.

Dependencies and integration points: It relies on `__noreturn` being defined by surrounding kernel headers and integrates with PowerPC 4xx reboot/restart machinery.

Risks and test signals: Because the function never returns, callers must not expect cleanup after invocation. Tests are limited to PPC4xx reboot paths, watchdog/reset-controller behavior, and build coverage for configs including this header.
