<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.c

## Purpose
Renesas R-Car Gen4 SYSC framework driver. It consumes Gen4 descriptor tables, creates generic PM domains, performs PDR-based power sequencing, and registers a onecell provider for R8A779A0/F0/G0/H0 style controllers.

## Important APIs, Types, And Functions
- `struct rcar_gen4_sysc_pd` wraps genpd with a PDR number, flags, and name.
- `rcar_gen4_sysc_power()` serializes and performs the PDR power transition, including interrupt mask/clear and PDRESR retry handling.
- `rcar_gen4_sysc_pwr_on_off()` waits for SYSCSR not-busy and writes PDRONCR/PDROFFCR.
- `clear_irq_flags()` clears and verifies SYSCISCR bits.
- `rcar_gen4_sysc_pd_setup()` configures genpd flags and initial state.
- `rcar_gen4_sysc_pd_init()` matches OF, maps registers, creates domains/subdomains, and registers the provider.

## Control Flow
At postcore init, the driver finds the first matching Gen4 SYSC node, maps MMIO, allocates onecell data, and walks the SoC's `rcar_gen4_sysc_area` list. CPU/SCU/no-control areas become always-on; device domains get PM clock integration with CPG MSSR attach/detach hooks and active wakeup. If a controllable device domain is off at boot, the driver powers it on before genpd registration. Power transitions compute register and bit indices from the PDR ID, enable and mask the completion interrupt, clear stale flags, repeatedly submit a power request until PDRESR is clear, then wait for the completion bit and clear it again.

## State And Persistence Behavior
Global state is the MMIO base, spinlock, and onecell data. Each runtime domain stores PDR ID and flags. Descriptor arrays are init-time only. The spinlock serializes all PDR sequences because SYSC registers and interrupt bits are shared.

## Dependencies And Integration Points
Depends on Gen4 descriptor objects declared in `rcar-gen4-sysc.h`, Device Tree compatibles, generic PM domains, simple QoS governor, and Renesas CPG MSSR clock attach helpers. Consumers use onecell power-domain indices equal to PDR IDs.

## Risks
PDR IDs index both register blocks and onecell domains, so descriptor mistakes can touch the wrong hardware. IRQ clear polling must succeed or subsequent requests may falsely complete. Initial power-on of off domains can hide bootloader power-state assumptions but is required for genpd baseline.

## Test Signals
Boot tests should show provider registration and no `Can not clear IRQ flags` or timeout errors. Runtime PM should toggle non-CPU domains and retain CPU/SCU domains as always-on. DT binding checks should match PDR IDs to onecell indices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.c -->
