# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/rx.h

Purpose: Documents and defines the wl1251 RX double-buffer protocol and RX descriptor format.

Important APIs and types: Defines alignment macros, descriptor flag masks, modulation bits, PLCP length, packet ID fields, `struct wl1251_rx_descriptor`, and `wl1251_rx()`.

Control flow: Header comments describe the firmware/host RX sequence: firmware interrupts, host reads one of two buffers, host triggers RX acknowledgement, firmware prepares the next packet.

State and persistence: No state in header; constants map firmware descriptor state into driver decisions. Descriptor fields include timestamp, length, flags, type, rate, modulation/preamble, channel/band, RSSI/RCPI/SNR.

Dependencies and integration points: Used by `rx.c`, `wl1251.h`, and allocation of `wl->rx_descriptor` in `main.c`.

Risks: This packed structure must match firmware layout exactly. Any change to alignment, flag masks, or descriptor layout risks corrupt RX parsing.

Test signals: Compile layout compatibility, RX rate/status correctness, encryption/FCS flags, and buffer toggling under sustained receive load.
