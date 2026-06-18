# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/posted_intr.h

## Purpose
Declares the posted interrupt API for VMX and provides a small bitmap helper for selecting the highest pending posted interrupt vector.

## Important APIs, Types, And Functions
The header declares load/put hooks, the wakeup handler, CPU initialization, APICv restore cleanup, pending interrupt query, VT-d IRTE update, and bypass-start notification. `pi_find_highest_vector()` uses `find_last_bit()` over the 256-bit PIR bitmap and returns `-1` when no vector is pending.

## Control Flow
VMX vCPU scheduling and interrupt code call these prototypes without depending on the implementation internals. `pi_find_highest_vector()` is synchronous and only interprets the current PIR bitmap; it does not clear bits or update descriptor control.

## State And Persistence
This header owns no storage. It describes operations over `struct pi_desc`, `struct kvm_vcpu`, `struct kvm`, and irqfd state managed by the implementation and by architecture code.

## Dependencies And Integration Points
Includes Linux bitmap/find/KVM host headers and `asm/posted_intr.h`. The declarations are consumed by VMX vCPU lifecycle, APICv, interrupt injection, irq bypass, and TDX code.

## Risks
The helper assumes a 256-vector PIR layout. Callers must handle synchronization around PIR mutation and descriptor ON/SN state; this header intentionally does not impose locking.

## Test Signals
Build coverage, APICv delivery tests, highest-vector selection checks, and irqfd posted-interrupt passthrough cover the interface.
