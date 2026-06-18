# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/commands.h

Purpose: declares the qtnfmac firmware command interface used by core, cfg80211 operations, and netdev paths. It is the public boundary for the QLINK command plane implemented in `commands.c`.

Important APIs/types/functions: prototypes cover firmware init/deinit, hardware/MAC/band capability discovery, VIF add/change/delete/up/down, AP start/stop, management frame registration/transmit/app IE setup, station info and station changes, key management, scan/connect/disconnect/external auth, regulatory notifications, channel stats/channel switch/channel get/CAC, MAC ACL, power-management and TX-power control, WoWLAN configuration, bridge upper-device notification, and OWE updates.

Control flow: callers include cfg80211 hooks and core attach/detach. Most functions synchronously build and send one firmware command and return Linux errno-style status. Some functions return data through caller-provided output structures such as `station_info`, `survey_info`, `cfg80211_chan_def`, `int *dbm`, or cached fields inside `qtnf_wmac`/`qtnf_bus`.

State and persistence: the header owns no state, but its API exposes operations that mutate firmware state and host runtime caches. It includes `core.h` and `bus.h`, making `struct qtnf_vif`, `struct qtnf_wmac`, and `struct qtnf_bus` part of the interface contract.

Dependencies and integration points: depends on Linux `nl80211.h` and cfg80211 data types from included headers. It is consumed by `core.c`, `cfg80211.c`, event responses, and transport bringup paths that need to initialize or tear down firmware.

Risks: this broad synchronous API couples cfg80211 semantics tightly to firmware QLINK support. Prototype changes have wide blast radius. Callers must pass initialized VIF/MAC/bus pointers and must respect command context constraints because implementations allocate memory and take the bus lock.

Test signals: compile coverage is important because this header is the shared contract. Runtime signals are successful core attach capability discovery, VIF creation/deletion, AP/STA workflows, scan completion, key programming, regulatory handling, and no lockdep warnings around command calls.
