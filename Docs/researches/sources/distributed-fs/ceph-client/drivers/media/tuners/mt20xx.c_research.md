# sources/distributed-fs/ceph-client/drivers/media/tuners/mt20xx.c

Purpose: legacy Microtune MT20xx analog tuner driver supporting MT2032 and MT2050 devices over the tuner-core I2C helper layer. It detects the part, installs chip-specific DVB tuner ops, computes PLL register values for TV/radio/digital-TV modes, and maintains the last tuned frequency.

Important APIs/types: `struct microtune_priv` stores `tuner_i2c_props`, XOGC, and cached `frequency`. Public entry is exported `microtune_attach()`. MT2032 helpers include `mt2032_compute_freq()`, `mt2032_set_if_freq()`, lock/VCO helpers, TV/radio setters, and `mt2032_init()`. MT2050 helpers include `mt2050_set_if_freq()`, antenna selection, TV/radio setters, and `mt2050_init()`. Common callbacks are `microtune_release()` and `microtune_get_frequency()`.

Control flow: attach allocates state, initializes tuner I2C properties, reads a 21-byte register block, extracts company/part/rev, dispatches to MT2032 or MT2050 initialization, names the tuner, and returns the frontend. MT2032 init writes programming-procedure defaults, adjusts crystal oscillator gain until XOK, and installs `mt2032_tuner_ops`. MT2032 tuning maps V4L2 analog parameters to RF Hz and IF2, computes LO1/LO2 divider/numerator fields from a 5.25 MHz reference, does a diagnostic spur check, writes selected register groups, polls lock with optional VCO optimization and LINT retry, then adjusts LOGC. MT2050 tuning computes two LOs from a 1.218 GHz first IF, writes six PLL bytes, and selects TV/radio antenna module parameters.

State and persistence: only `xogc` and last `frequency` persist in memory. Module parameters `debug`, `optimize_vco`, `tv_antenna`, and `radio_antenna` alter behavior globally for the module. Hardware state is programmed directly through I2C writes.

Dependencies and integration: depends on `tuner-i2c.h` helper APIs, DVB frontend tuner ops, V4L2 analog modes/stds, module parameters, and legacy tuner-core attach patterns.

Risks: unsupported detected parts return `NULL` without freeing the just-allocated private state. MT2032 spur checking only logs and does not retune away from spurs. Several I2C transfers log warnings but tuning often continues. Frequency math is old 32-bit integer code with manual scaling. Attach does not validate company code before part dispatch.

Test signals: detect MT2032/MT2050/unsupported parts, validate register writes for NTSC/PAL/radio/digital-TV paths, cover VCO optimization and lock retry, ensure unsupported attach frees or is handled by caller, test module parameter effects on antennas and VCO, and simulate I2C short writes.
