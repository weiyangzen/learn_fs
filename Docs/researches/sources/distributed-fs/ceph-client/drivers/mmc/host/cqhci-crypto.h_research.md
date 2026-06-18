# sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-crypto.h

Purpose: declares CQHCI crypto initialization and provides the task-descriptor crypto word builder used when MMC inline encryption is enabled.

Important APIs and types: exports `cqhci_crypto_init(struct cqhci_host *host)` when `CONFIG_MMC_CRYPTO` is enabled, with a no-op inline stub otherwise. `cqhci_crypto_prep_task_desc(struct mmc_request *mrq)` returns bits 64-127 for a CQHCI task descriptor, or zero for unencrypted requests or non-crypto builds.

Control flow: data request descriptor preparation calls `cqhci_crypto_prep_task_desc`. If the request has no `crypto_ctx`, no crypto bits are emitted. Otherwise the helper warns if the first DUN exceeds 32 bits, sets `CQHCI_CRYPTO_ENABLE_BIT`, encodes `mrq->crypto_key_slot`, and embeds `bc_dun[0]`.

State and persistence: the header stores no state. It consumes request-local crypto context and keyslot assignment supplied by the block/MMC layers; keyslot state is managed by `cqhci-crypto.c`.

Dependencies and integration points: includes `linux/mmc/host.h` and `cqhci.h`, and is included by CQHCI core code. Its conditional stubs keep the core buildable without MMC crypto support.

Risks: the descriptor helper assumes `max_dun_bytes_supported = 4` from initialization; if a custom crypto profile changes that contract, the warning may not be enough to prevent invalid descriptors. It only encodes the first DUN word.

Test signals: compile coverage in crypto and non-crypto configurations, encrypted CQE request descriptor inspection, and block crypto tests verifying keyslot and DUN propagation.
