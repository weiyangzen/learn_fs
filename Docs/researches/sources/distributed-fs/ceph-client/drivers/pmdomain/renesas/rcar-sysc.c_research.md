<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.c

## Purpose
Legacy Renesas R-Car/RZ SYSC framework driver. It consumes SoC descriptor tables, creates generic PM domains, performs SYSC register power-on/off sequencing, handles external request masking, and registers onecell providers for R-Car Gen1/2/3 style power areas.

## Important APIs, Types, And Functions
- `struct rcar_sysc_pd` is the runtime genpd plus channel offset/bit, interrupt bit, flags, and name.
- `struct rcar_pm_domains` stores the onecell provider and indexed genpd array.
- `rcar_sysc_power()` is the central register sequence; `rcar_sysc_pwr_on_off()` submits one power request after SYSCSR readiness.
- `rcar_sysc_pd_setup()` sets genpd flags, attach/detach hooks, initial power state, and callbacks.
- `rcar_sysc_pd_init()` maps the SYSC node, runs optional SoC init fixups, creates domains and subdomains; `rcar_sysc_pd_init_provider()` publishes the onecell provider.
- R8A7779 CPU helpers optionally export `rcar_sysc_power_down_cpu()` and `rcar_sysc_power_up_cpu()`.

## Control Flow
An early initcall finds a matching `renesas,*-sysc` node, selects the enabled SoC descriptor, runs `info->init()`, maps MMIO, captures optional external request mask settings, allocates onecell data, and iterates descriptor areas. Each area becomes an `rcar_sysc_pd`; CPU, SCU, and no-control domains are marked always-on, while device domains get `GENPD_FLAG_PM_CLK`, active wakeup, no-stay-on, and CPG MSTP/MSSR attach hooks. Controllable domains that are off at boot are powered on before genpd init. Parent fields add genpd subdomains. A later postcore initcall registers the provider once genpd infrastructure is ready.

## State And Persistence Behavior
Global state includes `rcar_sysc_base`, the spinlock, external mask offset/value, onecell data, and provider node. Runtime state is the allocated `rcar_sysc_pd` objects and hardware SYSC registers. Descriptor data is init-only. Power operations are serialized with `rcar_sysc_lock` because SMP CPU and I/O-device power paths can overlap.

## Dependencies And Integration Points
Depends on Device Tree compatible matching, SoC descriptor objects, Renesas CPG clock-domain attach helpers (`cpg_mstp_*` or `cpg_mssr_*`), generic PM domains, simple QoS governor, and Renesas public CPU power helpers for R8A7779. Consumers integrate via onecell `power-domains` indices.

## Risks
Power sequencing is MMIO timing-sensitive: SYSCSR readiness, PWRER retries, SYSCISR completion, and interrupt mask/clear ordering must be correct. Wrong `isr_bit` indexing can overwrite onecell entries or fail subdomain links. External request masking affects CPU/3DG domains and must be restored on every error path. Early init means allocation/mapping failures can leave partial setup.

## Test Signals
Boot should find exactly one matching SYSC, register a onecell provider, and add expected subdomains. Runtime PM tests should power-cycle non-always-on domains without PWRER/SYSCISR timeouts. CPU hotplug on R8A7779 should exercise exported CPU power helpers. Clock attach coverage should include both legacy MSTP and MSSR systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.c -->
