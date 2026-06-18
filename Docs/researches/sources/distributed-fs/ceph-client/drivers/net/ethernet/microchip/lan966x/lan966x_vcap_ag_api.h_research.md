## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_ag_api.h

Purpose: this small generated/public header exposes LAN966x VCAP capability descriptors to the rest of the driver.

Important APIs and types: it includes `vcap_api.h` and declares `extern const struct vcap_info lan966x_vcaps[];` and `extern const struct vcap_statistics lan966x_vcap_stats;`. The include guard is `__LAN966X_VCAP_AG_API_H__`.

Control flow: no control flow. Its role is linkage: implementation files include it to reference the generated VCAP descriptor arrays defined in `lan966x_vcap_ag_api.c`.

State and persistence: no local state. The declared objects are immutable descriptor tables compiled into the driver. They define how VCAP hardware state is interpreted and programmed by consumers.

Dependencies and integration: consumed by VCAP debugfs and any initialization path that needs LAN966x VCAP descriptors. It depends on the shared VCAP API type definitions. The header is intentionally narrow, keeping generated table internals private to the `.c` file.

Risks: declarations must stay type-compatible with the generated `.c` definitions and shared VCAP API. If the VCAP API changes these structures, this header and implementation must regenerate together. Test signals are compile/link coverage, VCAP initialization, and debugfs/statistics consumers resolving both exported arrays.
