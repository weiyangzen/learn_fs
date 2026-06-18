# subset-b-004812 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/ipw2200.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/ipw2200.h

## Purpose
Defines the private hardware, firmware, DMA, queue, command, notification, debug, and driver-state contract for the Intel PRO/Wireless 2200/2915 `ipw2200` driver. It is the central header consumed by `ipw2200.c` and bridges the generic `libipw` 802.11 stack to the device-specific PCI adapter.

## Important APIs, Types, and Functions
Important constants include firmware host command IDs such as `IPW_CMD_SYSTEM_CONFIG`, `IPW_CMD_SCAN_REQUEST`, `IPW_CMD_ASSOCIATE`, `IPW_CMD_WEP_KEY`, `IPW_CMD_RX_KEY`, `IPW_CMD_QOS_PARAMETERS`, and `IPW_CMD_WME_INFO`; status/config bits such as `STATUS_ASSOCIATED`, `STATUS_SCANNING`, `STATUS_RF_KILL_MASK`, `STATUS_SECURITY_UPDATED`, and `CFG_ASSOCIATE`; interrupt bits under `IPW_INTA_BIT_*`; register offsets for CSR, shared SRAM, DMA, TX/RX queues, EEPROM, ordinals, event logs, and error logs; and rate/ordinal/QoS tables. Core types include `struct clx2_queue`, `struct clx2_tx_queue`, `struct ipw_rx_queue`, `struct tfd_frame`, `struct tfd_data`, `struct ipw_rx_packet`, `struct ipw_cmd`, `struct ipw_sys_config`, `struct ipw_associate`, `struct ipw_scan_request_ext`, `struct ipw_fw_error`, `struct ipw_qos_info`, and the large `struct ipw_priv`. Inline helpers `ipw_get_scan_type` and `ipw_set_scan_type` pack two scan types per byte in extended scan requests.

## Control Flow
The header has no standalone execution, but it defines the state machine and ABI used by the C driver. Probe allocates an `alloc_libipw()` netdev whose private tail is `struct ipw_priv`; firmware load and alive response fill `dino_alive` and ordinal table addresses; TX/RX rings are described by `clx2_tx_queue` and `ipw_rx_queue`; interrupts indicate RX transfer, command completion, firmware initialization, RF-kill completion, and fatal errors; work items in `ipw_priv` drive association, scanning, RF-kill polling, restart, QoS activation, link transitions, and stats gathering.

## State and Persistence Behavior
Most packed structures model persistent hardware/firmware layout and must not drift: transmit frame descriptors, RX notification/frame payloads, EEPROM offsets, host command payloads, ordinals, firmware event/error logs, security keys, country info, and association requests. Runtime state persists in `ipw_priv`: PCI MMIO base, DMA queues, wait queues, status/config/capability words, current ESSID/BSSID/channel/rates/security, scan request state, calibration and statistics snapshots, EEPROM image, country code, IBSS duplicate tracking, delayed work, LED timers, command log, suspend timestamps, and optional promiscuous/radiotap state.

## Dependencies and Integration Points
Includes Linux PCI, netdevice, firmware, DMA, wireless extensions, workqueue, radiotap, and `libipw.h`. The C driver uses this header to map `libipw_xmit`, `libipw_rx`, `libipw_wx_*`, and `libipw_set_geo` onto ipw2200 firmware commands and rings. Hardware integration is through packed descriptors and memory/register offsets; user-facing integration is through netdev, wext, cfg80211 wiphy allocation from libipw, debug masks, optional proc/debug interfaces, and RF-kill/power-management state.

## Risks
This file is ABI-sensitive. Changing packing, field sizes, endian annotations, queue sizes, command IDs, interrupt masks, or register offsets can silently break firmware communication or DMA. `struct ipw_priv` mixes IRQ, tasklet, workqueue, and user ioctl/sysfs state, so changes to flags or work ownership can introduce teardown and suspend/resume races. Security state is split between `libipw_security`, firmware key commands, host crypto, and `STATUS_SECURITY_UPDATED`. QoS constants and scan-type packing are coupled to firmware expectations.

## Test Signals
Useful signals include module probe/remove, firmware load/alive response, RX/TX ring setup, interrupt enable/disable, command completion waits, RF-kill transitions, scan and scan abort, association/disassociation/roaming, WEP/TKIP/CCMP key updates, QoS parameter activation, EEPROM/country parsing, suspend/resume, fatal firmware error log dump, debug-mask output, monitor/promiscuous mode where configured, and netdev TX/RX through the `libipw` hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/ipw2200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto.c

## Purpose
Implements the shared crypto algorithm registry and per-device crypto context lifecycle for libipw. It registers a built-in `NULL` algorithm, lets WEP/TKIP/CCMP modules register `libipw_crypto_ops`, and manages delayed destruction of key contexts so RX/TX paths can finish while references are outstanding.

## Important APIs, Types, and Functions
`struct libipw_crypto_alg` links an algorithm name to a `libipw_crypto_ops`. Public functions are `libipw_crypt_info_init`, `libipw_crypt_info_free`, `libipw_crypt_delayed_deinit`, `libipw_register_crypto_ops`, `libipw_unregister_crypto_ops`, `libipw_get_crypto_ops`, `libipw_crypto_init`, and `libipw_crypto_exit`. Internal helpers are `libipw_crypt_deinit_entries`, `libipw_crypt_quiescing`, and `libipw_crypt_deinit_handler`.

## Control Flow
`libipw_crypt_info_init()` clears a per-device `libipw_crypt_info`, stores the caller's lock, initializes the delayed-deinit list, and sets up a timer. Key replacement calls `libipw_crypt_delayed_deinit()`, which unlinks the active key pointer, adds the old context to `crypt_deinit_list`, and starts a one-second timer. The timer frees entries only when their atomic refcount reaches zero, then reschedules while entries remain. Module init registers the `NULL` ops; crypto-specific modules register their own ops; lookup scans the global list under `libipw_crypto_lock`.

## State and Persistence Behavior
Global state is the `libipw_crypto_algs` list guarded by `libipw_crypto_lock`. Per-interface crypto state lives in `libipw_crypt_info`: active key pointers, default TX key index, delayed deletion list, timer, and quiesced flag. `libipw_crypt_info_free()` quiesces delayed deletion, synchronously deletes the timer, force-frees pending entries, and deinitializes all active key slots with module refcount drops.

## Dependencies and Integration Points
Depends on spinlocks, timers, atomic refcounts, module ownership, lists, and allocation. It is called by `alloc_libipw/free_libipw`, `libipw_wx.c`, and the data paths in `libipw_rx.c`/`libipw_tx.c`. Algorithm modules are `libipw_crypto_wep`, `libipw_crypto_tkip`, and `libipw_crypto_ccmp`.

## Risks
The registry lookup returns an ops pointer after dropping the global lock; module lifetime is protected only when users subsequently call `try_module_get`. Delayed deinit depends on every encrypt/decrypt path incrementing and decrementing `refcnt` correctly. If `crypt_quiesced` is set, new delayed entries are not added and the caller has already nulled the active pointer, so shutdown ordering must call force cleanup. `libipw_crypto_exit()` asserts the registry is empty after unregistering NULL, so algorithm exit ordering matters.

## Test Signals
Key replacement under traffic, module unload after active traffic, timer rescheduling with nonzero refcounts, WEP/TKIP/CCMP module load-on-demand, `free_libipw()` with pending delayed entries, duplicate/unknown algorithm lookup, and module init/exit ordering are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_ccmp.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_ccmp.c

## Purpose
Provides host-based CCMP encryption/decryption for libipw using the kernel AEAD crypto API with `ccm(aes)`. It implements the `libipw_crypto_ops` plugin named `CCMP`, including header/MIC insertion, AAD/nonce construction, replay protection, key management, and diagnostic stats.

## Important APIs, Types, and Functions
`struct libipw_ccmp_data` stores the 128-bit temporal key, key-set flag, TX/RX packet numbers, replay/decrypt error counters, key index, AEAD transform, and AAD scratch buffers. Important functions are `libipw_ccmp_init`, `libipw_ccmp_deinit`, `ccmp_init_iv_and_aad`, `libipw_ccmp_hdr`, `libipw_ccmp_encrypt`, `ccmp_replay_check`, `libipw_ccmp_decrypt`, `libipw_ccmp_set_key`, `libipw_ccmp_get_key`, `libipw_ccmp_print_stats`, `libipw_crypto_ccmp_init`, and `libipw_crypto_ccmp_exit`.

## Control Flow
Initialization allocates per-key state and a `ccm(aes)` AEAD transform. TX increments the 48-bit packet number, inserts an 8-byte CCMP header between the 802.11 header and payload, builds the CCM nonce from QoS control, transmitter address, and PN, appends an 8-byte MIC, and encrypts the payload/MIC with AAD covering masked 802.11 header fields. RX validates length, ExtIV, key index, and configured key, reconstructs PN, rejects replays, decrypts/authenticates through AEAD, updates `rx_pn`, then removes the CCMP header and MIC from the SKB.

## State and Persistence Behavior
The per-key context persists TX/RX PN across packets and reports CCMP format, replay, and decrypt error counts through `print_stats`. `set_key()` zeroes most state while preserving key index and AEAD transform, installs the key, optionally seeds RX PN from userspace sequence bytes, and configures auth size and key material in the crypto transform. `get_key()` returns the key and current TX sequence in Wireless Extensions byte order.

## Dependencies and Integration Points
Depends on `crypto_aead`, scatterlists, SKB head/tail operations, IEEE 802.11 header helpers, and libipw's crypto registry. `libipw_wx_set_encodeext()` creates this context for `IW_ENCODE_ALG_CCMP`; `libipw_tx.c` and `libipw_rx.c` invoke it via `encrypt_mpdu` and `decrypt_mpdu`.

## Risks
AAD/nonce construction is tightly coupled to 802.11 header layout, A4, and QoS rules; incorrect masking breaks interoperability. Replay checking assumes one RX PN per key context rather than per TID. Encryption mutates SKBs in place and requires exact headroom/tailroom from the TX allocator. `crypto_alloc_aead` is requested with `CRYPTO_ALG_ASYNC`, but requests are used synchronously without completion callback, so provider behavior matters. Key reset clears counters and PNs.

## Test Signals
Association with WPA2/CCMP, TX/RX encrypted unicast, QoS and non-QoS frames, A4/WDS-form headers if reachable, replay injection, wrong key index, missing ExtIV, MIC failure, seeded RX sequence, crypto provider errors, key replacement during traffic, and module unload after CCMP use are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_ccmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_tkip.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_tkip.c

## Purpose
Implements host-based TKIP for libipw. It supplies the `TKIP` crypto plugin with RC4 key mixing, IV/ExtIV handling, WEP-style ICV encryption, Michael MIC generation/verification, replay protection, countermeasure flags, and Wireless Extensions MIC failure events.

## Important APIs, Types, and Functions
`struct libipw_tkip_data` stores the 32-byte TKIP key, key-set flag, TX/RX TSC fields, cached phase1 TTAK values, pending RX counters awaiting MIC verification, replay/ICV/MIC failure counters, key index, ARC4 contexts, and flags. Important functions include `libipw_tkip_init/deinit`, `tkip_mixing_phase1`, `tkip_mixing_phase2`, `libipw_tkip_hdr`, `libipw_tkip_encrypt`, `tkip_replay_check`, `libipw_tkip_decrypt`, `libipw_michael_mic_add`, `libipw_michael_mic_verify`, `libipw_michael_mic_failure`, key get/set, stats printing, and module init/exit.

## Control Flow
TX first honors TKIP countermeasures by dropping protected packets. It derives/caches phase1 TTAK by transmitter address and IV32, derives the per-packet RC4 seed with IV16, inserts an 8-byte TKIP header, appends a CRC32 ICV, encrypts payload plus ICV with ARC4, and advances TSC. MSDU-level encryption appends an 8-byte Michael MIC before fragmentation/MPDU encryption. RX validates countermeasures, length, ExtIV, key index, key presence, and replay state, decrypts the payload and ICV, stores new TSC in temporary fields, removes IV/ICV, and only commits RX counters after Michael MIC verification succeeds.

## State and Persistence Behavior
Per-key state preserves phase1 cache, TX/RX TSC, counters, and countermeasure flags. `set_key()` clears most state while preserving ARC4 context objects and key index, seeds TX IV16 to 1, and optionally seeds RX TSC from userspace. `get_key()` returns key material and current TX sequence. MIC failures increment local failure stats and send `IWEVMICHAELMICFAILURE` with pairwise/group classification derived from destination address.

## Dependencies and Integration Points
Depends on libipw crypto ops, kernel ARC4, CRC32, SKB mutation, `michael_mic()` from IEEE 802.11 helpers, Wireless Extensions events, and FIPS mode. `libipw_wx_set_encodeext()` loads it for `IW_ENCODE_ALG_TKIP`; `libipw_tx.c` invokes both MSDU and MPDU encryption hooks, while `libipw_rx.c` invokes MPDU decrypt before defragmentation and MSDU MIC verify after reassembly.

## Risks
TKIP is legacy and disabled under FIPS. Replay state is per key context, not per TID. RX counter commit is intentionally delayed until MIC verification; changing that order weakens replay/MIC behavior. In-place SKB edits require exact headroom and tailroom. Michael MIC failure events can trigger supplicant countermeasures, so false positives are user-visible. The phase1 cache must be invalidated correctly on IV32 changes and ICV failures.

## Test Signals
WPA/TKIP association, fragmented and unfragmented TX/RX, QoS data, replayed TSC rejection, bad ICV, bad Michael MIC and user event delivery, countermeasure flag drops, seeded RX sequence, key replacement, FIPS rejection, module unload, and mixed multicast/group key traffic are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_tkip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_wep.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_wep.c

## Purpose
Implements host-based WEP encryption and decryption for libipw as the `WEP` crypto plugin. It handles RC4 key construction from IV plus shared key, IV insertion, ICV generation/verification, simple weak-IV avoidance, key set/get, and stats printing.

## Important APIs, Types, and Functions
`struct libipw_wep_data` stores the transmit IV counter, WEP key bytes and length, key index, and TX/RX ARC4 contexts. Important functions are `libipw_wep_init`, `libipw_wep_deinit`, `libipw_wep_build_iv`, `libipw_wep_encrypt`, `libipw_wep_decrypt`, `libipw_wep_set_key`, `libipw_wep_get_key`, `libipw_wep_print_stats`, `libipw_crypto_wep_init`, and `libipw_crypto_wep_exit`.

## Control Flow
Initialization rejects WEP in FIPS mode, allocates per-key state, records the key index, and randomizes the starting IV. TX requires four bytes of headroom and tailroom, pushes the 4-byte WEP IV/key-index field between header and payload, skips known weak RC4 IV patterns, appends little-endian CRC32 ICV over plaintext payload, and ARC4-encrypts payload plus ICV. RX reads the IV and key index, validates it matches the context key index, derives the ARC4 key, decrypts payload plus ICV, verifies CRC32, then removes IV and ICV from the SKB.

## State and Persistence Behavior
The WEP context persists the IV counter and key bytes for a key slot. `set_key()` accepts lengths up to 13 bytes, copies key material, and updates `key_len`. `get_key()` returns the stored key if the caller buffer is large enough. `deinit()` uses `kfree_sensitive()` to clear key material. There is no replay protection beyond WEP's weak IV mechanics.

## Dependencies and Integration Points
Depends on libipw's crypto registry, kernel ARC4, CRC32, random bytes, SKB head/tail operations, and FIPS status. `libipw_wx_set_encode()` creates WEP contexts for legacy key ioctls, while `libipw_wx_set_encodeext()` handles WEP through the extended API. `libipw_tx.c` and `libipw_rx.c` call this plugin through MPDU encrypt/decrypt hooks.

## Risks
WEP is cryptographically obsolete and disabled in FIPS mode. The code mutates SKBs in place and returns errors if headroom, tailroom, or length assumptions are violated. RX rejects frames whose key index does not match the context, so key-slot selection must match the IV byte. IV wrap and per-key IV reuse remain inherent WEP weaknesses. CRC failure returns a distinct negative value used by the RX debug path.

## Test Signals
Legacy WEP open/shared-key operation, 40-bit and 104-bit keys, default TX key switching, FIPS mode failure, bad ICV drops, wrong key index drops, SKB headroom/tailroom failure, key replacement under traffic, and module load/unload through Wireless Extensions are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_wep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_geo.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_geo.c

## Purpose
Implements channel geography helpers for libipw. It stores regulatory channel maps in `struct libipw_device`, validates channels against the active band and mode, and converts between channels, frequencies, indexes, and channel flags.

## Important APIs, Types, and Functions
Exported functions are `libipw_is_valid_channel`, `libipw_channel_to_index`, `libipw_channel_to_freq`, `libipw_freq_to_channel`, `libipw_set_geo`, `libipw_get_geo`, `libipw_get_channel_flags`, and `libipw_get_channel`. `bad_channel` is a static invalid-channel sentinel returned when lookup fails.

## Control Flow
All helpers first assume the driver has initialized `ieee->geo`. Validation scans 2.4 GHz channels if `freq_band` includes `LIBIPW_24GHZ_BAND`, requiring non-invalid channels and excluding B-only channels when the current mode includes G. It then scans 5 GHz channels if `freq_band` includes `LIBIPW_52GHZ_BAND`. Frequency conversion divides input frequency by 100000 before comparing against stored MHz values, matching Wireless Extensions frequency formatting. `libipw_set_geo()` copies the country name and channel arrays into the device.

## State and Persistence Behavior
State is entirely in-memory in `ieee->geo`, with separate BG and A channel arrays, channel counts, country/name bytes, flags, and max power. No external persistence is performed here; ipw2200 populates geography from EEPROM/country data and calls `libipw_set_geo()`.

## Dependencies and Integration Points
Depends on `libipw.h` types and is used by scan rendering in `libipw_wx.c`, association/channel selection in ipw drivers, and any code needing regulatory flags. The flag values include passive-only, 802.11h, B-only, no-IBSS, uniform spreading, radar detect, and invalid.

## Risks
The lookup logic uses `channel <= LIBIPW_24GHZ_CHANNELS` to decide whether a returned index maps to BG or A arrays; this is correct for normal channel numbering but fragile if unusual channel maps are introduced. `libipw_set_geo()` trusts source channel counts and copies without bounds checks against fixed array sizes. Calling helpers before geography initialization returns invalid/zero values and can suppress scan/association behavior.

## Test Signals
Country/EEPROM geography initialization, 2.4 GHz and 5 GHz channel validation, G-mode exclusion of B-only channels, invalid/radar/passive flags in scan output, frequency-to-channel and channel-to-frequency conversions, missing geography handling, and boundary channel counts are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_geo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_module.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_module.c

## Purpose
Provides libipw module initialization/exit and the allocation/free routines for `libipw_device`-backed netdevices. It also initializes scan cache storage, default 802.11/security behavior, cfg80211 wiphy stubs, crypto plugins, and optional debug procfs controls.

## Important APIs, Types, and Functions
Public functions are `alloc_libipw`, `free_libipw`, and `libipw_networks_age`. Internal helpers include `libipw_networks_allocate`, `libipw_networks_free`, `libipw_networks_initialize`, debug proc handlers, `libipw_init`, and `libipw_exit`. Module metadata describes the `libipw` 802.11 data/management/control stack.

## Control Flow
`alloc_libipw()` allocates an Ethernet netdev with space for `struct libipw_device` plus driver-private tail data. For non-monitor devices it allocates a minimal wiphy, sets station/adhoc interface modes, and attaches `wireless_dev`. It allocates 128 network records, initializes free/active lists, sets default fragmentation/RTS/scan age values, enables host WEP encrypt/decrypt defaults, initializes the device spinlock and crypto info, and returns the netdev. Module init optionally creates `/proc/net/ieee80211/debug_level`, prints version/copyright, and initializes crypto modules in NULL, CCMP, TKIP, WEP order with rollback on failure. Exit removes proc entries and unregisters crypto in the reverse broad order used by this file.

## State and Persistence Behavior
Per-device state initialized here includes scan lists, default open WEP behavior, host crypto flags, 802.1X enablement, WPA/drop/privacy flags, and crypto timers. `libipw_networks_age()` artificially ages active scan records by subtracting jiffies under `ieee->lock`. Debug state is global: `debug`, `libipw_debug_level`, and `libipw_proc`.

## Dependencies and Integration Points
Depends on netdevice allocation, cfg80211 wiphy APIs, procfs/seq_file under `CONFIG_LIBIPW_DEBUG`, net namespace proc root, and crypto modules. ipw2100/ipw2200 call `alloc_libipw()` during probe and `free_libipw()` during remove; TX/RX and wext code rely on the defaults initialized here.

## Risks
The wiphy is intentionally skeletal and lacks device/channel details until the driver later fills them. Allocation failure paths must free partially allocated network and wiphy state. Crypto init rollback ordering must stay aligned with registered modules. `free_libipw()` must run after driver callbacks/work that may use `ieee` are stopped, because it frees crypto state, scan records, wiphy, and netdev memory.

## Test Signals
Module load/unload, non-monitor and monitor netdev allocation, wiphy registration consumers, allocation failure injection, scan cache initialization and aging, debug proc read/write, crypto init rollback, key delayed-deinit cleanup on free, and ipw2100/ipw2200 probe/remove are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_rx.c

## Purpose
Implements libipw receive-side 802.11 processing. It handles monitor delivery, duplicate drops, optional host decryption, fragment reassembly, MSDU MIC verification, IV/ICV stripping for hardware crypto, 802.11-to-Ethernet decapsulation, scan/beacon/probe parsing, QoS IE parsing, network cache maintenance, and management-frame callback dispatch.

## Important APIs, Types, and Functions
Exported functions are `libipw_rx` and `libipw_rx_mgt`. Important internal helpers include monitor delivery, fragment-cache find/get/invalidate, `libipw_is_eapol_frame`, MPDU/MSDU decrypt wrappers, QoS element readers and converters, `libipw_parse_info_param`, `libipw_handle_assoc_resp`, `libipw_network_init`, `is_same_network`, `update_network`, `is_beacon`, and `libipw_process_probe_response`. Static SNAP headers implement RFC1042 and bridge-tunnel decapsulation.

## Control Flow
`libipw_rx()` receives an SKB containing an on-air 802.11 frame. It validates frame length/header length, updates Wireless Extensions spy stats, routes monitor-mode frames directly as `ETH_P_80211_RAW`, selects a crypto context from the IV key index, drops protected frames without a usable key, drops duplicate sequence-control values, derives Ethernet source/destination from ToDS/FromDS bits, filters non-data/null data subtypes, decrypts protected MPDUs, reassembles fragments in a four-entry cache, verifies MSDU-level crypto such as TKIP MIC, rejects unexpected unencrypted payloads except EAPOL, optionally strips hardware-left IV/ICV/MIC bytes, converts LLC/SNAP to Ethernet-II or 802.3 length form, updates netdev stats, and submits via `netif_rx()`. `libipw_rx_mgt()` dispatches management subtypes to driver callbacks and processes beacons/probe responses into the network cache.

## State and Persistence Behavior
RX mutates `ieee->prev_seq_ctl`, `ieee->frag_cache`, netdev RX/drop stats, `ieee->ieee_stats`, spy data, and crypto replay/MIC state. Management parsing updates or allocates entries from `network_free_list` into `network_list`, preserving `last_associate`, QoS active state, and old parameter count while replacing rates, stats, IEs, channel, capability, and 802.11h metadata. Cache replacement evicts the oldest scanned network when the fixed pool is exhausted.

## Dependencies and Integration Points
Depends on SKB APIs, netdevice stats, Wireless Extensions spy, crypto ops from `libipw_crypto_*`, IEEE 802.11 constants, `libipw_geo` for scan output consumers, and driver callbacks in `struct libipw_device`. ipw2100/ipw2200 feed data and management frames from hardware RX handlers into this file.

## Risks
Fragment reassembly is small and tasklet-assumed; stale or malicious fragments can consume entries until the two-second timeout. Duplicate detection uses one previous sequence-control value for the interface, which is simple and may over-drop in mixed traffic. Information-element parsing accepts malformed AP behavior by breaking instead of failing. Hardware crypto stripping relies on `ieee->sec.encode_alg[keyidx]` matching firmware output. In-place decrypt and decapsulation require strict length checks.

## Test Signals
Plain, WEP, TKIP, and CCMP RX; bad key, replay, ICV, and MIC failures; EAPOL exceptions; fragmented protected and unprotected frames; QoS data; monitor mode; RFC1042 and bridge-tunnel payloads; malformed IEs; scan cache insert/update/evict/age; beacon/probe/association callbacks; spy threshold events; hardware-decrypt IV stripping; and netif_rx drop accounting are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_spy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_spy.c

## Purpose
Implements the legacy Wireless Extensions spy API for libipw devices. It lets users configure a small list of MAC addresses to monitor signal quality, read the last quality samples, set threshold triggers, and emit threshold-crossing events.

## Important APIs, Types, and Functions
Exported handlers are `ipw_wx_set_spy`, `ipw_wx_get_spy`, `ipw_wx_set_thrspy`, `ipw_wx_get_thrspy`, and `libipw_spy_update`. Internal helpers are `get_spydata` and `iw_send_thrspy_event`. State lives in `struct iw_spy_data` embedded in `struct libipw_device`.

## Control Flow
`get_spydata()` returns the device spy state only when `ieee->spy_enabled` is true. `ipw_wx_set_spy()` disables spy collection by setting `spy_number` to zero, uses write memory barriers around the address/stat updates, copies up to the user-specified addresses from the wext buffer, clears stats, and re-enables the list length. `ipw_wx_get_spy()` returns configured addresses and their quality records, then clears updated flags. Threshold set/get simply copy low/high quality thresholds. `libipw_spy_update()` is called from RX processing with a source address and quality sample; it updates matching entries and sends `SIOCGIWTHRSPY` when level crosses below low or above high with hysteresis.

## State and Persistence Behavior
State is in-memory only: configured spy addresses, quality samples, thresholds, and per-address under-threshold booleans. No locks are taken in the update path; the code relies on RTNL serialization of wext handlers, temporary `spy_number` disablement, and memory barriers so interrupt/tasklet RX sees consistent enough data.

## Dependencies and Integration Points
Depends on Wireless Extensions, `iw_handler`, `wext`, netdevice, Ethernet helpers, and `libipw.h`. `libipw_rx()` calls `libipw_spy_update()` when spy records are configured and RX stats include signal/noise/quality masks.

## Risks
The lockless design is intentionally approximate and depends on small fixed arrays; extending it without synchronization would be risky. `wrqu->data.length` is assumed to be validated by the wext layer against `IW_MAX_SPY`. Threshold logic uses only `level`, so drivers must populate quality consistently. If `spy_enabled` is not set by the driver, all handlers return `-EOPNOTSUPP`.

## Test Signals
Enable spy support in ipw drivers, set/get zero and multiple spy addresses, RX updates for matching/nonmatching MACs, updated-flag clearing, threshold set/get, low-to-high and high-to-low event hysteresis, concurrent RX during address updates, and disabled-spy error paths are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_spy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_tx.c

## Purpose
Implements libipw transmit-side conversion from Ethernet SKBs to one or more 802.11 SKBs wrapped in a `libipw_txb`. It handles SNAP encapsulation, infrastructure/adhoc addressing, QoS classification, optional MSDU/MPDU host encryption, fragmentation, optional RTS frame insertion, FCS reservation, and handoff to the hardware driver callback.

## Important APIs, Types, and Functions
Exported functions are `libipw_xmit` and `libipw_txb_free`. Internal helpers include `libipw_copy_snap`, `libipw_encrypt_fragment`, `libipw_alloc_txb`, and `libipw_classify`. Static OUIs select RFC1042 or 802.1H bridge-tunnel SNAP encapsulation based on EtherType.

## Control Flow
`libipw_xmit()` first checks queue-full callback and enters `ieee->lock`. It rejects missing hardware transmit callback or too-small SKBs as successful consumption, chooses the active crypto key, decides whether encryption applies while exempting 802.1X EAPOL, drops unencrypted payloads when policy requires, builds a 3-address 802.11 data header for infrastructure or adhoc, optionally adds QoS control and maps IP TOS to TID, strips the Ethernet header, and computes payload bytes including SNAP. If MSDU crypto is needed, it builds a temporary full-frame SKB, adds SNAP and payload, invokes `encrypt_msdu`, and then fragments that encrypted MSDU. It computes fragment size from FTS/RTS/FCS/crypto overhead, allocates a `libipw_txb`, optionally creates an RTS frame, fills each fragment with header/SNAP/payload, encrypts each MPDU if needed, adds FCS reservation, unlocks, frees the original SKB, and invokes `hard_start_xmit`.

## State and Persistence Behavior
TX updates netdev TX packet/byte/error/drop stats, reads `ieee->sec`, `crypt_info.tx_keyidx`, host crypto booleans, `fts`, `rts`, `config`, `tx_headroom`, `bssid`, mode, and callbacks. Crypto contexts mutate per-key IV/PN/TSC state. The produced `libipw_txb` owns fragment SKBs until the hardware driver accepts and later frees it, or until libipw frees it on callback failure.

## Dependencies and Integration Points
Depends on SKB allocation/mutation, netdevice TX API, Ethernet/IP headers, IEEE 802.11 frame constants, libipw crypto ops, and driver callbacks. ipw2100/ipw2200 install `libipw_xmit` as `ndo_start_xmit` and implement `hard_start_xmit` to map `libipw_txb` fragments to firmware TX descriptors.

## Risks
The function consumes or mutates the input SKB even across some no-op success paths, so error semantics are delicate. Fragment-size arithmetic must account for header, FCS, and crypto prefix/postfix or it can overrun fragment buffers. `libipw_alloc_txb()` failure stops the netdev queue and returns busy. Host encryption requires crypto headroom/tailroom and assumes callbacks are synchronous. QoS header layout uses `struct libipw_hdr_3addrqos`, whose payload/qos positioning is unusual and must match existing consumers.

## Test Signals
TX in infrastructure and adhoc modes, queue-full behavior, EAPOL exemption, WEP/TKIP/CCMP host encryption, TKIP MSDU MIC, fragmented unicast, multicast/broadcast no-fragment path, RTS insertion, QoS TID mapping, FCS reserve/compute modes, hard_start_xmit busy/failure, allocation failure, and stats accounting are key validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_wx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_wx.c

## Purpose
Implements shared Wireless Extensions helpers for libipw scan result reporting and key configuration. It translates the internal network cache into wext scan events and maps legacy/extended encode ioctls onto libipw security state and host crypto contexts.

## Important APIs, Types, and Functions
Exported functions are `libipw_wx_get_scan`, `libipw_wx_set_encode`, `libipw_wx_get_encode`, `libipw_wx_set_encodeext`, and `libipw_wx_get_encodeext`. Internal helpers include `elapsed_jiffies_msecs` and `libipw_translate_scan`. Static `libipw_modes` maps internal A/B/G bitmasks to protocol suffix strings.

## Control Flow
`libipw_wx_get_scan()` locks `ieee->lock`, walks `network_list`, filters entries by `scan_age`, and serializes each visible network into wext events: AP address, ESSID, protocol name, mode, frequency, privacy flag, sorted rates, quality, WPA/RSN IEs, last beacon age, and channel flags such as invalid/DFS. `libipw_wx_set_encode()` handles legacy WEP: selects a key index, disables keys or creates a WEP crypto context, pads 40/104-bit keys, updates the default TX key, sets open vs restricted auth, and calls the driver `set_security` callback. `libipw_wx_set_encodeext()` handles WEP/TKIP/CCMP, group-vs-pairwise rules, module autoload, crypto context replacement, key install with RX sequence, TX-key selection, and security-level updates. Getters return key/security state from `ieee->sec`.

## State and Persistence Behavior
The file mutates `ieee->crypt_info.crypt[]`, `tx_keyidx`, `open_wep`, and staged `libipw_security` values passed to the driver callback. Actual persistent device/firmware programming is delegated through `ieee->set_security`. Scan reporting is read-only except for returning buffer length/flags. Crypto replacement uses delayed deinit so old key contexts persist until active references drain.

## Dependencies and Integration Points
Depends on Wireless Extensions stream helpers, module autoload (`request_module`), libipw crypto registry, `libipw_geo` channel conversion/flags, and driver `set_security` callbacks. ipw2100/ipw2200 wext handlers call these functions for `SIOCGIWSCAN`, `SIOCSIWENCODE`, `SIOCGIWENCODE`, and extended encode operations.

## Risks
Wext scan buffer sizing is approximate: it checks `SCAN_ITEM_SIZE` before each network but individual event expansion can vary. Key state is split between host crypto contexts and `ieee->sec`; drivers must honor `sec.flags` correctly. Extended pairwise keys are restricted mostly to infrastructure index 0 except WEP, which may not fit all modern use cases. `get_encodeext()` advertises TX sequence validity for TKIP/CCMP but does not fill a sequence field itself. Legacy WEP zero-key default behavior is surprising but preserved.

## Test Signals
Scan output with many APs, hidden SSIDs, WPA/RSN IEs, stale entries, DFS/invalid channel flags, small user buffers, WEP set/get/disable/default-key switching, TKIP/CCMP set via encodeext with RX sequence, group-key install, pairwise validation errors, crypto module autoload failure, set_security callback contents, and key replacement during traffic are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_wx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-debug.c

## Purpose
Provides Intel 3945-specific debugfs read handlers for firmware/uCode statistics in the `iwlegacy` driver. It formats RX, TX, and general statistics snapshots, including current, accumulated, delta, and max-delta counters, for userspace debug inspection.

## Important APIs, Types, and Functions
The exported integration object is `const struct il_debugfs_ops il3945_debugfs_ops`, with `.rx_stats_read`, `.tx_stats_read`, and `.general_stats_read` assigned to the local handlers. Functions are `il3945_stats_flag`, `il3945_ucode_rx_stats_read`, `il3945_ucode_tx_stats_read`, and `il3945_ucode_general_stats_read`. They read fields from `struct il_priv` under the `_3945` member: `stats`, `accum_stats`, `delta_stats`, and `max_delta`.

## Control Flow
Each debugfs read handler obtains `struct il_priv` from `file->private_data`, returns `-EAGAIN` unless `il_is_alive(il)` is true, allocates a temporary zeroed text buffer sized from the relevant stats structs, formats the statistics flag header, appends rows with `scnprintf`, copies to userspace with `simple_read_from_buffer`, frees the buffer, and returns the read result. RX stats print OFDM, CCK, and general non-PHY counters. TX stats print transmit counters such as preamble, Bluetooth defer/kill, CTS/ACK timeouts, and ack counts. General stats print debug, sleep/slot, timestamp, and diversity counters.

## State and Persistence Behavior
This file does not mutate device state. It reports the latest statistics notification from uCode plus accumulated/delta/max snapshots maintained elsewhere in the iwlegacy 3945 code. Values in current snapshots are little-endian firmware fields converted with `le32_to_cpu`; accumulated/delta/max fields are treated as host-order cached counters.

## Dependencies and Integration Points
Depends on `common.h`, `3945.h`, debugfs file operations, `simple_read_from_buffer`, allocation, endian helpers, `il_is_alive`, and `IL_ERR`. The common iwlegacy debugfs setup consumes `il3945_debugfs_ops` to install chip-specific stats readers.

## Risks
The output buffer sizes are manually estimated; future struct growth or additional fields could truncate output silently through `scnprintf`. The handlers allocate on every read and can return `-ENOMEM`. They do not take an explicit stats lock, so output may reflect concurrently updated mixed snapshots unless the surrounding driver serializes stats updates. Returning `-EAGAIN` for non-alive hardware is expected but user tooling must handle it.

## Test Signals
Read each debugfs stats file while the device is alive, down, resetting, and under traffic; verify current/accum/delta/max formatting, endian conversion of current firmware stats, no buffer overflow/truncation warnings, allocation failure handling, repeated partial reads through `ppos`, and correct registration through common debugfs ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-debug.c -->
