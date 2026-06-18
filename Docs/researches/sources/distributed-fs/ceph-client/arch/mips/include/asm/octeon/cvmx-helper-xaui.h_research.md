# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-xaui.h

## Purpose
`cvmx-helper-xaui.h` declares helper operations for XAUI packet interfaces. XAUI uses high-speed serial lanes and GMX XAUI controls, so the common helper framework delegates port probing, enablement, and link state synchronization to this backend.

## Important APIs, Types, And Functions
The exported calls are `__cvmx_helper_xaui_probe(int interface)`, `__cvmx_helper_xaui_enumerate(int interface)`, `__cvmx_helper_xaui_enable(int interface)`, `__cvmx_helper_xaui_link_get(int ipd_port)`, and `__cvmx_helper_xaui_link_set(int ipd_port, union cvmx_helper_link_info link_info)`.

## Control Flow
Probe identifies available XAUI ports without bringing the interface up. Enable is called after IPD is enabled but before PKO is active, so lane and GMX state are ready before packet transmission. Link get/set synchronize negotiated or externally determined link state with Octeon MAC configuration.

## State And Persistence
The implementation writes QLM/PCS/GMX/PKO hardware state. The header defines no data. Link configuration remains active until another link-set or interface reset.

## Dependencies And Integration Points
It is included by `cvmx-helper.h`, uses `union cvmx_helper_link_info`, and is selected for `CVMX_HELPER_INTERFACE_MODE_XAUI`. It integrates with QLM JTAG/errata support, GMX XAUI CSR definitions, board-specific link handling, IPD, and PKO.

## Risks
XAUI lane setup is model and board dependent. Incorrect QLM selection, errata handling, or link-set values can prevent link training or cause packet errors. The helper must be called in the expected packet I/O initialization order.

## Test Signals
Validate probe counts, lane lock/link-up, 10G traffic, error counters, link-down recovery, model-specific QLM workarounds, and that link set follows the exact state returned by link get.
