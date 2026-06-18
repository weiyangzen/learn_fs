<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,stm32-syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,stm32-syscon.yaml

## Purpose
This schema describes STM32 system configuration controllers, including syscfg/syscon blocks that may also provide clocks or firewall-related controls.

## Important APIs, Types, And Functions
Compatible branches include STM32F4 and STM32F7 syscfg with `syscon`, STM32MP157 syscfg with `syscon` and `simple-mfd`, and STM32MP25 syscfg variants. Properties include `reg`, optional clocks, `#clock-cells`, and child function nodes.

## Control Flow
Validation selects the variant branch and enforces strict properties. The schema allows declared child object behavior through `simple-mfd` when applicable.

## State And Persistence
The DT describes persistent syscfg registers and optional clock provider semantics. Runtime state is syscon/regmap and child-function driver state.

## Dependencies And Integration Points
It integrates with STM32 syscon users, common clock framework, simple-mfd child probing, and STM32 platform drivers.

## Risks
Variant-compatible order matters for syscon and MFD behavior. Missing clocks or clock cells can break consumers that rely on syscfg-derived clocks.

## Test Signals
`dtbs_check` validates syscfg nodes; syscon lookup, child probe, and clock registration validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,stm32-syscon.yaml -->
