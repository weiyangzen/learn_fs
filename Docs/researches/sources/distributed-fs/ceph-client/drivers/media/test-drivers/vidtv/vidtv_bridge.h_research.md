# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_bridge.h

Purpose: bridge state definition for vidtv.

Important APIs/types/functions: defines `NUM_FE` as 1, `VIDTV_PDEV_NAME` as `vidtv`, and `struct vidtv_dvb` containing platform, frontend, DVB adapter, demux/dmxdev, demux frontends, I2C adapter/clients, feed count/lock, streaming flag, mux pointer, and optional media device.

Control flow: no executable flow; `vidtv_bridge.c` uses this structure across probe, feed start/stop, streaming, and remove.

State and persistence: all bridge runtime state is centralized in `struct vidtv_dvb`. The feed lock protects feed-count and streaming transitions.

Dependencies and integration points: includes Linux I2C/platform types and DVB/media demux/frontend/media-device headers, plus `vidtv_mux.h`.

Risks: fixed one-frontend layout limits scaling; the include guard closing comment contains a typo but the macro itself is correct.

Test signals: build coverage and runtime bridge probe/start/stop paths exercising every field.
