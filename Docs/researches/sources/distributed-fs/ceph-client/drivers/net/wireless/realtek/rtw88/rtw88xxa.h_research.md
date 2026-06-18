## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw88xxa.h

Purpose: public declarations and hardware-layout definitions for the rtw88 88xxa common implementation. It defines packed EFUSE layouts, Jaguar PHY status words, bit masks, beacon timing constants, and exported function prototypes.

Important APIs/types: `struct rtw8821au_efuse`, `struct rtw8812au_efuse`, and `struct rtw88xxa_efuse` model the 512-byte logical EFUSE image and include a `static_assert` on size. `struct rtw_jaguar_phy_status_rpt` maps PHY status words `w0` through `w6`; many `RTW_JGRPHY_*` masks extract gain, channel, CFO, EVM, SNR, antenna, and CCK fields. `RF18_BW_MASK` and exported function prototypes form the compile-time contract for chip-specific files.

Control flow and state: no executable flow beyond declarations. Its state model is the binary interpretation of EFUSE and RX PHY report data consumed by `rtw88xxa.c`.

Dependencies and integration: includes byteorder and register definitions. It is included by common code and 88xxa chip files to keep EFUSE parsing, PHY status parsing, and chip ops consistent.

Risks and test signals: packed layout or bit-mask errors silently corrupt MAC address, regulatory, power, antenna, or RSSI interpretation. Test by validating `static_assert`, comparing EFUSE dumps against vendor docs, and checking RX status metrics and MAC address on 8821AU/8812AU hardware.
