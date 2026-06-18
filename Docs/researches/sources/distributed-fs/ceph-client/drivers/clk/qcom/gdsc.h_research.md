# sources/distributed-fs/ceph-client/drivers/clk/qcom/gdsc.h

## Purpose
This header defines the public descriptor contract for Qualcomm GDSC power domains. Clock-controller drivers include it to describe GDSC register offsets, allowed power states, sequencing flags, reset associations, optional supplies, and parent-domain relationships, then pass those descriptors to the implementation in `gdsc.c`.

## Important APIs, Types, And Functions
`struct gdsc` is the key type. It embeds `struct generic_pm_domain pd`, stores an optional parent domain, a regmap pointer, GDSCR and collapse-vote register offsets, optional hardware-control and clamp-IO registers, CXC register lists for retention bits, transition wait values, allowed power states, flags, reset-controller data, reset IDs, and optional regulator supply names and handles.

The power-state bitfields are `PWRSTS_OFF`, `PWRSTS_RET`, `PWRSTS_ON`, plus combined `PWRSTS_OFF_ON` and `PWRSTS_RET_ON`. The header documents that software cannot directly enter `PWRSTS_RET`; retention is reached by hardware when the parent domain enters a low-power state. Flags include `VOTABLE`, `CLAMP_IO`, `HW_CTRL`, `SW_RESET`, `AON_RESET`, `POLL_CFG_GDSCR`, `ALWAYS_ON`, `RETAIN_FF_ENABLE`, `NO_RET_PERIPH`, and `HW_CTRL_TRIGGER`.

`struct gdsc_desc` bundles a provider device, a sparse array of GDSC pointers, its size, and an optional parent PM-domain list. Public functions are `gdsc_register()`, `gdsc_unregister()`, and `gdsc_gx_do_nothing_enable()` when `CONFIG_QCOM_GDSC` is enabled. Stub inline definitions return `-ENOSYS` or no-op unregister when the config is disabled.

## Control Flow
The header itself has no runtime control flow, but it defines how callers drive the implementation. A clock controller declares static `struct gdsc` instances, places pointers in an ID-indexed array, fills a `struct gdsc_desc`, and lets qcom common clock code call `gdsc_register()`. The implementation then fills runtime-only fields such as `regmap`, `rcdev`, and `rsupply`, initializes each `generic_pm_domain`, and publishes the onecell provider.

## State And Persistence
Descriptor fields are static configuration. Runtime state is attached by `gdsc.c`: `regmap`, `rcdev`, optional regulator handles, genpd state, and subdomain registration. The important persistence semantics are encoded in `pwrsts` and flags. `PWRSTS_RET_ON`, `RETAIN_FF_ENABLE`, `NO_RET_PERIPH`, and CXC lists determine whether hardware state is expected to survive low-power transitions or be fully collapsed.

## Dependencies And Integration Points
The header depends on Linux PM domain types and forward declarations for regmap, regulator, and reset controllers. It is consumed by many qcom clock-controller drivers and by the qcom common clock registration path. Device-tree integration is indirect: sparse GDSC arrays indexed by dt-binding IDs become OF genpd onecell domains.

## Risks And Test Signals
The main risk is descriptor misuse. Wrong `pwrsts` can make genpd leave a domain on when software expects off, or collapse hardware that only supports retention. Wrong flags can poll the wrong register, skip needed reset/clamp sequencing, or enable hardware-control mode at the wrong time. Wrong `reset_count`, `resets`, or CXC lists can corrupt unrelated registers. Build coverage should include both `CONFIG_QCOM_GDSC=y/m` and disabled stub paths. Runtime signals are successful qcom clock-controller probe, correct genpd domain names and indexes, and expected power/retention behavior under runtime PM and system sleep.
