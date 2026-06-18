# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/Makefile

Purpose: Kbuild recipe for vidtv's virtual DVB modules.

Important APIs/types/functions: builds `dvb-vidtv-tuner.o`, `dvb-vidtv-demod.o`, and `dvb-vidtv-bridge.o`; the bridge module links `vidtv_bridge.o`, `vidtv_common.o`, `vidtv_ts.o`, `vidtv_psi.o`, `vidtv_pes.o`, `vidtv_s302m.o`, `vidtv_channel.o`, and `vidtv_mux.o`.

Control flow: enabling `CONFIG_DVB_VIDTV` builds all three modules. The bridge module depends on the mux, channel, PES, PSI, TS, and S302M pieces for transport stream generation.

State and persistence: build metadata only.

Dependencies and integration points: module names match `dvb_module_probe()` calls in `vidtv_bridge.c` for `dvb_vidtv_tuner` and `dvb_vidtv_demod`.

Risks: object/module naming mismatches prevent bridge probe from loading its virtual tuner/demod clients. Bridge object omissions break runtime stream generation.

Test signals: module link/load, `modprobe dvb_vidtv_bridge` causing tuner/demod probe, and symbol resolution for all vidtv helper objects.
