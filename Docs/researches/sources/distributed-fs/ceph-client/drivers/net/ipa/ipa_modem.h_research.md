# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_modem.h

Purpose: declares the modem netdev and SSR integration surface for the IPA driver.

Important APIs: `ipa_modem_start()` and `ipa_modem_stop()` create/destroy the modem network device; `ipa_modem_skb_rx()` is the endpoint RX delivery callback; `ipa_modem_suspend()` and `ipa_modem_resume()` coordinate endpoint suspend/resume with runtime PM; `ipa_modem_config()` and `ipa_modem_deconfig()` manage SSR notifier registration.

Control flow: QMI readiness calls start; driver remove and crash handling call stop; endpoint RX completion calls SKB RX; power runtime suspend/resume calls modem suspend/resume when the netdev exists.

State/persistence: state is opaque to this header and lives in `ipa_modem.c` via netdev private data and `ipa` fields.

Dependencies/integration: forward-declares `struct ipa`, `struct net_device`, and `struct sk_buff` for use by endpoint, power, main, and QMI code.

Risks: callers must respect lifecycle: no SKB RX after endpoints clear their `netdev` pointer, and start/stop are serialized in implementation.

Test signals: modem netdev starts after handshake, packet RX path compiles without circular dependencies, and runtime PM hooks can call suspend/resume safely when netdev is down.
