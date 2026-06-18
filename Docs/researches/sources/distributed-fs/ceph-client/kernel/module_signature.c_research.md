# sources/distributed-fs/ceph-client/kernel/module_signature.c

## Purpose
Validates the fixed trailer metadata of an appended module signature before PKCS#7 verification is attempted.

## Important APIs, Types, And Functions
Defines `mod_check_sig(const struct module_signature *ms, size_t file_len, const char *name)`.

## Control Flow
The helper rejects signatures whose big-endian `sig_len` would consume the whole file, rejects non-PKCS#7 signature types, and rejects any non-zero legacy algorithm/hash/signer/key-id/padding fields. A clean trailer returns 0 so higher-level code can verify the detached PKCS#7 blob.

## State And Persistence
No state is stored. The function only validates a caller-provided `struct module_signature`.

## Dependencies And Integration Points
Depends on `linux/module_signature.h`, byte-order conversion, printk, and callers in `kernel/module/signing.c`.

## Risks And Edge Cases
Trailer arithmetic prevents out-of-bounds signature extraction; mistakes here can cause malformed modules to reach PKCS#7 parsing. The expectation that algo/hash/signer/key-id fields are zero is part of the current module-signing ABI.

## Test Signals
Feed valid trailers, overlong `sig_len`, wrong `id_type`, and non-zero metadata fields. `module_sig_check` should map these to the expected load failures or unsupported-package errors.
