<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpcv2.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpcv2.c

## Purpose

`gpcv2.c` implements i.MX7D and i.MX8M-family GPCv2 PGC providers. It describes SoC-specific domains, valid register windows, CPU mapping bits, software PUP/PDN request bits, PGC control bits, optional regulators/resets/clocks, and ADB400 handshake bits.

## Important APIs, types, and functions

`struct imx_pgc_domain` embeds genpd and stores regmap, PGC register set, regulator, resets, bulk clocks, PGC bitmap, request/mapping/handshake bits, voltage, keep-clocks flag, and device. `imx_pgc_power_up()` and `imx_pgc_power_down()` implement the transition sequences. Static domain arrays cover i.MX7, i.MX8MQ/MM/MN/MP. `imx_gpcv2_probe()` instantiates child `imx-pgc-domain` devices, and `imx_pgc_domain_probe()` registers simple providers.

## Control flow

The top-level driver matches SoC data, creates a constrained regmap, walks `pgc` child nodes, copies the indexed static template into a child platform device, fills regmap/register pointers, and assigns power callbacks. The child probe acquires regulator/clocks/resets, maps CPU bits, initializes genpd as off, and registers a provider. System sleep temporarily holds runtime PM references for nested domains.

## State and persistence behavior

State persists in copied domain descriptors and hardware GPC CPU mapping, PUP/PDN request, PGC control, PWRHSK handshake, regulator, reset, and clock state. `keep_clocks` domains intentionally retain clocks where shared logic needs them.

## Dependencies and integration points

It depends on regmap MMIO, regulators, resets, clocks, runtime PM, genpd, platform child devices, and DT binding IDs. Block-controller drivers supply some bus-clock/reset context needed by ADB handshakes.

## Risks and edge cases

PGC offsets are RTL-derived despite reference manual issues, handshake masks are SoC-specific, some power-up handshakes use delays instead of polling, domains with `pxx = 0` are handshake-only, and runtime PM references must balance on errors and sleep.

## Test signals

Boot each compatible, validate DT indexes, regulator voltage, reset/clock handling, PUP/PDN timeouts, ADB handshakes with block controllers, active-wakeup USB domains, and runtime PM balance across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpcv2.c -->
