# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_endpoint.h

Purpose: declares the IPA endpoint model, endpoint names, configuration structures, replenish state flags, and public endpoint lifecycle/data-path APIs used by the rest of the driver.

Important APIs/types: `enum ipa_endpoint_name` gives stable logical names for AP and modem command/data endpoints. `struct ipa_endpoint_tx` describes TX sequencer and status destination. `struct ipa_endpoint_rx` describes RX buffer sizing, alignment, aggregation timeout/limits, EOF close, and HOL drop behavior. `struct ipa_endpoint_config` combines resource group, checksum, QMAP, aggregation, status, DMA mode, and direction-specific configuration. `struct ipa_endpoint` is the runtime object tying an IPA endpoint to a GSI EE/channel/event ring, default config, optional netdev, and RX replenish work.

Control flow: this header exposes the operations used by the probe/setup path (`ipa_endpoint_init`, `config`, `setup`, `enable_one`, `disable_one`, `teardown`, `exit`), runtime PM (`suspend`, `resume`), modem crash recovery (`modem_pause_all`, `modem_exception_reset_all`, `modem_hol_block_clear_all`), routing (`default_route_set/clear`), netdev TX (`skb_tx`), and GSI callbacks (`trans_complete`, `trans_release`).

State/persistence: persistent endpoint state is represented by bitmaps in the parent `struct ipa` plus fields in `struct ipa_endpoint`. `replenish_flags` separates whether RX replenishment is enabled from whether a replenish loop is active. `replenish_work` is global workqueue delayed state and must be cancelled during teardown.

Dependencies/integration: includes register/version definitions for sequencer and version-sensitive config values, Linux workqueue/types, and forward-declares GSI transactions, netdev, SKB, IPA, and data-table endpoint records.

Risks: the endpoint-name enum is used as an index into data arrays and `ipa->name_map`; ordering changes require coordinated config data updates. The direction-sensitive union in `ipa_endpoint_config` must match `toward_ipa`. RX buffer and aggregation comments document constraints enforced in the C file and data tables.

Test signals: compile-time users should include this header without circular dependencies, every required endpoint name maps to a non-empty config, runtime setup sets AP command/LAN/modem endpoint objects, and netdev endpoints have expected QMAP/checksum capabilities.
