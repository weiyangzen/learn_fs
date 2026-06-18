## sources/distributed-fs/ceph-client/arch/mips/alchemy/common/vss.c

Purpose: controls Au1300 media block power gating through VSS gate, clock/reset, and footer registers. The file is a temporary explicit power-management hook until the clock framework can own these transitions transparently.

Important APIs and functions: `au1300_vss_block_control(int block, int enable)` is exported. Internally `__enable_block()` and `__disable_block()` implement the databook-defined sequence for one block at a time. `VSS_ADDR(blk)` maps a block number to KSEG1 MMIO under `AU1300_VSS_PHYS_ADDR`.

Control flow: the public function returns immediately for non-Au1300 CPUs. On Au1300 it acquires `au1300_vss_lock`, then either enables the clock while reset is asserted, programs maximum gate setup time, enables footers in stages, starts the FSM, deasserts reset, and enables isolation cells; or reverses the process by disabling isolation cells, stopping the FSM, asserting reset, disabling clock, and clearing footers.

State and persistence: state is entirely in VSS hardware registers. The lock is static runtime state used for serialization; it is not persistent.

Dependencies and integration: depends on Alchemy CPU detection and raw MMIO access. Media drivers or platform code can call the exported symbol to power media blocks.

Risks: the sequence is order-sensitive and uses raw writes plus barriers without status polling, so incorrect block IDs or undocumented timing differences can leave a block inaccessible. The API silently no-ops on non-Au1300, which is convenient but can hide misrouted callers. There is no range validation for `block`.

Test signals: media block probe/use should succeed only after enabling the block. Suspend/resume or repeated enable/disable cycles should not wedge clocks or trigger bus errors. Kernel logs are absent, so tests must observe device behavior or register state.
