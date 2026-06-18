<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/access-helper.h -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/access-helper.h

### Purpose
`access-helper.h` centralizes safe reads of addresses and instructions from either user memory or kernel memory for instruction decoding paths.

### Important APIs, Types, And Functions
It provides inline helpers `__get_addr()`, `__get_inst16()`, and `__get_inst32()`. Each accepts an output pointer, source pointer, and `user` boolean.

### Control Flow
Each helper branches on `user`: user accesses call `get_user()`, while kernel accesses call `get_kernel_nofault()`. Errors propagate as the underlying helper return value.

### State, Persistence, And Dependencies
There is no retained state. It depends on `linux/uaccess.h` and on callers treating failed reads as fault conditions.

### Integration Points
Branch emulation, uprobes/kprobes, unaligned access handling, or other instruction-reading code can use this header to avoid open-coding user-versus-kernel access.

### Risks
Callers must pass correctly typed pointers and must not ignore faults. Instruction endianness and ISA mode interpretation are outside this helper, so it only solves safe access.

### Test Signals
Unit-style tests for user valid/invalid addresses, kernel nofault reads, 16-bit and 32-bit instruction fetches, and fault propagation in branch/probe paths are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/access-helper.h -->
