# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/generic.c

## Purpose
This is a generic PCI slot/endpoint power-control provider. It can power devices either through a named power sequencer from an OF graph topology or directly through all regulators and an optional clock described on the PCI node.

## Important APIs, types, and functions
`struct slot_pwrctrl` embeds `struct pci_pwrctrl` and stores regulator bulk data, optional clock, and optional `struct pwrseq_desc`. `slot_pwrctrl_probe()` acquires resources and registers the provider. `slot_pwrctrl_power_on()` uses either `pwrseq_power_on()` or regulator/clock enable. `slot_pwrctrl_power_off()` uses the matching pwrseq or regulator/clock disable path. The OF match table supports generic bridge class nodes (`pciclass,0604`) and Renesas UPD720201/UPD720202 (`pci1912,0014`).

## Control flow
When the pwrctrl core creates a platform device for a matching PCI DT node, probe allocates provider state. If the node has an OF graph, it obtains the `pcie` pwrseq handle and skips direct resource acquisition. Otherwise it obtains all regulators on the node and an optional unnamed clock. Probe then installs power callbacks, registers cleanup for regulator bulk data, initializes the core pwrctrl object, and registers readiness/notifier state. Later, the core calls the callbacks during host-controller power sequencing.

## State and persistence
State is per platform device and devm-managed except for regulator bulk data, which is freed by an explicit devm action. Runtime state consists of enabled regulators, prepared/enabled clock, or an active pwrseq. No state is saved across reboot or module unload.

## Dependencies and integration points
The provider depends on regulators, clocks, OF graph, the power sequencing consumer API, platform driver matching, and the pwrctrl core. It is used when hardware can be described generically with supplies/clocks or a pwrseq provider instead of a device-specific register sequence.

## Risks
If `pwrseq_power_on()` fails in graph mode, `slot_pwrctrl_power_on()` ignores its return value and reports success. In direct mode, a clock-enable failure after regulators are enabled is returned without disabling those regulators, leaving cleanup to later power-off or driver removal. Power-off disables regulators before the clock, which may or may not match every device's required sequencing. The generic match table must stay narrow enough to avoid claiming devices that need custom sequencing.

## Test signals
Test graph-based devices with a failing and successful `pcie` pwrseq, direct regulator-only nodes, regulator-plus-clock nodes, probe deferral for missing supplies/clocks, and repeated power-on/off cycles. Runtime checks should verify regulator and clock enable counts are balanced after failure and removal.
