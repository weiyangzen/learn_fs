# sources/distributed-fs/ceph-client/include/media/dvb_frontend.h

Purpose: Main DVB frontend kABI for demodulator/tuner drivers, frontend registration, tuning algorithms, DVBv5 property cache, frontend lifecycle, and suspend/resume helpers.

Important APIs/types/functions: Types include tuning settings, tuner info, analog parameters, `dvbfe_algo`, `dvbfe_search`, `dvb_tuner_ops`, `analog_demod_ops`, `dvb_frontend_internal_info`, `dvb_frontend_ops`, `dtv_frontend_properties`, and `dvb_frontend`. APIs register/unregister/detach frontends, suspend/resume/reinitialize, and provide precise sleep helper. Ops cover tuner init/sleep/set_params/status/RF metrics, analog demod callbacks, digital demod set/get/read status/statistics, DiSEqC/SEC controls, I2C gate, TS bus, LNA, and custom search.

Control flow: Drivers instantiate `dvb_frontend` with ops and register it with a `dvb_adapter`. Userspace property ioctls update `dtv_property_cache`; the frontend core chooses hardware, software zig-zag, custom, or recovery tuning and calls demod/tuner ops. Lifecycle calls stop device nodes/kthreads before explicit detach releases tuner/demod/SEC resources.

State and persistence: `dvb_frontend` owns kref, ops, adapter pointer, private demod/tuner/frontend/SEC/analog data, cached properties/statistics, callback, ID, and exit reason. Cache persists while registered and is restored across resume where possible.

Dependencies and integration: Depends on DVB device core, I2C, module/refcounting, mutex/delay/slab, bitops, and Linux DVB frontend UAPI. Integrates demods, tuners, SEC/LNB control, analog hybrids, and media adapters.

Risks and test signals: Risks include inconsistent frequency units, stale property cache, wrong release ordering, I2C gate deadlocks, suspend/resume retune failures, legacy callback semantics, and statistics not updated on unlocked signals. Test each delivery system, DVBv3/v5 ioctls, custom search states, DiSEqC timing, detach after unregister, suspend/resume with SEC restoration, and tuner/demod error paths.
