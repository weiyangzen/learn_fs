# sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/ixp4xx_crypto.c

## Purpose
This file implements a legacy Intel IXP4xx NPE-C hardware crypto driver for the Linux Crypto API. It registers asynchronous SKCIPHER and AEAD algorithms backed by the IXP4xx queue manager/NPE firmware, including DES, 3DES, AES ECB/CBC/CTR/RFC3686 CTR, and authenc HMAC-MD5/HMAC-SHA1 with CBC ciphers.

## Important APIs, Types, And Functions
- Hardware descriptors: `struct buffer_desc` represents NPE buffer chains; `struct crypt_ctl` is the command/control block submitted to the NPE.
- Per-request contexts: `struct ablk_ctx` tracks SKCIPHER source/destination descriptors, IV, encrypt flag, and fallback request; `struct aead_ctx` tracks AEAD DMA chains, IV scatterlist, scattered HMAC storage, and encrypt flag.
- Transform context: `struct ixp_ctx` owns encrypt/decrypt security-association contexts, auth/encryption keys, RFC3686 nonce/salt state, setup completion, and SKCIPHER fallback tfm.
- Descriptor allocation: `setup_crypt_desc()`, `get_crypt_desc()`, and `get_crypt_desc_emerg()` allocate coherent descriptor memory and hand out normal or emergency command slots under spinlocks.
- Initialization: `init_ixp_crypto()` locates the NPE/queue IDs from device tree or legacy defaults, loads/probes firmware, checks AES support, creates DMA pools, requests queue manager queues, and enables receive interrupts.
- Transform setup: `setup_cipher()`, `gen_rev_aes_key()`, `setup_auth()`, and `register_chain_var()` build NPE context memory and submit setup commands for AES reverse keys and HMAC inner/outer pads.
- Data submission: `ablk_perform()` and `aead_perform()` map scatterlists into NPE buffer chains, populate `crypt_ctl`, and submit queue entries. `ablk_rfc3686_crypt()` constructs the RFC3686 counter block.
- Completion: `irqhandler()` schedules `crypto_done_tasklet`; `crypto_done_action()` drains the receive queue; `one_packet()` frees DMA chains, restores/updates IVs, copies scattered tags, and calls Crypto API completion callbacks.
- Registration: `ixp_crypto_probe()` registers `ixp4xx_algos[]` and `ixp4xx_aeads[]`; `ixp_crypto_remove()` unregisters them and releases queues/pools/NPE resources.

## Control Flow
Probe initializes hardware resources, derives firmware capabilities, then registers supported Crypto API algorithms. A caller sets a key, which resets SA contexts and may submit asynchronous NPE setup work; the setkey path waits for setup completion before returning. Encrypt/decrypt requests check queue/configuration readiness, allocate a control descriptor, chain DMA buffers from SG lists, submit the descriptor to `send_qid`, and return `-EINPROGRESS`. The queue manager receive interrupt schedules a tasklet that consumes completed physical descriptor addresses, decodes success versus authentication failure from low bits, completes the original request, and returns the descriptor to the free pool.

## State And Persistence
Global runtime state includes the selected `npe_c`, queue IDs, DMA pools, coherent `crypt_virt`/`crypt_phys`, AES capability flag, and platform device pointer. Per-transform state persists keys and NPE context memory until tfm exit. Per-request state lives in Crypto API request contexts and is cleaned on completion/error. No state persists across driver unload or system reboot.

## Dependencies And Integration Points
The driver depends on IXP4xx platform NPE and queue-manager APIs, DMA pools/coherent memory, device tree phandles (`intel,npe-handle`, `queue-rx`, `queue-txready`), Crypto API SKCIPHER/AEAD/AUTHENC internals, DES/AES/HMAC helpers, tasklets, and platform driver matching for `intel,ixp4xx-crypto`.

## Risks
- `aead_perform()` uses `crypt->auth_len = req->assoclen + cryptlen` and special scattered-HMAC handling; off-by-one or SG length mismatches can corrupt authentication tag handling.
- SKCIPHER fallback is used for multi-entry source or destination SG lists, so hardware coverage is narrower than the registered algorithms suggest.
- Descriptor allocation uses only `NPE_QLEN` coherent descriptors despite emergency indexing up to `NPE_QLEN_TOTAL`; this deserves scrutiny because `setup_crypt_desc()` allocates `NPE_QLEN * sizeof(struct crypt_ctl)` while emergency slots index beyond `NPE_QLEN`.
- The AEAD registration loop checks `ixp4xx_algos[i].cfg_enc` when deciding AES support for AEAD entries; indexing a different array can skip or include the wrong AEADs if array order/length diverges.
- Several paths rely on `BUG_ON(qmgr_stat_overflow(send_qid))`, which can crash the kernel on queue-manager overflow.
- The driver uses legacy tasklets and direct SG virtual mapping assumptions (`sg_virt()`), both of which are sensitive to platform constraints.

## Test Signals
- Crypto API self-tests for all registered algorithms, including authenc MD5/SHA1 with DES/3DES/AES and RFC3686 CTR.
- Runtime tests on firmware revisions with and without AES support to verify registration filtering.
- Stress tests with queue saturation, in-place and out-of-place buffers, short tags, scattered tags, and asynchronous completions.
- KASAN/DMA API debug checks around descriptor allocation, SG mapping/unmapping, and error exits.
