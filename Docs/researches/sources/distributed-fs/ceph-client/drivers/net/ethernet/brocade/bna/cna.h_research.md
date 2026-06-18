# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/cna.h

## Purpose
Provides small common CNA definitions shared by the BNA Ethernet driver and lower BFA firmware infrastructure. It centralizes basic kernel includes, a state-machine fault logging macro, firmware file names, version extern, and a Fibre Channel symbolic-name limit used by adjacent common code.

## Important APIs, Types, and Functions
The key macro is `bfa_sm_fault(event)`, which logs state-machine assertion failures with source file, line, and event value. It declares `extern char bfa_version[]`, defines firmware names `CNA_FW_FILE_CT` and `CNA_FW_FILE_CT2`, and defines `FC_SYMNAME_MAX`.

## Control Flow and State
There is no runtime control flow beyond the logging macro. The firmware-name macros are consumed by firmware loading and module firmware declarations; the fault macro is used by BNA FSM default cases to report unexpected events without stopping execution.

## State and Persistence Behavior
No mutable state is defined here. Firmware filenames represent a userspace firmware ABI: the kernel firmware loader must find `ctfw-3.2.5.1.bin` or `ct2fw-3.2.5.1.bin` depending on PCI device generation.

## Dependencies and Integration Points
Includes core kernel, PCI, timer, interrupt, delay, VLAN, and Ethernet headers. It is included by `bna_types.h`, `bnad.c`, `bnad_ethtool.c`, `cna_fwimg.c`, and other BNA/BFA files. `MODULE_FIRMWARE()` in `bnad.c` uses these names.

## Risks and Test Signals
Risks are low but ABI-sensitive. Changing firmware filenames breaks device initialization; changing `bfa_sm_fault` behavior affects diagnostics for all BFA FSMs. Test signals are firmware-load success on CT/CT2 devices, module metadata containing both firmware names, and readable state-machine fault logs on invalid event injection.
