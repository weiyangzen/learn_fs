# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_request_mgr.h

## Purpose

`cc_request_mgr.h` declares the public request-manager interface used by ccree crypto modules and initialization code. It hides the software queue, backlog, completion tasklet, and hardware queue details behind descriptor submission functions.

## Important APIs, Types, And Functions

The header includes `cc_hw_queue_defs.h` to expose `struct cc_hw_desc`. It declares `cc_req_mgr_init()`, `cc_req_mgr_fini()`, `cc_send_request()` for asynchronous crypto requests, `cc_send_sync_request()` for blocking internal flows, `send_request_init()` for initialization-time descriptor sequences, and `complete_request()` for IRQ dispatch.

## Control Flow

Callers build descriptor arrays, fill a `struct cc_crypto_req` callback/argument, and submit through `cc_send_request()` or `cc_send_sync_request()`. The platform interrupt path calls `complete_request()` to defer completion processing.

## State And Persistence Behavior

The header declares stateful operations but owns no state. State is private to `cc_request_mgr.c` and stored in `drvdata->request_mgr_handle`.

## Dependencies And Integration Points

The API is used by hash, cipher, AEAD, SRAM initialization, FIPS, and driver init paths. It depends on `struct cc_drvdata`, `struct cc_crypto_req`, and `struct crypto_async_request` being visible from included driver/crypto headers in translation units.

## Risks And Edge Cases

The API does not encode descriptor length limits in the type system. Callers must obey the manager's maximum copied backlog sequence length and set queue-last descriptors correctly for flows that need hardware engine release. Asynchronous callbacks must tolerate `-EINPROGRESS` backlog notifications and final completions.

## Test Signals

Build coverage across all ccree modules catches declaration drift. Runtime validation is indirect through successful async hash/cipher/AEAD operations, synchronous setkey/init descriptor flows, and IRQ completion handling.
