# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu3-defs.h

## Purpose
This header defines the CIU3 interrupt-controller register map used by newer Octeon platforms. It models interrupt source control, interrupt destination tables, per-destination pending interrupts, NMI, timers, ECC status, BIST, constants, and global stop/control registers.

## Important APIs, Types, and Functions
Address macros include global control/status (`FUSE`, `BIST`, `CONST`, `CTL`, `GSTOP`, `NMI`), destination registers (`DESTX_PP_INT`, `DESTX_IO_INT`), interrupt destination table entries (`IDTX_CTL`, `IDTX_IO`, `IDTX_PPX`), interrupt source controls (`ISCX_CTL`, `ISCX_W1C`, `ISCX_W1S`), summary interrupt enables (`SISCX`), timers (`TIMX`), ECC control/status, readiness, and slowdown. Unions expose fields for IDT size/destination counts, source enable/raw/IDT mapping, destination pending/new interrupt flags, PP and IO destination masks, ECC syndrome injection and SBE/DBE status, NMI masks, and timer length/one-shot mode.

## Control Flow
The file itself has no code. IRQ setup writes IDT mappings, points sources at IDT entries, enables sources, then interrupt handlers read destination pending registers and source status, clearing or setting bits through W1C/W1S CSRs as needed.

## State and Persistence Behavior
CIU3 hardware stores interrupt routing tables, source enable/raw state, per-destination pending state, timer state, ECC error status, and NMI masks. This state persists until changed or reset. ECC status can latch memory errors and must be cleared according to hardware semantics.

## Dependencies and Integration Points
It depends on Octeon CSR address helpers and endian bitfield layout. It integrates with the Octeon interrupt controller driver, SMP/NMI handling, per-core timers, IO interrupt routing, ECC reporting, and platform discovery through `CONST`.

## Risks
CIU3 exposes very large indexed spaces (`ISCX` up to 20-bit source indices), making off-by-one or wrong-source programming dangerous. IDT and destination fields are topology-sensitive; incorrect PP/IO masks can misroute or lose interrupts. ECC injection fields must be kept out of production paths. W1C/W1S use is mandatory for concurrent interrupt updates.

## Test Signals
Signals include correct IRQ routing to CPUs and IO destinations, functioning per-core timers, NMI delivery, source enable/disable tests, ECC status reporting/injection tests where safe, and no stuck `newint`/`intr` destination bits under interrupt load.
