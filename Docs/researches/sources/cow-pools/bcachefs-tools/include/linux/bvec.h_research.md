# File Research: sources/cow-pools/bcachefs-tools/include/linux/bvec.h

Purpose: block vector and iterator shim.

Key contents:
- Defines `struct bio_vec` with virtual address and length.
- Defines `struct bvec_iter` with sector, residual size, index, and completed bytes.
- Defines `struct bvec_iter_all`.
- Provides bvec virtual address, current address/length, current bvec construction, and iterator advancement helpers.
- Defines `for_each_bvec()` iterator macro.

Important interactions:
- Used by `bio.h` and I/O paths to walk memory vectors.
- This userspace version stores virtual addresses directly rather than kernel pages.
