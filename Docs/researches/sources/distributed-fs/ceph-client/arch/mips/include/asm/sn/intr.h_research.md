<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/intr.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/intr.h

Purpose: Defines SGI SN hub interrupt send/clear macros and reserved interrupt level assignments for IP27/SN0.

Important APIs/types/functions: `LOCAL_HUB_SEND_INTR`, `REMOTE_HUB_SEND_INTR`, `LOCAL_HUB_CLR_INTR`, `REMOTE_HUB_CLR_INTR`, and interrupt numbers for UART, cross-calls, reschedule/call IPIs, bridge/IO errors, debug, clock, correction, NI, and panic events.

Control flow: Interrupt code writes hub PI pending set/clear registers using per-level bit shifts to raise or clear local or remote interrupts. The numeric constants reserve levels used by PROM, kernel, and platform devices.

State and persistence: State is hub interrupt pending/mask registers and assigned interrupt vector namespace. Macros directly mutate MMIO pending state.

Dependencies and integration points: Relies on hub address access macros and PI register offsets. Integrated by SN interrupt controller, SMP IPI, UART, error, and debug handlers.

Risks: Interrupt levels are shared ABI between PROM and kernel. Wrong level writes can disturb reserved PROM/debug or error interrupts.

Test signals: IPI tests, timer/UART interrupt delivery, error interrupt injection, and SN boot interrupt-controller initialization are useful.

Source read size: 112 lines, 2663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/intr.h -->
