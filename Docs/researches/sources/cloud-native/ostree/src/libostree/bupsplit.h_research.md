# sources/cloud-native/ostree/src/libostree/bupsplit.h

Purpose: This header declares the bupsplit rolling-checksum API and its chunk/window sizing constants.

Important APIs, types, and functions: It defines `BUP_BLOBBITS` as 13, `BUP_BLOBSIZE` as `1 << BUP_BLOBBITS`, `BUP_WINDOWBITS` as 7, and `BUP_WINDOWSIZE` as `1 << (BUP_WINDOWBITS - 1)`. It declares `uint32_t bupsplit_sum(uint8_t *buf, size_t ofs, size_t len)` and `int bupsplit_find_ofs(const unsigned char *buf, int len, int *bits)` inside an `extern "C"` block for C++ callers.

Control flow: No executable flow beyond preprocessor include guards and C++ linkage guards.

State and persistence behavior: None. Constants define deterministic algorithm parameters used by `bupsplit.c`.

Dependencies and integration points: Includes `<stdint.h>` and `<sys/types.h>`. Included by `bupsplit.c` and any libostree code that needs chunk boundary detection.

Risks: Changing constants changes chunk boundaries and can affect delta size, compatibility, and performance. The API exposes mutable `uint8_t *` for `bupsplit_sum` even though implementation only reads, which may limit const-correctness.

Test signals: Consumers should test against known chunk offsets and sums; no direct signal in this subset.
