# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/init.c

Purpose: Implements wl1251 firmware/hardware initialization after boot, programming encryption defaults, firmware templates, memory/data path layout, RX/TX queues, PHY defaults, beacon/power settings, and enabling firmware data paths.

Important APIs and functions: `wl1251_hw_init()` is the exported orchestration entry used by core start. Helper stages include `wl1251_hw_init_hwenc_config()`, `wl1251_hw_init_templates_config()`, `wl1251_hw_init_rx_config()`, `wl1251_hw_init_phy_config()`, `wl1251_hw_init_beacon_filter()`, `wl1251_hw_init_pta()`, `wl1251_hw_init_energy_detection()`, `wl1251_hw_init_beacon_broadcast()`, `wl1251_hw_init_power_auth()`, `wl1251_hw_init_mem_config()`, `wl1251_hw_init_tx_queue_config()`, and `wl1251_hw_init_data_path_config()`.

Control flow: `wl1251_hw_init()` runs a strict sequence of ACX and command operations. It first disables special feature bits and sets the default key, reserves firmware template memory with empty probe/null/PS-poll/QoS/beacon/TIM templates, configures memory, interrogates data-path parameters, applies RX filtering, configures all TX AC queues, applies PHY and connection monitor parameters, configures beacon filtering/coexistence/CCA/beacon DTIM behavior, enables RX and TX data paths on `wl->channel`, and finally authorizes CAM power mode.

State and persistence: The file allocates and stores `wl->target_mem_map` and `wl->data_path`; those pointers are later consumed by RX/TX paths and freed on error or device teardown. It reads firmware-provided memory addresses rather than persisting configuration externally. Initialization mutates firmware state through ACX commands, not disk state.

Dependencies and integration points: Depends on `acx.h` command helpers, `cmd.h` template/data-path commands, `reg.h` constants, and `wl12xx_80211.h` template structure sizes. It integrates with `wl1251_op_start()` in `main.c`, and its produced `target_mem_map` and `data_path` are essential for `tx.c`, `rx.c`, and interrupt handling.

Risks: Several AC queue configuration calls after `wl1251_cmd_configure()` ignore return values for `wl1251_acx_ac_cfg()`, so AC programming failures can be missed. Error paths free allocated objects but do not set all freed pointers to `NULL`, which is manageable because startup fails immediately but still worth checking in future edits. The order of ACX programming is firmware-sensitive and should not be refactored casually.

Test signals: Successful boot logs include firmware boot in `main.c` followed by the `wl1251_info()` line reporting TX/RX block counts. Failure signals are ACX warnings such as template, memory map, data path, or queue configuration failures. Regression testing should exercise start/stop, scan, RX/TX, and PS transitions after boot.
