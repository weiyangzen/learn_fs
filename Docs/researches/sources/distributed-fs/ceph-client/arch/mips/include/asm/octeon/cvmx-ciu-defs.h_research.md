# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu-defs.h

## Purpose
This header defines legacy Octeon CIU interrupt, watchdog, timer, reset, mailbox, QLM/JTAG, PCI, and BIST CSRs. It provides address builders and selected bitfield unions for core-local interrupt enables/status and platform control.

## Important APIs, Types, and Functions
`CVMX_CIU_ADDR()` is the base address builder. Macros cover per-core interrupt summaries/enables (`INTX_SUM0`, `INTX_EN0/1`, write-one set/clear variants, `EN2_PPX_IP4`, `SUM2_PPX_IP4`), global interrupt summary, timers, NMI, PCI INTA, reset/BIST/debug, QLM and JTAG controls, and soft reset/PCI reset controls. Inline address helpers `CVMX_CIU_MBOX_CLRX`, `CVMX_CIU_MBOX_SETX`, `CVMX_CIU_PP_POKEX`, and `CVMX_CIU_WDOGX` select family-specific addresses for CN68XX and later CIU layouts. Unions describe QLM tuning, QLM JTAG, soft PCI reset, timer, and watchdog fields.

## Control Flow
Most users compute a CSR address and read/write it. The inline helpers branch on `cvmx_get_octeon_family()` to handle families whose mailbox, poke, and watchdog registers moved. Interrupt code enables sources, reads summaries, acknowledges mailbox/timer/watchdog events, and routes them into MIPS interrupt lines.

## State and Persistence Behavior
CIU CSRs hold interrupt masks, pending summaries, watchdog counters/modes, timer lengths, reset state, and QLM control values. These are hardware persistent until reset or explicit writes. Watchdog and timer state changes can directly reset or interrupt cores.

## Dependencies and Integration Points
It depends on `asm/bitfield.h`, Octeon model/family helpers, and CSR address helpers. It integrates with MIPS interrupt setup, SMP mailbox IPIs, watchdog drivers, platform reset, PCI interrupt wiring, QLM configuration, and low-level board diagnostics.

## Risks
Family-specific address selection is high risk; the wrong CIU path can poke or watchdog the wrong register. Core IDs are masked, so sparse or multi-node numbering must be handled before using legacy CIU macros. Watchdog and reset fields can halt or reset hardware immediately. Interrupt write-one set/clear semantics must not be confused with normal read/modify/write.

## Test Signals
Signals include working timer interrupts, IPIs/mailboxes, watchdog poke/expiry behavior, PCI INTA delivery, reset paths, and no unexpected CIU BIST/debug errors across CN3xxx/CN6xxx/CN7xxx family builds.
