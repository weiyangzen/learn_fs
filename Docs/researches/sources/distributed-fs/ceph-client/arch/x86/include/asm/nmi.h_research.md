# sources/distributed-fs/ceph-client/arch/x86/include/asm/nmi.h

## Purpose
Declares x86 NMI handler registration, NMI source types, panic policy globals, perf counter reservation hooks, and NMI stop/restart helpers.

## Important APIs, Types, And Functions
Defines NMI types `NMI_LOCAL`, `NMI_UNKNOWN`, `NMI_SERR`, `NMI_IO_CHECK`, `NMI_MAX`, return values `NMI_DONE` and `NMI_HANDLED`, `NMI_FLAG_FIRST`, `nmi_handler_t`, `struct nmiaction`, `register_nmi_handler()`, `__register_nmi_handler()`, `unregister_nmi_handler()`, `set_emergency_nmi_handler()`, `stop_nmi()`, `restart_nmi()`, `local_touch_nmi()`, panic policy globals, and local-APIC perf counter reservation helpers.

## Control Flow
Handlers are registered as static `struct nmiaction` objects and linked into per-type lists. The NMI dispatcher invokes handlers by type, with first handlers prioritized. Unknown NMIs can be offered to fallback handlers.

## State And Persistence
State is in-memory handler lists, panic policy globals, perf NMI reservations, and emergency handler pointers. It persists while the kernel runs.

## Dependencies And Integration Points
Depends on irq work, PM, IRQ definitions, I/O, local APIC, perf, watchdog, and machine-check/trap code.

## Risks And Edge Cases
NMI handlers run in non-maskable context and must be minimal. Registration names are used for removal. Panic policy changes can make hardware noise fatal. Perf reservations must avoid counter conflicts.

## Test Signals
NMI watchdog tests, perf NMI reservation tests, unknown NMI injection, SERR/IOCHK paths, panic policy sysctl tests, and stop/restart NMI coverage are useful.
