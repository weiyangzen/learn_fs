<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/wlan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/wlan.h

Purpose: Describes the shared AR9170 WLAN descriptor, rate, encryption, RX status, TX control, and hardware queue layout used by carl9170 host code and firmware.

Important APIs/types/functions: Defines RX/TX PHY rate constants, encryption algorithm constants, RX status/error bits, TX MAC/PHY control bits, `_carl9170_tx_superdesc`, `_ar9170_tx_hwdesc`, `_carl9170_tx_superframe`, `ar9170_rx_head`, `ar9170_rx_phystatus`, `ar9170_rx_macstatus`, RX frame shape structs, `ar9170_get_decrypt_type()`, and `enum ar9170_txq`.

Control flow: No runtime flow except inline decrypt-type extraction. The descriptors drive `rx.c` parsing and `tx.c` superframe construction.

State and persistence: Defines packed wire-format structures and constants. It carries no runtime state but changes are ABI-sensitive between driver and firmware.

Dependencies and integration points: Includes `fwcmd.h`, is consumed by carl9170 RX/TX paths, and mirrors firmware-side definitions under `__CARL9170FW__`.

Risks and test signals: Primary risks are packed layout drift, endian mistakes, mismatched bit definitions, and the documented hardware limitation where QoS and aggregation cannot safely use independent hardware queues. Test signals are compile-time `BUILD_BUG_ON()` checks, working RX rate/status decoding, TX encryption/rate control, and stable A-MPDU operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/wlan.h -->
