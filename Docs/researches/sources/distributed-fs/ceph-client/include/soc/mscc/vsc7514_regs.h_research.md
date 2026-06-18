# sources/distributed-fs/ceph-client/include/soc/mscc/vsc7514_regs.h

Purpose: declares the VSC7514-specific Ocelot register-map data shared by platform and DSA glue.

Important APIs/types/functions: exports `vsc7514_vcap_props[]`, `vsc7514_regfields[REGFIELD_MAX]`, and `vsc7514_regmap[TARGET_MAX]`. These are defined in `drivers/net/ethernet/mscc/vsc7514_regs.c`.

Control flow: none in the header. Probe code selects these tables to bind generic Ocelot register targets, regfields, and VCAP property descriptions to VSC7514 hardware.

State and persistence: the header owns no mutable state. The declared arrays are static hardware-description data used to compute register offsets and field positions at runtime.

Dependencies and integration: includes `soc/mscc/ocelot_vcap.h` and relies on Ocelot target/regfield enums from the broader switch headers. It is included by VSC7514 Ethernet and DSA extension code.

Risks: any mismatch between these arrays and silicon layout redirects register writes to the wrong block. Test signals include VSC7514 probe, regmap access, VCAP rule programming, PTP initialization, and DSA/ext switch operation.
