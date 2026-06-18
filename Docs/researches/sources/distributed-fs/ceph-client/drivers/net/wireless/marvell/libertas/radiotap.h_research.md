# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/radiotap.h

## Purpose
Defines minimal radiotap headers and 802.11 frame-control masks used by Libertas monitor-mode TX and RX paths.

## Important Types And Constants
`struct tx_radiotap_hdr` carries the fixed radiotap header plus rate, tx power, RTS retries, and data retries. `TX_RADIOTAP_PRESENT` marks those fields. Frame-control masks and values define version, type, subtype, ToDS/FromDS combinations, and data/control/management types. `struct rx_radiotap_hdr` carries flags, rate, and antenna signal, with `RX_RADIOTAP_PRESENT`.

## Control Flow And State
No executable code. `tx.c` reads the TX radiotap rate and later fills retry count for TX feedback. `rx.c` prepends an RX radiotap header before delivering monitor-mode frames.

## Dependencies And Integration
Includes `<net/ieee80211_radiotap.h>` and is used by `rx.c` and `tx.c`.

## Risks And Test Signals
Risks include mismatched `it_present` bitmaps, missing alignment/padding handling, and invalid rate conversion. Test signals include monitor-mode packet injection with radiotap rate, radiotap RX visibility in packet capture, and TX feedback retry count updates.
