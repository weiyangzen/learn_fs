# sources/distributed-fs/ceph-client/drivers/regulator/rt4831-regulator.c

Purpose: registers the Richtek RT4831 display supply regulators: DSVLCM, DSVP, and DSVN. It is a platform child using a parent regmap from the RT4831 MFD.

Important APIs/types/functions: `rt4831_get_error_flags()` maps OTP, LCM overvoltage, and positive/negative short-circuit flags to regulator errors. `rt4831_dsvlcm_ops` supports voltage selection and bypass mode. `rt4831_dsvpn_ops` supports voltage selection, enable/disable, active discharge, and error flags. Descriptor tables define voltage ranges, mode bits, enable bits, and discharge bits.

Control flow: probe fetches the parent regmap, programs DSV mode to normal by default, then registers the three descriptors. DSVLCM bypass toggles the DSV mode field between normal and bypass; DSVP/DSVN use enable and discharge bits in `RT4831_REG_DSVEN`.

State and persistence: no private state. All state is represented by PMIC registers owned by the parent regmap. Error flags are read on demand from the flags register.

Dependencies and integration: depends on the RT4831 parent device creating a `rt4831-regulator` platform cell, a parent regmap, and OF regulator child nodes under `regulators`.

Risks and test signals: probe globally rewrites DSV mode to normal, which may override boot firmware state. Error mapping is rail-specific, so IDs must remain aligned with descriptor order. Tests should cover parent regmap absence, DSV mode initialization, bypass operations, active discharge bits, voltage range boundaries, and per-rail error flag mapping.
