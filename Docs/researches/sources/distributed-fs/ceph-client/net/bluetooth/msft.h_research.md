<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/msft.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/msft.h

Purpose: declares the internal interface for Microsoft Bluetooth extension support and provides no-op fallbacks when `CONFIG_BT_MSFTEXT` is disabled.

Important APIs/types/functions: defines feature masks for BR/EDR RSSI monitor, LE connection RSSI monitor, LE advertising RSSI monitor, LE advertising monitor, curve-validity, and concurrent advertisement monitor support. When enabled, it declares MSFT lifecycle, open/close, vendor-event, feature, monitor, filter-enable, suspend/resume, and curve-validity helpers. When disabled, inline stubs return false, zero, or `-EOPNOTSUPP` as appropriate.

Control flow: callers can invoke MSFT helpers unconditionally; compile-time stubs collapse behavior when the extension is not built. Enabled builds dispatch into `msft.c`.

State and persistence behavior: the header owns no state. Enabled implementations store per-controller state in `hdev->msft_data` and `hdev->msft_curve_validity`; disabled stubs leave controllers without MSFT runtime state.

Dependencies and integration points: integrates with HCI device setup/teardown, adv monitor offload, suspend/resume, and vendor-event dispatch. It depends on Bluetooth core types being visible from include context.

Risks: fallback return values must match caller expectations; for example monitor operations fail with `-EOPNOTSUPP`, while lifecycle functions silently do nothing. New MSFT features require updating both declarations and disabled stubs to keep build configurations consistent.

Test signals: build with and without `CONFIG_BT_MSFTEXT`; disabled builds should compile callers without unresolved symbols and report no MSFT monitor support, while enabled builds should execute the real feature and monitor paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/msft.h -->
