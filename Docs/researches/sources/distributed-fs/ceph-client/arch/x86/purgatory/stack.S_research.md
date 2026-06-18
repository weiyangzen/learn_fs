<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/stack.S -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/stack.S

## Purpose
Defines the purgatory stack storage.

## Important APIs, Types, And Functions
Exports `stack` and `stack_end` symbols around a fixed-size stack area.

## Control Flow
No executable control flow; entry assembly uses the symbols to initialize stack pointers.

## State And Persistence
The stack is temporary runtime storage while purgatory executes during kexec.

## Dependencies And Integration Points
Consumed by purgatory setup/entry assembly and linked into `purgatory.ro`.

## Risks And Edge Cases
Stack size must be sufficient for SHA verification and handoff code. Incorrect symbol alignment/size would corrupt adjacent purgatory data.

## Test Signals
Successful purgatory execution under kexec and absence of stack corruption indicate correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/stack.S -->
