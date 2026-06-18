# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx-shared.c

Purpose: includes shared TDX hypercall support into the compressed kernel.

Important APIs and state: the file itself only includes `error.h` and `../../coco/tdx/tdx-shared.c`; symbols such as `__tdx_hypercall()` are provided by the included shared implementation.

Control flow: include-only; runtime behavior belongs to the shared TDX implementation.

Dependencies and integration: links the decompressor TDX I/O overrides in `tdx.c` with common TDX module call helpers and failure handling.

Risks and test signals: failures in this glue surface as early TDX boot failures or inability to use TDVMCALL for I/O. Build and boot TDX guests with early serial output enabled and exercise `early_tdx_detect()` path.
