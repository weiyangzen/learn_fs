## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/decl.h

Purpose: this shared declaration header connects Libertas source files without pulling in all implementation headers.

Important types and APIs: `struct lbs_fw_table` maps card models to helper/main firmware names. `lbs_fw_cb` is the async firmware completion callback type. The header declares ethtool ops, TX/RX entry points, card lifecycle (`lbs_add_card()`, `lbs_remove_card()`, `lbs_start_card()`, `lbs_stop_card()`), interface lifecycle/type changes, multicast, suspend/resume, event/command response notifiers, rate conversion, and firmware loading helpers.

Control flow and integration: bus drivers use card and firmware helpers; core main code uses TX/RX and cfg/command declarations; firmware loading callbacks return helper/main firmware to bus-specific setup. This header is a central dependency for `dev.h`, `cmd.c`, `cfg.c`, `firmware.c`, and bus frontends.

State and persistence: no state is defined. Firmware table entries are normally static const arrays in bus code; returned firmware references must be released by callers according to the API.

Risks and tests: broad declaration headers can hide dependency cycles and stale prototypes. Test signals are full Libertas build across USB/SDIO/SPI and firmware load paths for one-stage and two-stage devices.
