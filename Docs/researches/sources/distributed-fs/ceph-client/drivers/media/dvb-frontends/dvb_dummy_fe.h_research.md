# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb_dummy_fe.h

### Purpose
`dvb_dummy_fe.h` exposes the attach API for dummy OFDM, QPSK, and QAM DVB frontends.

### Important APIs, Types, And Functions
It declares `dvb_dummy_fe_ofdm_attach()`, `dvb_dummy_fe_qpsk_attach()`, and `dvb_dummy_fe_qam_attach()` when `CONFIG_DVB_DUMMY_FE` is reachable, with inline warning stubs otherwise.

### Control Flow
The header has only Kconfig dispatch. Enabled builds use exported module functions; disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No state is stored here. It depends on Linux DVB frontend headers and `pr_warn()` availability from included kernel headers.

### Integration Points
Bridge or board drivers include this header to create dummy frontend objects while keeping compile-time optionality.

### Risks
Callers must treat `NULL` as a valid disabled-module result. The header exposes no configuration knobs, so behavior is fully determined by `dvb_dummy_fe.c`.

### Test Signals
Build both reachable and disabled Kconfig variants and verify callers properly handle `NULL` attach returns.
