# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_reg.h

Purpose: this header defines the shared MAC, TXDMA/RXDMA, protocol, EDCA, WMAC, security, power, EFUSE, firmware, and SDIO local register map and bit masks used by RTL8723BS HAL code.

Important APIs/types/macros: register constants cover system configuration (`REG_SYS_FUNC_EN`, `REG_APS_FSMCO`, `REG_MCUFWDL`, `REG_SYS_CFG`), MAC top (`REG_CR`, `REG_TRXDMA_CTRL`, `REG_HIMR/HISR`), TXDMA/RXDMA (`REG_RQPN`, `REG_AUTO_LLT`, `REG_RXDMA_AGG_PG_TH`), protocol (`REG_FWHW_TXQ_CTRL`, `REG_RRSR`, `REG_MACID_SLEEP`), EDCA/beacon/TSF registers, WMAC filters/CAM/security, EFUSE aliases, response rates, RCR bits, firmware download bits (`MCUFWDL_RDY`, `FWDL_ChkSum_rpt`, `WINTINI_RDY`, `RAM_DL_SEL`), queue mapping helpers, and SDIO device IDs/local registers/interrupt masks.

Control flow and integration: every HAL C file in this subset uses these constants for hardware access. SDIO ops rely on pseudo-address masks/device IDs; init relies on power, DMA, beacon, and interrupt masks; TX/RX paths use queue and RCR constants; firmware download uses MCUFWDL bits.

State and persistence: the header names hardware state but stores none. Its constants define how driver memory state maps to persistent hardware registers during a powered session.

Dependencies: requires `BIT`/`BIT0` style macros from included contexts. It is included via `hal_com.h` and other HAL headers.

Risks and test signals: register-map errors affect low-level hardware behavior and are hard to diagnose. The SDIO address-domain masks must match `_cvrt2ftaddr` logic. Tests should cover firmware download status bits, LLT init, TX page allocation, RX filter maps, beacon timing, CAM writes, SDIO interrupt clear behavior, and local register access in both power-on and power-save modes.
