## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl83xx.h

Purpose: this header declares the common RTL83xx Realtek DSA helper interface shared between transport front ends and chip-specific drivers.

Important APIs, types, and functions: `struct realtek_interface_info` carries transport-specific `reg_read` and `reg_write` callbacks used by `rtl83xx_probe()` to initialize regmap. The header declares lock/unlock helpers, user MDIO setup, common probe/register/unregister/shutdown/remove entry points, and reset assert/deassert helpers.

Control flow: there is no runtime implementation in the header. Its declarations define the sequence used by Realtek front-end drivers: probe allocates common state from `realtek_interface_info`, chip drivers register the DSA switch through `rtl83xx_register_switch()`, and teardown uses unregister/shutdown/remove helpers.

State and persistence: no state is stored in the header. The declared APIs operate on `struct realtek_priv`, DSA switch state, reset handles, and regmaps allocated in `rtl83xx.c`.

Dependencies and integration points: the header depends on declarations for `struct dsa_switch`, `struct realtek_priv`, and `struct device` from including translation units. It is included by RTL8365MB, RTL8366RB, LED support, and Realtek SMI/MDIO common code.

Risks: because the header provides only prototypes, build correctness depends on including it after headers that define the referenced types. Transport callbacks must follow the expected register/value contract used by the common regmap setup.

Test signals: compile coverage from all Realtek DSA modules, successful symbol resolution in namespace `REALTEK_DSA`, and runtime probe paths that pass valid transport callbacks into `rtl83xx_probe()`.
