<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,lan966x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,lan966x.h

Purpose: Defines DT clock IDs for the Microchip LAN966x clock controller, separating generated clock IDs and gate clocks.

Important APIs, types, and functions: Exports `GCK_ID_*` constants for QSPI, SDMMC, PI, MCAN, FLEXCOM, timer, and USB reference clocks, gate IDs such as `GCK_GATE_UHPHS`, `GCK_GATE_UDPHS`, `GCK_GATE_MCRAMC`, `GCK_GATE_HMATRIX`, and the `N_CLOCKS` count. No functions or types exist.

Control flow: No runtime flow is in the header. LAN966x provider code uses the IDs to register and look up generated/gated clocks.

State and persistence: IDs are persistent DT ABI. Gate state is in hardware registers and provider driver data.

Dependencies and integration points: Used by LAN966x DTS files and consumers for QSPI, SDMMC, CAN, FLEXCOM serial blocks, timers, USB, matrix, and RAM controller clocks.

Risks and test signals: Risks include mixing gate IDs with generator IDs and an incorrect `N_CLOCKS` bound. Test with `dtbs_check`, clock provider probe, and peripheral validation for QSPI, SDMMC, CAN, FLEXCOM UART/SPI/I2C modes, USB, and timer operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,lan966x.h -->
