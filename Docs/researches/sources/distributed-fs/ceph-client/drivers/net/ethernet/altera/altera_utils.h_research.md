# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_utils.h

Purpose: this header declares the Altera TSE register bit helper functions implemented in `altera_utils.c`.

Important APIs, types, and functions: it declares `tse_set_bit()`, `tse_clear_bit()`, `tse_bit_is_set()`, and `tse_bit_is_clear()`, all taking an MMIO base, register offset, and bit mask. The header includes Linux compiler and type definitions so callers can use `void __iomem`, `size_t`, and `u32`.

Control flow: the header has no runtime flow. Including C files call the declared helpers to update MAC and DMA-related registers.

State and persistence: no state is defined here. State changes happen in hardware when the implementation functions are called.

Dependencies and integration points: it is included by `altera_tse_main.c` and `altera_utils.c`. Its include guard is `__ALTERA_UTILS_H__`.

Risks: because the helpers perform unlocked read-modify-write operations, the header contract should remain clear that locking is a caller responsibility. Signature drift would affect every MAC configuration call site.

Test signals: build coverage is sufficient for declaration consistency; runtime tests are the same bit-level MAC reset/configuration/link-mode paths that exercise `altera_utils.c`.
