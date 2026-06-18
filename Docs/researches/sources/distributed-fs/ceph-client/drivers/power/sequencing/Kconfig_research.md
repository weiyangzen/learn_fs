# sources/distributed-fs/ceph-client/drivers/power/sequencing/Kconfig

## Purpose
`drivers/power/sequencing/Kconfig` defines the generic Linux power-sequencing subsystem and its provider drivers. The subsystem lets consumers request named power targets from a provider that sequences shared regulators, clocks, GPIOs, and delays.

## Important APIs, Types, and Functions
Important symbols are `POWER_SEQUENCING`, `POWER_SEQUENCING_QCOM_WCN`, `POWER_SEQUENCING_PCIE_M2`, and `POWER_SEQUENCING_THEAD_GPU`. Dependencies pull in OF, regulator, clock, GPIO, PCI/serdev support, and provider-specific platform constraints.

## Control Flow
Kconfig exposes the framework first, then provider drivers. Enabling provider symbols causes `drivers/power/sequencing/Makefile` to build `core.o` and selected providers. Consumer drivers depend on the exported pwrseq API at compile and probe time.

## State and Persistence Behavior
No runtime state exists in Kconfig. Persistent configuration state is carried in `.config` and determines whether the pwrseq bus/framework and providers exist.

## Dependencies and Integration Points
It integrates with kbuild, OF-based embedded platforms, M.2 connector support, Qualcomm WCN PMUs, and T-Head GPU sequencing.

## Risks and Edge Cases
Too-narrow dependencies hide useful providers under compile-test; too-broad dependencies can build providers without required framework APIs. Provider symbols must remain synchronized with Makefile object names.

## Test Signals
Run olddefconfig/allmodconfig, check menu visibility, compile provider combinations, and verify consumers defer cleanly when providers are disabled.
