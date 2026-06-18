
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_booke.h

## Purpose
Defines BookE-specific KVM tracepoints and symbolic decoders for exits, BookE 2.06 TLB operations, reference release, and queued interrupt priorities.

## Important APIs, Types, And Functions
Events are `kvm_exit`, `kvm_booke206_stlb_write`, `kvm_booke206_gtlb_write`, `kvm_booke206_ref_release`, and `kvm_booke_queue_irqprio`. Symbol macros include `kvm_trace_symbol_exit`, optional SPE/e500mc IRQ priority mappings, and `kvm_trace_symbol_irqprio`.

## Control Flow
Callers in e500 MMU and BookE interrupt code emit generated trace functions. `kvm_exit` snapshots PC, MSR, DAR, and last instruction from the vCPU. TLB events record MAS fields or PFN/flags. IRQ priority tracing records vCPU ID, priority, and pending exception bitmap.

## State And Persistence
No owned state. Trace events carry snapshots of vCPU and TLB metadata into the kernel tracing subsystem.

## Dependencies And Integration Points
Depends on BookE KVM structures/macros, optional `CONFIG_SPE_POSSIBLE` and `CONFIG_PPC_E500MC`, and Linux tracepoint infrastructure. It is included by e500 MMU and BookE backend code.

## Risks
The event name `kvm_exit` overlaps with PR trace headers under different `TRACE_SYSTEM` values, so trace tooling must select the correct system (`kvm_booke`). Optional symbol mappings must match configured interrupt priorities. MAS fields are architecture-specific and require consumers to know BookE encodings.

## Test Signals
Enable `kvm_booke:*` tracepoints while running e500 guests. TLB write/release events should appear during TLB misses and invalidations; queue IRQ priority events should appear when BookE exceptions are queued.
