# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/sdio_mcu.c

Purpose: SDIO-specific MCU transport and power-ownership control for MT7663S.

Important APIs and functions: `mt7663s_mcu_init_sched()` reads PSE/PLE quotas and TX descriptor count into `sdio->sched`. `mt7663s_mcu_send_message()` fills the mt7615 MCU descriptor and sends the skb on the WM MCU queue. `__mt7663s_mcu_drv_pmctrl()` clears firmware ownership via `WHLPCR_FW_OWN_REQ_CLR` and polls for driver ownership. `mt7663s_mcu_fw_pmctrl()` sets firmware ownership via `WHLPCR_FW_OWN_REQ_SET`, using `mt76_connac_skip_fw_pmctrl()` to avoid sleeping with tokens or wake refs. `mt7663s_mcu_init()` installs mt76 MCU ops, restarts firmware if N9 is already ready, loads firmware, clones mt7615 MCU ops to override PM callbacks, initializes SDIO scheduling, and marks MCU running.

Control flow: SDIO init first forces driver ownership, sets low-level MCU ops, handles pre-existing firmware state, loads firmware with `__mt7663_load_firmware()`, then patches the high-level `dev->mcu_ops` PM functions to SDIO-specific ownership routines.

State and persistence: Updates `MT76_STATE_PM`, `MT76_STATE_MCU_RUNNING`, PM wake/doze timestamps and counters, SDIO scheduler quotas/deficit, and firmware ownership state in WHLPCR. Firmware image persists only in device memory after load.

Dependencies: mt76 SDIO register helpers, Connac PM helpers, mt7615 MCU parser/fill logic, firmware loader, and register definitions for PSE/PLE/PP/CONN.

Risks: Ownership polling timeouts leave the host and firmware disagreeing about who may access registers. PM stats are updated only after successful transitions. Cloning `dev->mcu_ops` assumes base MCU init populated all required callbacks before override. Firmware restart polling on `MT_CONN_ON_MISC` must match chip state bits.

Test signals: Firmware load on SDIO, successful driver/firmware ownership transitions, PM doze/awake stats, SDIO scheduler values, MCU command replies, and resume from low power without command timeouts.
