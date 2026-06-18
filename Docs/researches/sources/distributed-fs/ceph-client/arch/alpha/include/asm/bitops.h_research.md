# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/bitops.h

This header provides Alpha atomic and non-atomic bit operations plus bit-scan and hweight helpers. Atomic setters/clearers/changers use 32-bit `ldl_l/stl_c` loops over the addressed word; test-and operations return whether the bit was previously set and insert SMP barriers around lock-like operations.

Important APIs include `set_bit`, `clear_bit`, `clear_bit_unlock`, `change_bit`, `test_and_set_bit`, `test_and_set_bit_lock`, `test_and_clear_bit`, `test_and_change_bit`, non-atomic `arch___*` variants, `xor_unlock_is_negative_byte`, `ffz`, `__ffs`, `ffs`, `fls64`, `__fls`, `fls`, hweight hooks, and `sched_find_first_bit`. EV67-capable builds use CIX helpers such as `__kernel_cttz`, `__kernel_ctlz`, and `__kernel_ctpop`; older CPUs use byte-compare/extract sequences and `__flsm1_tab`.

State is the target bitmap word. Dependencies are `asm/compiler.h`, barriers, and generic bitops includes for little-endian/ext2/non-instrumented helpers. Risks include 32-bit word addressing of bitmaps on a 64-bit architecture, missing barriers for lock/unlock semantics, and CPU feature ifdefs that must match compiler flags. Tests should exercise lock bitops, bitmap scans, scheduler bitmap selection, and EV6/EV67 versus generic builds.
