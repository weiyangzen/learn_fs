# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/bitmap.c

Purpose: supplies minimal bitmap set/clear primitives for EFI stub code that cannot rely on the full kernel bitmap implementation.

Important APIs/types/functions: defines `__bitmap_set()` and `__bitmap_clear()`.

Control flow: both helpers compute the starting word, first-word mask, and total end bit, then iterate whole words applying set or clear masks. The final partial word is masked with `BITMAP_LAST_WORD_MASK()`.

State and persistence behavior: no internal state; mutates caller-provided bitmaps.

Dependencies and integration points: used by EFI stub unaccepted-memory helpers and depends only on lightweight bitmap macros available in the freestanding stub build.

Risks and test signals: off-by-one errors would mark wrong physical ranges accepted/unaccepted. Test signals include bitmap operations crossing word boundaries, zero/partial lengths, and unaccepted-memory boot tests using the stub bitmap implementation.
