# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu2-defs.h

## Purpose
This compact header defines CIU2 interrupt-controller CSR addresses for Octeon chips using the second-generation CIU layout. It focuses on per-core IP2/IP3 summary, source, enable, acknowledge, and write-one set/clear registers.

## Important APIs, Types, and Functions
Macros cover IP2 work queue, watchdog, and RML sources/enables; IP3 mailbox enable write-one clear/set; IP2/IP3 acknowledgements; raw work-queue status; per-core summaries; and `CVMX_CIU2_INTR_CIU_READY`. All address macros use `CVMX_ADD_IO_SEG()` and mask `block_id` or offset to 31 cores.

## Control Flow
There is no executable logic. Interrupt code selects a per-core CSR, reads summary/source/raw state, enables or disables bits through direct or W1S/W1C registers, and acknowledges delivered interrupts.

## State and Persistence Behavior
The CIU2 hardware keeps per-core pending, enable, and acknowledgement state. Enable bits persist until changed. Pending state reflects hardware interrupt sources and is cleared through the appropriate acknowledge or source-specific handling.

## Dependencies and Integration Points
It depends on Octeon CSR address mapping. It integrates with the Octeon IRQ driver, POW/work-queue interrupt delivery, watchdog interrupt handling, mailbox/IPI routing, and RML error/status interrupts.

## Risks
The register map is per-core and heavily offset-based; using the wrong `block_id` targets a different core. W1C/W1S register pairs must be used instead of unsafe read/modify/write under interrupt concurrency. The file provides addresses only, so callers must know the correct bit assignments from hardware context.

## Test Signals
Runtime signals include correct IP2/IP3 interrupt routing on CIU2 systems, mailbox IPI delivery, watchdog interrupt handling, work-queue interrupts, and clean enable/disable behavior with no stuck pending bits.
