# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-config.h

## Purpose
This header supplies default CVMX executive configuration values for Octeon networking and hardware helper code. It sizes FPA pools, reserves FAU and scratchpad regions, configures PKO queues, and selects packet-input helper behavior.

## Important APIs, Types, and Functions
Constants configure debug prints, null-pointer protection, LLM ports, PKO queues per interface/PCI/loop port, and helper max ports. FPA constants define pool sizes and assign packet, WQE, and output-buffer pools. FAU allocation macros and enums (`cvmx_fau_reg_64_t`, `32_t`, `16_t`, `8_t`) reserve aligned register ranges and define `CVMX_FAU_REG_AVAIL_BASE` and end. Scratchpad constants reserve `CVMX_SCR_SCRATCH`. Helper macros set first and chained packet skips, backpressure, IPD enable, POW tag type, input tag fields, skip mode, and forced RGMII backpressure disable.

## Control Flow
There is no runtime code. Other CVMX helpers include these macros at compile time to size pools, initialize IPD/PKO/FPA/FAU, and select packet tag/backpressure behavior. The linked FAU enum pattern ensures later register-size classes start at the previous class end.

## State and Persistence Behavior
The header defines compile-time configuration, not runtime state. Its values shape persistent hardware initialization such as FPA pool sizes, IPD buffer skips, input tag generation, and PKO queue layout.

## Dependencies and Integration Points
It references helper constants such as `CVMX_HELPER_PKO_MAX_PORTS_INTERFACE*`, `CVMX_CACHE_LINE_SIZE`, `CVMX_POW_TAG_TYPE_ORDERED`, and `CVMX_PIP_PORT_CFG_MODE_SKIPL2`. It integrates with FPA, FAU, IPD/PIP, PKO, POW, and Ethernet helper setup.

## Risks
Pool sizes and packet skip constants are data-path ABI choices; wrong values can break buffer alignment, DMA layout, or packet parsing. `CVMX_HELPER_ENABLE_IPD` is off by default, so callers must explicitly enable packet input after final configuration. FAU allocation enums currently reserve no counters; adding counters must preserve alignment and avoid exceeding 2048 bytes.

## Test Signals
Signals include successful packet I/O initialization, correct FPA pool block sizes, valid packet buffer headroom, expected POW tag fields, no FAU register overlap, and no packet drops from backpressure or IPD-enable sequencing mistakes.
