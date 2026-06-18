## sources/distributed-fs/ceph-client/arch/mips/kvm/interrupt.c

Purpose: Delivers queued MIPS KVM virtual exceptions/interrupts to callback-provided IRQ injection logic.

Important APIs, types, and functions: `kvm_mips_deliver_interrupts()` walks `vcpu->arch.pending_exceptions_clr` and `pending_exceptions` and invokes `kvm_mips_callbacks->irq_clear()` or `irq_deliver()` for each set priority. `kvm_mips_pending_timer()` checks the timer exception bit.

Control flow: Clear requests are processed before delivery requests, preserving a deterministic priority pass through bit order. Each bit index corresponds to exception priorities defined in `interrupt.h`.

State and persistence: Uses per-VCPU bitmaps `pending_exceptions` and `pending_exceptions_clr`. The actual IRQ line state is delegated to the active KVM MIPS callback implementation.

Dependencies and integration points: Depends on `interrupt.h`, `kvm_mips_callbacks`, and exit handling in `mips.c`, which calls delivery before re-entering the guest.

Risks: The function does not clear bits itself; callback implementations must manage bitmap state correctly. Priority definitions and callback IRQ mappings must stay in sync.

Test signals: Timer, IO, and IPI queue/dequeue paths; simultaneous clear and deliver bits; Loongson priority mapping; re-entry delivery after guest exits.
