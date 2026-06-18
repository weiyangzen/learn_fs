# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw.h

## Purpose
Defines the legacy shared 802.11 support layer used by Intel ipw2100/ipw2200 drivers. It provides frame layouts, scan cache records, security/key state, channel geography, crypto operation registration, TX/RX entry points, Wireless Extensions helpers, and the `struct libipw_device` object embedded in each netdev.

## Important APIs, Types, and Functions
Important types include `struct libipw_rx_stats`, `struct libipw_frag_entry`, `struct libipw_security`, 1/2/3/4-address 802.11 headers, management-frame structs, `struct libipw_txb`, QoS element/parameter structs, `struct libipw_network`, `enum libipw_state`, `struct libipw_channel`, `struct libipw_geo`, `struct libipw_crypto_ops`, `struct libipw_crypt_info`, `struct libipw_device`, and `struct libipw_crypt_data`. Public entry points declared here include `alloc_libipw`, `free_libipw`, `libipw_xmit`, `libipw_txb_free`, `libipw_rx`, `libipw_rx_mgt`, geography helpers, scan/key wext helpers, spy handlers, crypto registry calls, and crypto module init/exit functions. Inline helpers compute header length, payload pointer, mode validity, and rate class.

## Control Flow
The header defines contracts rather than executing code. Device drivers allocate a netdev with `alloc_libipw()`, fill mode/frequency/security callbacks and hardware transmit callback, receive data via `libipw_rx()`, receive management frames via `libipw_rx_mgt()`, and hand Ethernet TX through `libipw_xmit()`. Wireless Extensions wrappers call `libipw_wx_*` to expose scan results and configure keys. Crypto modules register `libipw_crypto_ops` that are later looked up by name for WEP/TKIP/CCMP.

## State and Persistence Behavior
`struct libipw_device` is long-lived per network interface and owns network scan lists, a fixed 128-entry network cache, channel geography, security flags and key material, host crypto booleans, WEP/TKIP/CCMP crypt contexts, fragmentation cache, association BSSID/state, mode/frequency capabilities, RSSI calibration, duplicate sequence tracking, spy state, and callback table. The packed frame and information-element structs mirror on-air 802.11 layout. Scan entries keep `last_scanned`, WPA/RSN IEs, QoS/802.11h data, rates, and stats until aged or replaced.

## Dependencies and Integration Points
Depends on Linux netdevice, Wireless Extensions, cfg80211, IEEE 802.11 definitions, SKB, list, spinlock, timer, and module APIs. It is consumed by `ipw2100.c`, `ipw2200.c`, and all `libipw_*` implementation files. It also defines the crypto plugin ABI shared by `libipw_crypto.c`, `libipw_crypto_wep.c`, `libipw_crypto_tkip.c`, and `libipw_crypto_ccmp.c`.

## Risks
The header mixes on-air packed structures, kernel-private runtime state, and exported module APIs, so apparently small layout or semantic changes can affect hardware drivers, wext behavior, and crypto modules. The security model is legacy and state is duplicated between `sec`, `crypt_info`, host crypto booleans, and driver firmware callbacks. Fragment cache limits and duplicate sequence tracking are simple and may drop valid traffic if used outside the assumed station/tasklet path. Include-order and config dependencies matter for Wireless Extensions, debug, and cfg80211 symbols.

## Test Signals
Compile coverage for ipw2100/ipw2200 with WEP/TKIP/CCMP modules, netdev allocation/free, scan result parsing, RX reassembly/decryption, TX fragmentation/encryption, wext key set/get, QoS frame paths, channel geography, spy events, monitor mode, and module unload after delayed crypto deinit are the primary signals.
