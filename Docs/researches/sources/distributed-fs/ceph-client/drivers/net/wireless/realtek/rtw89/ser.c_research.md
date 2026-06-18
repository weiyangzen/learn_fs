# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ser.c

Purpose: implements rtw89 system error recovery. It translates MAC/FW error notifications into a queued state machine that performs L1 recovery, escalates to L2 restart, captures firmware/core-dump data, and coordinates TX/RX pause/resume.

Important APIs/functions: `rtw89_ser_init()` initializes queues, flags, work items, and state tables; `rtw89_ser_deinit()` stops workers; `rtw89_ser_notify()` maps MAC error codes to SER events; `rtw89_ser_recfg_done()` completes L2 mac80211 reconfiguration. Internal state handlers cover idle, L1 pre-reset, TRX reset, HCI recovery, and L2 reset.

Control flow: notifications enqueue `ser_msg` items processed by `ser_hdl_work`. Every event runs the current state's handler; transitions emit state-out and state-in events. L1 recovery stops queues, halts DMA with HCI `mac_lv1_rcvy`, resets HCI, signals firmware M2/M4 stages, and resumes queues. Timeouts escalate to L2. L2 captures reserved PLE and firmware backtrace through indirect MAC memory reads, resets CAM/vif/mac-id state, stops core, restarts hardware with `ieee80211_restart_hw()`, then waits for reconfiguration or timeout.

State and persistence: `struct rtw89_ser` holds state, flags, message list, delayed alarm event, recovery counters, and prehandle flag. Recovery state is transient; counters persist for the device lifetime.

Dependencies/integration: mac80211 queues/restart, HCI ops, MAC error status register protocol, CAM/vif bookkeeping, power-save exit, firmware packet list cleanup, devcoredump.

Risks: message allocation under GFP_ATOMIC can fail; timeout handling can promote recoverable L1 to disruptive L2. L2 forcibly resets lists and CAM mappings, so ordering with WoWLAN/reconfig is sensitive.

Test signals: inject MAC error codes, observe SER debug state transitions, recovery counters, devcoredump availability, TX/RX queue recovery, and successful mac80211 reconfigure completion.
