# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_vnd.h

Purpose: Declares the virtual RMNET net_device API used by handlers, MAP command processing, and configuration code.

Important APIs: Creation and deletion are exposed through `rmnet_vnd_newlink()` and `rmnet_vnd_dellink()`. Data path helpers include RX/TX stat fixups and flow control. Device lifecycle/configuration helpers include `rmnet_vnd_setup()`, `rmnet_vnd_validate_real_dev_mtu()`, and `rmnet_vnd_update_dev_mtu()`.

Control flow and integration: `rmnet_map_command.c` uses `rmnet_vnd_do_flow_control()`. `rmnet_handlers.c` uses RX/TX fixups. RMNET rtnetlink/config code calls setup and link lifecycle helpers.

State and persistence: The header declares functions that mutate endpoint tables, virtual net_device private fields, queue state, and per-cpu stats, but defines no state itself.

Risks and test signals: Prototype drift can break boundaries between config and data path. Compile coverage should include RMNET as module/built-in, and runtime tests should verify callers observe correct endpoint and MTU behavior.
