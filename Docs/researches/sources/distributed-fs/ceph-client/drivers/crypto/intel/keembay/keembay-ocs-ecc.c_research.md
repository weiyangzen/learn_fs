# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-ecc.c

## Purpose
This file implements the Keem Bay OCS ECC platform driver and Crypto API KPP algorithms for ECDH over NIST P-256 and P-384. It uses the hardware ECC block for scalar multiplication and modular arithmetic, with software ECC helpers for representation and validation.

## Important APIs, Types, And Functions
- `struct ocs_ecc_dev` holds the platform device, MMIO base, crypto engine, IRQ completion, and IRQ number.
- `struct ocs_ecc_ctx` holds the selected OCS device, curve, and private key.
- MMIO helpers: `ocs_ecc_wait_idle()`, `ocs_ecc_cmd_start()`, `ocs_ecc_write_cmd_and_data()`, `ocs_ecc_trigger_op()`, `ocs_ecc_read_cx_out()`, and `ocs_ecc_read_cy_out()`.
- Hardware math: `kmb_ecc_point_mult()` loads point/scalar/curve parameters, uses RNG-generated side-channel mask data, triggers multiplication, and reads X/Y output. `kmb_ecc_do_scalar_op()` performs modular multiply, add, or power operations.
- Validation: `kmb_ocs_ecc_is_pubkey_valid_partial()` checks nonzero, coordinate ranges, and curve equation; `kmb_ocs_ecc_is_pubkey_valid_full()` also checks `nQ` is zero.
- Key handling: `kmb_ecc_is_key_valid()` enforces private-key range; `kmb_ecc_gen_privkey()` generates a private key with random bits and validates it; `kmb_ocs_ecdh_set_secret()` decodes and stores or generates the private key.
- KPP operations: `kmb_ecc_do_shared_secret()` validates peer public key and computes shared X coordinate; `kmb_ecc_do_public_key()` computes and validates the public key.
- Algorithm registrations: `ocs_ecdh_p256` and `ocs_ecdh_p384` are `kpp_engine_alg` registrations.
- Platform lifecycle: `kmb_ocs_ecc_probe()` maps registers, requests IRQ, adds the device, starts crypto engine, and registers KPP algorithms; remove unregisters and exits.

## Control Flow
Transform init selects the curve and binds the single OCS ECC device. `set_secret` decodes user ECDH parameters and stores a private key in internal digit order. Public-key or shared-secret requests validate sizes and queue to `crypto_engine`. The engine callback dispatches based on `req->src`: no source means generate public key; source means compute shared secret. Hardware operations wait for idle, load operands through DATA_IN, trigger an interrupt-producing command, wait for completion, and read result registers.

## State And Persistence
Per-device state is runtime-only MMIO/engine/IRQ state in `ocs_ecc_dev`. Per-transform state persists the private key until tfm exit, where only the first word is currently zeroed via `memzero_explicit(tctx->private_key, sizeof(*tctx->private_key))`; the intended cleanup likely should cover the whole array. Request-local buffers for public/shared keys are stack or allocated ECC points and are freed before return.

## Dependencies And Integration Points
The driver depends on Crypto API KPP/ECDH, `crypto_engine`, Linux ECC internals (`ecc_curve`, `ecc_point`, `vli_*`, `ecc_swap_digits()`), kernel RNG, platform resources, MMIO polling, IRQ completions, OF matching on `intel,keembay-ocs-ecc`, and FIPS-related headers.

## Risks
- `kmb_ocs_ecdh_exit_tfm()` appears to clear only one `u64` of `private_key`, leaving most key material in memory.
- `kmb_ecc_gen_privkey()` generates one random candidate and fails if invalid instead of retrying, so key generation can spuriously fail.
- Public-key validation and scalar operations are hardware-assisted but involve many sequential operations; timeout or interrupt handling failures must be surfaced cleanly.
- Shared-secret output copies only `min(curve_bytes, req->dst_len)` after earlier size checks are limited; consumers need clear expectations for truncation.
- Device list lookup assumes a device is present during tfm init and may be fragile around hot-unplug/remove races.

## Test Signals
- KPP self-tests for `ecdh-nist-p256-keembay-ocs` and `ecdh-nist-p384-keembay-ocs`.
- Negative tests for invalid private keys, invalid public coordinates, zero points, wrong source/destination sizes, and RNG failure injection.
- KASAN/KMSAN checks to confirm private-key cleanup covers all words.
- IRQ timeout and spurious interrupt tests around `ocs_ecc_trigger_op()` and `ocs_ecc_irq_handler()`.
