# File Research: sources/cow-pools/bcachefs-tools/ccan/array_size/array_size.h

- Vendored CCAN `ARRAY_SIZE` helper.
- Computes visible array length and, when compiler support exists, rejects pointer arguments using `typeof` and `__builtin_types_compatible_p`.
