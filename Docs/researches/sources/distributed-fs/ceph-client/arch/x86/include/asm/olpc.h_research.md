# sources/distributed-fs/ceph-client/arch/x86/include/asm/olpc.h

## Purpose
Declares OLPC XO platform identification, board revision helpers, DCON presence checks, power-management hooks, PCI init, and GPIO assignments.

## Important APIs, Types, And Functions
Defines `struct olpc_platform_t`, flags `OLPC_F_PRESENT` and `OLPC_F_DCON`, `olpc_board()`, `olpc_board_pre()`, `machine_is_olpc()`, `olpc_has_dcon()`, `olpc_board_at_least()`, optional `do_olpc_suspend_lowlevel()`, `olpc_xo1_pm_wakeup_set()`, `olpc_xo1_pm_wakeup_clear()`, `pci_olpc_init()`, and GPIO constants for DCON, SMBus, lid, EC SCI, thermal alarm, and workaux lines.

## Control Flow
Platform detection fills `olpc_platform_info`; inline helpers query flags and board revision. Power-management and PCI setup code calls the declared platform hooks only when configured.

## State And Persistence
State is `olpc_platform_info` and hardware GPIO/PM state. It persists for the running kernel and through suspend as managed by platform code.

## Dependencies And Integration Points
Depends on Geode GPIO helpers. Integrates with OLPC platform setup, DCON display controller driver, GPIO users, PCI quirks, and XO-1 power management.

## Risks And Edge Cases
Board revision comparisons encode OLPC prototype numbering. Incorrect GPIO constants break platform devices. Stubs for non-OLPC builds must keep generic x86 code harmless.

## Test Signals
Boot on XO-1/XO variants, DCON driver probe, lid/EC SCI GPIO interrupts, suspend/resume wakeup, PCI init, and non-OLPC build coverage are useful.
