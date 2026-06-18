<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/text-patching.h

## Purpose
Declares the architecture API for writing a single OpenRISC instruction into kernel text or vmalloc text.

## Important APIs, Types, And Functions
`int patch_insn_write(void *addr, u32 insn);` writes a 4-byte instruction and returns an error code.

## Control Flow
Runtime patching users such as jump labels call this API after computing the replacement instruction. The implementation serializes patching and invalidates I-cache over the patched word.

## State And Persistence
No header state. The implementation mutates executable kernel memory until it is patched again or rebooted.

## Dependencies And Integration Points
Depends on Linux integer types and `kernel/patching.c`. Used by `kernel/jump_label.c`.

## Risks
Callers must pass aligned instruction addresses and fully encoded OpenRISC instructions. Incorrect patching can crash all CPUs.

## Test Signals
Jump-label toggling under `CONFIG_JUMP_LABEL`, alignment-error tests, and instruction-cache coherency after patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/text-patching.h -->
