# sources/distributed-fs/ceph-client/include/linux/reset/socfpga.h

Purpose: this tiny header declares the early initialization hook for Altera/Intel SoCFPGA reset support.

Important APIs/types/functions: it declares `void __init socfpga_reset_init(void);` and no other symbols.

Control flow: architecture/platform initialization calls `socfpga_reset_init()` during early boot to set up SoCFPGA reset controller integration.

State and persistence: no state is defined in the header. The implementation initializes platform reset-controller state and hardware mappings.

Dependencies and integration points: integrates with SoCFPGA platform init code and the Linux reset controller framework. It relies on the `__init` annotation being visible to includers.

Risks: calling order matters because reset controllers may be needed by later device probes. Test signals include SoCFPGA boot logs, reset provider registration, and successful consumer reset lookup during device probe.
