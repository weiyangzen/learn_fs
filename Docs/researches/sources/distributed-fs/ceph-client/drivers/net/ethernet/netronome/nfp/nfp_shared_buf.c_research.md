# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_shared_buf.c

## Purpose

`nfp_shared_buf.c` registers firmware-described NFP shared buffers with devlink and implements devlink shared-buffer pool get/set callbacks via the NFP mailbox. It exposes buffer pool size, type, threshold type, and cell size to Linux devlink users.

## Important APIs, Types, and Functions

Public functions are `nfp_shared_buf_pool_get()`, `nfp_shared_buf_pool_set()`, `nfp_shared_buf_register()`, and `nfp_shared_buf_unregister()`. Local helper `nfp_shared_buf_pool_unit()` finds a shared buffer's pool size unit in `pf->shared_bufs`.

## Control Flow

Registration first requires PF mailbox support, reads the shared-buffer count runtime symbol, maps the shared-buffer descriptor table, allocates `pf->shared_bufs`, copies each descriptor from IO memory, and calls `devlink_sb_register()` for each shared buffer. Pool get validates unit size, sends `NFP_MBOX_POOL_GET`, checks reply length, and scales firmware size units to bytes. Pool set validates unit size and byte alignment, converts bytes to firmware units, and sends `NFP_MBOX_POOL_SET`. Unregister iterates registered shared buffers and frees the descriptor array.

## State and Persistence Behavior

Persistent driver state is `pf->shared_bufs` and `pf->num_shared_bufs`. Runtime firmware state includes pool sizes and threshold types changed through mailbox commands. Devlink registration state is tied to the PF devlink instance.

## Dependencies and Integration Points

It depends on devlink shared-buffer APIs, NFP runtime symbols `NFP_SHARED_BUF_COUNT_SYM_NAME` and `NFP_SHARED_BUF_TABLE_SYM_NAME`, mailbox commands, ABI structures from `nfp_abi.h`, CPP area mapping, and PF app/main lifecycle that calls register/unregister during PF probe/remove.

## Risks and Edge Cases

No mailbox means no shared-buffer registration, which is a supported no-op. Descriptor entries may grow in future firmware, so the code computes table entry stride from mapped area size and copies only known fields. Partial devlink registration failure must unregister previous buffers. Pool set rejects sizes not divisible by the unit size.

## Test Signals

Probe with no mailbox, no shared-buffer symbol, multiple shared buffers, larger descriptor strides, mailbox short replies, invalid unit size, pool get/set through `devlink sb`, and unregister after partial registration failure.
