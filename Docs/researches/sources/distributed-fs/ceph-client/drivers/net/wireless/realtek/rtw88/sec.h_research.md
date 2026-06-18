## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sec.h

Purpose: declares security CAM registers, command/config bits, and exported security helpers for rtw88.

Important APIs/types: constants include `RTW_SEC_CMD_REG`, `RTW_SEC_WRITE_REG`, `RTW_SEC_READ_REG`, `RTW_SEC_CONFIG`, CAM entry shift, default-key count, write/clear/poll command bits, TX/RX decrypt enable bits, default-key search bits, and `RTW_SEC_ENGINE_EN`. Prototypes expose CAM allocation, write, clear, backup, and engine enable functions.

Control flow and state: no local runtime flow. The constants define how `sec.c` builds CAM write commands and toggles MAC security features.

Dependencies and integration: included wherever rtw88 key installation, hardware crypto, or WoWLAN CAM backup needs security register definitions. It depends on core `struct rtw_dev`, `rtw_sec_desc`, mac80211 station/key types through included headers.

Risks and test signals: register-bit mistakes can disable encryption/decryption or corrupt CAM. Test by compiling all users, verifying encrypted traffic offload, checking CAM backup counts, and validating key removal clears hardware entries.
