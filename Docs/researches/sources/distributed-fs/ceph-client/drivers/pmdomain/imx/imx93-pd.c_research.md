<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-pd.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-pd.c

## Purpose

`imx93-pd.c` implements simple i.MX93 SRC slice power domains. Each platform device maps one slice's control/status registers, optional clocks, and a simple OF genpd provider.

## Important APIs, types, and functions

`struct imx93_power_domain` embeds genpd and stores device, MMIO base, and bulk clocks. `imx93_pd_on()` enables clocks, clears soft power-down, and polls SSAR clear. `imx93_pd_off()` sets soft power-down, polls power-switch status, and disables clocks. Probe synchronizes initial state from isolation status and registers a provider.

## Control flow

The driver matches `fsl,imx93-src-slice`. Probe maps resources, gets clocks, names the genpd after the device, determines initial off state, enables clocks for initially-on slices, initializes genpd, and registers a simple provider. Genpd callbacks later control power transitions.

## State and persistence behavior

State persists in slice software-control and function-status registers plus clock enable counts. Initial genpd status is synchronized from hardware isolation status.

## Dependencies and integration points

It depends on platform resources, MMIO polling, bulk clocks, genpd, modules, and OF matching. i.MX93 block-control drivers can use these slice domains as upstream runtime PM parents.

## Risks and edge cases

Power-on timeout leaves clocks enabled, initial state detection depends on isolation status, fixed 10 ms polling may be short for faulty clocks, and some defined status masks are unused.

## Test signals

Test initial on/off slices, clock acquisition, SSAR and PSW timeouts, DT provider attach, block-controller runtime PM interactions, removal, and clock counts across failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-pd.c -->
