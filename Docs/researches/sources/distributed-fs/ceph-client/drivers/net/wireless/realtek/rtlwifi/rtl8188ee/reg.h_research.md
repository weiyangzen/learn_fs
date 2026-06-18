# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/reg.h

`reg.h` is the RTL8188E/RTL92C-style hardware register and bit-field map used by the RTL8188EE driver. It contains no executable code, but it is the driver-wide ABI to MAC, PCIe, USB-named legacy registers, eFuse/EEPROM, CAM security, DMA queues, interrupts, baseband, OFDM/CCK PHY, RF, wake-on-WLAN, and descriptor-related constants.

Important constants include register offsets such as `REG_SYS_FUNC_EN`, `REG_MCUFWDL`, `REG_HIMR`, `REG_RQPN`, `REG_PCIE_CTRL_REG`, `REG_EDCA_BE_PARAM`, `REG_RCR`, `REG_CAMCMD`, and `REG_TSFTR`; interrupt masks such as `IMR_*`, `HSIMR_*`, and `HSISR_*`; receive filters such as `RCR_*`; EEPROM/eFuse layout constants; rate bitmaps; security CAM encodings; and PHY/RF masks such as `MASKDWORD`, `RFREG_OFFSET_MASK`, and `BRFSI_RFENV`.

There is no control flow, but the definitions encode hardware state transitions for firmware download, TX/RX activation, interrupt delivery, RF path setup, hardware security, and power/clock gating. Persistent device configuration is represented through EEPROM/eFuse offsets and defaults.

The header is included throughout RTL8188EE code and is mapped into rtlwifi common register slots by `sw.c`. Risks are bit-exactness and register drift: wrong offsets or masks can break firmware readiness, interrupts, DMA, CAM security, RF calibration, or power management. Test signals include successful probe, firmware readiness, interrupts, TX/RX, suspend/resume, hardware encryption, eFuse parsing, channel switching, and WoWLAN events.
