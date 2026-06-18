# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/bits.h

Purpose: supplies HRT bit-mask and bitfield helper macros for fixed-width register packing.

Important APIs/types/functions: `_hrt_ones(n)` maps constants 0 through 32 to masks, and helpers `_hrt_mask()`, `_hrt_get_bits()`, `_hrt_set_bits()`, `_hrt_get_bit()`, `_hrt_set_bit()`, `_hrt_set_lower_half()`, and `_hrt_set_upper_half()` build on those masks.

Control flow: all behavior is macro expansion. The macros compute masks, extract shifted fields, and update ranges inside a word.

State and persistence: no state. Effects occur only in expressions evaluated by callers.

Dependencies and integration: depends on Linux `CONCATENATE()` from `<linux/args.h>`. Used by atomisp HRT-generated register configuration code.

Risks and test signals: `_hrt_ones(n)` only works for compile-time tokens with defined mappings. Shift behavior depends on integer width, and `_hrt_set_bit()` uses `1 << b` rather than an unsigned wider literal. Tests are compile-time coverage of generated users and runtime bitfield examples for boundary widths 0, 1, 16, 31, and 32.
