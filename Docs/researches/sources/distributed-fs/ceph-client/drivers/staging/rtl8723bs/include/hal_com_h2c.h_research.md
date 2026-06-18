# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_h2c.h

Purpose: this header defines shared host-to-controller command payload lengths and the reserved-page location structure used when communicating with RTL8723B firmware.

Important APIs/types/macros: constants include `H2C_RSVDPAGE_LOC_LEN`, `H2C_MEDIA_STATUS_RPT_LEN`, `H2C_PWRMODE_LEN`, `H2C_PSTUNEPARAM_LEN`, `H2C_MACID_CFG_LEN`, and `H2C_RSSI_SETTING_LEN`. `struct rsvdpage_loc` records firmware reserved-page offsets for probe response, PS-Poll, null data, QoS null, and BT QoS null frames.

Control flow and integration: this header has no code. `rtl8723b_hal_init.c` includes it for firmware variable initialization and H2C-related operations. `sdio_halinit.c` includes it for BT/WLAN calibration H2C command use. Reserved-page download and firmware power-mode helpers rely on these sizes and locations when packaging commands.

State and persistence: H2C payloads are transient command buffers sent to firmware. Reserved-page locations may be cached while firmware is running, but the header only defines shape and sizes.

Dependencies: no heavy dependencies beyond local include ordering. It is intentionally small and common to HAL command code.

Risks and test signals: payload length constants must match firmware expectations exactly; off-by-one command buffers can corrupt adjacent H2C boxes or be ignored. Tests should verify firmware accepts power mode, PS tune, media status, MACID config, and reserved-page commands, especially after firmware download and after low-power transitions.
