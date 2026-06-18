# sources/distributed-fs/ceph-client/arch/x86/kvm/tss.h

## Purpose
`tss.h` declares the in-memory layouts KVM's x86 instruction emulator uses when emulating task-state-segment based task switches. It models the architectural 32-bit and 16-bit TSS formats closely enough for the emulator to read and write guest TSS memory while preserving field offsets mandated by the x86 architecture.

## Important APIs, Types, And Functions
The file exports only two structure definitions: `struct tss_segment_32` and `struct tss_segment_16`. The 32-bit layout contains the previous-task link, three privilege stack pairs, `cr3`, saved instruction pointer and flags, general-purpose registers, segment selectors, LDT selector, debug-trap bit, and I/O bitmap offset. The 16-bit layout contains the corresponding 16-bit task link, privilege stacks, saved IP/FLAGS, general registers, segment selectors, and LDT selector. There are no functions, macros, or inline helpers in this header.

## Control Flow
There is no local executable control flow. Runtime behavior is driven by consumers in `arch/x86/kvm/emulate.c`, which allocate these structs on the stack, fetch guest TSS bytes into them, update task-switch state, and write the modified task image back to guest memory. `offsetof(struct tss_segment_32, eip)` and `offsetof(struct tss_segment_32, ldt_selector)` are used by emulator logic, so member order is a hard ABI with the guest architectural format.

## State And Persistence
The structs represent persisted guest architectural state, not host-owned persistent state. KVM copies guest memory into these layouts during emulation and may write modified state back to guest memory. Any padding introduced by the compiler would be risky; the current field sequence uses naturally aligned 32-bit or 16-bit members and relies on the standard C layout matching the architecture.

## Dependencies And Integration Points
The header depends on Linux integer typedefs (`u16`, `u32`) being available through includers. Its main integration point is the x86 emulator task-switch path, including helpers that read/write 16-bit and 32-bit TSS images and validate segment/TSS descriptors.

## Risks And Edge Cases
The largest risk is silent layout drift: changing field type, order, or implicit packing assumptions can corrupt guest task switches. The 32-bit TSS includes an `io_map` offset, while the 16-bit TSS does not; consumers must select the right structure based on descriptor type. Emulation paths also need robust bounds checks when guest memory provides an incomplete TSS or malicious descriptor limit.

## Test Signals
Useful signals are KVM emulator tests for far `JMP`/`CALL`/`IRET` task switches, nested task return, 16-bit protected-mode task switches, privilege-stack loading, LDT selector propagation, debug-trap handling, and failure injection for too-small TSS limits or unreadable guest TSS memory. Build-time offset checks would be valuable if not already covered elsewhere.
