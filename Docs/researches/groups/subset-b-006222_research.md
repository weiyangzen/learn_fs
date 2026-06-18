# Research: subset-b-006222

Grouped research for mac80211 build, crypto, aggregation, airtime, and cfg80211 integration files. Each source file section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/Makefile -->
# sources/distributed-fs/ceph-client/net/mac80211/Makefile

Purpose: this kbuild file defines the `mac80211.o` composite object for `CONFIG_MAC80211` and selects the translation units that make up the Linux mac80211 subsystem copy in this source tree. It is the integration point that pulls together core interface management, station state, key handling, WPA helpers, scan/offchannel logic, HT/VHT/HE/EHT/UHR handling, aggregation, airtime accounting, cfg80211 hooks, mesh, debugfs, minstrel rate control, tests, and WBRF support.

Important build APIs and targets: `obj-$(CONFIG_MAC80211) += mac80211.o` registers the module/object. `mac80211-y := ...` lists mandatory objects including `aead_api.o`, `agg-tx.o`, `agg-rx.o`, `aes_cmac.o`, `aes_gmac.o`, `cfg.o`, and `airtime.o`, which are the implementation files in this work item. Conditional fragments add `led.o`, debugfs files, mesh files, `pm.o`, and minstrel rate-control objects. `obj-y += tests/` always descends into the tests directory when this makefile is included. `CFLAGS_trace.o := -I$(src)` gives trace compilation local include visibility. `ccflags-y += -DDEBUG` globally compiles this subtree with `DEBUG` defined.

Control flow and dependencies: there is no runtime control flow, but the object ordering and conditional inclusion affect available symbols. `cfg.o` contributes `mac80211_config_ops`, later used by `main.c` when creating the wiphy. `aead_api.o`, `aes_cmac.o`, and `aes_gmac.o` satisfy crypto calls from `key.c`, `wpa.c`, `rx.c`, and `tx.c`. `agg-tx.o` and `agg-rx.o` expose exported BA session helpers for drivers and internal action-frame processing. `airtime.o` exposes airtime calculators used by TX scheduling and status accounting.

State and persistence behavior: build state is derived from Kconfig symbols such as `CONFIG_MAC80211_MESH`, `CONFIG_MAC80211_DEBUGFS`, `CONFIG_MAC80211_RC_MINSTREL`, and `CONFIG_PM`; no persistent runtime state is managed here. The most notable cross-cutting build-time state is `-DDEBUG`, which can change logging, warnings, and debug-only paths throughout mac80211.

Integration points: this file integrates with the kernel kbuild system, Kconfig feature switches, and subtree tests. It also establishes that the crypto helpers and aggregation files are part of the same object, enabling internal non-exported symbol references across mac80211.

Risks: omitting a file here causes unresolved symbols or silent feature loss. Adding `ccflags-y += -DDEBUG` across the whole subsystem can increase logging volume and change code guarded by debug macros. Conditional feature objects must match Kconfig declarations and any external symbol users.

Test signals: kbuild compilation for all relevant Kconfig combinations is the main signal. Useful coverage includes `CONFIG_MAC80211`, mesh on/off, debugfs on/off, PM on/off, and minstrel on/off. Link-time unresolved-symbol failures would quickly expose object list regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aead_api.c -->
# sources/distributed-fs/ceph-client/net/mac80211/aead_api.c

Purpose: this file is a small mac80211 wrapper around the kernel Crypto API AEAD interface. It centralizes common authenticated encryption/decryption setup for CCM and GCM based WLAN ciphers, including scatterlist construction, AEAD request allocation, associated-data handling, MIC placement, key setup, and transform teardown.

Important APIs: `aead_encrypt()` builds a three-entry scatterlist of AAD, payload, and MIC output, sets the IV/nonce pointer from `b_0`, marks the AAD length with `aead_request_set_ad()`, and calls `crypto_aead_encrypt()`. `aead_decrypt()` mirrors the setup but includes `data_len + mic_len` in the crypt length and rejects `data_len == 0` with `-EINVAL`. `aead_key_setup_encrypt()` allocates a `struct crypto_aead` by algorithm name, sets the raw key, sets the authentication tag length, and returns either the transform or an `ERR_PTR`. `aead_key_free()` calls `crypto_free_aead()`.

Control flow: each operation computes `mic_len` from `crypto_aead_authsize(tfm)` and `reqsize` from the transform-specific request size. A single allocation holds the `aead_request` and a copied AAD buffer. The AAD copy is important because the request scatterlist points into allocation-owned memory while the crypto call runs. Encryption writes the authentication tag through the MIC scatterlist element; decryption authenticates the tag supplied in that element. Both paths scrub request memory with `kfree_sensitive()` before returning.

State and persistence behavior: the per-operation request allocation is transient and uses `GFP_ATOMIC`, so callers may use it in atomic TX/RX crypto contexts. Persistent crypto state lives in the `struct crypto_aead` transform returned by `aead_key_setup_encrypt()` and is owned by mac80211 key state until `aead_key_free()`.

Dependencies and integration: the file depends on `<crypto/aead.h>`, scatterlists, Linux error-pointer conventions, and `aead_api.h`. `aes_ccm.h` and `aes_gcm.h` inline wrappers call these helpers with `ccm(aes)` and `gcm(aes)`. Higher-level users are WPA/GCMP/CCMP paths in `wpa.c` and key allocation/freeing in `key.c`.

Risks: incorrect AAD length, nonce block format, or MIC length from callers produces authentication failures. The helpers assume synchronous completion even though transforms are allocated with `CRYPTO_ALG_ASYNC`; if an async provider returned `-EINPROGRESS` without caller completion handling, the current stack would not wait. Allocation with `GFP_ATOMIC` can fail under pressure, so callers must propagate `-ENOMEM`.

Test signals: CCMP/GCMP encrypt/decrypt known-answer tests, replay/MIC failure tests in WPA receive paths, and fault injection for `kzalloc()` and `crypto_aead_setkey()` failures are useful. Runtime signals include successful association with CCMP/GCMP networks and absence of MIC/authentication errors under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aead_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aead_api.h -->
# sources/distributed-fs/ceph-client/net/mac80211/aead_api.h

Purpose: this header declares the shared AEAD helper interface used by mac80211 cipher-specific wrappers. It hides kernel Crypto API request setup details from `aes_ccm.h` and `aes_gcm.h`, while still exposing transform ownership explicitly through `struct crypto_aead *`.

Important APIs and types: `aead_key_setup_encrypt(const char *alg, const u8 key[], size_t key_len, size_t mic_len)` creates and configures an AEAD transform. `aead_encrypt()` and `aead_decrypt()` accept a transform, nonce/control block pointer, associated data pointer and length, mutable data buffer, payload length, and MIC buffer. `aead_key_free()` releases the transform. The header includes `<crypto/aead.h>` and `<linux/crypto.h>`, so users can name `struct crypto_aead` and Crypto API constants.

Control flow: the header itself has no execution flow, but it defines the call contract used by inline cipher wrappers. Callers are responsible for formatting the nonce block (`b_0` for CCM or `j_0` for GCM), passing the correct AAD start pointer and length, and allocating a MIC buffer whose size matches the transform authsize configured at setup.

State and persistence behavior: state is represented only by the opaque `struct crypto_aead` pointer. The header does not prescribe storage, but in mac80211 the transform is normally stored in key-specific state and freed when the key is destroyed.

Dependencies and integration: `aes_ccm.h` and `aes_gcm.h` are the direct consumers. The implementation in `aead_api.c` relies on Linux scatterlists, error pointers, AEAD requests, and sensitive-memory free semantics. Higher-level integration reaches `key.c` and `wpa.c` through the cipher-specific headers.

Risks: the interface is low level and trusts callers on buffer lengths and nonce/AAD format. Passing stack or transient buffers is okay because the implementation copies AAD, but data and MIC buffers are used in place. Misconfigured `mic_len` at setup time affects every later encrypt/decrypt operation on that transform.

Test signals: build coverage catches prototype mismatches. Runtime crypto tests should validate both header consumers, including CCMP and GCMP key setup, encryption, decryption, and negative authentication cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aead_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_ccm.h -->
# sources/distributed-fs/ceph-client/net/mac80211/aes_ccm.h

Purpose: this header provides inline AES-CCM helpers for mac80211 CCMP-style protection. It adapts WLAN-specific AAD layout to the generic AEAD helper interface in `aead_api.h`.

Important APIs: `CCM_AAD_LEN` is defined as 32, matching the maximum WLAN CCMP AAD workspace. `ieee80211_aes_key_setup_encrypt()` creates a `ccm(aes)` transform with caller-supplied key length and MIC length. `ieee80211_aes_ccm_encrypt()` and `ieee80211_aes_ccm_decrypt()` pass `b_0`, the AAD payload after its two-byte length prefix, the parsed big-endian AAD length, the data buffer, and the MIC buffer to the generic AEAD helpers. `ieee80211_aes_key_free()` releases the transform.

Control flow and data contract: the most important behavior is the AAD convention. Callers pass an AAD buffer whose first two bytes contain the big-endian AAD length, followed by the actual AAD bytes. The inline wrappers skip the prefix (`aad + 2`) and compute `aad_len` with `be16_to_cpup((__be16 *)aad)`. The same convention is used for both encryption and decryption. The payload buffer is encrypted/decrypted in place by the lower helper.

State and persistence behavior: no local state exists in this header. Persistent state is the `struct crypto_aead` transform created for each key and owned by mac80211 key state.

Dependencies and integration: this header depends on `aead_api.h`, endian helpers available in kernel headers, and Crypto API transform semantics. It is included by `key.c` for CCMP key setup/free and `wpa.c` for CCMP encryption/decryption.

Risks: the wrapper assumes the two-byte AAD length prefix is present and valid; malformed caller buffers can produce wrong authentication input. The function name `ieee80211_aes_key_setup_encrypt()` is generic despite selecting CCM, so nearby code must avoid confusing it with GCM/GMAC setup names. MIC length is caller-configurable, which is required for CCMP variants but must match the cipher suite.

Test signals: CCMP and CCMP-256 known-answer tests, association traffic protected by CCMP, and negative MIC tests should exercise these wrappers. Static build coverage should include all CCMP key lengths and MIC sizes used by mac80211.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_ccm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_cmac.c -->
# sources/distributed-fs/ceph-client/net/mac80211/aes_cmac.c

Purpose: this file computes AES-CMAC MICs for IEEE 802.11 management frame protection, including BIP-CMAC-128 and BIP-CMAC-256 style MIC lengths. It wraps the kernel `aes-cbc-macs` CMAC primitives with WLAN-specific AAD and beacon timestamp handling.

Important API: `ieee80211_aes_cmac(const struct aes_cmac_key *key, const u8 *aad, const u8 *data, size_t data_len, u8 *mic, unsigned int mic_len)` is the only function. It initializes an `aes_cmac_ctx`, feeds a fixed 20-byte AAD, feeds frame body bytes excluding the trailing MIC field, appends zero bytes the size of the MIC field, finalizes into a full AES block, and copies the requested MIC length to `mic`.

Control flow: after `aes_cmac_init()`, the function always authenticates `AAD_LEN` bytes. It then inspects the frame-control field at the start of AAD. For beacons, it masks the variable Timestamp field by authenticating eight zero bytes and then resumes with `data + 8`; for other management frames it authenticates the body directly. In both cases it subtracts `mic_len` from the authenticated data region and then feeds zero bytes for the MIC field itself before finalizing.

State and persistence behavior: no persistent state is kept in this file. The CMAC key is prepared elsewhere, typically in key allocation, and passed in. The local `zero` array and CMAC context are transient. The function writes only the caller-provided MIC output.

Dependencies and integration: it depends on `<crypto/aes-cbc-macs.h>`, `<net/mac80211.h>` frame helpers such as `ieee80211_is_beacon()`, `key.h` cipher constants, and `aes_cmac.h`. It is called by `wpa.c` for BIP-CMAC transmit and receive validation, with key material prepared in `key.c`.

Risks: the function assumes `data_len` is at least `mic_len`, and for beacons at least `8 + mic_len`; callers must validate frame sizes. A wrong AAD construction or failure to zero the mutable beacon timestamp would break interoperability. Since `mic_len` may be 8 or 16 depending on suite, callers must pass the suite-appropriate value.

Test signals: BIP-CMAC known-answer tests should include beacon and non-beacon management frames. RX tests should verify replay rejection and MIC failure counters, while TX tests should ensure the MMIE MIC field is zeroed for calculation and then populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_cmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_cmac.h -->
# sources/distributed-fs/ceph-client/net/mac80211/aes_cmac.h

Purpose: this header declares the mac80211 AES-CMAC MIC calculation helper used by management frame protection code. It keeps the CMAC implementation detail out of WPA/key paths while exposing the prepared-key type from the kernel AES CBC-MAC support.

Important API and types: the header includes `<crypto/aes-cbc-macs.h>` so callers can use `struct aes_cmac_key`. It declares `ieee80211_aes_cmac()` with key, AAD, frame data, data length, MIC output, and MIC length arguments.

Control flow and contract: the declared function calculates a MIC over WLAN-specific AAD and frame body data. Callers must provide a prepared CMAC key, an AAD buffer with the frame-control information expected by the implementation, a frame body whose final `mic_len` bytes represent the MIC field, and an output buffer large enough for the requested MIC.

State and persistence behavior: the header defines no state. Persistent key state is held by mac80211 key objects in `key.c`; `aes_cmac.c` consumes that state without owning it.

Dependencies and integration: direct users are WPA management protection routines in `wpa.c` and key preparation in `key.c`. The helper is part of `mac80211.o` through the Makefile, so it is available internally without module boundary complexity.

Risks: because only one generic MIC function is exposed, misuse with the wrong `mic_len` or an incorrectly prepared AAD buffer will produce valid-looking but non-interoperable MICs. Compile-time type checking covers the key pointer type but not buffer sizing.

Test signals: compile coverage validates prototypes. Runtime coverage comes from BIP-CMAC transmit/decrypt tests, protected management frame association tests, and negative MIC/replay tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_cmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_gcm.h -->
# sources/distributed-fs/ceph-client/net/mac80211/aes_gcm.h

Purpose: this header provides inline AES-GCM helpers for GCMP and GCMP-256 data protection in mac80211. It maps WLAN AAD layout and GCMP MIC sizing onto the shared AEAD helper implementation.

Important APIs: `GCM_AAD_LEN` is defined as 32. `ieee80211_aes_gcm_encrypt()` and `ieee80211_aes_gcm_decrypt()` pass the GCM initial counter block `j_0`, AAD after the two-byte length prefix, the parsed AAD length, payload, and MIC buffer to `aead_encrypt()`/`aead_decrypt()`. `ieee80211_aes_gcm_key_setup_encrypt()` creates a `gcm(aes)` AEAD transform using `IEEE80211_GCMP_MIC_LEN` as the authsize. `ieee80211_aes_gcm_key_free()` releases it.

Control flow and data contract: like `aes_ccm.h`, the wrapper assumes the caller supplied a two-byte big-endian AAD length prefix. The wrapper does not construct `j_0`; GCMP code in `wpa.c` is responsible for nonce/counter block construction. Encryption and decryption operate in place on the data buffer, with the authentication tag supplied separately as `mic`.

State and persistence behavior: no state is held in this header. A configured `struct crypto_aead` transform persists in the mac80211 key object until freed.

Dependencies and integration: it includes `aead_api.h`, relies on `IEEE80211_GCMP_MIC_LEN` from mac80211 headers available to consumers, and integrates with `key.c` for transform allocation/free plus `wpa.c` for GCMP frame processing.

Risks: the wrapper hardcodes the GCMP MIC length, so alternate suites must match `IEEE80211_GCMP_MIC_LEN`. Incorrect AAD prefix, `j_0` construction, or key length causes authentication failures. As with other AEAD helpers, async Crypto API completion assumptions should be watched if providers change.

Test signals: GCMP and GCMP-256 known-answer tests, real encrypted data traffic, replay rejection, MIC failure accounting, and failure injection around transform allocation are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_gcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_gmac.c -->
# sources/distributed-fs/ceph-client/net/mac80211/aes_gmac.c

Purpose: this file implements AES-GMAC MIC generation/verification support for IEEE 802.11 BIP-GMAC-128 and BIP-GMAC-256 management frame protection. It uses the kernel AEAD GCM transform as a GMAC engine by encrypting/authenticating with zero plaintext length and all relevant frame bytes as associated data.

Important APIs: `ieee80211_aes_gmac()` computes the GMAC tag using a configured `struct crypto_aead`, 20-byte WLAN AAD, 12-byte nonce, frame data, frame length, and MIC buffer. `ieee80211_aes_gmac_key_setup()` allocates `gcm(aes)`, sets the key and `IEEE80211_GMAC_MIC_LEN` authsize, and returns the transform or `ERR_PTR`. `ieee80211_aes_gmac_key_free()` releases the transform.

Control flow: `ieee80211_aes_gmac()` rejects frames shorter than the GMAC MIC length. It allocates one sensitive block holding the AEAD request, a zero buffer the size of the MIC, and a copied AAD. For beacon frames, it builds a five-entry scatterlist: AAD, eight zero bytes replacing Timestamp, the post-timestamp frame body excluding MIC, zeroed MIC field, and output MIC. For other frames, it uses AAD, frame body excluding MIC, zeroed MIC field, and output MIC. It builds a 16-byte GCM IV from the 12-byte nonce plus zeros and counter byte `0x01`, sets crypt length to zero, marks associated data as `GMAC_AAD_LEN + data_len`, and calls `crypto_aead_encrypt()`.

State and persistence behavior: per-call AEAD request state is transient and allocated with `GFP_ATOMIC`; key state persists in the transform. The copied AAD and zero region are freed with `kfree_sensitive()` to avoid retaining authentication material.

Dependencies and integration: it depends on Crypto API AEAD/GCM, AES block sizing, mac80211 frame helpers, `key.h`, and `aes_gmac.h`. Key setup/free is used in `key.c`; MIC calculation is used by `wpa.c` BIP-GMAC TX/RX paths and error counters in key/debugfs paths.

Risks: scatterlist associated-data length must exactly match the 802.11 BIP-GMAC calculation, including zeroing the beacon Timestamp and MIC field. Any caller that passes a too-short beacon body could underflow the `data_len - 8 - MIC` calculation; frame validation before this helper is therefore critical. As with `aead_api.c`, async transform behavior is not explicitly waited on.

Test signals: BIP-GMAC-128/256 known-answer tests should include beacon and non-beacon frames. RX tests should exercise replay and MIC failures; TX tests should verify nonce construction and produced MMIE tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_gmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_gmac.h -->
# sources/distributed-fs/ceph-client/net/mac80211/aes_gmac.h

Purpose: this header declares the AES-GMAC interface used by mac80211 BIP-GMAC management protection paths. It exposes GMAC-specific AAD and nonce lengths and the three transform/MIC helper functions implemented in `aes_gmac.c`.

Important APIs and constants: `GMAC_AAD_LEN` is 20 bytes and `GMAC_NONCE_LEN` is 12 bytes. `ieee80211_aes_gmac_key_setup()` creates a key-specific `gcm(aes)` AEAD transform. `ieee80211_aes_gmac()` computes or verifies the GMAC tag over WLAN AAD and frame data, depending on caller comparison. `ieee80211_aes_gmac_key_free()` releases the transform.

Control flow and contract: callers must prepare the 20-byte AAD, 12-byte nonce, frame data including a trailing MIC field, and MIC output/comparison buffer. The implementation treats frame data as associated data and writes a GMAC tag into `mic`.

State and persistence behavior: no local state is declared. The `struct crypto_aead` pointer returned by setup is persistent key state and must be freed on key destruction.

Dependencies and integration: it includes `<linux/crypto.h>` for Crypto API types. It is consumed by `key.c` for BIP-GMAC key lifecycle and `wpa.c` for protected management frame processing.

Risks: the interface cannot enforce nonce uniqueness, frame length validity, or correct AAD construction. Those invariants are security-critical and live in callers. Compile-time constants reduce accidental length drift between setup and use.

Test signals: build coverage for BIP-GMAC suites, known-answer MIC tests, nonce/replay tests, and association tests using protected management frames with GMAC suites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/aes_gmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/agg-rx.c -->
# sources/distributed-fs/ceph-client/net/mac80211/agg-rx.c

Purpose: this file manages receive-side A-MPDU Block Ack aggregation sessions for mac80211. It handles incoming ADDBA requests, session creation/teardown, reorder-buffer allocation when the driver does not own reordering, timers, ADDBA extension elements for HE/EHT/S1G cases, and driver notifications through `ampdu_action`.

Important APIs and functions: `__ieee80211_start_rx_ba_session()` is the core setup path. `__ieee80211_stop_rx_ba_session()` tears sessions down and optionally sends DELBA. `ieee80211_process_addba_request()` parses an ADDBA request action frame and calls the setup helper. Driver-facing exports include `ieee80211_stop_rx_ba_session()`, `ieee80211_manage_rx_ba_offl()`, and `ieee80211_rx_ba_timer_expired()`. `ieee80211_add_addbaext()` and `ieee80211_retrieve_addba_ext_data()` handle extended ADDBA element data and larger EHT/MLO buffer sizes.

Control flow: incoming ADDBA processing extracts dialog token, timeout, start sequence, policy, TID, and buffer size from the management frame, then retrieves optional extension data. The setup path validates TID range, S1G NDP BA requirements, HT/HE/S1G capability, `WLAN_STA_BLOCK_BA`, BA policy, and max buffer sizes. If a duplicate request has the same dialog token, it may return success only when the timeout did not change. If a conflicting session exists, it stops the old session. Hardware that advertises `SUPPORTS_REORDERING_BUFFER` receives only a driver `IEEE80211_AMPDU_RX_START` callback. Otherwise mac80211 allocates `tid_ampdu_rx`, timers, reorder queues, and reorder timestamps before notifying the driver and installing the RCU pointer.

State and persistence behavior: per-TID state lives in `sta->ampdu_mlme.tid_rx[tid]`, `agg_session_valid`, token arrays, and timer bitmaps. Reorder buffers hold queued `sk_buff`s until release. Session timers track inactivity, and reorder timers drive timeout release. Teardown clears the RCU pointer/valid bit, marks removed under `reorder_lock`, synchronously deletes timers, purges queues, and frees via RCU.

Dependencies and integration: this code depends on `sta_info`, `ieee80211_i.h`, `driver-ops.h`, timers, RCU, wiphy work, and action-frame TX helpers. It integrates with RX reorder release paths, driver `ampdu_action`, management frame parsing in `iface.c`, and TX-side helpers for shared ADDBA extension code.

Risks: races between timers, RCU readers, and teardown are the main risk; correct lockdep/wiphy locking is essential. Buffer-size negotiation must stay aligned with HT/HE/EHT limits and driver capabilities. Incorrect duplicate ADDBA handling can leave peers with inconsistent BA state. Memory pressure can reject sessions.

Test signals: interoperability tests with HT/HE/EHT APs, forced DELBA, duplicate ADDBA requests, timeout expiry, hardware-vs-software reorder-buffer modes, S1G NDP BA negotiation, and stress tests around station teardown while timers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/agg-rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/agg-tx.c -->
# sources/distributed-fs/ceph-client/net/mac80211/agg-tx.c

Purpose: this file manages transmit-side A-MPDU Block Ack aggregation sessions. It starts and stops per-station/per-TID TX BA sessions, sends ADDBA and BAR frames, coordinates driver `ampdu_action` callbacks, tracks handshake state bits, gates TXQs while sequence numbers and pending queues are stabilized, and handles peer ADDBA responses.

Important APIs and functions: exported driver/subsystem APIs include `ieee80211_start_tx_ba_session()`, `ieee80211_stop_tx_ba_session()`, `ieee80211_start_tx_ba_cb_irqsafe()`, `ieee80211_stop_tx_ba_cb_irqsafe()`, `ieee80211_refresh_tx_agg_session_timer()`, and `ieee80211_send_bar()`. Internal core routines include `ieee80211_tx_ba_session_handle_start()`, `__ieee80211_stop_tx_ba_session()`, `ieee80211_agg_tx_operational()`, `ieee80211_process_addba_resp()`, and queue/pending helpers such as `ieee80211_agg_splice_packets()`.

Control flow: starting a session validates station capabilities, interface type, hardware flags, retry backoff, MFP authorization, and idle TID state. It allocates `tid_ampdu_tx`, initializes pending queues and timers, assigns a dialog token, stores the object in `tid_start_tx`, and queues station MLME work. The work path moves into `tid_tx`, synchronizes with TX, calls driver `IEEE80211_AMPDU_TX_START`, sends ADDBA immediately or after driver readiness, and starts the response timer. When the driver callback and peer ADDBA response have both arrived, `ieee80211_agg_tx_operational()` notifies `IEEE80211_AMPDU_TX_OPERATIONAL`, marks the TXQ AMPDU-capable, splices pending frames, and clears stop bits.

Stop flow: `ieee80211_stop_tx_ba_session()` marks `WANT_STOP` and queues work. `__ieee80211_stop_tx_ba_session()` validates reason, clears pending start state, sets `STOPPING`, stops the TXQ, deletes timers, clears `OPERATIONAL`, synchronizes network TX paths, calls driver stop actions, and leaves final freeing to `ieee80211_stop_tx_ba_cb()`. Teardown splices pending frames back to local queues, removes the RCU pointer, restarts TXQ, and optionally sends DELBA.

State and persistence behavior: per-TID persistent state lives in `sta->ampdu_mlme.tid_tx`, `tid_start_tx`, retry counters, last request timestamps, dialog token allocator, and `struct tid_ampdu_tx` fields such as `state`, `pending`, `ssn`, `buf_size`, `amsdu`, timers, and NDP flag. Global queue-stop refcounts in `local->agg_queue_stop[]` avoid premature queue wake across concurrent sessions.

Dependencies and integration: this file uses `driver-ops.h`, `wme.h`, TXQ scheduling, station MLME work, action-frame TX helpers, RCU, timers, and shared ADDBA extension parsing from RX aggregation. Rate control and TX code call `ieee80211_start_tx_ba_session()`, and drivers complete setup/teardown via the irqsafe callback exports.

Risks: state-bit ordering and synchronization with lockless TX are delicate. Missing `synchronize_net()` or incorrect queue splicing can reorder frames or leak pending packets. Driver callbacks after stop/destroy must be tolerated. ADDBA response parsing must reject wrong tokens and zero buffer sizes. Retry throttling protects peers that decline aggregation.

Test signals: BA session start/stop under traffic, peer decline and timeout, duplicate/late ADDBA responses, station destroy during teardown, driver delayed callbacks, BAR transmission, S1G NDP BA, and stress tests with many stations/TIDs starting and stopping concurrently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/agg-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/airtime.c -->
# sources/distributed-fs/ceph-client/net/mac80211/airtime.c

Purpose: this file estimates RX, reported TX, and expected TX airtime for mac80211 frames. It converts rate information for legacy, HT, VHT, HE, and EHT encodings into microsecond duration estimates used by scheduling/accounting paths, including TXQ airtime fairness.

Important data and APIs: compile-time macros generate `airtime_mcs_groups[]`, a table of per-MCS average packet durations for stream count, guard interval, and channel width combinations. `struct mcs_group` stores a shift and up to 14 rate durations. Exported functions are `ieee80211_calc_rx_airtime()`, `ieee80211_calc_tx_airtime()`, and `ieee80211_calc_expected_tx_airtime()`. Internal helpers include `ieee80211_calc_legacy_rate_duration()`, `ieee80211_get_rate_duration()`, `ieee80211_fill_rate_info()`, and `ieee80211_fill_rx_status()`.

Control flow: legacy rates are calculated from bitrate, short preamble, CCK status, payload length, preamble/PLCP, and SIFS constants. Non-legacy status is mapped to an MCS table group by encoding, NSS/streams, GI, and bandwidth. The table duration is shifted back, scaled from `AVG_PKT_SIZE` to actual length, divided down from 1024-usec units, and combined with an overhead estimate. `ieee80211_calc_tx_airtime()` iterates `info->status.rates`, computes duration for each retry rate, multiplies by retry count, and stops when a rate is invalid. `ieee80211_calc_expected_tx_airtime()` uses a station's last TX rate when present, applies aggregation overhead reduction heuristics for non-legacy AMPDU, and otherwise falls back to the lowest configured basic rate for the interface.

State and persistence behavior: the only persistent data is the static const rate-duration table. The functions read current wiphy bands, BSS channel context, basic rates, and station `last_rate`/`last_rate_info`; they do not mutate state.

Dependencies and integration: it depends on `<net/mac80211.h>`, `ieee80211_i.h`, and `sta_info.h`. TX scheduling calls expected airtime from `tx.c`, and exported RX/TX calculators can be used by other mac80211 paths or modules. The code relies on nl80211 `rate_info` flags and `ieee80211_rx_status` encoding conventions.

Risks: this is an estimator, not a PHY simulator. Incorrect group index calculation can read wrong table entries; guard checks reject unsupported stream counts and MCS indexes. EHT 320 MHz and high MCS handling must stay aligned with nl80211 enum values. Expected TX aggregation heuristics may under- or over-estimate airtime, affecting fairness rather than correctness.

Test signals: unit tests around known rate/length combinations, boundary tests for every bandwidth/GI/encoding, invalid MCS/NSS handling, TX retry summation, expected-airtime fallback without station, and scheduler behavior under mixed legacy/HE/EHT traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/airtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/cfg.c -->
# sources/distributed-fs/ceph-client/net/mac80211/cfg.c

Purpose: this is the mac80211 implementation of `struct cfg80211_ops`. It translates nl80211/cfg80211 operations into mac80211 interface, key, station, AP, mesh, scan, power, channel, NAN, QoS, measurement, MLO, and driver-callback operations. The exported `mac80211_config_ops` table at the end is the central cfg80211 integration surface registered by `main.c` when creating the wiphy.

Important API surface: major operation groups include virtual interface add/delete/change, P2P/NAN start-stop, key add/delete/get/default selection, AP start/change/stop, station add/change/delete/get/dump, mesh path/config/join/leave, scan and scheduled scan, authentication/association wrappers, TX power and wiphy parameter setting, CQM RSSI config, radar/CAC, channel switch, color change, QoS map and TXQ stats, FTM/PMSR, TID config, SAR, interface links, link stations, hardware timestamping, TTLM, EPCS, and NAN scheduling. Helper functions such as `ieee80211_link_or_deflink()`, `ieee80211_assign_beacon()`, `sta_apply_parameters()`, `sta_link_apply_parameters()`, `cfg80211_beacon_dup()`, `__ieee80211_channel_switch()`, and `ieee80211_color_change()` handle common state transitions.

Control flow: cfg80211 calls enter through `mac80211_config_ops`; most functions convert `wiphy`, `wireless_dev`, or `net_device` to `ieee80211_local` and `ieee80211_sub_if_data`, assert the wiphy mutex where required, validate interface type and link ID, update mac80211 state, call driver ops through `drv_*` wrappers when hardware involvement is needed, and notify BSS/config changes through `ieee80211_link_info_change_notify()` or cfg80211 notification helpers. AP start builds link/channel state, beacon/probe/FILS/unsolicited-probe templates, crypto control-port configuration, HE/EHT/UHR flags, MBSSID data, and driver AP state. AP stop reverses this by clearing RCU template pointers, flushing stations/keys, aborting CAC, stopping the driver, purging PS buffers, and releasing channel contexts.

State and persistence behavior: this file mutates most long-lived mac80211 state: interface flags, monitor flags, NAN config and IDR function registry, key links and default key pointers, beacon/probe/FILS/short-beacon RCU objects, link `bss_conf`, station flags/capabilities/link state, mesh config/path tables, scan state, power-save/SMPS requests, bitrate masks, channel contexts/reservations, CSA/color-change pending beacons, ACK-status IDR entries, QoS maps, TXQ statistics, TID configs, and MLO link bitmaps. RCU is used for templates, keys, station links, and monitor/channel data; timers/work items handle CAC, CSA finalization, color collision/change, and NAN events.

Dependencies and integration: the file depends on cfg80211/nl80211 public structures, mac80211 internals (`ieee80211_i.h`, `rate.h`, `mesh.h`, `wme.h`), driver operation wrappers, station/key/channel/scan/MLME subsystems, and optional Kconfig blocks for mesh, PM, and testmode. It delegates managed-mode auth/assoc/deauth/disassoc to MLME, IBSS/OCB/mesh to their modules, crypto key lifecycle to `key.c`, and hardware-specific work to driver callbacks.

Risks: the blast radius is high because many cfg80211 operations converge here. Link-ID validation for MLO, RCU pointer replacement, beacon template memory layout, station state transitions, and channel context reservation/finalization are especially error-prone. Security-sensitive paths include rejecting WEP/TKIP in FIPS mode, key install ordering, MFP flags, management frame registration, and replay sequence reporting. CSA/color-change interactions must avoid overlapping countdowns and must unblock queues on failure. NAN IDR operations and callbacks need locking discipline to avoid stale cookies or leaks.

Test signals: broad nl80211 integration tests are required. Important scenarios include interface type changes, monitor options while up/down, key install/delete/get/defaults for pairwise/group/MLO links, AP start/change/stop with MBSSID/FILS/FTM/S1G, station add/change/delete including TDLS/NAN/MLO links, mesh path/config operations, scan restrictions while AP beacons, power-save/SMPS CQM changes, bitrate masks preserving basic rates, CAC start/end, CSA and color-change finalization/abort, TXQ stats, NAN function add/delete/match/terminate, and hardware timestamp/TID/SAR operations with missing driver ops returning `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/cfg.c -->
