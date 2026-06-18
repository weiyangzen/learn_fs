# sources/distributed-fs/ceph-client/drivers/mfd/rz-mtu3.h

### Purpose
`rz-mtu3.h` is the private macro table header used by the RZ/G2L MTU3 MFD parent to define channel-specific register offset arrays. It encodes the irregular 8-bit, 16-bit, and 32-bit register layouts for MTU channels without duplicating index assignments in the C file.

### Important APIs, Types, And Functions
The header defines initializer macros `MTU_8BIT_CH_0`, `MTU_8BIT_CH_1_2`, `MTU_8BIT_CH_3_4_6_7`, `MTU_8BIT_CH_5`, `MTU_8BIT_CH_8`, `MTU_16BIT_CH_0`, `MTU_16BIT_CH_1_2`, `MTU_16BIT_CH_3_6`, `MTU_16BIT_CH_4_7`, `MTU_16BIT_CH_5`, `MTU_32BIT_CH_1`, and `MTU_32BIT_CH_8`. Each macro assigns supplied physical offsets to indices named by public `RZ_MTU3_*` register enums.

### Control Flow
There is no runtime control flow. The macros expand at compile time into sparse-ish initializer lists for `rz_mtu3_8bit_ch_reg_offs`, `rz_mtu3_16bit_ch_reg_offs`, and `rz_mtu3_32bit_ch_reg_offs` in `rz-mtu3.c`.

### State, Persistence, And Dependencies
The header owns no state. Its values become persistent compiled-in mapping data used for all child MMIO accesses. It depends on the public `RZ_MTU3_*` enum/index definitions already visible to the including C file.

### Integration Points
This file is tightly coupled to `rz-mtu3.c` and the public `linux/mfd/rz-mtu3.h` register-index enums. Counter and PWM child behavior indirectly depends on these macros because every exported parent read/write helper resolves logical registers through arrays initialized with them.

### Risks
Any enum-index drift, missing initializer, or wrong offset argument causes silent access to the wrong timer register. The macros do not perform bounds checking, and unsupported registers default to zero-filled entries if accessed incorrectly. Formatting has trailing backslashes on some macro definitions, so edits should be checked carefully by compilation.

### Test Signals
Build tests catch syntax and missing enum names. Runtime tests should compare logical register accesses against the hardware manual for each channel family, especially channels 5 and 8 with distinct layouts, channels 4/7 with ADC trigger registers, and the 32-bit-only mappings.
