## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-extable.h

### Purpose
Defines ARM64 assembly and inline-asm exception table record macros for uaccess, kaccess, BPF, copy, and unaligned zeropad fixups.

### Important APIs, Types, And Functions
Defines exception types `EX_TYPE_NONE`, `EX_TYPE_BPF`, `EX_TYPE_UACCESS_ERR_ZERO`, `EX_TYPE_KACCESS_ERR_ZERO`, `EX_TYPE_UACCESS_CPY`, and `EX_TYPE_LOAD_UNALIGNED_ZEROPAD`; data bitfields such as `EX_DATA_REG_ERR`, `EX_DATA_REG_ZERO`, and `EX_DATA_UACCESS_WRITE`; and macros `_ASM_EXTABLE_UACCESS*`, `_ASM_EXTABLE_KACCESS*`, `_ASM_EXTABLE_LOAD_UNALIGNED_ZEROPAD`, plus assembler helpers `_asm_extable_uaccess`, `_cond_uaccess_extable`, and `_asm_extable_uaccess_cpy`.

### Control Flow
Fault-prone instructions emit records into `__ex_table` with relative instruction/fixup offsets, type, and packed data. The runtime exception handler uses those records to branch to fixups, zero registers, set error registers, or complete copy semantics.

### State, Persistence, And Dependencies
The header emits static exception table metadata; no writable state. Dependencies include bit masks and GPR number macros, plus stringify support in C inline-asm mode.

### Integration Points
Used by uaccess assembly, copy routines, BPF JIT helpers, zeropad loads, and kernel access fixups.

### Risks
Incorrect register encoding, type values, or relative offsets will mis-handle faults and can create kernel memory disclosure or usercopy corruption. Inline-asm and assembler macro variants must stay equivalent.

### Test Signals
Run usercopy fault injection, KASAN/KFENCE invalid-user-pointer tests, BPF fault tests, unaligned zeropad tests, and objdump validation of `__ex_table` records.
