<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/stm32.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/stm32.yaml

## Purpose
This root platform schema catalogs STM32 boards and SoCs across STM32F, STM32H, STM32MP1, and STM32MP2 families.

## Important APIs, Types, And Functions
It validates many ordered compatible chains for Discovery/Nucleo/Eval boards, DH/Octavo/Engicam/PHYTEC/Seeed/Avenger96 boards, DHCOM/DHCOR SOMs, and STM32MP15/13/25 variants, ending in the appropriate ST SoC fallback such as `st,stm32mp157`, `st,stm32mp135`, or `st,stm32mp257`.

## Control Flow
The root node name is `/`; `oneOf` selects a precise board, module, and SoC fallback chain. Some branches are board families with intermediate SOM fallbacks.

## State And Persistence
It records immutable platform identity only.

## Dependencies And Integration Points
It integrates with STM32 board DTS files, machine selection, and SoC/board-specific driver quirks.

## Risks
SOM/carrier fallback ordering is the main maintenance risk. New boards should preserve module and SoC fallback hierarchy so common support still matches.

## Test Signals
`dtbs_check` validates root compatible lists; boot on representative STM32 boards validates runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/stm32.yaml -->
