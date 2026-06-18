# sources/distributed-fs/eos/namespace/ns_quarkdb/QClPerformance.hh

Purpose: declares `QClPerfMonitor`, a qclient callback implementation for collecting QuarkDB RTT metrics.

Important APIs/types/functions: constructor initializes min/max/avg, `SendPerfMarker` receives performance callbacks, and `GetPerfMarkers` returns a metrics map. State includes atomic min/max/avg, timestamp-to-peak map, and mutex.

Control flow: callback and collection methods are implemented in the `.cc`.

State and persistence: transient process-local metrics only.

Dependencies and integration: derives from `qclient::QPerfCallback`; returned through namespace group performance monitor.

Risks: callback must stay fast because qclient invokes it from its event loop. The internal map is small but still mutex-protected inside callback.

Test signals: integration monitoring can validate marker emission and returned keys.
