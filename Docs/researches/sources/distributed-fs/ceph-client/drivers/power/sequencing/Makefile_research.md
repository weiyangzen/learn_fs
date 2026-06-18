# sources/distributed-fs/ceph-client/drivers/power/sequencing/Makefile

## Purpose
`drivers/power/sequencing/Makefile` maps power-sequencing Kconfig symbols to framework and provider objects.

## Important APIs, Types, and Functions
It builds `core.o` for `CONFIG_POWER_SEQUENCING`, `pwrseq-qcom-wcn.o` for Qualcomm WCN PMUs, `pwrseq-pcie-m2.o` for M.2 connectors, and `pwrseq-thead-gpu.o` for T-Head GPU sequencing.

## Control Flow
Kbuild evaluates the selected symbols and compiles the core and provider modules/built-ins. Providers rely on `core.o` exporting the pwrseq provider and consumer APIs.

## State and Persistence Behavior
There is no runtime state. Build products persist in the kernel object tree.

## Dependencies and Integration Points
It depends on symbol names in `drivers/power/sequencing/Kconfig` and source filenames in this directory.

## Risks and Edge Cases
If a provider object is listed without the core dependency satisfied, link errors or unresolved exports can occur. Missing entries silently make Kconfig-enabled providers unavailable.

## Test Signals
Build with each provider enabled as built-in and module, compare Kconfig-to-Makefile coverage, and run allmodconfig.
