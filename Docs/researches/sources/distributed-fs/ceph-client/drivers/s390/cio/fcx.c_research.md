# sources/distributed-fs/ceph-client/drivers/s390/cio/fcx.c

Purpose: provides exported helper functions for constructing and finalizing FCX transport-command-word control blocks.

Important APIs/types/functions: getters and setters include `tcw_get_intrg()`, `tcw_get_data()`, `tcw_get_tccb()`, `tcw_get_tsb()`, `tcw_set_intrg()`, `tcw_set_data()`, `tcw_set_tccb()`, and `tcw_set_tsb()`. Builders include `tcw_init()`, `tccb_init()`, `tsb_init()`, `tccb_add_dcw()`, `tcw_add_tidaw()`, and `tcw_finalize()`. Internal helpers compute TCA size, DCW data counts, and CBC padding for output TIDALs.

Control flow: callers initialize TCW/TCCB/TSB, add DCWs and optional TIDAWs, set pointers, and call `tcw_finalize()`. Finalization terminates the TIDAW list, writes a TCAT into the TCCB, computes input/output counts, transport count, CBC padding, and `tccbl`.

State and persistence behavior: functions mutate caller-supplied memory only. Address fields are converted through DMA32/DMA64 virtual-address helpers and have no persistent backing beyond the supplied buffers.

Dependencies and integration points: consumed by transport-mode CCW drivers and `itcw.c`; relies on `asm/fcx.h` layout contracts, DMA address conversion helpers, Linux error pointers, and exported symbols for loadable modules.

Risks and test signals: buffer sizing and alignment are caller-sensitive. `tcw_finalize()` assumes TCCB `tcal` is current and TIDAW storage is contiguous without TTICs. Tests should cover DCW chaining and non-chaining, `-ENOSPC`, read and write counts, output TIDAL CBC insertion, zero TIDAWs, and pointer round-trips through DMA helpers.
