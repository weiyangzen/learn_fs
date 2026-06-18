# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_timesync.h

Purpose: declares the internal QAIC timesync service interface.

Important APIs and types: includes MHI declarations and exposes `qaic_timesync_init`, `qaic_timesync_deinit`, and `qaic_mqts_ch_stop_timer`.

Control flow: the main driver registers/de-registers both timesync MHI drivers through this API and calls the stop helper from suspend to quiesce the periodic timer.

State and persistence: none in the header. Runtime state is allocated per MHI channel by `qaic_timesync.c`.

Dependencies and integration: intentionally small coupling point between `qaic_drv.c` and the timesync implementation.

Risks and test signals: build coverage should ensure suspend code handles absent `mqts_ch` safely and init/deinit ordering remains paired.
