# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-dummy-fe.c

Purpose: provides a synthetic DVB-C frontend for ddbridge debug/test configurations. `ddbridge_dummy_fe_qam_attach()` allocates a small state object, copies a static `dvb_frontend_ops`, stores the state in `demodulator_priv`, and exports the symbol for `ddbridge-core.c` dummy tuner attachment.

Important APIs/types/functions: `struct ddbridge_dummy_fe_state` embeds `struct dvb_frontend`. The frontend ops implement `init`, `sleep`, `set_frontend`, `get_frontend`, `read_status`, BER, strength, SNR, uncorrected block reads, and `release`. `read_status()` always reports full lock; metrics return zero; `set_frontend()` only forwards to an attached tuner if one exists.

Control flow: attach is called by `demod_attach_dummy()` when the core is configured for a dummy tuner. Userspace sees a DVB-C frontend with fixed capability metadata. Tuning calls succeed without hardware, and release frees the allocation.

State and persistence: only the allocation behind `demodulator_priv` persists for the frontend lifetime. It has no hardware registers, no DMA, no saved settings, and no durable state.

Dependencies/integration: depends on DVB frontend core and `ddbridge-dummy-fe.h`. It integrates through `dvb_attach(ddbridge_dummy_fe_qam_attach)` in the ddbridge core.

Risks and test signals: because it always reports lock, it is not a signal-quality simulator and can mask real tuning path failures if enabled accidentally. Test by loading with the relevant dummy parameter, confirming frontend registration, issuing basic tuning/status calls, and verifying module removal calls `release()` without leaks.
