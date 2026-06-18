# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ser.h

Purpose: declares the rtw89 SER lifecycle and notification interface.

Important APIs: `rtw89_ser_init()` and `rtw89_ser_deinit()` set up and tear down the recovery worker state. `rtw89_ser_notify()` is the exported path for MAC/FW error codes. `rtw89_ser_recfg_done()` is called when L2 restart reconfiguration has completed.

Control flow/integration: code that detects hardware or firmware errors includes this header to notify the SER state machine. Core restart/reconfiguration code calls the done hook to unblock L2 recovery.

State and persistence: no state is defined here; it relies on `struct rtw89_dev` and embedded `struct rtw89_ser` from `core.h`.

Dependencies: includes `core.h` for the device structure and kernel integer types.

Risks/test signals: interface drift breaks error-reporting call sites. Build coverage and simulated MAC error tests validate the declarations and event mapping.
