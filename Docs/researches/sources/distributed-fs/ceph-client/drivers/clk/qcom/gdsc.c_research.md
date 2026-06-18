# sources/distributed-fs/ceph-client/drivers/clk/qcom/gdsc.c

## Purpose
This file implements Qualcomm Globally Distributed Switch Controller support as Linux generic power domains. It provides the shared runtime logic used by qcom clock-controller drivers to register GDSC descriptors, sequence power on/off, coordinate optional regulators and resets, configure retention behavior, expose genpd hardware-trigger mode, and publish onecell power-domain providers for device tree consumers.

## Important APIs, Types, And Functions
The central object is `struct gdsc` from `gdsc.h`, embedded around `struct generic_pm_domain`. `gdsc_register()` is the provider entry point called by qcom clock drivers; it allocates `genpd_onecell_data`, fetches optional supplies, initializes every GDSC, wires subdomain relationships, and calls `of_genpd_add_provider_onecell()`. `gdsc_unregister()` removes subdomains and unregisters the OF provider. `gdsc_gx_do_nothing_enable()` is exported for GPU GX domains where the CPU should enable only the parent supply and leave actual GX power-up to GMU firmware.

The low-level helpers are focused on register sequencing. `gdsc_check_status()` reads either the GDSCR, a separate hardware-control status register, or CFG_GDSCR and checks `PWR_ON_MASK`, `GDSC_POWER_UP_COMPLETE`, or `GDSC_POWER_DOWN_COMPLETE`. `gdsc_poll_status()` polls for up to `STATUS_POLL_TIMEOUT_US`. `gdsc_update_collapse_bit()` writes either an APCS collapse-vote register/mask or the GDSCR `SW_COLLAPSE_MASK`. `gdsc_toggle_logic()` performs regulator enable/disable, collapse bit writes, special votable disable delay, hardware-controller delay, and status polling.

Other helpers manage related state: reset assertion/deassertion through `reset_controller_dev`, memory/peripheral retention bits in CXC branch registers, GMEM IO clamps and AON reset, retain-FF setup, hardware-control mode, and subdomain list add/remove rollback.

## Control Flow
Registration starts in `gdsc_register()`. It allocates the onecell domain table, gets optional regulators named by each `gdsc.supply`, stores the shared `regmap` and reset controller in each descriptor, and calls `gdsc_init()` for every non-null entry. Once each domain is initialized, it adds subdomain relationships either to an explicit `gdsc.parent`, to the provider device's own PM domain, or to each parent in `desc->pd_list`. On success, it publishes the domain array to OF consumers.

`gdsc_init()` programs default transition waits, disables hardware trigger and software override, optionally forces always-on domains on, reads current hardware status, synchronizes regulator state if the domain is already on, casts a vote for already-on votable domains, enables retain-FF and hardware-control mode when requested, forces or clears memory retention bits based on current state and allowed power states, sets genpd flags and callbacks, and calls `pm_genpd_init()`.

At runtime, `gdsc_enable()` handles ON-only domains by deasserting resets. For normal domains it optionally toggles software resets, releases clamp IO, powers on through `gdsc_toggle_logic()`, forces memory retention if OFF is supported, waits for clock and memory timing, sets retain-FF, and enables hardware trigger mode when supported. `gdsc_disable()` reverses the path: it disables hardware trigger mode and waits for the domain to be on again, clears memory retention for OFF-capable domains, leaves RET+ON-only domains on because retention is entered only by parent hardware state, collapses the domain if OFF is allowed, and asserts clamp IO. `gdsc_set_hwmode()` and `gdsc_get_hwmode()` implement the genpd device hardware-mode hooks for domains flagged `HW_CTRL_TRIGGER`.

## State And Persistence
The persistent hardware state includes GDSCR bits, CFG_GDSCR power complete bits, optional separate hardware-control status, collapse-vote registers, CXC `RETAIN_MEM` and `RETAIN_PERIPH` bits, clamp and reset bits, regulator enable state, and reset-controller state. Software state is mostly static descriptor state plus devm-managed onecell arrays and optional regulator handles.

The implementation deliberately synchronizes with pre-existing hardware state during init. If firmware or another master left a domain on, the driver enables the regulator handle, votes on votable GDSCs, sets retain-FF if requested, and initializes genpd as powered. Memory retention bits are forced for domains currently on or capable of retention and cleared for fully off domains. There is no independent save/restore layer; system persistence depends on the hardware retention model and parent-domain transitions.

## Dependencies And Integration Points
This file depends on regmap MMIO access, Linux generic PM domains, OF genpd providers, reset-controller callbacks, optional regulator consumers, jiffies/ktime delay helpers, and descriptor data supplied by individual qcom clock controller drivers. It integrates with clock drivers through `gdsc_register()` and `gdsc_unregister()`, with device drivers through genpd attach APIs, with reset providers through `rcdev`, and with regulators through optional named supplies.

Subdomain support allows a GDSC to be nested under another GDSC, under the provider device's PM domain, or under a list of PM domains. That makes this code a shared integration layer between qcom clock-controller nodes and larger RPMh/genpd topology.

## Risks And Test Signals
The highest risks are sequencing and status interpretation. Polling the wrong register or bit can produce false on/off state or timeouts. Missing the 1 microsecond hardware-controller delay can read stale status. Incorrect votable handling can remove another master's vote or fail to cast a required local vote. Regulator error paths must leave supplies balanced, and subdomain rollback must remove only relationships added during the failed registration attempt. Retention and clamp flags are SoC-specific; a wrong descriptor flag can lose register context or leave IO clamped.

Useful test signals include qcom clock-controller probes successfully registering GDSCs, `/sys/kernel/debug/pm_genpd/` showing expected domains and hierarchy, domain on/off transitions without `status stuck` warnings, balanced regulator enable counts across runtime PM cycles, reset-controlled domains leaving reset on enable and entering reset on ON-only disable paths, successful hardware-mode set/get for flagged domains, and GPU recovery paths using `gdsc_gx_do_nothing_enable()` without CPU-side GX power-up.
