# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_hw.c

## Purpose

`chtls_hw.c` implements Chelsio TLS hardware programming helpers: TCB field updates, receive quiesce control, key-context slot bitmap management, TLS key-context construction, and memory-write work requests that install RX/TX TLS keys into adapter key memory.

## Important APIs, Types, and Functions

- TCB helpers: `chtls_set_tcb_field()`, `chtls_set_tcb_field_rpl_skb()`, `chtls_set_tcb_keyid()`, `chtls_set_tcb_seqno()`, `chtls_set_tcb_quiesce()`, and `chtls_set_quiesce_ctrl()`.
- Key map: `chtls_init_kmap()` initializes `cdev->kmap`; `get_new_keyid()` allocates a bitmap slot; `free_tls_keyid()` releases RX/TX slots; `keyid_to_addr()` converts a key ID to hardware memory address units.
- Key context: `chtls_key_info()` supports TLS 1.2 AES-GCM-128 and AES-GCM-256, computes GHASH H, fills Chelsio key context headers, copies salt/key/H, and clears the copied key.
- TX SCMD setup: `chtls_set_scmd()` sets TLS AES-GCM command fields.
- Public key install: `chtls_setkey()` flushes pending TX data for TX keys, allocates a key slot, builds `FW_ULPTX_WR`/`ULP_TX_MEM_WRITE`, enqueues/sends it, then programs TCB fields for RX keys or sets TX sequence state for TX keys.

## Control Flow

For `setsockopt(SOL_TLS, TLS_TX/TLS_RX)`, `chtls_main.c` copies crypto info into `csk->tlshws.crypto_info` and calls `chtls_setkey()`. The key path reserves a hardware key slot, builds a memory-write request containing a key context, and sends it through the offload queue while charging WR credits. For RX keys, it also writes the key ID into TCB word 31, enables TLS ULP raw bits, resets sequence number, and clears RX quiesce. For TX keys, it initializes `tx_seq_no` and records the key ID for later TX WRs.

## State and Persistence Behavior

Key-slot state is volatile in `cdev->kmap.addr` under `kmap.lock`. Socket TLS hardware state is in `csk->tlshws.rxkey`, `txkey`, `keylen`, `scmd`, `crypto_info`, and `tx_seq_no`. WR credit state is updated when key memory-write and TCB WRs are enqueued. Key material copied from userspace is zeroed from the stored crypto-info key area after constructing the key context.

## Dependencies and Integration Points

The file depends on Chelsio CPL/ULPTX/FW layouts, TCB field definitions, Linux TLS crypto-info structs, AES helpers, and `chtls_io.c` WR queue functions. It integrates with `chtls_destroy_sock()` via `free_tls_keyid()` and with `chtls_sendmsg()` through the `txkey` state that enables TLS TX WR generation.

## Risks and Edge Cases

- `cdev->kmap.available` is initialized to the number of longs, not decremented on allocation; capacity enforcement is actually via `find_first_zero_bit()`.
- Partial failure in `chtls_setkey()` after key allocation calls `free_tls_keyid()`, which frees both RX and TX keys, not only the just-failed direction.
- Key install consumes WR credits; callers depend on enough credits being present before key programming.
- RX TCB setup requires several sequential writes; failure after some writes can leave hardware partially configured.

## Test Signals

Test AES-GCM-128 and AES-GCM-256 for TX and RX, key memory exhaustion, setsockopt after abort shutdown, pending TX flush before TX key replacement, RX quiesce clearing, key ID reuse after socket destroy, and malformed TLS version/cipher rejection through the caller.
