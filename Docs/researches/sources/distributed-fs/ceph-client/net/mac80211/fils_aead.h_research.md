<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/fils_aead.h -->
# sources/distributed-fs/ceph-client/net/mac80211/fils_aead.h

## Purpose
Declares the FILS AEAD entry points used by mac80211 managed association code to encrypt outgoing FILS association requests and decrypt incoming FILS association responses.

## Important APIs, Types, and Functions
`fils_encrypt_assoc_req(struct sk_buff *skb, struct ieee80211_mgd_assoc_data *assoc_data)` mutates an association request SKB in place by adding AES-SIV overhead and encrypting FILS-protected payload bytes. `fils_decrypt_assoc_resp(struct ieee80211_sub_if_data *sdata, u8 *frame, size_t *frame_len, struct ieee80211_mgd_assoc_data *assoc_data)` decrypts and authenticates a response buffer in place and updates the effective frame length. The header relies on types provided by including translation units, primarily SKB, `ieee80211_sub_if_data`, and `ieee80211_mgd_assoc_data`.

## Control Flow
This header has no control flow beyond include guards. It forms the compile-time contract between FILS crypto implementation and MLME callers.

## State and Persistence
No state is declared here. The stateful contract is that `assoc_data` must already contain the FILS KEK and both nonces for the active association attempt, and callers must treat input frame buffers as mutable.

## Dependencies and Integration Points
Included by `fils_aead.c` and used by managed association code in `mlme.c`. It depends indirectly on `ieee80211_i.h` definitions for the association data structure and on `skbuff` declarations from surrounding includes.

## Risks
The prototypes do not encode key/nonce readiness, minimum frame size, or SKB tailroom expectations; these are runtime obligations. Because the implementation mutates buffers in place, accidental reuse of the original plaintext/ciphertext buffer after failure would be a caller bug. Any future standalone includer may need forward declarations or additional includes if it does not already see the involved struct names.

## Test Signals
Header-level signal is compile coverage from `mlme.c` and `fils_aead.c`. Behavioral signals belong to `fils_aead.c`: successful FILS association, malformed frame rejection, and crypto-authentication failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/fils_aead.h -->
