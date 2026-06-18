# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_gsi.h

Purpose: declares the IPA-to-GSI callback surface implemented by `ipa_gsi.c`.

Important APIs: transaction callbacks `ipa_gsi_trans_complete()` and `ipa_gsi_trans_release()` are invoked by GSI when transfer work finishes or resources are about to be freed. Channel accounting callbacks `ipa_gsi_channel_tx_queued()` and `ipa_gsi_channel_tx_completed()` report queued/completed byte counts for netdev queue management. `ipa_gsi_endpoint_data_empty()` centralizes the empty endpoint-data predicate used during endpoint initialization.

Control flow: the header has no logic, but it defines the callback contract: GSI gives only a transaction or `(gsi, channel_id)` pair; IPA must recover endpoint context via the parent `struct ipa` and channel map.

State/persistence: no state is defined here. It forward-declares `struct gsi`, `struct gsi_trans`, and endpoint-data records.

Dependencies/integration: included by GSI and IPA endpoint/data code to avoid direct knowledge of endpoint internals in the GSI layer.

Risks: callback signatures are part of the GSI/IPA integration boundary; count/byte semantics must stay aligned with GSI queue accounting.

Test signals: successful compilation of GSI callback registration, TX BQL accounting in modem netdev traffic tests, and endpoint init skipping only intended empty entries.
