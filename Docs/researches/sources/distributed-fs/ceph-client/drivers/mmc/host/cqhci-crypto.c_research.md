# sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-crypto.c

Purpose: implements CQHCI inline-encryption support by bridging MMC CQHCI crypto capability/configuration registers to the Linux block-layer `blk_crypto_profile` keyslot API.

Important APIs and functions: public `cqhci_crypto_init` initializes crypto support. Internal keyslot callbacks are `cqhci_crypto_keyslot_program` and `cqhci_crypto_keyslot_evict`, grouped in `cqhci_crypto_ops`. Helpers include `cqhci_crypto_program_key`, `cqhci_crypto_clear_keyslot`, `cqhci_find_blk_crypto_mode`, and `cqhci_host_from_crypto_profile`.

Control flow: initialization checks both `MMC_CAP2_CRYPTO` and CQHCI `CAP.CS`; unsupported cases clear the MMC crypto cap and return success. Standard profiles read `CQHCI_CCAP`, derive the crypto configuration array offset, allocate and cache crypto capability entries, initialize the block crypto profile with `config_count + 1` slots, advertise AES-256-XTS data-unit sizes, and set raw key support with a four-byte DUN limit. All keyslots are cleared before use, and CQHCI 128-bit task descriptors are forced. Programming a key selects a matching capability entry, builds a crypto configuration entry, writes key/config dwords with CFGE cleared first and set last, then wipes the temporary config.

State and persistence: persistent driver state is cached in `cq_host->crypto_capabilities`, `crypto_cap_array`, `crypto_cfg_register`, and `mmc->crypto_profile`. Actual keys persist only in controller keyslot registers until evicted, reset, or reprogrammed. Temporary key material is scrubbed with `memzero_explicit`.

Dependencies and integration points: depends on `linux/blk-crypto.h`, `blk-crypto-profile.h`, MMC host crypto profile helpers, and CQHCI register definitions in `cqhci.h`. It integrates with `cqhci-core.c` through `cqhci_crypto_init` and with task descriptor generation through `cqhci_crypto_prep_task_desc` in the header.

Risks: only AES-256-XTS is mapped, so other hardware modes are ignored. CQHCI supports only 32 DUN bits here, which may limit devices or filesystems needing larger data-unit numbers. Capability `sdus_mask` is multiplied by 512 when advertised, so incorrect hardware capability reporting can expose invalid data-unit sizes. Keyslot register writes must preserve the CFGE ordering or the controller can observe partial keys.

Test signals: build with `CONFIG_MMC_CRYPTO`, probe on CQHCI hardware advertising `CAP.CS`, block-layer inline encryption self-tests, keyslot program/evict tracing, encrypted filesystem I/O, and invalid-capability/error-path tests. Verify `MMC_CAP2_CRYPTO` is cleared when hardware or profile setup is unsupported.
