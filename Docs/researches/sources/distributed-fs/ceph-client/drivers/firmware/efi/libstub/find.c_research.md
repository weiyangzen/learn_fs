
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/find.c

Purpose: supplies minimal bitmap search helpers for the EFI stub environment where the full kernel library may not be available.

Important APIs/types/functions: exports `_find_next_bit()` and `_find_next_zero_bit()`, both implemented through the local `FIND_NEXT_BIT` macro using word masks, `__ffs()`, and `BITMAP_FIRST_WORD_MASK()`.

Control flow: the macro validates the start bit, masks the first word, scans subsequent bitmap words until a nonzero candidate is found or the size is exhausted, and returns either the found bit index or `nbits`.

State and persistence behavior: no state. The functions only inspect caller-provided bitmap memory.

Dependencies and integration points: depends on Linux bitmap/bitops helpers and is used by stub code such as unaccepted-memory bitmap iteration when linked without full lib support.

Risks and test signals: callers must provide enough bitmap words for `nbits`; the helper assumes native-endian unsigned long bitmaps. Test signals are boundary searches at zero, at the final bit, beyond `nbits`, all-set/all-clear maps, and maps spanning multiple words.
