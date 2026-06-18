<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-keyctl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-keyctl.c

## Purpose

This optional MCU feature exposes the Turris Omnia board private signing key through the kernel keyctl asymmetric signing interface, while keeping private key operations inside the MCU.

## Important APIs, Types, And Functions

`omnia_msg_signed_irq_handler()` collects a completed signature from the MCU. `omnia_mcu_sign()` sends a SHA-256 digest to `OMNIA_CMD_CRYPTO_SIGN_MESSAGE`, waits for the message-signed completion, and copies the signature. `omnia_mcu_get_public_key()` returns the cached board public key. `omnia_signing_key_subtype` describes key size, digest size, signature size, hash algorithm, and callbacks. `omnia_mcu_register_keyctl()` reads the public key, initializes synchronization, requests the message-signed IRQ, and creates a Turris signing key.

## Control Flow

Registration is skipped unless `OMNIA_FEAT_CRYPTO` is present. A keyctl sign request enters `omnia_mcu_sign()`, takes `sign_lock`, rejects concurrent signing, sends the digest command, marks a request pending, and waits. The nested IRQ handler reads the signature response, stores result/error, clears pending state, and completes the waiter. The signer copies the signature out and clears the stored signature buffer.

## State And Persistence

The public key is cached in `mcu->board_public_key`. Signing state includes a completion, lock, pending flag, error code, and temporary signature buffer. The private key remains persistent inside the MCU and is never exposed to the kernel.

## Dependencies And Integration Points

It depends on the Turris signing key helper, Linux keyrings/asymmetric key operations, SHA-256 constants, the MCU GPIO IRQ helper, and crypto feature bits.

## Risks

Only one signing request can be active; concurrent callers get `-EBUSY`. If the IRQ is lost, sign waits indefinitely unless interrupted. The API signs exactly `SHA256_DIGEST_SIZE` bytes and assumes callers selected compatible raw/sha256 parameters. Signature data is explicitly cleared only after successful copy.

## Test Signals

Test feature absence, public-key read length validation, key creation, valid keyctl sign/query/read, concurrent sign rejection, interrupt completion, MCU error propagation, interruptible wait, and signature buffer clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-keyctl.c -->
