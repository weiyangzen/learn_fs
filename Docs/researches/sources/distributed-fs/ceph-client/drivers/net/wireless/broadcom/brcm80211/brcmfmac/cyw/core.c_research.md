# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/core.c

Purpose: Provides Cypress/Infineon firmware-vendor operations for brcmfmac, especially SAE/external authentication, CYW event-code mapping, `event_msgs_ext` activation, and cfg80211 auth management-frame overrides.

Important APIs/types/functions: Defines CYW firmware event numbers and `brcmf_cyw_ops` with `set_sae_password`, `alloc_fweh_info`, `activate_events`, `get_cfg80211_ops`, and `register_event_handlers`. Main functions: `brcmf_cyw_mgmt_tx()`, `brcmf_cyw_external_auth()`, `brcmf_cyw_notify_ext_auth_req()`, `brcmf_notify_auth_frame_rx()`, and `brcmf_notify_mgmt_tx_status()`.

Control flow: Vendor attach allocates a CYW-sized FWEH table and maps abstract events to firmware codes. Event activation sends an `event_msgs_ext` mask. The mgmt_tx hook passes non-auth frames to generic cfg80211 but converts auth frames into `mgmt_frame` bsscfg iovar calls and waits for TX status events. External-auth events become cfg80211 requests/RX management frames, and TX/off-channel events complete pending auth TX.

State and persistence behavior: Runtime state lives in FWEH info, mutated cfg80211 ops, vif management TX status bits/completion/id, and firmware iovar state. No filesystem persistence.

Dependencies and integration points: Plugs into fwvid, FWEH, FWIL, cfg80211 external auth, and generic brcmf cfg80211 code.

Risks: Authentication flow is timing-sensitive. Packet id is zero, so firmware status matching must be consistent. `brcmf_notify_auth_frame_rx()` computes `mgmt_frame_len` before length validation, though it returns before allocation on short events. Ops mutation assumes the generic ops table is writable.

Test signals: WPA3/SAE association, non-auth mgmt TX fallback, SAE password length rejection, `event_msgs_ext` programming, auth-frame RX, TX status success/failure/timeout.
