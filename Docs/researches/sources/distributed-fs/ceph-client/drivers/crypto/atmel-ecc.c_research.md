# sources/distributed-fs/ceph-client/drivers/crypto/atmel-ecc.c

## Purpose

`atmel-ecc.c` registers a KPP implementation of `ecdh-nist-p256` backed by Microchip/Atmel ATECC508A-class I2C secure elements. The device generates and stores a random private key internally, returns the public key, and computes shared secrets using its ECDH command. Software fallback is used when the caller supplies its own private key or otherwise requests unsupported behavior.

## Important APIs, Types, And Functions

`struct atmel_ecdh_ctx` stores the selected I2C client, fallback KPP transform, generated public key, curve id, and fallback flag. `atmel_ecdh_set_secret()` decodes crypto ECDH parameters and either triggers on-device GenKey or configures fallback. `atmel_ecdh_generate_public_key()` returns the saved device-generated public key. `atmel_ecdh_compute_shared_secret()` builds asynchronous `atmel_i2c_work_data` and queues an ECDH command. Client load balancing uses `atmel_ecc_i2c_client_alloc()` and `tfm_count`.

## Control Flow

Module init initializes a global client list and registers an I2C driver. Probe calls the shared `atmel_i2c_probe()` sanity check, adds the client to the list, and registers the KPP algorithm. Transform init chooses the least-used I2C client and allocates fallback. `set_secret()` with an empty private key asks the device to generate a key in slot 2 and stores the returned public key. Shared-secret requests validate the peer public key length, allocate work, initialize an ECDH I2C command, enqueue it, and complete in `atmel_ecdh_done()` after copying the response to the destination sg.

## State And Persistence Behavior

The device persistently stores/generated private key material in `DATA_SLOT_2`; the driver stores only the returned public key in memory. Global state is a list of probed I2C clients protected by a spinlock and per-client active transform counters. Per-request I2C work is heap-allocated and freed on completion. Removing a busy client logs an emergency warning because the I2C remove path cannot fail and in-flight work may later touch freed memory.

## Dependencies And Integration Points

The driver depends on the shared Atmel I2C command layer, Linux KPP/ECDH crypto APIs, I2C device/OF matching for `atmel,atecc508a`, workqueues, scatterlist helpers, and crypto fallback transforms. It exports a higher-priority hardware-backed `ecdh-nist-p256` algorithm.

## Risks And Test Signals

Risks include global algorithm registration conflicts with multiple devices, lack of serialization between `set_secret()` and in-flight public/shared-secret operations as documented in the context comment, unsafe remove while transforms exist, fallback tfm substitution on the original request, and reliance on locked secure-element zones. Test with ECDH selftests, multiple I2C devices, fallback with caller-supplied private keys, invalid peer key sizes, async cancellation/unbind scenarios, and I2C error/status injection.
