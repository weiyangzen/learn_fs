# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/common.h

Purpose: Provides ath6kl shared constants, data-path sizing formulas, LLC/SNAP header layout, crypto enum, common forward declarations, and the buffer allocation prototype.

Important APIs and types: `ATH6KL_MAX_IE` caps IE storage. `ath6kl_printk()` is the printf-annotated logging helper. `ATH6KL_ABI_VERSION` documents host/firmware ABI version. Signal quality metric indexes identify SNR/RSSI/all metrics. `WMI_MAX_TX_DATA_FRAME_LENGTH` and `WMI_MAX_AMSDU_RX_DATA_FRAME_LENGTH` compute WMI data buffer sizes including WMI, Ethernet, and LLC/SNAP headers. `EPPING_ALIGNMENT_PAD` computes HTC frame alignment padding. `struct ath6kl_llc_snap_hdr` is packed DSAP/SSAP/control/OUI/ethertype layout. `enum ath6kl_crypto_type` maps NONE/WEP/TKIP/AES/WAPI bit values. `ath6kl_buf_alloc()` allocates skb buffers.

Control flow: No executable flow is defined. Macros are evaluated by TX/RX and WMI paths for buffer sizing and crypto selection.

State and persistence: No state. Constants form part of the host/firmware interface contract and data-path memory layout.

Dependencies and integration points: Includes `linux/netdevice.h` and references WMI data headers, Ethernet headers, HTC frame headers, HTC credit distribution types, ath6kl core types, and HT capability structures. Used widely by core, WMI, TX/RX, cfg80211, and HTC code.

Risks: Buffer length macros must match firmware frame format; underestimation can overflow or truncate frames, while ABI version mismatches can hide incompatible firmware changes. Crypto enum values are consumed by WMI firmware commands and must not be renumbered casually.

Test signals: Compile consumers, validate TX/RX maximum frame handling, AMSDU receive buffer sizing, WMI crypto command values, ABI compatibility checks, and skb allocation behavior at maximum sizes.
