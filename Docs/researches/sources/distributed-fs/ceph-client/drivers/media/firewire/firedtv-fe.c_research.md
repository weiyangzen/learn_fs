# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-fe.c

Purpose: Builds the FireDTV DVB frontend operations table and translates DVB frontend callbacks into AV/C tuner, LNB, and isochronous stream operations.

Important APIs/types/functions: `fdtv_dvb_init()` establishes a FireWire CMP point-to-point connection and starts isochronous reception. `fdtv_sleep()` stops isochronous reception and breaks CMP. `fdtv_diseqc_send_master_cmd()`, `fdtv_set_tone()`, and `fdtv_set_voltage()` update LNB state/commands. Status/stat readers call `avc_tuner_status()`. `fdtv_set_frontend()` calls `avc_tuner_dsd()`. `fdtv_frontend_init()` fills `fdtv->fe.ops` and capabilities for DVB-S, DVB-S2, DVB-C, or DVB-T models.

Control flow: Frontend init is called during DVB adapter registration after the model type was detected. Opening the frontend chooses an isochronous channel from adapter number, establishes CMP on the model subunit, and starts the FireWire ISO context. Tuning encodes current properties into AV/C. Status reads fetch a fresh tuner-status descriptor and map `no_rf` to no lock or otherwise report full lock. Sleep tears down ISO/CMP and resets `isochannel` to -1.

State and persistence: Runtime state includes `fdtv->isochannel`, cached voltage/tone values, frontend ops/info, and model type. Hardware state is live FireWire/CMP and AV/C tuner state.

Dependencies/integration: Depends on DVB frontend APIs, FireDTV AV/C/CMP helpers, and FireWire ISO backend functions. It is the interface between DVB frontend core and the FireDTV transport layer.

Risks and test signals: Test every model type's delsys/caps/frequency limits, init failure when CMP or ISO start fails, sleep after partial init, DiSEqC command forwarding, tone/voltage defaults before first tune, status behavior for `no_rf`, unsupported ucblocks, and model detection failure. Isochannel selection is a FIXME and uses adapter number rather than IRM allocation, so multi-device/channel collision tests matter.
