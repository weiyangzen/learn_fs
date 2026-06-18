# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-extable.h

## Purpose

`asm-extable.h` defines LoongArch assembly exception-table encodings and helpers for normal fixups, uaccess err/zero fixups, and BPF fixups. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important APIs include `EX_TYPE_*`, `__ASM_EXTABLE_RAW`, `_ASM_EXTABLE`, `_ASM_EXTABLE_UACCESS_ERR_ZERO`, and packed `EX_DATA_REG` fields. Concrete declarations observed in the file: Includes: `linux/bits.h`, `linux/stringify.h`, `asm/gpr-num.h`. Macros: `__ASM_ASM_EXTABLE_H`, `EX_TYPE_NONE`, `EX_TYPE_FIXUP`, `EX_TYPE_UACCESS_ERR_ZERO`, `EX_TYPE_BPF`, `__ASM_EXTABLE_RAW`, `_ASM_EXTABLE`, `EX_DATA_REG_ERR_SHIFT`, `EX_DATA_REG_ERR`, `EX_DATA_REG_ZERO_SHIFT`, `EX_DATA_REG_ZERO`, `EX_DATA_REG`, `_ASM_EXTABLE_UACCESS_ERR_ZERO`, `_ASM_EXTABLE_UACCESS_ERR`.

## Control Flow, State, And Persistence

No direct runtime flow; macros emit exception-table records consumed by the exception fixup engine during faults.

## Dependencies And Integration Points

It integrates with uaccess assembly, BPF JIT/exception paths, linker exception-table sorting, and fault handlers.

## Risks And Test Signals

Risks are wrong relative/absolute encoding, invalid register packing, and broken uaccess residual/error handling. Test signals are uaccess fault tests, BPF probe tests, and exception-table objdump inspection.
 A local static signal for this file is that it has 66 lines and 1717 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
