# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-j721e-wiz.c

## Purpose
TI WIZ SERDES wrapper driver for J721E-family, AM64, J7200, J784S4, and J721S2. It configures wrapper registers around a child SERDES, registers clocks, provides full/lane resets, handles Type-C lane swap, selects lane modes, and creates the child `serdes` platform device.

## APIs, Flow, And State
`struct wiz` stores wrapper/SCM regmaps, regmap fields, clocks, lane types, master lanes, reset controller, Type-C GPIO, child device, and suspend mux state. Probe maps the child SERDES resource, optionally gets `ti,scm`, reads `num-lanes`, parses Type-C GPIO/debounce, scans child lane nodes, allocates fields, registers resets and clocks, initializes WIZ if not already configured, and instantiates the child SERDES. `wiz_init()` resets WIZ, selects DP/QSGMII/USXGMII modes, configures Ethernet MAC dividers, and enables raw auto-start. Reset deassertion handles Type-C swap and per-lane enable/full-rate divider.

## Dependencies And Integration
Uses regmap-field, common clock, reset-controller, GPIO descriptors, runtime PM, syscon SCM, OF platform child creation, and TI WIZ clock binding IDs.

## Risks And Tests
USXGMII mode writes can lose earlier errors, cleanup differs by variant, and Type-C swap correctness depends on DT lane metadata or GPIO timing. Test all compatibles, clock topologies, SCM override, full/lane reset IDs, child create/destroy, Type-C swap, suspend/resume mux restore, and register-failure injection.
