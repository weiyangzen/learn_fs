# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/rx.h

## Purpose
`rx.h` defines wlcore RX descriptor formats, descriptor bit masks, RX alignment modes, packet classes, RSSI bounds, and public RX helper prototypes. It is the shared contract between RX parsing code, hardware-specific status conversion, and firmware command/filter code.

## Important APIs, Types, and Constants
The central type is packed `struct wl1271_rx_descriptor`, matching firmware-provided RX metadata: length, status, flags, rate, channel, RSSI/SNR, timestamp, packet class, HLID, and padding length. Constants define band/encryption/status masks, MIC/decrypt failures, RX buffer size encodings, alignment flags (`RX_BUF_UNALIGNED_PAYLOAD`, `RX_BUF_PADDED_PAYLOAD`), and `enum wl_rx_buf_align`. Public prototypes include `wlcore_rx()`, `wlcore_rate_to_idx()` via implementation naming mismatch in the header's legacy `wl1271_rate_to_idx()`, and PM RX filter helpers.

## Control Flow and Integration
The header has no execution flow, but its definitions drive `rx.c` parsing and hardware-specific descriptor interpretation. Packet classes distinguish management/data/beacon/EAPOL/BA/AMSDU/logger frames. Alignment constants tell `rx.c` how to reserve or pull bytes before passing SKBs up.

## State, Risks, and Test Signals
No state is stored in the header. ABI risk is high because struct packing and bit positions must match firmware exactly. Compile tests, RX descriptor decoding tests on both aligned and blocksize-aligned hardware, and encrypted/MIC-failure packet tests validate this contract.
