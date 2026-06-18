# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_common.h

Purpose: shared constants and bounded memory helper declarations for vidtv.

Important APIs/types/functions: defines 90 kHz and 27 MHz clock constants, mux sleep intervals, and prototypes for `vidtv_memcpy()`/`vidtv_memset()`.

Control flow: header only.

State and persistence: no state.

Dependencies and integration points: included by TS/PES/mux/common code for timing constants and safe writer helpers.

Risks: changing clock constants affects PCR/PTS calculations across mux and PES code. Sleep interval changes affect mux rate buffer sizing and output cadence.

Test signals: build coverage and transport stream timing validation through PCR/PTS analysis.
