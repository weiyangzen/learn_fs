# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_labels.c

## Purpose
This file implements conntrack label bit replacement and per-network label-user accounting. Labels are stored in the conntrack extension area and exposed to netfilter users for classification. The code provides atomic masked replacement, event notification when labels change, and simple reference accounting to know whether label extensions are in use for a network namespace.

## Important APIs, Types, And Functions
`replace_u32()` is the internal cmpxchg loop for one 32-bit word. `nf_connlabels_replace()` is the exported label update API; it applies `data` under an optional mask to the label bitset and emits `IPCT_LABEL` through `nf_conntrack_event_cache()` if any word changes. `nf_connlabels_get()` validates the requested bit index and increments `net->ct.labels_used`. `nf_connlabels_put()` decrements that counter.

## Control Flow
`nf_connlabels_replace()` first looks up `struct nf_conn_labels` with `nf_ct_labels_find(ct)`. If the extension is absent, it returns `-ENOSPC`. It clamps the caller's word count to the extension size, applies each word with `replace_u32()`, and then pads remaining words by clearing them with another `replace_u32()` pass. If any update changed bits, it queues a conntrack label event. The mask semantics are inverted for the helper: `replace_u32(address, mask ? ~mask[i] : 0, data[i])` preserves masked-out bits and toggles in the new value according to the implementation's XOR-style composition.

## State And Persistence
Label state lives in each conntrack's label extension and lasts for the conntrack lifetime. The namespace-level `labels_used` atomic tracks active label users but is not persisted. No disk state exists.

## Dependencies And Integration Points
The file depends on `nf_conntrack_labels.h` for extension lookup and maximum size, and on conntrack ecache for `IPCT_LABEL` notifications. Netlink conntrack code calls `nf_connlabels_replace()` when handling `CTA_LABELS` and `CTA_LABELS_MASK`.

## Risks
Concurrency correctness depends on the cmpxchg loop because labels may be updated without taking the conntrack lock. Mask interpretation is subtle and must match userspace API expectations. Missing label extensions return `-ENOSPC`, so callers must ensure extensions are enabled/attached before updating. Bit range validation in `nf_connlabels_get()` protects the fixed extension size.

## Test Signals
Tests should cover unmasked replacement, masked replacement preserving other bits, no event when data is unchanged, event on change, truncation when `words32` exceeds extension size, padding behavior for shorter writes, absent-extension `-ENOSPC`, out-of-range `nf_connlabels_get()` returning `-ERANGE`, and balanced get/put accounting warnings.
