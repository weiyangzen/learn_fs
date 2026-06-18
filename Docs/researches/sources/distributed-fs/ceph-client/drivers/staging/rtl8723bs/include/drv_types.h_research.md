# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/drv_types.h

Purpose: this is the central RTL8723BS driver type aggregation header. It pulls in the common Wi-Fi, MLME, xmit, recv, power, IO, security, EFUSE, event, cfg80211, and HAL headers and defines the top-level runtime objects.

Important APIs/types/macros: `struct registry_priv` stores module/registry configuration such as wireless mode, channel, power, HT/AMPDU, WMM/UAPSD, antenna, TX power, firmware power-save, and queue options. `struct dvobj_priv` represents the shared device object, including primary adapter, hardware locks, CAM cache, pipe mapping, IO error counters, power control, traffic stats, and `sdio_data`. `struct adapter` is the per-interface root object containing MLME, command/event, IO, xmit, recv, station, security, registry, EEPROM, HAL data, netdev, firmware readiness, removal/stop flags, and debug knobs. Macros include `GET_PRIMARY_ADAPTER`, `adapter_to_dvobj`, `adapter_to_pwrctl`, `RTW_CANNOT_IO/RX/TX`, and `myid`.

Control flow and integration: all HAL C files in this subset include `drv_types.h` directly or indirectly. HAL init reads registry options, stores HAL state through `HalData`, and checks adapter stop/removal flags. SDIO ops use `dvobj_priv.intf_data`; TX/RX paths use adapter xmit/recv substructures.

State and persistence: this header defines the in-memory persistence boundary for the driver. `adapter`, `dvobj_priv`, `registry_priv`, and substructures retain state across operations until interface teardown.

Dependencies: extremely broad, including Linux networking headers and most local Realtek subsystem headers. Include ordering is significant and can hide circular dependencies.

Risks and test signals: because this header couples most subsystems, small type changes have wide compile and behavioral impact. Tests should include full driver build, probe/remove, multi-interface assumptions, power transitions, TX/RX disable flags, and registry option combinations such as `wifi_spec`, `ant_num`, and TX power controls.
