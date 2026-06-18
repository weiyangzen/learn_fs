## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/hvcall.S

### Purpose
`hvcall.S` generates low-level PS3 LV1 hypercall wrapper functions that marshal input/output registers according to the shared LV1 call table.

### Important APIs, Types, And Functions
The file defines the `lv1call` instruction sequence and macro families such as `LV1_0_IN_1_OUT`, `LV1_1_IN_4_OUT`, `LV1_6_IN_3_OUT`, `LV1_7_IN_6_OUT`, and `LV1_8_IN_1_OUT`. Including `<asm/lv1call.h>` expands `_lv1_<name>` global functions.

### Control Flow
Each wrapper saves LR, may spill output pointer arguments to the caller stack frame or red-zone area, loads the LV1 API number into r11, executes the hypervisor call opcode, sign-extends the return code in r3, restores the stack, writes output registers r4+ into caller-provided pointers, restores LR, and returns.

### State, Persistence, And Dependencies
There is no persistent state; the wrappers obey the PPC64 ABI stack and register convention. Dependencies include the exact LV1 call ABI, `STACK_FRAME_MIN_SIZE`, `LRSAVE`, and the LV1 call manifest.

### Integration Points
All PS3 platform C code calls `_lv1_*` wrappers directly or through inline macros, and `exports.c` exports the same symbols for modules.

### Risks
Any macro with the wrong input/output arity corrupts stack slots or output pointers. The 6+ argument variants rely on correct stack parameter offsets. Return sign extension must match LV1 negative error codes.

### Test Signals
Assembly build, objdump inspection of representative wrappers, boot-time LV1 calls, module link tests, and runtime hypercall error propagation validate it.
