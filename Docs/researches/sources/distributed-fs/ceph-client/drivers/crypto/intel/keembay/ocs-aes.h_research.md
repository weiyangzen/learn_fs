# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-aes.h

## Purpose
This header declares the public low-level OCS AES/SM4 interface shared between the Keem Bay AES/SM4 Crypto API front end and register/DMA implementation.

## Important APIs, Types, And Functions
- `enum ocs_cipher` selects AES or SM4.
- `enum ocs_mode` enumerates ECB, CBC, CTR, CCM, GCM, and CTS hardware modes.
- `enum ocs_instruction` selects encrypt, decrypt, expand, or bypass.
- `struct ocs_aes_dev` stores device list linkage, device pointer, IRQ, MMIO base, interrupt completion, DMA error mask, and crypto engine.
- `struct ocs_dll_desc` describes a coherent OCS DMA linked list.
- Public functions include `ocs_aes_set_key()`, `ocs_aes_op()`, `ocs_aes_gcm_op()`, `ocs_aes_ccm_op()`, `ocs_create_linked_list_from_sg()`, and `ocs_aes_irq_handler()`.
- Inline `ocs_aes_bypass_op()` wraps `ocs_aes_op()` in bypass mode for DMA copying.

## Control Flow
The front-end driver allocates/owns `struct ocs_aes_dev`, builds DMA lists into `struct ocs_dll_desc`, then calls these functions to program hardware. IRQ handling is exported so the platform probe can register it directly.

## State And Persistence
The header defines runtime state containers but stores no state by itself. State persists as long as the platform device or request context owns those structures.

## Dependencies And Integration Points
It depends on DMA mapping types and forward uses `struct scatterlist` and `struct crypto_engine` through included kernel headers from consumers. It is paired with `ocs-aes.c` and `keembay-ocs-aes-core.c`.

## Risks
- `ocs_aes_bypass_op()` hardcodes AES ECB mode with BYPASS instruction; callers must ensure this remains semantically a DMA copy and not a crypto operation.
- Header consumers must initialize `irq_completion`, `base_reg`, `dev`, and `engine` before using the public APIs.

## Test Signals
- Compile coverage for both front-end and low-level objects.
- Runtime bypass-copy tests through CTS/non-in-place and AEAD AAD-copy paths.
