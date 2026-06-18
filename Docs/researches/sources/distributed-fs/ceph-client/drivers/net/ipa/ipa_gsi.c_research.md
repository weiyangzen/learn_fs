# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_gsi.c

Purpose: provides the IPA-side callbacks consumed by the generic software interface (GSI) layer and a helper for detecting empty endpoint data entries.

Important APIs/functions: `ipa_gsi_trans_complete()` maps a GSI transaction back to the owning `struct ipa` and dispatches completion to `ipa_endpoint_trans_complete()`. `ipa_gsi_trans_release()` dispatches resource release to `ipa_endpoint_trans_release()`. `ipa_gsi_channel_tx_queued()` and `ipa_gsi_channel_tx_completed()` update Linux netdev byte queue accounting for endpoint-backed netdevices. `ipa_gsi_endpoint_data_empty()` treats AP entries with zero channel TLVs as unused config slots.

Control flow: GSI owns transaction progress; when it calls into IPA, this file uses `container_of(trans->gsi, struct ipa, gsi)` or `container_of(gsi, struct ipa, gsi)` and `ipa->channel_map[channel_id]` to find the endpoint. The endpoint module then handles SKB/page ownership and RX replenish. TX queue accounting is conditional on `endpoint->netdev`.

State/persistence: no durable state is owned here. It relies on `ipa->channel_map[]` being populated by endpoint init and netdev pointers being set by modem netdev start/stop.

Dependencies/integration: integrates `gsi_trans`, `gsi`, endpoint callbacks, endpoint config data from `ipa_data`, and netdev BQL helpers (`netdev_sent_queue`, `netdev_completed_queue`).

Risks: stale or missing `channel_map` entries would crash callback dispatch. Queue accounting assumes byte/count values passed by GSI match netdev-visible SKB traffic. Empty endpoint detection is part of endpoint validation semantics; changing it changes which data-table slots are ignored.

Test signals: GSI TX/RX completions reach endpoint handlers, netdev BQL counters advance and complete, and endpoint data arrays with empty AP slots are skipped without invalid endpoint errors.
