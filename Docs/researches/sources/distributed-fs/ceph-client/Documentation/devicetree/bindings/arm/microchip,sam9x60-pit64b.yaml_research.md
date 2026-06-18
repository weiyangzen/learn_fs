<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sam9x60-pit64b.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sam9x60-pit64b.yaml

## Purpose
This schema describes Microchip PIT64B, a 64-bit periodic interval timer used by SAM9X60, SAM9X7, SAMA7D65, and SAMA7G5 families.

## Important APIs, Types, And Functions
Compatible is either `microchip,sam9x60-pit64b` or a newer SoC-specific string followed by that fallback. Required properties are `reg`, `interrupts`, and `clocks`; `clock-names` can contain one or two names from `pclk` and `gclk`.

## Control Flow
Validation enforces one MMIO resource, one interrupt, one or two clocks, and no unevaluated properties.

## State And Persistence
The DT records the timer register block, interrupt line, and clock sources. Runtime state is managed by the timer/clocksource driver.

## Dependencies And Integration Points
It depends on interrupt and clock provider bindings, including AT91/Microchip clock IDs in examples.

## Risks
Clock-name ordering must match clock phandles. Missing `gclk` may be valid for some designs but wrong for hardware needing a generated clock.

## Test Signals
`dt_binding_check` validates examples; boot-time clocksource/clockevent registration and timer interrupt delivery validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sam9x60-pit64b.yaml -->
