# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/Hal8192CPhyReg.h

Purpose: this header defines BB/PMAC/RF register offsets and bit masks used by the RTL8723B PHY and RF configuration code. Despite the 8192C name, the RTL8723BS PHY code includes these shared definitions.

Important APIs/types/macros: it exports register constants for Page 8 RF mode/HSSI/LSSI/TxAGC registers, Page 9 RF mode/path switch, Page A CCK system registers, Page C/D OFDM registers, Page E IQK and TxAGC registers, and RF6052 RF register IDs such as `RF_CHNLBW`. It also defines masks including `bRFMOD`, `b3WireDataLength`, `b3WireAddressLength`, `bRFSI_RFENV`, `bLSSIReadAddress`, `bLSSIReadEdge`, `bLSSIReadBackData`, `bCCKSideBand`, and byte/dword masks.

Control flow and integration: there is no executable code. `rtl8723b_phycfg.c` uses these constants for BB masked reads/writes, RF serial access, channel/bandwidth switching, and TX power index programming. `rtl8723b_rf6052.c` uses the RFENV/HSSI/LSSI masks and `RF_CHNLBW`; `rtl8723b_hal_init.c` uses `rOFDM0_RxDSP` for notch filtering.

State and persistence: the header describes hardware register state but stores none. The masks determine which hardware bits are preserved or overwritten by callers.

Dependencies: depends only on kernel `BIT` macros being available indirectly through including contexts. It is included through HAL/PHY headers.

Risks and test signals: incorrect offsets or masks can corrupt unrelated BB/RF fields. Some constants are legacy or path-B-oriented while this chip is configured as one RF path, so callers must pair them with the correct `hal_com_data.PHYRegDef`. Test signals include successful BB/RF init, correct RF readback, stable channel/bandwidth switching, and expected TxAGC register writes for every supported rate.
