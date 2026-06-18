# sources/distributed-fs/ceph-client/net/ipv6/seg6_hmac.c

## Purpose

`seg6_hmac.c` implements SRv6 HMAC key storage, HMAC computation, inbound validation, and outbound HMAC TLV population. It supports SHA-1 and SHA-256 algorithms for SRH authentication material.

## Important APIs, Types, And Functions

The main exported APIs are `seg6_hmac_compute()`, `seg6_hmac_validate_skb()`, `seg6_hmac_info_lookup()`, `seg6_hmac_info_add()`, `seg6_hmac_info_del()`, `seg6_push_hmac()`, `seg6_hmac_net_init()`, and `seg6_hmac_net_exit()`. Key records are `struct seg6_hmac_info`, stored in a per-net rhashtable keyed by `hmackeyid`. `struct hmac_storage` provides a per-CPU ring buffer protected by `local_lock_t` for building the HMAC input text.

Internal helpers include `seg6_get_tlv_hmac()` for locating the fixed-position HMAC TLV at the end of an SRH, `seg6_hinfo_release()` / `seg6_free_hi()` for RCU freeing, and `rht_params` for rhashtable configuration.

## Control Flow

`seg6_get_tlv_hmac()` first checks that the SRH is long enough for the segment list plus HMAC TLV area, then requires `sr_has_hmac()`, locates the TLV 40 bytes before the encoded end of the SRH, and verifies type and length.

`seg6_hmac_compute()` builds the RFC-style authentication text from source address, first-segment, flags, big-endian key ID, and all segment addresses. It rejects inputs that exceed the fixed per-CPU ring buffer, disables bottom halves, locks the per-CPU buffer, copies the fields, runs the configured HMAC algorithm, zero-pads the SHA-1 result to the SRv6 HMAC field length, and unlocks. Unsupported algorithms trigger a one-time warning and `-EINVAL`.

`seg6_hmac_validate_skb()` reads the per-interface `seg6_require_hmac` policy. A positive value requires a TLV; a negative value disables validation; zero validates only if a TLV is present. When validation is required or present, it looks up the key under RCU, computes expected bytes, and uses `crypto_memneq()` for constant-time comparison.

`seg6_hmac_info_add()` prepares algorithm-specific key material before inserting into the rhashtable. Delete removes the key and RCU-frees it. `seg6_push_hmac()` finds the TLV, zeroes the output field, looks up the key, computes, and writes the HMAC for outbound packet construction.

## State And Persistence Behavior

HMAC keys persist per network namespace in `seg6_pernet_data->hmac_infos`. Records are looked up locklessly under RCU and removed with RCU freeing, while administrative mutation is serialized by callers in `seg6.c`. The compute buffer is per-CPU scratch state only and is not persisted. Per-net initialization creates the rhashtable, and exit frees all records through `rhashtable_free_and_destroy()`.

## Dependencies And Integration Points

This file depends on SRv6 core state from `seg6.c`, crypto helpers for SHA-1/SHA-256 HMAC, IPv6 skb layout, per-interface IPv6 configuration, and generic netlink-managed key records. `seg6_iptunnel.c` calls `seg6_push_hmac()` when adding outbound SRHs that carry an HMAC TLV, while SRH receive logic can call `seg6_hmac_validate_skb()` based on interface policy.

## Risks And Edge Cases

The HMAC input has a hard ring size limit that currently allows 14 segments; larger segment lists fail with `-EMSGSIZE`. Correctness depends on callers passing a validated SRH, because TLV positioning is computed from header fields. SHA-1 outputs are zero-padded, so comparison length remains fixed but security strength follows SHA-1. Key dumps elsewhere expose secrets to privileged generic netlink readers. The local lock and bottom-half disabling are important because compute can run in packet paths; removing them would corrupt per-CPU scratch data.

## Test Signals

Tests should cover SHA-1 and SHA-256 vectors, invalid algorithms, missing HMAC TLV, wrong TLV length/type, policies `require`, `optional`, and `ignore`, wrong key ID, tampered segment list/source address, max segment count boundary, and concurrent add/delete/validate under RCU with KASAN/lockdep enabled.
