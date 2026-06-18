# sources/distributed-fs/ceph-client/net/mac80211/aes_cmac.c

Purpose: this file computes AES-CMAC MICs for IEEE 802.11 management frame protection, including BIP-CMAC-128 and BIP-CMAC-256 style MIC lengths. It wraps the kernel `aes-cbc-macs` CMAC primitives with WLAN-specific AAD and beacon timestamp handling.

Important API: `ieee80211_aes_cmac(const struct aes_cmac_key *key, const u8 *aad, const u8 *data, size_t data_len, u8 *mic, unsigned int mic_len)` is the only function. It initializes an `aes_cmac_ctx`, feeds a fixed 20-byte AAD, feeds frame body bytes excluding the trailing MIC field, appends zero bytes the size of the MIC field, finalizes into a full AES block, and copies the requested MIC length to `mic`.

Control flow: after `aes_cmac_init()`, the function always authenticates `AAD_LEN` bytes. It then inspects the frame-control field at the start of AAD. For beacons, it masks the variable Timestamp field by authenticating eight zero bytes and then resumes with `data + 8`; for other management frames it authenticates the body directly. In both cases it subtracts `mic_len` from the authenticated data region and then feeds zero bytes for the MIC field itself before finalizing.

State and persistence behavior: no persistent state is kept in this file. The CMAC key is prepared elsewhere, typically in key allocation, and passed in. The local `zero` array and CMAC context are transient. The function writes only the caller-provided MIC output.

Dependencies and integration: it depends on `<crypto/aes-cbc-macs.h>`, `<net/mac80211.h>` frame helpers such as `ieee80211_is_beacon()`, `key.h` cipher constants, and `aes_cmac.h`. It is called by `wpa.c` for BIP-CMAC transmit and receive validation, with key material prepared in `key.c`.

Risks: the function assumes `data_len` is at least `mic_len`, and for beacons at least `8 + mic_len`; callers must validate frame sizes. A wrong AAD construction or failure to zero the mutable beacon timestamp would break interoperability. Since `mic_len` may be 8 or 16 depending on suite, callers must pass the suite-appropriate value.

Test signals: BIP-CMAC known-answer tests should include beacon and non-beacon management frames. RX tests should verify replay rejection and MIC failure counters, while TX tests should ensure the MMIE MIC field is zeroed for calculation and then populated.
