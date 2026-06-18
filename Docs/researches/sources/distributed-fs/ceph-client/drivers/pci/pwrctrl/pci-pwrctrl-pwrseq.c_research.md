# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.c

## Purpose
This provider wraps the power sequencing subsystem for specific PCI endpoints, currently Qualcomm WCN-family WLAN devices. It gives the PCI pwrctrl core a uniform `power_on`/`power_off` callback pair backed by a named pwrseq target.

## Important APIs, types, and functions
`struct pwrseq_pwrctrl` embeds `struct pci_pwrctrl` and stores the pwrseq descriptor. `struct pwrseq_pwrctrl_pdata` supplies the pwrseq target name and an optional device validator. `pwrseq_pwrctrl_qcm_wcn_validate_device()` rejects older/incomplete WCN DT nodes that lack `vddaon-supply`. `pwrseq_pwrctrl_probe()` obtains match data, validates the node, gets the pwrseq, and registers the provider. The OF match table covers QCA6390, WCN6855, and WCN7850 PCI IDs.

## Control flow
The pwrctrl core creates a platform device for a matching PCI node. Probe retrieves per-compatible data, runs the optional validator, allocates provider state, obtains the named pwrseq target (`wlan` for the current devices), installs callbacks, initializes pwrctrl state, and registers readiness with the core. Host-controller pwrctrl calls later invoke `pwrseq_power_on()` and `pwrseq_power_off()`.

## State and persistence
State is devm-managed per platform device: the pwrctrl wrapper and pwrseq handle. Runtime power state is owned by the power sequencing provider. No persistent storage is used.

## Dependencies and integration points
The file depends on platform driver OF matching, generic device properties, the pwrseq consumer API, and the pwrctrl core. It integrates with Qualcomm WLAN DT bindings where the PMU/regulator sequencing is provided separately and the PCI endpoint node needs to be powered before enumeration.

## Risks
The validator prevents indefinite probe deferral on known incomplete WCN nodes, but future compatibles need equivalent validation if old DTs exist. Probe fails with `-EINVAL` if match data is absent or has no target, so OF table data is required. Power sequencing errors propagate through the pwrctrl core and can block host bridge scanning.

## Test signals
Validate matching for each supported compatible, successful and failed `devm_pwrseq_get()`, missing `vddaon-supply` rejection, and balanced power-on/off through host-controller probe/remove. DT compatibility tests should cover old WCN nodes without PMU supplies and new nodes with complete pwrseq wiring.
