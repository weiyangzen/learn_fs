# sources/distributed-fs/ceph-client/include/dt-bindings/clock/agilex-clock.h

Purpose: defines Intel/Altera Agilex SoC clock IDs for DT clock consumers.

Important APIs/types/functions: IDs cover fixed-rate oscillator/internal/free clocks, main/peripheral PLLs and outputs, MPU/boot/NOC/fixed-factor free clocks, S2F user clocks, EMAC free/PTP clocks, GPIO/SDMMC/PSI references, gated MPU/L4/CoreSight/timer/S2F/EMAC/GPIO/NAND/SDMMC/SPI/USB/NAND ECC clocks, and `AGILEX_NUM_CLKS`.

Control flow: DTS clock cells use these IDs; the Agilex clock driver registers providers and gates/dividers accordingly.

State and persistence: numeric values are DT ABI.

Dependencies and integration: standalone clock binding used by Agilex DTS and clock controller.

Risks and test signals: missing ID 42 and other gaps must be mirrored by provider tables. Test clock lookup for peripherals, CoreSight clocks, EMAC PTP, SDMMC, USB, and provider count.
