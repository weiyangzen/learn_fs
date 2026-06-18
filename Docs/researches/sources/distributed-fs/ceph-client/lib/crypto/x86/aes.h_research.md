# sources/distributed-fs/ceph-client/lib/crypto/x86/aes.h

Purpose: x86 architecture dispatch layer for AES key expansion, encryption, and decryption.

Important APIs/types/functions: declares AES-NI assembly functions and defines `aes_preparekey_arch()`, `aes_encrypt_arch()`, `aes_decrypt_arch()`, and `aes_mod_init_arch()`. It owns static key `have_aes`.

Control flow: module init enables `have_aes` if `X86_FEATURE_AES` is present. Key preparation uses AES-NI only for AES-128 and AES-256 and only when `irq_fpu_usable()` is true; AES-192 and unavailable-FPU cases use `aes_expandkey_generic()`. Encrypt/decrypt similarly bracket AES-NI calls in `kernel_fpu_begin()`/`kernel_fpu_end()` or fall back to generic routines.

State and persistence: persistent state is the read-only-after-init static branch. Per-call state is caller-owned key/output buffers. FPU state is temporarily borrowed and restored through kernel FPU APIs.

Dependencies: `<asm/fpu/api.h>`, CPU feature detection, static keys, generic AES functions and key structs from the including implementation.

Integration points: included by the generic AES library source to override architecture hooks via `#define aes_mod_init_arch`.

Risks: FPU availability in interrupt context is critical; bypassing `irq_fpu_usable()` would corrupt kernel FPU state. AES-192 fallback means mixed performance and timing properties across key sizes. Static key enable assumes boot CPU feature uniformity acceptable for this library.

Test signals: AES library self-tests should compare accelerated and generic outputs. Runtime feature gating can be exercised only on matching x86 hardware or emulation.
