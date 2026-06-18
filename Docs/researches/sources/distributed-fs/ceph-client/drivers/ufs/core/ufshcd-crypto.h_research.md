# sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-crypto.h

## Purpose

This header provides request-time inline encryption helpers and crypto lifecycle declarations for the UFS host controller.

## Important APIs, Types, and Functions

Inline helpers include `ufshcd_prepare_lrbp_crypto()`, `ufshcd_prepare_req_desc_hdr_crypto()`, `ufshcd_crypto_fill_prdt()`, and `ufshcd_crypto_clear_prdt()`. It declares lifecycle functions implemented in `ufshcd-crypto.c` and provides disabled stubs under non-crypto builds.

## Control Flow

For encrypted requests, the LRB records blk-crypto keyslot index and DUN. Request descriptor preparation sets crypto enable, CCI, and lower/upper DUN fields. Variant drivers may fill crypto PRDT entries. If keys are stored in PRDT due to a quirk, clear helper zeroizes PRDT entries after use.

## State and Persistence Behavior

The header mutates per-request LRB fields and request descriptor headers. It does not own persistent state, but it handles sensitive key/DUN metadata paths.

## Dependencies and Integration Points

It depends on SCSI command/request structures, blk-crypto fields, UFS descriptors, UFSHCI crypto layout, and variant `fill_crypto_prdt` operations.

## Risks and Test Signals

Risks include missing crypto clearing for key-in-PRDT hardware, wrong DUN width, stale keyslot indexes, and disabled-config stubs hiding missing feature tests. Test signals include encrypted and unencrypted request descriptor fields, PRDT fill/clear with quirks, and crypto-disabled builds.
