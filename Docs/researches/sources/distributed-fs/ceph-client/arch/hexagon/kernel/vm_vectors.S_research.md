# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_vectors.S

## Purpose

`vm_vectors.S` defines provisional and real Hexagon VM event vectors. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important labels include `_K_provisional_vec` and `_K_VM_event_vector`, which point VM events at the architecture entry stubs. Concrete declarations observed in the file: Includes: `asm/hexagon_vm.h`. Assembly entry labels: `_K_provisional_vec`, `_K_VM_event_vector`.

## Control Flow, State, And Persistence

Boot flow starts with provisional vectoring and later installs the real vector table used for exceptions, interrupts, trap0, machine check, and debug entry.

## Dependencies And Integration Points

It integrates with HVM vector registers, `head.S`, and `vm_entry.S`.

## Risks And Test Signals

Risks are wrong vector ordering or early exception jumps to unmapped code. Test signals are early boot exceptions, timer IRQ entry, syscall trap, and debug trap tests.
 A local static signal for this file is that it has 36 lines and 628 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
