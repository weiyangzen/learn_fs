
# sources/distributed-fs/openafs/src/util/base64.c

Purpose: `base64.c` provides a compact integer base-64 encoder/decoder for SGI XFS IOPS builds only, guarded by `AFS_SGI_XFS_IOPS_ENV`.

Important APIs: under the guard, `int_to_base64(b64_string_t s, int a)` emits a string using `+`, `,`, digits, uppercase, and lowercase letters. `base64_to_int(char *s)` decodes that alphabet back into an `int`.

Control flow: encoding special-cases zero, handles the top two bits, then emits six-bit groups from the highest nonzero group down. Decoding maps characters before `'0'` relative to `'+'`, digits to 2-11, uppercase to 12-37, and lowercase to 38-63.

State and persistence: static alphabet only; no persistent state.

Dependencies and integration: compiled only for the SGI/XFS environment. `Makefile.in` includes `base64.lo` in RPC utility objects.

Risks: outside the guard no functions are compiled, so prototypes must match platform build choices. Decoder has no validation and includes an unused local pointer. Test signals should compile both guarded and unguarded configurations, round-trip representative values, and reject or document invalid-character behavior.
