<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml` is a PHY binding for `STMicroelectronics STM32MP25 USB3/PCIe COMBOPHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Single lane PHY shared (exclusive) between the USB3 and PCIe controllers. Supports 5Gbit/s for USB3 and PCIe gen2 or 2.5Gbit/s for PCIe gen1..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `st,stm32mp25-combophy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `wakeup-source`, `interrupts`, `access-controllers`, `st,ssc-on`, `st,rx-equalizer`, `st,output-micro-ohms`, `st,output-vswing-microvolt`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `access-controllers`, `clock-names`, `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `reset-names`, `resets`, `st,output-micro-ohms`, `st,output-vswing-microvolt`, `st,rx-equalizer`, `st,ssc-on`, `wakeup-source`. Important numeric/constant limits include `const=st,stm32mp25-combophy`, `maxItems=1`, `const=1`, `minItems=2`, `const=apb`, `const=ker`, `const=pad`, `const=phy`, `minimum=0`, `maximum=7`, `minimum=3999000`, `maximum=6090000`, `minimum=442000`, `maximum=803000`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `interrupts` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-combophy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/st/stm32mp251.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `interrupts`, `st,ssc-on`, `st,rx-equalizer`, `st,output-micro-ohms`, `st,output-vswing-microvolt`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `st,stm32mp25-combophy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml -->
