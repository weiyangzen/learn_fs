# subset-b-000610 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ingenic,rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ingenic,rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ingenic,rtc.yaml` defines the Devicetree binding contract for Ingenic SoCs Real-Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ingenic,rtc.yaml` is a Devicetree YAML schema for Ingenic SoCs Real-Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `ingenic,jz4725b-rtc`, `ingenic,jz4740-rtc`, `ingenic,jz4760-rtc`, `ingenic,jz4770-rtc`, `ingenic,jz4780-rtc`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Paul Cercueil <paul@crapouillou.net>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `clock-names`: const `rtc` Required. `#clock-cells`: const `0` `system-power-controller`: Indicates that the RTC is responsible for powering OFF the system. `ingenic,reset-pin-assert-time-ms`: Reset pin low-level assertion time after wakeup (assuming RTC clock at 32 kHz) `ingenic,min-wakeup-pin-assert-time-ms`: Minimum wakeup pin assertion time (assuming RTC clock at 32 kHz)

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 2.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/ingenic,rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ingenic,rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/intersil,isl12022.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/intersil,isl12022.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/intersil,isl12022.yaml` defines the Devicetree binding contract for Intersil ISL12022 Real-time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/intersil,isl12022.yaml` is a Devicetree YAML schema for Intersil ISL12022 Real-time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `isil,isl12022`; required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: const `isil,isl12022` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `#clock-cells`: const `0` `isil,battery-trip-levels-microvolt`: ordered items; The battery voltages at which the first alarm and second alarm should trigger (normally ~85% and ~75% of nominal V_BAT).

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/intersil,isl12022.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/intersil,isl12022.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/isil,isl12026.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/isil,isl12026.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/isil,isl12026.yaml` defines the Devicetree binding contract for Intersil ISL12026 I2C RTC/EEPROM. The ISL12026 is a combination RTC and EEPROM device connected via I2C. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `isil,isl12026`; required properties `compatible`, `reg`. Maintainers: Piyush Patle <piyushpatle228@gmail.com>. Property contract: `compatible`: const `isil,isl12026` Required. `reg`: maxItems 1; I2C address of the RTC portion (must be 0x6f) Required. `isil,pwr-bsw`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Value written to the PWR.BSW bit for proper device operation. `isil,pwr-sbib`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Value written to the PWR.SBIB bit for proper device operation.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint32`, `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/isil,isl12026.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/isil,isl12026.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/isil,isl1208.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/isil,isl1208.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/isil,isl1208.yaml` defines the Devicetree binding contract for Intersil ISL1209/19 I2C RTC/Alarm chip with event in. ISL12X9 have additional pins EVIN and EVDET for tamper detection, while the ISL1208 and ISL1218 do not. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `isil,isl1208`, `isil,isl1209`, `isil,isl1218`, `isil,isl1219`; required properties `compatible`, `reg`. Maintainers: Biju Das <biju.das.jz@bp.renesas.com>, Trent Piepho <tpiepho@gmail.com>. Property contract: `compatible`: enum `isil,isl1208`, `isil,isl1209`, `isil,isl1218`, `isil,isl1219` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 2; minItems 1 `interrupt-names`: minItems 1; ordered items `clocks`: maxItems 1 `clock-names`: enum `xin`, `clkin`; Use xin, if connected to an external crystal. Use clkin, if connected to an external clock signal. `isil,ev-evienb`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Enable or disable internal pull on EVIN pin Default will leave the non-volatile configuration of the pullup as is. <0> : Enables internal pull-up on e...

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint32`, `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/isil,isl1208.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/isil,isl1208.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/loongson,rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/loongson,rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/loongson,rtc.yaml` defines the Devicetree binding contract for Loongson Real-Time Clock. The Loongson family chips use an on-chip counter 0 (Time Of Year counter) as the RTC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `loongson,ls1b-rtc`, `loongson,ls1c-rtc`, `loongson,ls2k0300-rtc`, `loongson,ls2k0500-rtc`, `loongson,ls2k1000-rtc`, `loongson,ls2k2000-rtc`, `loongson,ls7a-rtc`; required properties `compatible`, `reg`. Maintainers: Binbin Zhou <zhoubinbin@loongson.cn>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/loongson,rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/loongson,rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,armada-380-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,armada-380-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,armada-380-rtc.yaml` defines the Devicetree binding contract for RTC controller for the Armada 38x, 7K and 8K SoCs. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,armada-380-rtc.yaml` is a Devicetree YAML schema for RTC controller for the Armada 38x, 7K and 8K SoCs. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `marvell,armada-380-rtc`, `marvell,armada-8k-rtc`; required properties `compatible`, `reg`, `reg-names`, `interrupts`. Maintainers: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Property contract: `compatible`: enum `marvell,armada-380-rtc`, `marvell,armada-8k-rtc` Required. `reg`: ordered items Required. `reg-names`: ordered items Required. `interrupts`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/marvell,armada-380-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,armada-380-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,pxa-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,pxa-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,pxa-rtc.yaml` defines the Devicetree binding contract for PXA Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,pxa-rtc.yaml` is a Devicetree YAML schema for PXA Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `marvell,pxa-rtc`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Property contract: `compatible`: const `marvell,pxa-rtc` Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/marvell,pxa-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/marvell,pxa-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt2712-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt2712-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt2712-rtc.yaml` defines the Devicetree binding contract for MediaTek MT2712 on-SoC RTC. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt2712-rtc.yaml` is a Devicetree YAML schema for MediaTek MT2712 on-SoC RTC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `mediatek,mt2712-rtc`; required properties `reg`, `interrupts`. Maintainers: Ran Bi <ran.bi@mediatek.com>. Property contract: `compatible`: const `mediatek,mt2712-rtc` `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/mediatek,mt2712-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt2712-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt7622-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt7622-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt7622-rtc.yaml` defines the Devicetree binding contract for MediaTek MT7622 on-SoC RTC. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt7622-rtc.yaml` is a Devicetree YAML schema for MediaTek MT7622 on-SoC RTC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `mediatek,mt7622-rtc`, `mediatek,soc-rtc`; required properties `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Sean Wang <sean.wang@mediatek.com>. Property contract: `compatible`: ordered items `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `clock-names`: const `rtc` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/mediatek,mt7622-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mediatek,mt7622-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microchip,mpfs-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microchip,mpfs-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microchip,mpfs-rtc.yaml` defines the Devicetree binding contract for Microchip PolarFire Soc (MPFS) RTC. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microchip,mpfs-rtc.yaml` is a Devicetree YAML schema for Microchip PolarFire Soc (MPFS) RTC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `microchip,mpfs-rtc`, `microchip,pic64gx-rtc`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Daire McNamara <daire.mcnamara@microchip.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required. `clocks`: ordered items Required. `clock-names`: ordered items Required. `resets`: maxItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/microchip,mpfs-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microchip,mpfs-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3028.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3028.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3028.yaml` defines the Devicetree binding contract for Microchip RV-3028 RTC. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3028.yaml` is a Devicetree YAML schema for Microchip RV-3028 RTC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `microcrystal,rv3028`; required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: const `microcrystal,rv3028` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `#clock-cells`: const `0` `trickle-resistor-ohms`: enum `3000`, `5000`, `9000`, `15000` `vdd-supply` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/microcrystal,rv3028.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3028.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3032.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3032.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3032.yaml` defines the Devicetree binding contract for Microchip RV-3032 RTC. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3032.yaml` is a Devicetree YAML schema for Microchip RV-3032 RTC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `microcrystal,rv3032`; required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: const `microcrystal,rv3032` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `start-year` is accepted as a schema-defined property `trickle-resistor-ohms`: enum `1000`, `2000`, `7000`, `11000` `trickle-voltage-millivolt`: ref /schemas/types.yaml#/definitions/uint32; enum `1750`, `3000`, `4400` `wakeup-source` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint32`, `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/microcrystal,rv3032.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/microcrystal,rv3032.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/motorola,cpcap-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/motorola,cpcap-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/motorola,cpcap-rtc.yaml` defines the Devicetree binding contract for Motorola CPCAP PMIC RTC. This module is part of the Motorola CPCAP MFD device. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `motorola,cpcap-rtc`; required properties `compatible`, `interrupts`. Maintainers: Svyatoslav Ryhel <clamor95@gmail.com>. Property contract: `compatible`: const `motorola,cpcap-rtc` Required. `interrupts`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 0.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/motorola,cpcap-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/motorola,cpcap-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,msc313-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,msc313-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,msc313-rtc.yaml` defines the Devicetree binding contract for Mstar MSC313e RTC. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,msc313-rtc.yaml` is a Devicetree YAML schema for Mstar MSC313e RTC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `mstar,msc313-rtc`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Daniel Palmer <daniel@0x0f.com>, Romain Perier <romain.perier@gmail.com>. Property contract: `compatible`: enum `mstar,msc313-rtc` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `start-year` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/mstar,msc313-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,msc313-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,ssd202d-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,ssd202d-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,ssd202d-rtc.yaml` defines the Devicetree binding contract for Mstar SSD202D Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,ssd202d-rtc.yaml` is a Devicetree YAML schema for Mstar SSD202D Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `mstar,ssd202d-rtc`; required properties `compatible`, `reg`. Maintainers: Daniel Palmer <daniel@0x0f.com>, Romain Perier <romain.perier@gmail.com>. Property contract: `compatible`: enum `mstar,ssd202d-rtc` Required. `reg`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/mstar,ssd202d-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/mstar,ssd202d-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,ma35d1-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,ma35d1-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,ma35d1-rtc.yaml` defines the Devicetree binding contract for Nuvoton MA35D1 Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,ma35d1-rtc.yaml` is a Devicetree YAML schema for Nuvoton MA35D1 Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nuvoton,ma35d1-rtc`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Min-Jen Chen <mjchen@nuvoton.com>. Property contract: `compatible`: enum `nuvoton,ma35d1-rtc` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nuvoton,ma35d1-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,ma35d1-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,nct3018y.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,nct3018y.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,nct3018y.yaml` defines the Devicetree binding contract for NUVOTON NCT3018Y Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,nct3018y.yaml` is a Devicetree YAML schema for NUVOTON NCT3018Y Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nuvoton,nct3018y`; required properties `compatible`, `reg`. Maintainers: Medad CChien <ctcchien@nuvoton.com>, Mia Lin <mimi05633@gmail.com>. Property contract: `compatible`: const `nuvoton,nct3018y` Required. `reg`: maxItems 1 Required. `start-year` is accepted as a schema-defined property `reset-source` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nuvoton,nct3018y.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nuvoton,nct3018y.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nvidia,tegra20-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nvidia,tegra20-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nvidia,tegra20-rtc.yaml` defines the Devicetree binding contract for NVIDIA Tegra real-time clock. The Tegra RTC maintains seconds and milliseconds counters, and five alarm registers. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nvidia,tegra114-rtc`, `nvidia,tegra124-rtc`, `nvidia,tegra186-rtc`, `nvidia,tegra194-rtc`, `nvidia,tegra20-rtc`, `nvidia,tegra210-rtc`, `nvidia,tegra234-rtc`, `nvidia,tegra264-rtc`, `nvidia,tegra30-rtc`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `clock-names`: ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nvidia,tegra20-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nvidia,tegra20-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nvidia,vrs-10.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nvidia,vrs-10.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nvidia,vrs-10.yaml` defines the Devicetree binding contract for NVIDIA Voltage Regulator Specification Real Time Clock. NVIDIA VRS-10 (Voltage Regulator Specification) is a Power Management IC (PMIC) that implements a power sequencing solution with I2C interface. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nvidia,vrs-10`; required properties `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`. Maintainers: Shubhi Garg <shgarg@nvidia.com>. Property contract: `compatible`: const `nvidia,vrs-10` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `interrupt-controller` is accepted as a schema-defined property Required. `#interrupt-cells`: const `2` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nvidia,vrs-10.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nvidia,vrs-10.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,lpc1788-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,lpc1788-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,lpc1788-rtc.yaml` defines the Devicetree binding contract for NXP LPC1788 real-time clock. The LPC1788 RTC provides calendar and clock functionality together with periodic tick and alarm interrupt support. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,lpc1788-rtc`, `nxp,lpc1850-rtc`; required properties `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Maintainers: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `clock-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,lpc1788-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,lpc1788-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,lpc3220-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,lpc3220-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,lpc3220-rtc.yaml` defines the Devicetree binding contract for NXP LPC32xx SoC Real-time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,lpc3220-rtc.yaml` is a Devicetree YAML schema for NXP LPC32xx SoC Real-time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,lpc3220-rtc`; required properties `compatible`, `reg`. Maintainers: Frank Li <Frank.Li@nxp.com>. Property contract: `compatible`: enum `nxp,lpc3220-rtc` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `clocks`: maxItems 1 `start-year` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,lpc3220-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,lpc3220-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2123.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2123.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2123.yaml` defines the Devicetree binding contract for NXP PCF2123 SPI Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2123.yaml` is a Devicetree YAML schema for NXP PCF2123 SPI Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,pcf2123`; required properties `compatible`, `reg`. Maintainers: Javier Carrasco <javier.carrasco.cruz@gmail.com>. Property contract: `compatible`: enum `nxp,pcf2123` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/spi/spi-peripheral-props.yaml#`, `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/spi/spi-peripheral-props.yaml#`, `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,pcf2123.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2123.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2127.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2127.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2127.yaml` defines the Devicetree binding contract for NXP PCF2127 Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2127.yaml` is a Devicetree YAML schema for NXP PCF2127 Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,pca2129`, `nxp,pcf2127`, `nxp,pcf2129`, `nxp,pcf2131`; required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: enum `nxp,pca2129`, `nxp,pcf2127`, `nxp,pcf2129`, `nxp,pcf2131` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `start-year` is accepted as a schema-defined property `reset-source` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/spi/spi-peripheral-props.yaml#`, `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,pcf2127.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf2127.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85063.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85063.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85063.yaml` defines the Devicetree binding contract for NXP PCF85063 Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85063.yaml` is a Devicetree YAML schema for NXP PCF85063 Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `microcrystal,rv8063`, `microcrystal,rv8263`, `nxp,pca85073a`, `nxp,pcf85063`, `nxp,pcf85063a`, `nxp,pcf85063tp`; required properties `compatible`, `reg`. Maintainers: Alexander Stein <alexander.stein@ew.tq-group.com>. Property contract: `compatible`: enum `microcrystal,rv8063`, `microcrystal,rv8263`, `nxp,pcf85063`, `nxp,pcf85063a`, `nxp,pcf85063tp`, `nxp,pca85073a` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `#clock-cells`: const `0` `clock-output-names`: maxItems 1 `quartz-load-femtofarads`: enum `7000`, `12500`; The capacitive load of the quartz(x-tal). `clock`: ref /schemas/clock/fixed-clock.yaml; Provide this if the square wave pin is used as boot-enabled fixed clock. `wakeup-source` is accepted as a schema-defined property `spi-cs-high` is accepted as a schema-defined property `spi-3wire` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/spi/spi-peripheral-props.yaml#`, `rtc.yaml#`, 2 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/clock/fixed-clock.yaml`, `/schemas/spi/spi-peripheral-props.yaml#`, `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 2.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,pcf85063.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85063.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8523.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8523.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8523.yaml` defines the Devicetree binding contract for NXP PCF8523 Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8523.yaml` is a Devicetree YAML schema for NXP PCF8523 Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,pcf8523`; required properties `compatible`, `reg`. Maintainers: Sam Ravnborg <sam@ravnborg.org>. Property contract: `compatible`: const `nxp,pcf8523` Required. `reg`: maxItems 1 Required. `quartz-load-femtofarads`: enum `7000`, `12500`; The capacitive load of the crystal, expressed in femto Farad (fF).

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,pcf8523.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8523.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85363.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85363.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85363.yaml` defines the Devicetree binding contract for Philips PCF85263/PCF85363 Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85363.yaml` is a Devicetree YAML schema for Philips PCF85263/PCF85363 Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,pcf85263`, `nxp,pcf85363`; required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: enum `nxp,pcf85263`, `nxp,pcf85363` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `#clock-cells`: const `0` `clock-output-names`: maxItems 1 `quartz-load-femtofarads`: enum `6000`, `7000`, `12500`; The capacitive load of the quartz(x-tal). `start-year` is accepted as a schema-defined property `wakeup-source` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,pcf85363.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf85363.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8563.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8563.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8563.yaml` defines the Devicetree binding contract for Philips PCF8563/Epson RTC8564 Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8563.yaml` is a Devicetree YAML schema for Philips PCF8563/Epson RTC8564 Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `epson,rtc8564`, `microcrystal,rv8564`, `nxp,pca8565`, `nxp,pcf8563`; required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: enum `epson,rtc8564`, `microcrystal,rv8564`, `nxp,pca8565`, `nxp,pcf8563` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `#clock-cells`: const `0` `clock-output-names`: maxItems 1 `start-year` is accepted as a schema-defined property `wakeup-source` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,pcf8563.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,pcf8563.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,s32g-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,s32g-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,s32g-rtc.yaml` defines the Devicetree binding contract for NXP S32G2/S32G3 Real Time Clock (RTC). RTC hardware module present on S32G2/S32G3 SoCs is used as a wakeup source. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,s32g2-rtc`, `nxp,s32g3-rtc`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Bogdan Hamciuc <bogdan.hamciuc@nxp.com>, Ciprian Marian Costea <ciprianmarian.costea@nxp.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `clock-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,s32g-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,s32g-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/qcom-pm8xxx-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/qcom-pm8xxx-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/qcom-pm8xxx-rtc.yaml` defines the Devicetree binding contract for Qualcomm PM8xxx PMIC RTC device. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/qcom-pm8xxx-rtc.yaml` is a Devicetree YAML schema for Qualcomm PM8xxx PMIC RTC device. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `qcom,pm8018-rtc`, `qcom,pm8058-rtc`, `qcom,pm8921-rtc`, `qcom,pm8941-rtc`, `qcom,pmk8350-rtc`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Satya Priya <quic_c_skakit@quicinc.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 2; minItems 1 Required. `reg-names`: minItems 1; ordered items `interrupts`: maxItems 1 Required. `allow-set-time`: ref /schemas/types.yaml#/definitions/flag; Indicates that the setting of RTC time is allowed by the host CPU. `nvmem-cells`: ordered items `nvmem-cell-names`: ordered items `qcom,no-alarm`: RTC alarm is not owned by the OS `qcom,uefi-rtc-info`: RTC offset is stored as a four-byte GPS time offset in a 12-byte UEFI variable 882f8c2b-9646-435f-8de5-f208ff80c1bd-RTCInfo `wakeup-source` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/qcom-pm8xxx-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/qcom-pm8xxx-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rz-rtca3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rz-rtca3.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rz-rtca3.yaml` defines the Devicetree binding contract for Renesas RTCA-3 Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rz-rtca3.yaml` is a Devicetree YAML schema for Renesas RTCA-3 Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,r9a08g045-rtca3`, `renesas,r9a09g056-rtca3`, `renesas,r9a09g057-rtca3`, `renesas,rz-rtca3`; required properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, `resets`. Maintainers: Claudiu Beznea <claudiu.beznea.uj@bp.renesas.com>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required. `interrupt-names`: ordered items Required. `clocks`: ordered items Required. `clock-names`: ordered items Required. `resets`: maxItems 2; minItems 1 Required. `reset-names`: maxItems 2; minItems 1 `power-domains`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`, 2 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/renesas,rz-rtca3.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rz-rtca3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rzn1-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rzn1-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rzn1-rtc.yaml` defines the Devicetree binding contract for Renesas RZ/N1 SoCs Real-Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rzn1-rtc.yaml` is a Devicetree YAML schema for Renesas RZ/N1 SoCs Real-Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,r9a06g032-rtc`, `renesas,rzn1-rtc`; required properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`. Maintainers: Miquel Raynal <miquel.raynal@bootlin.com>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 3; minItems 3 Required. `interrupt-names`: ordered items Required. `clocks`: maxItems 2; minItems 1 Required. `clock-names`: minItems 1; ordered items Required. `power-domains`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/renesas,rzn1-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,rzn1-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,sh-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,sh-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,sh-rtc.yaml` defines the Devicetree binding contract for Real Time Clock for Renesas SH and ARM SoCs. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,sh-rtc.yaml` is a Devicetree YAML schema for Real Time Clock for Renesas SH and ARM SoCs. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,r7s72100-rtc`, `renesas,sh-rtc`; required properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`. Maintainers: Chris Brandt <chris.brandt@renesas.com>, Geert Uytterhoeven <geert+renesas@glider.be>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 3 Required. `interrupt-names`: ordered items Required. `clocks`: maxItems 4; minItems 1 Required. `clock-names`: maxItems 4; minItems 1; ordered items Required. `power-domains`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/renesas,sh-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/renesas,sh-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-ds1307.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-ds1307.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-ds1307.yaml` defines the Devicetree binding contract for Dallas DS1307 and compatible RTC. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-ds1307.yaml` is a Devicetree YAML schema for Dallas DS1307 and compatible RTC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `dallas,ds1307`, `dallas,ds1308`, `dallas,ds1337`, `dallas,ds1338`, `dallas,ds1339`, `dallas,ds1340`, `dallas,ds1341`, `dallas,ds1388`, `epson,rx8025`, `epson,rx8130`, `isil,isl12057`, `maxim,ds3231`, `microchip,mcp7940x`, `microchip,mcp7941x`, `pericom,pt7c4338`, `st,m41t0`, ... (18 total); required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 2; minItems 1 `interrupt-names`: maxItems 2 `#clock-cells`: const `1` `clock-output-names`: From common clock binding to override the default output clock name. `wakeup-source`: Enables wake up of host system on alarm. `vcc-supply` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml`. It is commonly instantiated as a bus child where `reg` selects the device address or MMIO window, depending on the compatible. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/rtc-ds1307.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-ds1307.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc.yaml` defines the Devicetree binding contract for Real Time Clock of the i.MX SoCs. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc.yaml` is a Devicetree YAML schema for Real Time Clock of the i.MX SoCs. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,imx1-rtc`, `fsl,imx21-rtc`, `fsl,imx31-rtc`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Philippe Reynes <tremyfr@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `clock-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/rtc-mxc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc_v2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc_v2.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc_v2.yaml` defines the Devicetree binding contract for i.MX53 Secure Real Time Clock (SRTC). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc_v2.yaml` is a Devicetree YAML schema for i.MX53 Secure Real Time Clock (SRTC). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,imx53-rtc`; required properties `compatible`, `reg`, `clocks`, `interrupts`. Maintainers: Patrick Bruenn <p.bruenn@beckhoff.com>. Property contract: `compatible`: enum `fsl,imx53-rtc` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/rtc-mxc_v2.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc-mxc_v2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc.yaml` defines the Devicetree binding contract for Real Time Clock Common Properties. This document describes generic bindings which can be used to describe Real Time Clock devices in a device tree. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values none extracted from `compatible`; required properties none. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `aux-voltage-chargeable`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Tells whether the battery/supercap of the RTC (if any) is chargeable or not: 0: not chargeable 1: chargeable `quartz-load-femtofarads`: The capacitive load of the quartz(x-tal), expressed in femto Farad (fF). The default value shall be listed (if optional), and likewise all valid value... `start-year`: ref /schemas/types.yaml#/definitions/uint32; If provided, the default hardware range supported by the RTC is shifted so the first usable year is the specified one. `trickle-diode-disable`: ref /schemas/types.yaml#/definitions/flag; Do not use internal trickle charger diode. Should be given if internal trickle charger diode should be disabled. `trickle-resistor-ohms`: Selected resistor for trickle charger. Should be given if trickle charger should be enabled. `trickle-voltage-millivolt`: Selected voltage for trickle charger. Should be given if trickle charger should be enabled and the trickle voltage is different from the RTC main powe... `wakeup-source`: ref /schemas/types.yaml#/definitions/flag; Enables wake up of host system on alarm. `reset-source`: ref /schemas/types.yaml#/definitions/flag; The RTC is able to reset the machine.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 0.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: true` intentionally leaves extension room, usually because this is a common/shared schema. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/s3c-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/s3c-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/s3c-rtc.yaml` defines the Devicetree binding contract for Samsung S3C, S5P and Exynos Real Time Clock controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/s3c-rtc.yaml` is a Devicetree YAML schema for Samsung S3C, S5P and Exynos Real Time Clock controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `samsung,exynos3250-rtc`, `samsung,exynos7-rtc`, `samsung,exynos850-rtc`, `samsung,s3c6410-rtc`; required properties none. Maintainers: Krzysztof Kozlowski <krzk@kernel.org>. Property contract: `compatible`: schema keys oneOf `reg`: maxItems 1 `interrupts`: maxItems 2; minItems 2; Two interrupt numbers to the cpu should be specified. First interrupt number is the rtc alarm interrupt and second interrupt number is the rtc tick in... `clocks`: maxItems 2 `clock-names`: ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/s3c-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/s3c-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sa1100-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sa1100-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sa1100-rtc.yaml` defines the Devicetree binding contract for Marvell Real Time Clock controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sa1100-rtc.yaml` is a Devicetree YAML schema for Marvell Real Time Clock controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `mrvl,mmp-rtc`, `mrvl,sa1100-rtc`; required properties `compatible`, `reg`, `interrupts`, `interrupt-names`. Maintainers: Alessandro Zummo <a.zummo@towertech.it>, Alexandre Belloni <alexandre.belloni@bootlin.com>, Rob Herring <robh@kernel.org>. Property contract: `compatible`: enum `mrvl,sa1100-rtc`, `mrvl,mmp-rtc` Required. `reg`: maxItems 1 Required. `interrupts`: minItems 2 Required. `interrupt-names`: ordered items Required. `clocks`: maxItems 1 `resets`: maxItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/sa1100-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sa1100-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sophgo,cv1800b-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sophgo,cv1800b-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sophgo,cv1800b-rtc.yaml` defines the Devicetree binding contract for Real Time Clock of the Sophgo CV1800 SoC. The RTC (Real Time Clock) is an independently powered module in the chip. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `sophgo,cv1800b-rtc`; required properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`. Maintainers: sophgo@lists.linux.dev. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required. `interrupt-names`: ordered items Required. `clocks`: ordered items Required. `clock-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/rtc/rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/rtc/rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/sophgo,cv1800b-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sophgo,cv1800b-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sprd,sc2731-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sprd,sc2731-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sprd,sc2731-rtc.yaml` defines the Devicetree binding contract for Spreadtrum SC2731 Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sprd,sc2731-rtc.yaml` is a Devicetree YAML schema for Spreadtrum SC2731 Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `sprd,sc2730-rtc`, `sprd,sc2731-rtc`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Orson Zhai <orsonzhai@gmail.com>, Baolin Wang <baolin.wang7@gmail.com>, Chunyan Zhang <zhang.lyra@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 0.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/sprd,sc2731-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sprd,sc2731-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m41t80.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m41t80.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m41t80.yaml` defines the Devicetree binding contract for ST M41T80 family of RTC and compatible. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m41t80.yaml` is a Devicetree YAML schema for ST M41T80 family of RTC and compatible. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `microcrystal,rv4162`, `st,m41t62`, `st,m41t65`, `st,m41t80`, `st,m41t81`, `st,m41t81s`, `st,m41t82`, `st,m41t83`, `st,m41t84`, `st,m41t85`, `st,m41t87`; required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: enum `st,m41t62`, `st,m41t65`, `st,m41t80`, `st,m41t81`, `st,m41t81s`, `st,m41t82`, `st,m41t83`, `st,m41t84`, ... (11 total) Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `#clock-cells`: const `1` `clock-output-names`: maxItems 1; From common clock binding to override the default output clock name. `clock`: ref /schemas/clock/fixed-clock.yaml#

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/clock/fixed-clock.yaml#`, `rtc.yaml`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/st,m41t80.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m41t80.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m48t86.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m48t86.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m48t86.yaml` defines the Devicetree binding contract for ST M48T86 / Dallas DS12887 RTC with SRAM. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m48t86.yaml` is a Devicetree YAML schema for ST M48T86 / Dallas DS12887 RTC with SRAM. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `st,m48t86`; required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: enum `st,m48t86` Required. `reg`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/st,m48t86.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,m48t86.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,stm32-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,stm32-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,stm32-rtc.yaml` defines the Devicetree binding contract for STMicroelectronics STM32 Real Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,stm32-rtc.yaml` is a Devicetree YAML schema for STMicroelectronics STM32 Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `st,stm32-rtc`, `st,stm32h7-rtc`, `st,stm32mp1-rtc`, `st,stm32mp25-rtc`; required properties `compatible`, `reg`, `clocks`, `interrupts`. Maintainers: Gabriel Fernandez <gabriel.fernandez@foss.st.com>. Property contract: `compatible`: enum `st,stm32-rtc`, `st,stm32h7-rtc`, `st,stm32mp1-rtc`, `st,stm32mp25-rtc` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 2; minItems 1 Required. `clock-names`: ordered items `st,syscfg`: ref /schemas/types.yaml#/definitions/phandle-array; ordered items; Phandle/offset/mask triplet. The phandle to pwrcfg used to access control register at offset, and change the dbp (Disable Backup Protection) bit repre... `assigned-clocks`: maxItems 1; override default rtc_ck parent clock reference to the rtc_ck clock entry `assigned-clock-parents`: maxItems 1; override default rtc_ck parent clock phandle of the new parent clock of rtc_ck

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` 3 conditional branch(es). Pattern `^rtc-[a-z]+-[0-9]+$` accepts child objects with properties `function`, `pins`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/pinctrl/pinmux-node.yaml`, `/schemas/types.yaml#/definitions/phandle-array`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 2.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/st,stm32-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/st,stm32-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sunplus,sp7021-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sunplus,sp7021-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sunplus,sp7021-rtc.yaml` defines the Devicetree binding contract for Sunplus SP7021 Real Time Clock controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sunplus,sp7021-rtc.yaml` is a Devicetree YAML schema for Sunplus SP7021 Real Time Clock controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `sunplus,sp7021-rtc`; required properties `compatible`, `reg`, `reg-names`, `clocks`, `resets`, `interrupts`. Maintainers: Vincent Shih <vincent.sunplus@gmail.com>. Property contract: `compatible`: const `sunplus,sp7021-rtc` Required. `reg`: maxItems 1 Required. `reg-names`: ordered items Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `resets`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/sunplus,sp7021-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/sunplus,sp7021-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ti,bq32000.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ti,bq32000.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ti,bq32000.yaml` defines the Devicetree binding contract for TI BQ32000 I2C Serial Real-Time Clock. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ti,bq32000.yaml` is a Devicetree YAML schema for TI BQ32000 I2C Serial Real-Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `ti,bq32000`; required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: const `ti,bq32000` Required. `reg`: const `104` Required. `interrupts`: maxItems 1 `start-year` is accepted as a schema-defined property `trickle-resistor-ohms`: enum `1120`, `20180` `trickle-diode-disable` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/ti,bq32000.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ti,bq32000.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ti,k3-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ti,k3-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ti,k3-rtc.yaml` defines the Devicetree binding contract for Texas Instruments K3 Real Time Clock. This RTC appears in the AM62x family of SoCs. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `ti,am62-rtc`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Nishanth Menon <nm@ti.com>. Property contract: `compatible`: enum `ti,am62-rtc` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `clock-names`: ordered items Required. `power-domains`: maxItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/ti,k3-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/ti,k3-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/trivial-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/trivial-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/trivial-rtc.yaml` defines the Devicetree binding contract for Trivial RTCs. This is a list of trivial RTC devices that have simple device tree bindings, consisting only of a compatible field, an address and possibly an interrupt line. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `abracon,abb5zes3`, `abracon,abeoz9`, `aspeed,ast2400-rtc`, `aspeed,ast2500-rtc`, `aspeed,ast2600-rtc`, `cnxt,cx92755-rtc`, `dallas,ds1374`, `dallas,ds1672`, `dallas,ds3232`, `dallas,m41t00`, `dfrobot,sd2405al`, `emmicro,em3027`, `epson,rx8010`, `epson,rx8035`, `epson,rx8111`, `epson,rx8571`, ... (35 total); required properties `compatible`, `reg`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>. Property contract: `compatible`: enum `abracon,abb5zes3`, `abracon,abeoz9`, `aspeed,ast2400-rtc`, `aspeed,ast2500-rtc`, `aspeed,ast2600-rtc`, `cnxt,cx92755-rtc`, `dallas,ds1374`, `dallas,ds1672`, ... (35 total) Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `start-year` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 0.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/trivial-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/trivial-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/xlnx,zynqmp-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/xlnx,zynqmp-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/xlnx,zynqmp-rtc.yaml` defines the Devicetree binding contract for Xilinx Zynq Ultrascale+ MPSoC Real Time Clock. RTC controller for the Xilinx Zynq MPSoC Real Time Clock. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `xlnx,versal-net-rtc`, `xlnx,versal-rtc`, `xlnx,zynqmp-rtc`; required properties `compatible`, `reg`, `interrupts`, `interrupt-names`. Maintainers: Michal Simek <michal.simek@amd.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 2 Required. `interrupt-names`: ordered items Required. `clocks`: maxItems 1 `clock-names`: ordered items `power-domains`: maxItems 1 `calibration`: ref /schemas/types.yaml#/definitions/uint32; calibration value for 1 sec period which will be programmed directly to calibration register.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint32`, `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/xlnx,zynqmp-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/xlnx,zynqmp-rtc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250.yaml` defines the Devicetree binding contract for UART (Universal Asynchronous Receiver/Transmitter). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250.yaml` is a Devicetree YAML schema for UART (Universal Asynchronous Receiver/Transmitter). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `altr,16550-FIFO128`, `altr,16550-FIFO32`, `altr,16550-FIFO64`, `andestech,uart16550`, `aspeed,ast2400-vuart`, `aspeed,ast2500-vuart`, `cavium,octeon-3860-uart`, `exar,xr16l2550`, `exar,xr16l2551`, `exar,xr16l2552`, `fsl,16550-FIFO64`, `fsl,ns16550`, `intel,xscale-uart`, `loongson,ls2k0500-uart`, `loongson,ls2k1000-uart`, `loongson,ls2k1500-uart`, ... (47 total); required properties `reg`, `interrupts`. Maintainers: devicetree@vger.kernel.org. Property contract: `compatible`: schema keys oneOf `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: minItems 1; ordered items `clock-names`: maxItems 2; minItems 1 `resets`: maxItems 1 `dmas`: maxItems 4; minItems 1 `dma-names`: maxItems 4; minItems 1 `clock-frequency` is accepted as a schema-defined property `current-speed`: ref /schemas/types.yaml#/definitions/uint32; The current active speed of the UART. `reg-offset`: ref /schemas/types.yaml#/definitions/uint32; Offset to apply to the mapbase from the start of the registers. `reg-shift`: Quantity to shift the register offsets by. `reg-io-width`: The size (in bytes) of the IO accesses that should be performed on the device. There are some systems that require 32-bit accesses to the UART (e.g. T... `used-by-rtas`: Set to indicate that the port is in use by the OpenFirmware RTAS and should not be registered. Additional top-level properties constrained but not expanded here: `no-loopback-test`, `fifo-size`, `auto-flow-control`, `tx-threshold`, `overrun-throttle-ms`, `rts-gpios`, `cts-gpios`, `dtr-gpios`, `dsr-gpios`, `rng-gpios`, `dcd-gpios`, `aspeed,sirq-polarity-sense`, `aspeed,lpc-io-reg`, `aspeed,lpc-interrupts`.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`, `/schemas/memory-controllers/mc-peripheral-props.yaml#`, 6 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/memory-controllers/mc-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 3.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/8250.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250_omap.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250_omap.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250_omap.yaml` defines the Devicetree binding contract for 8250 compliant UARTs on TI's OMAP2+ and K3 SoCs. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250_omap.yaml` is a Devicetree YAML schema for 8250 compliant UARTs on TI's OMAP2+ and K3 SoCs. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `ti,am3352-uart`, `ti,am4372-uart`, `ti,am64-uart`, `ti,am654-uart`, `ti,dra742-uart`, `ti,j721e-uart`, `ti,omap2-uart`, `ti,omap3-uart`, `ti,omap4-uart`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Vignesh Raghavendra <vigneshr@ti.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 2; minItems 1; First entry is module IRQ required for normal IO operation. Second entry is optional and corresponds to system wakeup IRQ where supported. Required. `clocks`: maxItems 1 `clock-names`: const `fclk` `power-domains` is accepted as a schema-defined property `dmas`: maxItems 2; minItems 1 `dma-names`: ordered items `ti,hwmods`: ref /schemas/types.yaml#/definitions/string; Must be "uart<n>", n being the instance number (1-based) This property is applicable only on legacy platforms mainly omap2/3 and ti81xx and should not... `rs485-rts-active-high` is accepted as a schema-defined property `clock-frequency` is accepted as a schema-defined property `current-speed` is accepted as a schema-defined property `overrun-throttle-ms` is accepted as a schema-defined property `wakeup-source` is accepted as a schema-defined property Additional top-level properties constrained but not expanded here: `pinctrl-0`, `pinctrl-1`, `pinctrl-names`.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`, `/schemas/serial/rs485.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/rs485.yaml#`, `/schemas/serial/serial.yaml#`, `/schemas/types.yaml#/definitions/string`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/8250_omap.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/8250_omap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/actions,owl-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/actions,owl-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/actions,owl-uart.yaml` defines the Devicetree binding contract for Actions Semi Owl UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/actions,owl-uart.yaml` is a Devicetree YAML schema for Actions Semi Owl UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `actions,owl-uart`, `actions,s500-uart`, `actions,s900-uart`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Kanak Shilledar <kanakshilledar111@protonmail.com>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/actions,owl-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/actions,owl-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,juart-1.0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,juart-1.0.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,juart-1.0.yaml` defines the Devicetree binding contract for Altera JTAG UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,juart-1.0.yaml` is a Devicetree YAML schema for Altera JTAG UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `altr,juart-1.0`; required properties `compatible`. Maintainers: Dinh Nguyen <dinguyen@kernel.org>. Property contract: `compatible`: const `altr,juart-1.0` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 0.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/altr,juart-1.0.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,juart-1.0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,uart-1.0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,uart-1.0.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,uart-1.0.yaml` defines the Devicetree binding contract for Altera UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,uart-1.0.yaml` is a Devicetree YAML schema for Altera UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `altr,uart-1.0`; required properties `compatible`. Maintainers: Dinh Nguyen <dinguyen@kernel.org>. Property contract: `compatible`: const `altr,uart-1.0` Required. `clock-frequency`: Frequency of the clock input to the UART.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 0.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/altr,uart-1.0.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/altr,uart-1.0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/amlogic,meson-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/amlogic,meson-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/amlogic,meson-uart.yaml` defines the Devicetree binding contract for Amlogic Meson SoC UART Serial Interface. The Amlogic Meson SoC UART Serial Interface is present on a large range of SoCs, and can be present either in the "Always-On" power domain or the "Everything-Else" power domain. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `amlogic,a4-uart`, `amlogic,a9-uart`, `amlogic,meson-a1-uart`, `amlogic,meson-ao-uart`, `amlogic,meson-g12a-uart`, `amlogic,meson-gx-uart`, `amlogic,meson-s4-uart`, `amlogic,meson6-uart`, `amlogic,meson8-uart`, `amlogic,meson8b-uart`, `amlogic,s6-uart`, `amlogic,s7-uart`, `amlogic,s7d-uart`, `amlogic,t7-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Neil Armstrong <neil.armstrong@linaro.org>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `clock-names`: ordered items Required. `fifo-size`: ref /schemas/types.yaml#/definitions/uint32; enum `64`, `128`; The fifo size supported by the UART channel.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint32`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/amlogic,meson-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/amlogic,meson-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,dcc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,dcc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,dcc.yaml` defines the Devicetree binding contract for ARM DCC (Data communication channel) serial emulation. ARM DCC (Data communication channel) serial emulation interface available via JTAG can be also used as one of serial line tightly coupled with every ARM CPU available in the system. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `arm,dcc`; required properties `compatible`. Maintainers: Michal Simek <michal.simek@amd.com>. Property contract: `compatible`: const `arm,dcc` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/arm,dcc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,dcc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,mps2-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,mps2-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,mps2-uart.yaml` defines the Devicetree binding contract for Arm MPS2 UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,mps2-uart.yaml` is a Devicetree YAML schema for Arm MPS2 UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `arm,mps2-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Vladimir Murzin <vladimir.murzin@arm.com>. Property contract: `compatible`: const `arm,mps2-uart` Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/arm,mps2-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,mps2-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,sbsa-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,sbsa-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,sbsa-uart.yaml` defines the Devicetree binding contract for ARM SBSA UART. This UART uses a subset of the PL011 registers and consequently lives in the PL011 driver. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `arm,sbsa-uart`; required properties `compatible`, `reg`, `interrupts`, `current-speed`. Maintainers: Andre Przywara <andre.przywara@arm.com>. Property contract: `compatible`: const `arm,sbsa-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `current-speed`: fixed baud rate set by the firmware Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 0.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/arm,sbsa-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/arm,sbsa-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/atmel,at91-usart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/atmel,at91-usart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/atmel,at91-usart.yaml` defines the Devicetree binding contract for Atmel Universal Synchronous Asynchronous Receiver/Transmitter (USART). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/atmel,at91-usart.yaml` is a Devicetree YAML schema for Atmel Universal Synchronous Asynchronous Receiver/Transmitter (USART). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `atmel,at91rm9200-dbgu`, `atmel,at91rm9200-usart`, `atmel,at91sam9260-dbgu`, `atmel,at91sam9260-usart`, `microchip,lan9691-usart`, `microchip,sam9x60-dbgu`, `microchip,sam9x60-usart`, `microchip,sam9x7-dbgu`, `microchip,sam9x7-usart`, `microchip,sama7d65-usart`; required properties `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `atmel,usart-mode`. Maintainers: Richard Genoud <richard.genoud@bootlin.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: minItems 1; ordered items Required. `clock-names`: minItems 1; ordered items Required. `dmas`: ordered items `dma-names`: ordered items `atmel,usart-mode`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Must be either <AT91_USART_MODE_SPI> for SPI or <AT91_USART_MODE_SERIAL> for USART (found in dt-bindings/mfd/at91-usart.h). Required. `atmel,use-dma-rx`: use of PDC or DMA for receiving data `atmel,use-dma-tx`: use of PDC or DMA for transmitting data `atmel,fifo-size`: ref /schemas/types.yaml#/definitions/uint32; enum `16`, `32`; Maximum number of data the RX and TX FIFOs can store for FIFO capable USARTS.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/rs485.yaml#`, `/schemas/serial/serial.yaml#`, `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 3.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/atmel,at91-usart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/atmel,at91-usart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm2835-aux-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm2835-aux-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm2835-aux-uart.yaml` defines the Devicetree binding contract for BCM2835 AUXILIARY UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm2835-aux-uart.yaml` is a Devicetree YAML schema for BCM2835 AUXILIARY UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `brcm,bcm2835-aux-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Pratik Farkase <pratikfarkase94@gmail.com>, Florian Fainelli <florian.fainelli@broadcom.com>, Stefan Wahren <wahrenst@gmx.net>. Property contract: `compatible`: const `brcm,bcm2835-aux-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/brcm,bcm2835-aux-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm2835-aux-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm6345-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm6345-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm6345-uart.yaml` defines the Devicetree binding contract for BCM63xx UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm6345-uart.yaml` is a Devicetree YAML schema for BCM63xx UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `brcm,bcm6345-uart`; required properties `reg`, `interrupts`, `clocks`. Maintainers: Rafał Miłecki <rafal@milecki.pl>. Property contract: `compatible`: const `brcm,bcm6345-uart` `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `clock-names`: const `refclk`

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/brcm,bcm6345-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm6345-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm7271-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm7271-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm7271-uart.yaml` defines the Devicetree binding contract for Broadcom 8250 based serial port. The Broadcom UART is based on the basic 8250 UART but with enhancements for more accurate high speed baud rates and support for DMA. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `brcm,bcm7271-uart`, `brcm,bcm7278-uart`; required properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`. Maintainers: Al Cooper <alcooperx@gmail.com>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 5; minItems 1 Required. `reg-names`: The UART register block and optionally the DMA register blocks. Required. `interrupts`: maxItems 2; minItems 1 Required. `interrupt-names`: minItems 1; ordered items; The UART interrupt and optionally the DMA interrupt. Required. `clocks`: maxItems 1 Required. `clock-names`: const `sw_baud` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/brcm,bcm7271-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/brcm,bcm7271-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cdns,uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cdns,uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cdns,uart.yaml` defines the Devicetree binding contract for Cadence UART Controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cdns,uart.yaml` is a Devicetree YAML schema for Cadence UART Controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `axiado,ax3000-uart`, `cdns,uart-r1p12`, `cdns,uart-r1p8`, `xlnx,xuartps`, `xlnx,zynqmp-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Michal Simek <michal.simek@amd.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 2 Required. `clock-names`: ordered items Required. `resets`: maxItems 1 `power-domains`: maxItems 1 `cts-override`: Override the CTS modem status signal. This signal will always be reported as active instead of being obtained from the modem status register. Define t...

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`, `rs485.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rs485.yaml#`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/cdns,uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cdns,uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cirrus,ep7209-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cirrus,ep7209-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cirrus,ep7209-uart.yaml` defines the Devicetree binding contract for Cirrus Logic CLPS711X Universal Asynchronous Receiver/Transmitter (UART). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cirrus,ep7209-uart.yaml` is a Devicetree YAML schema for Cirrus Logic CLPS711X Universal Asynchronous Receiver/Transmitter (UART). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `cirrus,ep7209-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `syscon`. Maintainers: Alexander Shiyan <shc_work@mail.ru>. Property contract: `compatible`: const `cirrus,ep7209-uart` Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required. `clocks`: maxItems 1 Required. `syscon`: ref /schemas/types.yaml#/definitions/phandle; Phandle to SYSCON node, which contains UART control bits. Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`, `/schemas/types.yaml#/definitions/phandle`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/cirrus,ep7209-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cirrus,ep7209-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cnxt,cx92755-usart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cnxt,cx92755-usart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cnxt,cx92755-usart.yaml` defines the Devicetree binding contract for Conexant Digicolor USART. Note: this binding is only applicable for using the USART peripheral as UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `cnxt,cx92755-usart`; required properties `compatible`, `reg`, `clocks`, `interrupts`. Maintainers: Baruch Siach <baruch@tkos.co.il>. Property contract: `compatible`: const `cnxt,cx92755-usart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/cnxt,cx92755-usart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/cnxt,cx92755-usart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/esp,esp32-acm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/esp,esp32-acm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/esp,esp32-acm.yaml` defines the Devicetree binding contract for ESP32S3 ACM gadget controller. Fixed function USB CDC-ACM gadget controller of the Espressif ESP32S3 SoC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `esp,esp32s3-acm`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Max Filippov <jcmvbkbc@gmail.com>. Property contract: `compatible`: const `esp,esp32s3-acm` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/esp,esp32-acm.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/esp,esp32-acm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/esp,esp32-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/esp,esp32-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/esp,esp32-uart.yaml` defines the Devicetree binding contract for ESP32xx UART controllers. ESP32 UART controller is a part of the ESP32 SoC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `esp,esp32-uart`, `esp,esp32s3-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Max Filippov <jcmvbkbc@gmail.com>. Property contract: `compatible`: enum `esp,esp32-uart`, `esp,esp32s3-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/esp,esp32-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/esp,esp32-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl,s32-linflexuart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl,s32-linflexuart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl,s32-linflexuart.yaml` defines the Devicetree binding contract for Freescale LINFlexD UART. The LINFlexD controller implements several LIN protocol versions, as well as support for full-duplex UART communication through 8-bit and 9-bit frames. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,s32v234-linflexuart`, `nxp,s32g2-linflexuart`, `nxp,s32g3-linflexuart`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Chester Lin <chester62515@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/fsl,s32-linflexuart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl,s32-linflexuart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-imx-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-imx-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-imx-uart.yaml` defines the Devicetree binding contract for Freescale i.MX Universal Asynchronous Receiver/Transmitter (UART). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-imx-uart.yaml` is a Devicetree YAML schema for Freescale i.MX Universal Asynchronous Receiver/Transmitter (UART). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,imx1-uart`, `fsl,imx21-uart`, `fsl,imx25-uart`, `fsl,imx27-uart`, `fsl,imx31-uart`, `fsl,imx35-uart`, `fsl,imx50-uart`, `fsl,imx51-uart`, `fsl,imx53-uart`, `fsl,imx6q-uart`, `fsl,imx6sl-uart`, `fsl,imx6sll-uart`, `fsl,imx6sx-uart`, `fsl,imx6ul-uart`, `fsl,imx7d-uart`, `fsl,imx8mm-uart`, ... (19 total); required properties `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Maintainers: Fabio Estevam <festevam@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: minItems 1; ordered items Required. `clocks`: maxItems 2 Required. `clock-names`: ordered items Required. `dmas`: ordered items `dma-names`: ordered items `wakeup-source` is accepted as a schema-defined property `fsl,dte-mode`: ref /schemas/types.yaml#/definitions/flag; Indicate the uart works in DTE mode. The uart works in DCE mode by default. `fsl,inverted-tx`: ref /schemas/types.yaml#/definitions/flag; Indicate that the hardware attached to the peripheral inverts the signal transmitted, and that the peripheral should invert its output using the INVT ... `fsl,inverted-rx`: ref /schemas/types.yaml#/definitions/flag; Indicate that the hardware attached to the peripheral inverts the signal received, and that the peripheral should invert its input using the INVR regi... `fsl,dma-info`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 2; minItems 2; First cell contains the size of DMA buffer chunks, second cell contains the amount of chunks used for the device. Multiplying both numbers is the tota...

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`, `rs485.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32-array`, `rs485.yaml#`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/fsl-imx-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-imx-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-lpuart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-lpuart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-lpuart.yaml` defines the Devicetree binding contract for Freescale low power universal asynchronous receiver/transmitter (lpuart). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-lpuart.yaml` is a Devicetree YAML schema for Freescale low power universal asynchronous receiver/transmitter (lpuart). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,imx7ulp-lpuart`, `fsl,imx8dxl-lpuart`, `fsl,imx8qm-lpuart`, `fsl,imx8qxp-lpuart`, `fsl,imx8ulp-lpuart`, `fsl,imx93-lpuart`, `fsl,imx94-lpuart`, `fsl,imx95-lpuart`, `fsl,imxrt1050-lpuart`, `fsl,imxrt1170-lpuart`, `fsl,ls1021a-lpuart`, `fsl,ls1028a-lpuart`, `fsl,vf610-lpuart`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Fugang Duan <fugang.duan@nxp.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: minItems 1; ordered items Required. `clock-names`: minItems 1; ordered items Required. `power-domains`: maxItems 1 `dmas`: ordered items `dma-names`: ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rs485.yaml#`, `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rs485.yaml#`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/fsl-lpuart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-lpuart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-mxs-auart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-mxs-auart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-mxs-auart.yaml` defines the Devicetree binding contract for Freescale MXS Application UART (AUART). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-mxs-auart.yaml` is a Devicetree YAML schema for Freescale MXS Application UART (AUART). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `alphascale,asm9260-auart`, `fsl,imx23-auart`, `fsl,imx28-auart`; required properties `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`. Maintainers: Fabio Estevam <festevam@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: minItems 1; ordered items `clock-names`: minItems 1; ordered items `dmas`: ordered items Required. `dma-names`: ordered items Required. `uart-has-rtscts` is accepted as a schema-defined property `rts-gpios` is accepted as a schema-defined property `cts-gpios` is accepted as a schema-defined property `dtr-gpios` is accepted as a schema-defined property `dsr-gpios` is accepted as a schema-defined property `rng-gpios` is accepted as a schema-defined property `dcd-gpios` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/fsl-mxs-auart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl-mxs-auart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/google,goldfish-tty.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/google,goldfish-tty.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/google,goldfish-tty.yaml` defines the Devicetree binding contract for Google Goldfish TTY. Android goldfish TTY device generated by Android emulator. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `google,goldfish-tty`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Kuan-Wei Chiu <visitorckw@gmail.com>. Property contract: `compatible`: const `google,goldfish-tty` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/google,goldfish-tty.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/google,goldfish-tty.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/ingenic,uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/ingenic,uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/ingenic,uart.yaml` defines the Devicetree binding contract for Ingenic SoCs UART controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/ingenic,uart.yaml` is a Devicetree YAML schema for Ingenic SoCs UART controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `ingenic,jz4725b-uart`, `ingenic,jz4740-uart`, `ingenic,jz4750-uart`, `ingenic,jz4755-uart`, `ingenic,jz4760-uart`, `ingenic,jz4770-uart`, `ingenic,jz4775-uart`, `ingenic,jz4780-uart`, `ingenic,x1000-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Maintainers: Paul Cercueil <paul@crapouillou.net>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `clock-names`: ordered items Required. `dmas`: ordered items Required. `dma-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/ingenic,uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/ingenic,uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/lantiq,asc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/lantiq,asc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/lantiq,asc.yaml` defines the Devicetree binding contract for Lantiq SoC ASC serial controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/lantiq,asc.yaml` is a Devicetree YAML schema for Lantiq SoC ASC serial controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `lantiq,asc`; required properties `compatible`, `reg`, `interrupts`. Maintainers: John Crispin <john@phrozen.org>, Songjun Wu <songjun.wu@linux.intel.com>. Property contract: `compatible`: const `lantiq,asc` Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required. `clocks`: ordered items `clock-names`: ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/lantiq,asc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/lantiq,asc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/litex,liteuart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/litex,liteuart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/litex,liteuart.yaml` defines the Devicetree binding contract for LiteUART serial controller. LiteUART serial controller is a part of the LiteX FPGA SoC builder. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `litex,liteuart`; required properties `compatible`, `reg`. Maintainers: Karol Gugala <kgugala@antmicro.com>, Mateusz Holenko <mholenko@antmicro.com>. Property contract: `compatible`: const `litex,liteuart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/litex,liteuart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/litex,liteuart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/marvell,armada-3700-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/marvell,armada-3700-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/marvell,armada-3700-uart.yaml` defines the Devicetree binding contract for Marvell Armada-3700 UART. Marvell UART is a non standard UART used in some of Marvell EBU SoCs (e.g. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `marvell,armada-3700-uart`, `marvell,armada-3700-uart-ext`; required properties `compatible`, `reg`, `interrupts`, `interrupt-names`. Maintainers: Pali Rohár <pali@kernel.org>. Property contract: `compatible`: enum `marvell,armada-3700-uart`, `marvell,armada-3700-uart-ext` Required. `reg`: maxItems 1 Required. `interrupts`: minItems 2; ordered items Required. `interrupt-names`: maxItems 3; minItems 2 Required. `clocks`: maxItems 1; UART reference clock used to derive the baud rate. If absent, only fixed baud rate from the bootloader is supported.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 2.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/marvell,armada-3700-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/marvell,armada-3700-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/maxim,max310x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/maxim,max310x.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/maxim,max310x.yaml` defines the Devicetree binding contract for Maxim MAX310X Advanced Universal Asynchronous Receiver-Transmitter (UART). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/maxim,max310x.yaml` is a Devicetree YAML schema for Maxim MAX310X Advanced Universal Asynchronous Receiver-Transmitter (UART). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `maxim,max14830`, `maxim,max3107`, `maxim,max3108`, `maxim,max3109`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Hugo Villeneuve <hvilleneuve@dimonoff.com>. Property contract: `compatible`: enum `maxim,max3107`, `maxim,max3108`, `maxim,max3109`, `maxim,max14830` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `clock-names`: enum `xtal`, `osc` Required. `gpio-controller` is accepted as a schema-defined property `#gpio-cells`: const `2` `gpio-line-names`: maxItems 16; minItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/serial/serial.yaml#`, `/schemas/serial/rs485.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/rs485.yaml#`, `/schemas/serial/serial.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/maxim,max310x.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/maxim,max310x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/mediatek,uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/mediatek,uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/mediatek,uart.yaml` defines the Devicetree binding contract for MediaTek Universal Asynchronous Receiver/Transmitter (UART). The MediaTek UART is based on the basic 8250 UART and compatible with 16550A, with enhancements for high speed baud rates and support for DMA. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `mediatek,mt2701-uart`, `mediatek,mt2712-uart`, `mediatek,mt6572-uart`, `mediatek,mt6577-uart`, `mediatek,mt6580-uart`, `mediatek,mt6582-uart`, `mediatek,mt6589-uart`, `mediatek,mt6755-uart`, `mediatek,mt6765-uart`, `mediatek,mt6779-uart`, `mediatek,mt6795-uart`, `mediatek,mt6797-uart`, `mediatek,mt6893-uart`, `mediatek,mt7622-uart`, `mediatek,mt7623-uart`, `mediatek,mt7629-uart`, ... (29 total); required properties `compatible`, `reg`, `clocks`, `interrupts`. Maintainers: Matthias Brugger <matthias.bgg@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1; The base address of the UART register bank Required. `interrupts`: maxItems 2; minItems 1 Required. `interrupt-names`: minItems 1; ordered items; The UART interrupt and optionally the RX in-band wakeup interrupt. `clocks`: minItems 1; ordered items Required. `clock-names`: minItems 1; ordered items `dmas`: ordered items `dma-names`: ordered items `pinctrl-0` is accepted as a schema-defined property `pinctrl-1` is accepted as a schema-defined property `pinctrl-names`: minItems 1; ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/mediatek,uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/mediatek,uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/microchip,pic32mzda-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/microchip,pic32mzda-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/microchip,pic32mzda-uart.yaml` defines the Devicetree binding contract for Microchip PIC32 UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/microchip,pic32mzda-uart.yaml` is a Devicetree YAML schema for Microchip PIC32 UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `microchip,pic32mzda-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Andrei Pistirica <andrei.pistirica@microchip.com>, Purna Chandra Mandal <purna.mandal@microchip.com>. Property contract: `compatible`: const `microchip,pic32mzda-uart` Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/microchip,pic32mzda-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/microchip,pic32mzda-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nuvoton,ma35d1-serial.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nuvoton,ma35d1-serial.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nuvoton,ma35d1-serial.yaml` defines the Devicetree binding contract for Nuvoton MA35D1 Universal Asynchronous Receiver/Transmitter (UART). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nuvoton,ma35d1-serial.yaml` is a Devicetree YAML schema for Nuvoton MA35D1 Universal Asynchronous Receiver/Transmitter (UART). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nuvoton,ma35d1-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Min-Jen Chen <mjchen@nuvoton.com>, Jacky Huang <ychuang3@nuvoton.com>. Property contract: `compatible`: const `nuvoton,ma35d1-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/nuvoton,ma35d1-serial.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nuvoton,ma35d1-serial.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra194-tcu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra194-tcu.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra194-tcu.yaml` defines the Devicetree binding contract for NVIDIA Tegra Combined UART (TCU). The TCU is a system for sharing a hardware UART instance among multiple systems within the Tegra SoC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nvidia,tegra194-tcu`, `nvidia,tegra234-tcu`; required properties `compatible`, `mbox-names`, `mboxes`. Maintainers: Thierry Reding <thierry.reding@gmail.com>, Jonathan Hunter <jonathanh@nvidia.com>. Property contract: `compatible`: schema keys oneOf Required. `mbox-names`: ordered items Required. `mboxes`: ordered items; List of phandles to mailbox channels used for receiving and transmitting data from and to the hardware UART. Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/nvidia,tegra194-tcu.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra194-tcu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra20-hsuart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra20-hsuart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra20-hsuart.yaml` defines the Devicetree binding contract for NVIDIA Tegra20/Tegra30 high speed (DMA based) UART controller driver. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra20-hsuart.yaml` is a Devicetree YAML schema for NVIDIA Tegra20/Tegra30 high speed (DMA based) UART controller driver. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nvidia,tegra124-hsuart`, `nvidia,tegra186-hsuart`, `nvidia,tegra194-hsuart`, `nvidia,tegra20-hsuart`, `nvidia,tegra30-hsuart`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `reset-names`, `dmas`, `dma-names`. Maintainers: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `resets`: ordered items Required. `reset-names`: ordered items Required. `dmas`: ordered items Required. `dma-names`: ordered items Required. `nvidia,enable-modem-interrupt`: ref /schemas/types.yaml#/definitions/flag; Enable modem interrupts. Should be enable only if all 8 lines of UART controller are pinmuxed. `nvidia,adjust-baud-rates`: ref /schemas/types.yaml#/definitions/uint32-matrix; ordered items; List of entries providing percentage of baud rate adjustment within a range. Each entry contains a set of 3 values: range low/high and adjusted rate. ...

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32-matrix`, `serial.yaml`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/nvidia,tegra20-hsuart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra20-hsuart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra264-utc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra264-utc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra264-utc.yaml` defines the Devicetree binding contract for NVIDIA Tegra UTC (UART Trace Controller) client. Represents a client interface of the Tegra UTC (UART Trace Controller). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nvidia,tegra264-utc`; required properties `compatible`, `reg`, `reg-names`, `interrupts`, `tx-threshold`, `rx-threshold`. Maintainers: Kartik Rajput <kkartik@nvidia.com>, Thierry Reding <thierry.reding@gmail.com>, Jonathan Hunter <jonathanh@nvidia.com>. Property contract: `compatible`: const `nvidia,tegra264-utc` Required. `reg`: ordered items Required. `reg-names`: ordered items Required. `interrupts`: maxItems 1 Required. `tx-threshold`: schema keys minimum, maximum Required. `rx-threshold`: schema keys minimum, maximum Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/nvidia,tegra264-utc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nvidia,tegra264-utc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,lpc3220-hsuart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,lpc3220-hsuart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,lpc3220-hsuart.yaml` defines the Devicetree binding contract for NXP LPC32xx SoC High Speed UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,lpc3220-hsuart.yaml` is a Devicetree YAML schema for NXP LPC32xx SoC High Speed UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,lpc3220-hsuart`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Vladimir Zapolskiy <vz@mleia.com>, Piotr Wojtaszczyk <piotr.wojtaszczyk@timesys.com>. Property contract: `compatible`: const `nxp,lpc3220-hsuart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/nxp,lpc3220-hsuart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,lpc3220-hsuart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,sc16is7xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,sc16is7xx.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,sc16is7xx.yaml` defines the Devicetree binding contract for NXP SC16IS7xx Advanced Universal Asynchronous Receiver-Transmitter (UART). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,sc16is7xx.yaml` is a Devicetree YAML schema for NXP SC16IS7xx Advanced Universal Asynchronous Receiver-Transmitter (UART). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,sc16is740`, `nxp,sc16is741`, `nxp,sc16is750`, `nxp,sc16is752`, `nxp,sc16is760`, `nxp,sc16is762`; required properties `compatible`, `reg`. Maintainers: Hugo Villeneuve <hvilleneuve@dimonoff.com>. Property contract: `compatible`: enum `nxp,sc16is740`, `nxp,sc16is741`, `nxp,sc16is750`, `nxp,sc16is752`, `nxp,sc16is760`, `nxp,sc16is762` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1; When missing, device driver uses polling instead. `clocks`: maxItems 1 `reset-gpios`: maxItems 1 `clock-frequency`: When there is no clock provider visible to the platform, this is the source crystal or external clock frequency for the IC in Hz. `gpio-controller` is accepted as a schema-defined property `#gpio-cells`: const `2` `gpio-line-names`: maxItems 8; minItems 1 `irda-mode-ports`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 2; minItems 1; ordered items; An array that lists the indices of the port that should operate in IrDA mode: 0: port A 1: port B `nxp,modem-control-line-ports`: ref /schemas/types.yaml#/definitions/uint32-array; maxItems 2; minItems 1; ordered items; An array that lists the indices of the port that should have shared GPIO lines configured as modem control lines: 0: port A 1: port B

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/serial/serial.yaml#`, `/schemas/serial/rs485.yaml#`; `oneOf` 2 additional composition item(s). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/rs485.yaml#`, `/schemas/serial/serial.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/nxp,sc16is7xx.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/nxp,sc16is7xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/pl011.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/pl011.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/pl011.yaml` defines the Devicetree binding contract for ARM AMBA Primecell PL011 serial UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/pl011.yaml` is a Devicetree YAML schema for ARM AMBA Primecell PL011 serial UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `arm,pl011`, `arm,primecell`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Rob Herring <robh@kernel.org>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 2; When present, the first clock listed must correspond to the clock named UARTCLK on the IP block, i.e. the clock to the external serial line, whereas t... `clock-names`: ordered items `resets`: maxItems 1 `power-domains`: maxItems 1 `dmas`: maxItems 2; minItems 1 `dma-names`: minItems 1; ordered items `pinctrl-0` is accepted as a schema-defined property `pinctrl-1` is accepted as a schema-defined property `pinctrl-names`: minItems 1; ordered items; When present, must have one state named "default", and may contain a second name named "sleep". The former state sets up pins for ordinary operation w... `auto-poll`: Enables polling when using RX DMA. `poll-rate-ms`: Rate at which poll occurs when auto-poll is set. default 100ms. Additional top-level properties constrained but not expanded here: `poll-timeout-ms`, `reg-io-width`.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/arm/primecell.yaml#`, `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/arm/primecell.yaml#`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/pl011.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/pl011.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qca,ar9330-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qca,ar9330-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qca,ar9330-uart.yaml` defines the Devicetree binding contract for Qualcomm Atheros AR9330 High-Speed UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qca,ar9330-uart.yaml` is a Devicetree YAML schema for Qualcomm Atheros AR9330 High-Speed UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `qca,ar9330-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Oleksij Rempel <o.rempel@pengutronix.de>. Property contract: `compatible`: const `qca,ar9330-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `clock-names`: const `uart` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/qca,ar9330-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qca,ar9330-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,msm-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,msm-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,msm-uart.yaml` defines the Devicetree binding contract for Qualcomm MSM SoC Serial UART. The MSM serial UART hardware is designed for low-speed use cases where a dma-engine isn't needed. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `qcom,msm-uart`; required properties `compatible`, `clock-names`, `clocks`, `interrupts`, `reg`. Maintainers: Bjorn Andersson <andersson@kernel.org>, Krzysztof Kozlowski <krzk@kernel.org>. Property contract: `compatible`: const `qcom,msm-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `clock-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/qcom,msm-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,msm-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,msm-uartdm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,msm-uartdm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,msm-uartdm.yaml` defines the Devicetree binding contract for Qualcomm MSM Serial UARTDM. The MSM serial UARTDM hardware is designed for high-speed use cases where the transmit and/or receive channels can be offloaded to a dma-engine. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `qcom,msm-uartdm`, `qcom,msm-uartdm-v1.1`, `qcom,msm-uartdm-v1.2`, `qcom,msm-uartdm-v1.3`, `qcom,msm-uartdm-v1.4`; required properties `compatible`, `clock-names`, `clocks`, `interrupts`, `reg`. Maintainers: Andy Gross <agross@kernel.org>, Bjorn Andersson <bjorn.andersson@linaro.org>, Krzysztof Kozlowski <krzk@kernel.org>. Property contract: `compatible`: ordered items Required. `reg`: minItems 1; ordered items Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 2 Required. `clock-names`: ordered items Required. `power-domains`: maxItems 1 `dmas`: maxItems 2 `dma-names`: ordered items `interconnects`: maxItems 1 `operating-points-v2` is accepted as a schema-defined property `qcom,rx-crci`: ref /schemas/types.yaml#/definitions/uint32; Identificator for Client Rate Control Interface to be used with RX DMA channel. Required when using DMA for reception with UARTDM v1.3 and below. `qcom,tx-crci`: ref /schemas/types.yaml#/definitions/uint32; Identificator for Client Rate Control Interface to be used with TX DMA channel. Required when using DMA for transmission with UARTDM v1.3 and below.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`, `/schemas/types.yaml#/definitions/uint32`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/qcom,msm-uartdm.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,msm-uartdm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,sa8255p-geni-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,sa8255p-geni-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,sa8255p-geni-uart.yaml` defines the Devicetree binding contract for Qualcomm Geni based QUP UART interface. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,sa8255p-geni-uart.yaml` is a Devicetree YAML schema for Qualcomm Geni based QUP UART interface. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `qcom,sa8255p-geni-debug-uart`, `qcom,sa8255p-geni-uart`; required properties `compatible`, `reg`, `interrupts`, `power-domains`, `power-domain-names`. Maintainers: Praveen Talari <quic_ptalari@quicinc.com>. Property contract: `compatible`: enum `qcom,sa8255p-geni-uart`, `qcom,sa8255p-geni-debug-uart` Required. `reg`: maxItems 1 Required. `interrupts`: minItems 1; ordered items Required. `interrupt-names`: minItems 1; ordered items; The UART interrupt and optionally the RX in-band wakeup interrupt as not all UART instances have a wakeup-capable interrupt routed via the PDC. `power-domains`: maxItems 2; minItems 2 Required. `power-domain-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/qcom,sa8255p-geni-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,sa8255p-geni-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,serial-geni-qcom.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,serial-geni-qcom.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,serial-geni-qcom.yaml` defines the Devicetree binding contract for Qualcomm Geni based QUP UART interface. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,serial-geni-qcom.yaml` is a Devicetree YAML schema for Qualcomm Geni based QUP UART interface. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `qcom,geni-debug-uart`, `qcom,geni-uart`; required properties `compatible`, `clocks`, `clock-names`, `interrupts`, `reg`. Maintainers: Andy Gross <agross@kernel.org>, Bjorn Andersson <bjorn.andersson@linaro.org>. Property contract: `compatible`: enum `qcom,geni-uart`, `qcom,geni-debug-uart` Required. `reg`: maxItems 1 Required. `interrupts`: minItems 1; ordered items Required. `clocks`: maxItems 1 Required. `clock-names`: const `se` Required. `power-domains`: maxItems 1 `interconnects`: maxItems 2 `interconnect-names`: ordered items `operating-points-v2` is accepted as a schema-defined property `pinctrl-0` is accepted as a schema-defined property `pinctrl-1` is accepted as a schema-defined property `pinctrl-names`: minItems 1; ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`, `/schemas/soc/qcom/qcom,se-common-props.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`, `/schemas/soc/qcom/qcom,se-common-props.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/qcom,serial-geni-qcom.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/qcom,serial-geni-qcom.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/rda,8810pl-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/rda,8810pl-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/rda,8810pl-uart.yaml` defines the Devicetree binding contract for RDA Micro UART Interface. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/rda,8810pl-uart.yaml` is a Devicetree YAML schema for RDA Micro UART Interface. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `rda,8810pl-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Manivannan Sadhasivam <manivannan.sadhasivam@linaro.org>. Property contract: `compatible`: const `rda,8810pl-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/rda,8810pl-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/rda,8810pl-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,em-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,em-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,em-uart.yaml` defines the Devicetree binding contract for Renesas EMMA Mobile UART Interface. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,em-uart.yaml` is a Devicetree YAML schema for Renesas EMMA Mobile UART Interface. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,em-uart`, `renesas,r9a09g011-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Magnus Damm <magnus.damm@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: minItems 1; ordered items Required. `clock-names`: minItems 1; ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/renesas,em-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,em-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,hscif.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,hscif.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,hscif.yaml` defines the Devicetree binding contract for Renesas High Speed Serial Communication Interface with FIFO (HSCIF). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,hscif.yaml` is a Devicetree YAML schema for Renesas High Speed Serial Communication Interface with FIFO (HSCIF). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,hscif`, `renesas,hscif-r8a7742`, `renesas,hscif-r8a7743`, `renesas,hscif-r8a7744`, `renesas,hscif-r8a7745`, `renesas,hscif-r8a77470`, `renesas,hscif-r8a774a1`, `renesas,hscif-r8a774b1`, `renesas,hscif-r8a774c0`, `renesas,hscif-r8a774e1`, `renesas,hscif-r8a7778`, `renesas,hscif-r8a7779`, `renesas,hscif-r8a7790`, `renesas,hscif-r8a7791`, `renesas,hscif-r8a7792`, `renesas,hscif-r8a7793`, ... (35 total); required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`. Maintainers: Geert Uytterhoeven <geert+renesas@glider.be>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 4; minItems 1 Required. `clock-names`: maxItems 4; minItems 1; ordered items Required. `resets`: maxItems 1 `power-domains`: maxItems 1 Required. `dmas`: maxItems 4; minItems 2; Must contain a list of pairs of references to DMA specifiers, one for transmission, and one for reception. `dma-names`: maxItems 4; minItems 2; ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/renesas,hscif.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,hscif.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,rsci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,rsci.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,rsci.yaml` defines the Devicetree binding contract for Renesas RSCI Serial Communication Interface. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,rsci.yaml` is a Devicetree YAML schema for Renesas RSCI Serial Communication Interface. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,r9a08g046-rsci`, `renesas,r9a09g047-rsci`, `renesas,r9a09g056-rsci`, `renesas,r9a09g057-rsci`, `renesas,r9a09g077-rsci`, `renesas,r9a09g087-rsci`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`. Maintainers: Geert Uytterhoeven <geert+renesas@glider.be>, Lad Prabhakar <prabhakar.mahadev-lad.rj@bp.renesas.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: minItems 4; ordered items Required. `interrupt-names`: minItems 4; ordered items `clocks`: maxItems 6; minItems 2 Required. `clock-names`: schema keys oneOf Required. `resets`: ordered items `reset-names`: ordered items `power-domains`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`, 3 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/renesas,rsci.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,rsci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,sci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,sci.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,sci.yaml` defines the Devicetree binding contract for Renesas Serial Communication Interface. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,sci.yaml` is a Devicetree YAML schema for Renesas Serial Communication Interface. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,r9a07g043-sci`, `renesas,r9a07g044-sci`, `renesas,r9a07g054-sci`, `renesas,sci`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Geert Uytterhoeven <geert+renesas@glider.be>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required. `interrupt-names`: ordered items `clocks`: maxItems 2; minItems 1 Required. `clock-names`: maxItems 2; minItems 1; ordered items Required. `uart-has-rtscts` is explicitly forbidden in this branch

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/renesas,sci.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,sci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scif.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scif.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scif.yaml` defines the Devicetree binding contract for Renesas Serial Communication Interface with FIFO (SCIF). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scif.yaml` is a Devicetree YAML schema for Renesas Serial Communication Interface with FIFO (SCIF). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,rcar-gen1-scif`, `renesas,rcar-gen2-scif`, `renesas,rcar-gen3-scif`, `renesas,rcar-gen4-scif`, `renesas,rcar-gen5-scif`, `renesas,scif`, `renesas,scif-r7s72100`, `renesas,scif-r7s9210`, `renesas,scif-r8a7742`, `renesas,scif-r8a7743`, `renesas,scif-r8a7744`, `renesas,scif-r8a7745`, `renesas,scif-r8a77470`, `renesas,scif-r8a774a1`, `renesas,scif-r8a774a3`, `renesas,scif-r8a774b1`, ... (46 total); required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`. Maintainers: Geert Uytterhoeven <geert+renesas@glider.be>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: schema keys oneOf Required. `interrupt-names`: minItems 4; ordered items `clocks`: maxItems 4; minItems 1 Required. `clock-names`: maxItems 4; minItems 1; ordered items Required. `resets`: maxItems 1 `power-domains`: maxItems 1 Required. `dmas`: maxItems 4; minItems 2; Must contain a list of pairs of references to DMA specifiers, one for transmission, and one for reception. `dma-names`: maxItems 4; minItems 2; ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`, 5 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/renesas,scif.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scif.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifa.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifa.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifa.yaml` defines the Devicetree binding contract for Renesas Serial Communications Interface with FIFO A (SCIFA). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifa.yaml` is a Devicetree YAML schema for Renesas Serial Communications Interface with FIFO A (SCIFA). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,rcar-gen2-scifa`, `renesas,scifa`, `renesas,scifa-r8a73a4`, `renesas,scifa-r8a7740`, `renesas,scifa-r8a7742`, `renesas,scifa-r8a7743`, `renesas,scifa-r8a7744`, `renesas,scifa-r8a7745`, `renesas,scifa-r8a7790`, `renesas,scifa-r8a7791`, `renesas,scifa-r8a7793`, `renesas,scifa-r8a7794`, `renesas,scifa-sh73a0`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`. Maintainers: Geert Uytterhoeven <geert+renesas@glider.be>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `clock-names`: enum `fck` Required. `resets`: maxItems 1 `power-domains`: maxItems 1 Required. `dmas`: maxItems 4; minItems 2; Must contain a list of pairs of references to DMA specifiers, one for transmission, and one for reception. `dma-names`: maxItems 4; minItems 2; ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/renesas,scifa.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifb.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifb.yaml` defines the Devicetree binding contract for Renesas Serial Communications Interface with FIFO B (SCIFB). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifb.yaml` is a Devicetree YAML schema for Renesas Serial Communications Interface with FIFO B (SCIFB). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `renesas,rcar-gen2-scifb`, `renesas,scifb`, `renesas,scifb-r8a73a4`, `renesas,scifb-r8a7740`, `renesas,scifb-r8a7742`, `renesas,scifb-r8a7743`, `renesas,scifb-r8a7744`, `renesas,scifb-r8a7745`, `renesas,scifb-r8a7790`, `renesas,scifb-r8a7791`, `renesas,scifb-r8a7793`, `renesas,scifb-r8a7794`, `renesas,scifb-sh73a0`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`. Maintainers: Geert Uytterhoeven <geert+renesas@glider.be>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `clock-names`: enum `fck` Required. `resets`: maxItems 1 `power-domains`: maxItems 1 Required. `dmas`: maxItems 4; minItems 2; Must contain a list of pairs of references to DMA specifiers, one for transmission, and one for reception. `dma-names`: maxItems 4; minItems 2; ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/renesas,scifb.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/renesas,scifb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/rs485.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/rs485.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/rs485.yaml` defines the Devicetree binding contract for RS485 serial communications. The RTS signal is capable of automatically controlling line direction for the built-in half-duplex mode. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values none extracted from `compatible`; required properties none. Maintainers: Rob Herring <robh@kernel.org>. Property contract: `rs485-rts-delay`: ref /schemas/types.yaml#/definitions/uint32-array; ordered items; prop-encoded-array <a b> `rs485-rts-active-high`: ref /schemas/types.yaml#/definitions/flag; drive RTS high when sending (this is the default). `rs485-rts-active-low`: ref /schemas/types.yaml#/definitions/flag; drive RTS low when sending (default is high). `rs485-rx-active-high`: ref /schemas/types.yaml#/definitions/flag; Polarity of receiver enable signal (when separate from RTS). True indicates active high (default is low). `linux,rs485-enabled-at-boot-time`: ref /schemas/types.yaml#/definitions/flag; enables the rs485 feature at boot time. It can be disabled later with proper ioctl. `rs485-rx-during-tx`: ref /schemas/types.yaml#/definitions/flag; enables the receiving of data even while sending data. `rs485-term-gpios`: maxItems 1; GPIO pin to enable RS485 bus termination. `rs485-rx-during-tx-gpios`: maxItems 1; Output GPIO pin that sets the state of rs485-rx-during-tx. This signal can be used to control the RX part of an RS485 transceiver. Thereby the active ...

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32-array`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 0.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: true` intentionally leaves extension room, usually because this is a common/shared schema. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/rs485.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/rs485.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/samsung_uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/samsung_uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/samsung_uart.yaml` defines the Devicetree binding contract for Samsung S3C, S5P, Exynos, and S5L (Apple SoC) SoC UART Controller. Each Samsung UART should have an alias correctly numbered in the "aliases" node, according to serialN format, where N is the port number (non-negative decimal integer) as specified by User's Manual of respective SoC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `apple,s5l-uart`, `axis,artpec8-uart`, `axis,artpec9-uart`, `google,gs101-uart`, `samsung,exynos2200-uart`, `samsung,exynos4210-uart`, `samsung,exynos5433-uart`, `samsung,exynos7-uart`, `samsung,exynos7870-uart`, `samsung,exynos7885-uart`, `samsung,exynos850-uart`, `samsung,exynos8890-uart`, `samsung,exynos8895-uart`, `samsung,exynosautov9-uart`, `samsung,exynosautov920-uart`, `samsung,s3c6400-uart`, ... (18 total); required properties `compatible`, `clocks`, `clock-names`, `interrupts`, `reg`. Maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Greg Kroah-Hartman <gregkh@linuxfoundation.org>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 2; minItems 1; RX interrupt and optionally TX interrupt. Required. `clocks`: maxItems 5; minItems 2 Required. `clock-names`: maxItems 5; minItems 2 Required. `power-domains`: maxItems 1 `dmas`: ordered items `dma-names`: ordered items `reg-io-width`: enum `1`, `4`; The size (in bytes) of the IO accesses that should be performed on the device. `samsung,uart-fifosize`: ref /schemas/types.yaml#/definitions/uint32; enum `16`, `64`, `256`; The fifo size supported by the UART channel.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`, 5 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint32`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 2.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/samsung_uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/samsung_uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/serial-peripheral-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/serial-peripheral-props.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/serial-peripheral-props.yaml` defines the Devicetree binding contract for Common Properties for Serial-attached Devices. Devices connected over serial/UART, expressed as children of a serial controller, might need similar properties, e.g. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values none extracted from `compatible`; required properties none. Maintainers: Rob Herring <robh@kernel.org>, Greg Kroah-Hartman <gregkh@linuxfoundation.org>. Property contract: `max-speed`: ref /schemas/types.yaml#/definitions/uint32; The maximum baud rate the device operates at. This should only be present if the maximum is less than the slave device can support. For example, a par... `current-speed`: ref /schemas/types.yaml#/definitions/uint32; The current baud rate the device operates at. This should only be present in case a driver has no chance to know the baud rate of the slave device. Ex...

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint32`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 0.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: true` intentionally leaves extension room, usually because this is a common/shared schema. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/serial-peripheral-props.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/serial-peripheral-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/serial.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/serial.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/serial.yaml` defines the Devicetree binding contract for Serial Interface Generic. This document lists a set of generic properties for describing UARTs in a device tree. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values none extracted from `compatible`; required properties none. Maintainers: Rob Herring <robh@kernel.org>, Greg Kroah-Hartman <gregkh@linuxfoundation.org>. Property contract: `label` is accepted as a schema-defined property `cts-gpios`: maxItems 1; Must contain a GPIO specifier, referring to the GPIO pin to be used as the UART's CTS line. `dcd-gpios`: maxItems 1; Must contain a GPIO specifier, referring to the GPIO pin to be used as the UART's DCD line. `dsr-gpios`: maxItems 1; Must contain a GPIO specifier, referring to the GPIO pin to be used as the UART's DSR line. `dtr-gpios`: maxItems 1; Must contain a GPIO specifier, referring to the GPIO pin to be used as the UART's DTR line. `rng-gpios`: maxItems 1; Must contain a GPIO specifier, referring to the GPIO pin to be used as the UART's RNG line. `rts-gpios`: maxItems 1; Must contain a GPIO specifier, referring to the GPIO pin to be used as the UART's RTS line. `uart-has-rtscts`: ref /schemas/types.yaml#/definitions/flag; The presence of this property indicates that the UART has dedicated lines for RTS/CTS hardware flow control, and that they are available for use (wire... `rx-tx-swap`: RX and TX pins are swapped. `cts-rts-swap`: CTS and RTS pins are swapped. `rx-threshold`: ref /schemas/types.yaml#/definitions/uint32; RX FIFO threshold configuration (in bytes). `tx-threshold`: ref /schemas/types.yaml#/definitions/uint32; TX FIFO threshold configuration (in bytes). `port`: ref /schemas/graph.yaml#/properties/port

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^(bluetooth|bluetooth-gnss|embedded-controller|gnss|gps|mcu|onewire)$` accepts child objects with properties none.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `serial-peripheral-props.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: true` intentionally leaves extension room, usually because this is a common/shared schema. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/serial.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/serial.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sifive-serial.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sifive-serial.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sifive-serial.yaml` defines the Devicetree binding contract for SiFive asynchronous serial interface (UART). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sifive-serial.yaml` is a Devicetree YAML schema for SiFive asynchronous serial interface (UART). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `canaan,k210-uarths`, `sifive,fu540-c000-uart`, `sifive,fu740-c000-uart`, `sifive,uart0`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Pragnesh Patel <pragnesh.patel@sifive.com>, Paul Walmsley <paul.walmsley@sifive.com>, Palmer Dabbelt <palmer@sifive.com>. Property contract: `compatible`: ordered items; Should be something similar to "sifive,<chip>-uart" for the UART as integrated on a particular chip, and "sifive,uart<version>" for the general UART I... Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/sifive-serial.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sifive-serial.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/snps,arc-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/snps,arc-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/snps,arc-uart.yaml` defines the Devicetree binding contract for Synopsys ARC UART. Synopsys ARC UART is a non-standard UART used in some of the ARC FPGA boards. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `snps,arc-uart`; required properties `compatible`, `reg`, `interrupts`, `clock-frequency`, `current-speed`. Maintainers: Vineet Gupta <vgupta@kernel.org>. Property contract: `compatible`: const `snps,arc-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clock-frequency`: the input clock frequency for the UART Required. `current-speed`: baud rate for UART Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/snps,arc-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/snps,arc-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/snps-dw-apb-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/snps-dw-apb-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/snps-dw-apb-uart.yaml` defines the Devicetree binding contract for Synopsys DesignWare ABP UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/snps-dw-apb-uart.yaml` is a Devicetree YAML schema for Synopsys DesignWare ABP UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `anlogic,dr1v90-uart`, `brcm,bcm11351-dw-apb-uart`, `brcm,bcm21664-dw-apb-uart`, `renesas,r9a06g032-uart`, `renesas,rzn1-uart`, `rockchip,px30-uart`, `rockchip,rk1808-uart`, `rockchip,rk3036-uart`, `rockchip,rk3066-uart`, `rockchip,rk3128-uart`, `rockchip,rk3188-uart`, `rockchip,rk3288-uart`, `rockchip,rk3308-uart`, `rockchip,rk3328-uart`, `rockchip,rk3368-uart`, `rockchip,rk3399-uart`, ... (30 total); required properties `compatible`, `reg`. Maintainers: Rob Herring <robh@kernel.org>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 `clocks`: maxItems 2; minItems 1 `clock-names`: ordered items `resets`: maxItems 2; minItems 1 `power-domains`: maxItems 1 `dmas`: maxItems 2 `dma-names`: ordered items `clock-frequency` is accepted as a schema-defined property `snps,uart-16550-compatible`: reflects the value of UART_16550_COMPATIBLE configuration parameter. Define this if your UART does not implement the busy functionality. `reg-shift` is accepted as a schema-defined property `reg-io-width` is accepted as a schema-defined property `dcd-override`: Override the DCD modem status signal. This signal will always be reported as active instead of being obtained from the modem status register. Define t... Additional top-level properties constrained but not expanded here: `dsr-override`, `cts-override`, `ri-override`.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`, `rs485.yaml#`, 2 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rs485.yaml#`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 3.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/snps-dw-apb-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/snps-dw-apb-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,milbeaut-usio-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,milbeaut-usio-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,milbeaut-usio-uart.yaml` defines the Devicetree binding contract for Socionext Milbeaut UART controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,milbeaut-usio-uart.yaml` is a Devicetree YAML schema for Socionext Milbeaut UART controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `socionext,milbeaut-usio-uart`; required properties `compatible`, `reg`, `interrupts`, `interrupt-names`. Maintainers: Sugaya Taichi <sugaya.taichi@socionext.com>. Property contract: `compatible`: const `socionext,milbeaut-usio-uart` Required. `reg`: maxItems 1 Required. `interrupts`: ordered items Required. `interrupt-names`: ordered items Required. `clocks`: maxItems 1 `auto-flow-control`: Enable automatic flow control.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/serial/serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/serial/serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/socionext,milbeaut-usio-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,milbeaut-usio-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,uniphier-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,uniphier-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,uniphier-uart.yaml` defines the Devicetree binding contract for UniPhier UART controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,uniphier-uart.yaml` is a Devicetree YAML schema for UniPhier UART controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `socionext,uniphier-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Masahiro Yamada <yamada.masahiro@socionext.com>. Property contract: `compatible`: const `socionext,uniphier-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `resets`: maxItems 1 `auto-flow-control`: ref /schemas/types.yaml#/definitions/flag; enable automatic flow control support.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/socionext,uniphier-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/socionext,uniphier-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sprd-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sprd-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sprd-uart.yaml` defines the Devicetree binding contract for Spreadtrum serial UART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sprd-uart.yaml` is a Devicetree YAML schema for Spreadtrum serial UART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `sprd,sc9632-uart`, `sprd,sc9836-uart`, `sprd,sc9860-uart`, `sprd,sc9863a-uart`, `sprd,ums512-uart`, `sprd,ums9620-uart`, `sprd,ums9632-uart`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Orson Zhai <orsonzhai@gmail.com>, Baolin Wang <baolin.wang7@gmail.com>, Chunyan Zhang <zhang.lyra@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 3; minItems 1 `clock-names`: ordered items; "enable" for UART module enable clock, "uart" for UART clock, "source" for UART source (parent) clock. `dmas`: maxItems 2; minItems 1 `dma-names`: minItems 1; ordered items

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/sprd-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sprd-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,asc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,asc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,asc.yaml` defines the Devicetree binding contract for STMicroelectronics STi SoCs Serial Port. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,asc.yaml` is a Devicetree YAML schema for STMicroelectronics STi SoCs Serial Port. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `st,asc`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Patrice Chotard <patrice.chotard@foss.st.com>. Property contract: `compatible`: const `st,asc` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `st,hw-flow-ctrl`: When set, enable hardware flow control. `st,force-m1`: When set, force asc to be in Mode-1. This is recommended for high bit rates above 19.2K.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/st,asc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,asc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,stm32-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,stm32-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,stm32-uart.yaml` defines the Devicetree binding contract for STMicroelectronics STM32 USART. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,stm32-uart.yaml` is a Devicetree YAML schema for STMicroelectronics STM32 USART. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `st,stm32-uart`, `st,stm32f7-uart`, `st,stm32h7-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Erwan Le Ray <erwan.leray@foss.st.com>. Property contract: `compatible`: enum `st,stm32-uart`, `st,stm32f7-uart`, `st,stm32h7-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `resets`: maxItems 1 `power-domains`: maxItems 1 `dmas`: maxItems 2; minItems 1 `dma-names`: maxItems 2; minItems 1; ordered items `label`: label associated with this uart `st,hw-flow-ctrl`: ref /schemas/types.yaml#/definitions/flag; enable hardware flow control (deprecated) `rx-tx-swap` is accepted as a schema-defined property `cts-gpios` is accepted as a schema-defined property `rts-gpios` is accepted as a schema-defined property `wakeup-source` is accepted as a schema-defined property Additional top-level properties constrained but not expanded here: `rx-threshold`, `tx-threshold`, `access-controllers`.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rs485.yaml#`, `serial.yaml#`, 3 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`, `rs485.yaml#`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/st,stm32-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/st,stm32-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sunplus,sp7021-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sunplus,sp7021-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sunplus,sp7021-uart.yaml` defines the Devicetree binding contract for Sunplus SoC SP7021 UART Controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sunplus,sp7021-uart.yaml` is a Devicetree YAML schema for Sunplus SoC SP7021 UART Controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `sunplus,sp7021-uart`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `resets`. Maintainers: Hammer Hsieh <hammerh0314@gmail.com>. Property contract: `compatible`: const `sunplus,sp7021-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required. `resets`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/sunplus,sp7021-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/sunplus,sp7021-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/via,vt8500-uart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/via,vt8500-uart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/via,vt8500-uart.yaml` defines the Devicetree binding contract for VIA VT8500 and WonderMedia WM8xxx UART Controller. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/via,vt8500-uart.yaml` is a Devicetree YAML schema for VIA VT8500 and WonderMedia WM8xxx UART Controller. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `via,vt8500-uart`, `wm,wm8880-uart`; required properties `compatible`, `clocks`, `interrupts`, `reg`. Maintainers: Alexey Charkov <alchark@gmail.com>. Property contract: `compatible`: enum `via,vt8500-uart`, `wm,wm8880-uart` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/via,vt8500-uart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/via,vt8500-uart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/xlnx,opb-uartlite.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/xlnx,opb-uartlite.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/xlnx,opb-uartlite.yaml` defines the Devicetree binding contract for Xilinx Axi Uartlite. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/xlnx,opb-uartlite.yaml` is a Devicetree YAML schema for Xilinx Axi Uartlite. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `xlnx,opb-uartlite-1.00.b`, `xlnx,xps-uartlite-1.00.a`; required properties `compatible`, `reg`, `interrupts`, `current-speed`, `xlnx,data-bits`, `xlnx,use-parity`. Maintainers: Peter Korsgaard <jacmet@sunsite.dk>. Property contract: `compatible`: schema keys contains Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 `clock-names`: const `s_axi_aclk` `port-number`: ref /schemas/types.yaml#/definitions/uint32; Set Uart port number `current-speed`: ref /schemas/types.yaml#/definitions/uint32; The fixed baud rate that the device was configured for. Required. `xlnx,data-bits`: enum `5`, `6`, `7`, `8`; The fixed number of data bits that the device was configured for. Required. `xlnx,use-parity`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Whether parity checking was enabled when the device was configured. Required. `xlnx,odd-parity`: ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Whether odd parity was configured.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint32`, `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/xlnx,opb-uartlite.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/xlnx,opb-uartlite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/allwinner,sun4i-a10-ps2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/allwinner,sun4i-a10-ps2.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/allwinner,sun4i-a10-ps2.yaml` defines the Devicetree binding contract for Allwinner A10 PS2 Host Controller. A20 PS2 is dual role controller (PS2 host and PS2 device). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `allwinner,sun4i-a10-ps2`; required properties `compatible`, `reg`, `interrupts`, `clocks`. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Property contract: `compatible`: const `allwinner,sun4i-a10-ps2` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with serio input drivers and interrupt/clock/reset providers used by keyboard or PS/2 controller nodes. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serio/allwinner,sun4i-a10-ps2.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/allwinner,sun4i-a10-ps2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/arm,pl050.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/arm,pl050.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/arm,pl050.yaml` defines the Devicetree binding contract for Arm Ltd. PrimeCell PL050 PS/2 Keyboard/Mouse Interface. The Arm PrimeCell PS2 Keyboard/Mouse Interface (KMI) is an AMBA compliant peripheral that can be used to implement a keyboard or mouse interface that is IBM PS2 or AT compatible. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `arm,pl050`, `arm,primecell`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Andre Przywara <andre.przywara@arm.com>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `clock-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with serio input drivers and interrupt/clock/reset providers used by keyboard or PS/2 controller nodes. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serio/arm,pl050.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/arm,pl050.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/ps2-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/ps2-gpio.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/ps2-gpio.yaml` defines the Devicetree binding contract for GPIO based PS/2. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/ps2-gpio.yaml` is a Devicetree YAML schema for GPIO based PS/2. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values none extracted from `compatible`; required properties `compatible`, `data-gpios`, `clk-gpios`, `interrupts`. Maintainers: Danilo Krummrich <danilokrummrich@dk-develop.de>. Property contract: `compatible`: const `ps2-gpio` Required. `interrupts`: maxItems 1; The given interrupt should trigger on the falling edge of the clock line. Required. `data-gpios`: maxItems 1; the gpio used for the data signal - this should be flagged as active high using open drain with (GPIO_ACTIVE_HIGH | GPIO_OPEN_DRAIN) from <dt-bindings... Required. `clk-gpios`: maxItems 1; the gpio used for the clock signal - this should be flagged as active high using open drain with (GPIO_ACTIVE_HIGH | GPIO_OPEN_DRAIN) from <dt-binding... Required. `write-enable`: Indicates whether write function is provided to serio device. Possibly providing the write function will not work, because of the tough timing require...

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with serio input drivers and interrupt/clock/reset providers used by keyboard or PS/2 controller nodes. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serio/ps2-gpio.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/ps2-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml` defines the Devicetree binding contract for Eckelmann SIOX GPIO bus. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml` is a Devicetree YAML schema for Eckelmann SIOX GPIO bus. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `eckelmann,siox-gpio`; required properties `compatible`, `din-gpios`, `dout-gpios`, `dclk-gpios`, `dld-gpios`. Maintainers: Frank Li <Frank.Li@nxp.com>. Property contract: `compatible`: const `eckelmann,siox-gpio` Required. `din-gpios`: maxItems 1 Required. `dout-gpios`: maxItems 1 Required. `dclk-gpios`: maxItems 1 Required. `dld-gpios`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates through Devicetree schema validation and the matching Linux platform, bus, or MFD driver. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/qcom,slim-ngd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/qcom,slim-ngd.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/qcom,slim-ngd.yaml` defines the Devicetree binding contract for Qualcomm SoC SLIMBus Non Generic Device (NGD) Controller. SLIMBus NGD controller is a light-weight driver responsible for communicating with SLIMBus slaves directly over the bus using messaging interface and communicating with master component residing on ADSP for bandwidth and data-channel management The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `qcom,slim-ngd-v1.5.0`, `qcom,slim-ngd-v2.1.0`; required properties `compatible`, `reg`, `#address-cells`, `#size-cells`, `dmas`, `dma-names`, `interrupts`. Maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Srinivas Kandagatla <srinivas.kandagatla@linaro.org>. Property contract: `compatible`: enum `qcom,slim-ngd-v1.5.0`, `qcom,slim-ngd-v2.1.0` Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `dmas`: maxItems 2 Required. `dma-names`: ordered items Required. `#address-cells`: const `1` Required. `#size-cells`: const `0` Required. `iommus`: maxItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^slim@[0-9a-f]+$` accepts child objects with properties `reg`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `slimbus.yaml#`. It integrates with SLIMbus controller/device enumeration and, for Qualcomm NGD, with clocks, DMA or interconnect-like SoC resources. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/slimbus/qcom,slim-ngd.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/qcom,slim-ngd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/slimbus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/slimbus.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/slimbus.yaml` defines the Devicetree binding contract for SLIM (Serial Low Power Interchip Media) bus. SLIMbus is a 2-wire bus, and is used to communicate with peripheral components like audio-codec. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values none extracted from `compatible`; required properties `#address-cells`, `#size-cells`. Maintainers: Srinivas Kandagatla <srinivas.kandagatla@linaro.org>. Property contract: `#address-cells`: const `2` Required. `#size-cells`: const `0` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^.*@[0-9a-f]+,[0-9a-f]+$` accepts child objects with properties `compatible`, `reg`; required child fields: `compatible`, `reg`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with SLIMbus controller/device enumeration and, for Qualcomm NGD, with clocks, DMA or interconnect-like SoC resources. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: true` intentionally leaves extension room, usually because this is a common/shared schema. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/slimbus/slimbus.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/slimbus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/altera/altr,sys-mgr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/altera/altr,sys-mgr.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/altera/altr,sys-mgr.yaml` defines the Devicetree binding contract for Altera SOCFPGA System Manager. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/altera/altr,sys-mgr.yaml` is a Devicetree YAML schema for Altera SOCFPGA System Manager. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `altr,sys-mgr`, `altr,sys-mgr-s10`; required properties `compatible`, `reg`. Maintainers: Dinh Nguyen <dinguyen@kernel.org>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `cpu1-start-addr`: ref /schemas/types.yaml#/definitions/uint32; CPU1 start address in hex

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint32`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/altera/altr,sys-mgr.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/altera/altr,sys-mgr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,canvas.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,canvas.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,canvas.yaml` defines the Devicetree binding contract for Amlogic Canvas Video Lookup Table. A canvas is a collection of metadata that describes a pixel buffer. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `amlogic,canvas`, `amlogic,meson8-canvas`, `amlogic,meson8b-canvas`, `amlogic,meson8m2-canvas`; required properties `compatible`, `reg`. Maintainers: Neil Armstrong <neil.armstrong@linaro.org>, Maxime Jourdan <mjourdan@baylibre.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/amlogic/amlogic,canvas.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,canvas.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-clk-measure.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-clk-measure.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-clk-measure.yaml` defines the Devicetree binding contract for Amlogic Internal Clock Measurer. The Amlogic SoCs contains an IP to measure the internal clocks. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `amlogic,c3-clk-measure`, `amlogic,meson-axg-clk-measure`, `amlogic,meson-g12a-clk-measure`, `amlogic,meson-gx-clk-measure`, `amlogic,meson-sm1-clk-measure`, `amlogic,meson8-clk-measure`, `amlogic,meson8b-clk-measure`, `amlogic,s4-clk-measure`; required properties `compatible`, `reg`. Maintainers: Neil Armstrong <neil.armstrong@linaro.org>. Property contract: `compatible`: enum `amlogic,meson-gx-clk-measure`, `amlogic,meson8-clk-measure`, `amlogic,meson8b-clk-measure`, `amlogic,meson-axg-clk-measure`, `amlogic,meson-g12a-clk-measure`, `amlogic,meson-sm1-clk-measure`, `amlogic,c3-clk-measure`, `amlogic,s4-clk-measure` Required. `reg`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-clk-measure.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-clk-measure.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-hhi-sysctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-hhi-sysctrl.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-hhi-sysctrl.yaml` defines the Devicetree binding contract for Amlogic Meson System Control registers. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-hhi-sysctrl.yaml` is a Devicetree YAML schema for Amlogic Meson System Control registers. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `amlogic,meson-axg-ao-sysctrl`, `amlogic,meson-axg-hhi-sysctrl`, `amlogic,meson-gx-ao-sysctrl`, `amlogic,meson-gx-hhi-sysctrl`, `amlogic,meson-hhi-sysctrl`; required properties `compatible`, `reg`, `clock-controller`. Maintainers: Neil Armstrong <neil.armstrong@linaro.org>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `clock-controller`: schema keys type Required. `power-controller`: ref /schemas/power/amlogic,meson-ee-pwrc.yaml `pinctrl`: schema keys type `phy`: schema keys type

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` 5 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/clock/amlogic,gxbb-aoclkc.yaml#`, `/schemas/clock/amlogic,gxbb-clkc.yaml#`, `/schemas/clock/amlogic,meson8-clkc.yaml#`, `/schemas/phy/amlogic,g12a-mipi-dphy-analog.yaml`, `/schemas/phy/amlogic,meson-axg-mipi-pcie-analog.yaml`, `/schemas/power/amlogic,meson-ee-pwrc.yaml`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 2.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-hhi-sysctrl.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/amlogic/amlogic,meson-gx-hhi-sysctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/aspeed/uart-routing.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/aspeed/uart-routing.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/aspeed/uart-routing.yaml` defines the Devicetree binding contract for Aspeed UART Routing Controller. The Aspeed UART routing control allow to dynamically route the inputs for the built-in UARTS and physical serial I/O ports. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `aspeed,ast2400-uart-routing`, `aspeed,ast2500-uart-routing`, `aspeed,ast2600-uart-routing`; required properties `compatible`. Maintainers: Oskar Senft <osk@google.com>, Chia-Wei Wang <chiawei_wang@aspeedtech.com>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/aspeed/uart-routing.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/aspeed/uart-routing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm23550-cdc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm23550-cdc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm23550-cdc.yaml` defines the Devicetree binding contract for Broadcom BCM23550 Cluster Dormant Control. The Cluster Dormant Control block keeps the CPU in idle state. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `brcm,bcm23550-cdc`; required properties `compatible`, `reg`. Maintainers: Florian Fainelli <f.fainelli@gmail.com>. Property contract: `compatible`: const `brcm,bcm23550-cdc` Required. `reg`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/bcm/brcm,bcm23550-cdc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm23550-cdc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2711-avs-monitor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2711-avs-monitor.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2711-avs-monitor.yaml` defines the Devicetree binding contract for Broadcom AVS Monitor. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2711-avs-monitor.yaml` is a Devicetree YAML schema for Broadcom AVS Monitor. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `brcm,bcm2711-avs-monitor`; required properties `compatible`, `reg`, `thermal`. Maintainers: Stefan Wahren <wahrenst@gmx.net>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `thermal`: ref /schemas/thermal/brcm,avs-ro-thermal.yaml; Broadcom AVS ring oscillator thermal Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/thermal/brcm,avs-ro-thermal.yaml`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/bcm/brcm,bcm2711-avs-monitor.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2711-avs-monitor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-pm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-pm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-pm.yaml` defines the Devicetree binding contract for BCM2835 PM (Power domains, watchdog). The PM block controls power domains and some reset lines, and includes a watchdog timer. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `brcm,bcm2711-pm`, `brcm,bcm2712-pm`, `brcm,bcm2835-pm`, `brcm,bcm2835-pm-wdt`; required properties `compatible`, `reg`, `#power-domain-cells`, `#reset-cells`. Maintainers: Nicolas Saenz Julienne <nsaenz@kernel.org>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 3; minItems 1 Required. `reg-names`: minItems 1; ordered items `clocks`: maxItems 4; minItems 4 `clock-names`: ordered items `#power-domain-cells`: const `1` Required. `#reset-cells`: const `1` Required. `system-power-controller`: schema keys type `timeout-sec` is accepted as a schema-defined property

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `/schemas/watchdog/watchdog.yaml#`, 1 conditional branch(es). No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/watchdog/watchdog.yaml#`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-pm.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-pm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-vchiq.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-vchiq.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-vchiq.yaml` defines the Devicetree binding contract for Broadcom VCHIQ firmware services. The VCHIQ communication channel can be provided by BCM283x and Capri SoCs, to communicate with the VPU-side OS services. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `brcm,bcm2835-vchiq`, `brcm,bcm2836-vchiq`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Nicolas Saenz Julienne <nsaenz@kernel.org>. Property contract: `compatible`: schema keys oneOf Required. `reg`: minItems 1; Physical base address and length of the doorbell register pair Required. `interrupts`: minItems 1; Interrupt number of the doorbell interrupt Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-vchiq.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/bcm/brcm,bcm2835-vchiq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/cirrus/cirrus,ep9301-syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/cirrus/cirrus,ep9301-syscon.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/cirrus/cirrus,ep9301-syscon.yaml` defines the Devicetree binding contract for Cirrus Logic EP93xx Platforms System Controller. Central resources are controlled by a set of software-locked registers, which can be used to prevent accidental accesses. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `cirrus,ep9301-syscon`, `cirrus,ep9302-syscon`, `cirrus,ep9307-syscon`, `cirrus,ep9312-syscon`, `cirrus,ep9315-syscon`; required properties `compatible`, `reg`, `#clock-cells`, `clocks`. Maintainers: Alexander Sverdlin <alexander.sverdlin@gmail.com>, Nikita Shubin <nikita.shubin@maquefel.me>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `clocks`: ordered items Required. `#clock-cells`: const `1` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^pins-` accepts child objects with properties `function`, `groups`; required child fields: `function`, `groups`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/pinctrl/pinmux-node.yaml`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/cirrus/cirrus,ep9301-syscon.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/cirrus/cirrus,ep9301-syscon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/cix/cix,sky1-system-control.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/cix/cix,sky1-system-control.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/cix/cix,sky1-system-control.yaml` defines the Devicetree binding contract for Cix Sky1 SoC system control register region. An wide assortment of registers of the system controller on Sky1 SoC, including resets, usb, wakeup sources and so on. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `cix,sky1-s5-system-control`, `cix,sky1-system-control`; required properties `compatible`, `reg`. Maintainers: Gary Yang <gary.yang@cixtech.com>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `#reset-cells`: const `1`

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/cix/cix,sky1-system-control.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/cix/cix,sky1-system-control.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-scc-qmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-scc-qmc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-scc-qmc.yaml` defines the Devicetree binding contract for PowerQUICC CPM QUICC Multichannel Controller (QMC). The QMC (QUICC Multichannel Controller) emulates up to 64 channels within one serial controller using the same TDM physical interface routed from TSA. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,cpm1-scc-qmc`, `fsl,mpc866-scc-qmc`, `fsl,mpc885-scc-qmc`; required properties `compatible`, `reg`, `reg-names`, `interrupts`, `fsl,tsa-serial`, `#address-cells`, `#size-cells`. Maintainers: Herve Codina <herve.codina@bootlin.com>. Property contract: `compatible`: ordered items Required. `reg`: ordered items Required. `reg-names`: ordered items Required. `interrupts`: maxItems 1; SCC interrupt line in the CPM interrupt controller Required. `#address-cells`: const `1` Required. `#size-cells`: const `0` Required. `fsl,tsa-serial`: ref /schemas/types.yaml#/definitions/phandle-array; ordered items; Should be a phandle/number pair. The phandle to TSA node and the TSA serial interface to use. Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^channel@([0-9]|[1-5][0-9]|6[0-3])$` accepts child objects with properties `reg`, `fsl,operational-mode`, `fsl,reverse-data`, `fsl,tx-ts-mask`, `fsl,rx-ts-mask`, `compatible`, `fsl,framer`; required child fields: `reg`, `fsl,tx-ts-mask`, `fsl,rx-ts-mask`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint64`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-scc-qmc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-scc-qmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-tsa.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-tsa.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-tsa.yaml` defines the Devicetree binding contract for PowerQUICC CPM Time-slot assigner (TSA) controller. The TSA is the time-slot assigner that can be found on some PowerQUICC SoC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,cpm1-tsa`, `fsl,mpc866-tsa`, `fsl,mpc885-tsa`; required properties `compatible`, `reg`, `reg-names`, `#address-cells`, `#size-cells`. Maintainers: Herve Codina <herve.codina@bootlin.com>. Property contract: `compatible`: ordered items Required. `reg`: ordered items Required. `reg-names`: ordered items Required. `#address-cells`: const `1` Required. `#size-cells`: const `0` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^tdm@[0-1]$` accepts child objects with properties `reg`, `fsl,common-rxtx-pins`, `clocks`, `clock-names`, `fsl,rx-frame-sync-delay-bits`, `fsl,tx-frame-sync-delay-bits`, `fsl,clock-falling-edge`, `fsl,fsync-rising-edge`, `fsl,double-speed-clock`; required child fields: `reg`, `clocks`, `clock-names`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32-matrix`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-tsa.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,cpm1-tsa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-firmware.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-firmware.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-firmware.yaml` defines the Devicetree binding contract for Freescale QUICC Engine module Firmware Node. This node defines a firmware binary that is embedded in the device tree, for the purpose of passing the firmware from bootloader to the kernel, or from the hypervisor to the guest. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,qe-firmware`; required properties `compatible`, `fsl,firmware`. Maintainers: Frank Li <Frank.Li@nxp.com>. Property contract: `compatible`: enum `fsl,qe-firmware` Required. `fsl,firmware`: ref /schemas/types.yaml#/definitions/uint8-array; A standard property. This property contains the firmware binary "blob". Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/uint8-array`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-firmware.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-firmware.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ic.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ic.yaml` defines the Devicetree binding contract for Freescale QUICC Engine module Interrupt Controller (IC). `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ic.yaml` is a Devicetree YAML schema for Freescale QUICC Engine module Interrupt Controller (IC). The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,qe-ic`; required properties `compatible`, `reg`, `interrupt-controller`, `#interrupt-cells`. Maintainers: Frank Li <Frank.Li@nxp.com>. Property contract: `compatible`: const `fsl,qe-ic` Required. `reg`: maxItems 1 Required. `interrupts`: minItems 1; ordered items `interrupt-controller` is accepted as a schema-defined property Required. `#interrupt-cells`: const `1` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ic.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-muram.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-muram.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-muram.yaml` defines the Devicetree binding contract for Freescale QUICC Engine Multi-User RAM (MURAM). Multi-User RAM (MURAM) The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,cpm-muram`, `fsl,qe-muram`; required properties `compatible`, `ranges`. Maintainers: Frank Li <Frank.Li@nxp.com>. Property contract: `compatible`: ordered items Required. `#address-cells`: const `1` `#size-cells`: const `1` `ranges`: maxItems 1 Required. `mode`: ref /schemas/types.yaml#/definitions/string; enum `host`, `slave`

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^data\-only@[a-f0-9]+$` accepts child objects with properties `compatible`, `reg`; required child fields: `compatible`, `reg`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/string`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-muram.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-muram.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-si.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-si.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-si.yaml` defines the Devicetree binding contract for Freescale QUICC Engine module Serial Interface Block (SI). The SI manages the routing of eight TDM lines to the QE block serial drivers, the MCC and the UCCs, for receive and transmit. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,ls1043-qe-si`, `fsl,t1040-qe-si`; required properties `compatible`, `reg`. Maintainers: Frank Li <Frank.Li@nxp.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-si.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-si.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-siram.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-siram.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-siram.yaml` defines the Devicetree binding contract for Freescale QUICC Engine module Serial Interface Block RAM(SIRAM). store the routing entries of SI The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,ls1043-qe-siram`, `fsl,t1040-qe-siram`; required properties `compatible`, `reg`. Maintainers: Frank Li <Frank.Li@nxp.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-siram.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-siram.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-tsa.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-tsa.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-tsa.yaml` defines the Devicetree binding contract for PowerQUICC QE Time-slot assigner (TSA) controller. The TSA is the time-slot assigner that can be found on some PowerQUICC SoC. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,mpc8321-tsa`, `fsl,qe-tsa`; required properties `compatible`, `reg`, `reg-names`, `#address-cells`, `#size-cells`. Maintainers: Herve Codina <herve.codina@bootlin.com>. Property contract: `compatible`: ordered items Required. `reg`: ordered items Required. `reg-names`: ordered items Required. `#address-cells`: const `1` Required. `#size-cells`: const `0` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^tdm@[0-3]$` accepts child objects with properties `reg`, `fsl,common-rxtx-pins`, `clocks`, `clock-names`, `fsl,rx-frame-sync-delay-bits`, `fsl,tx-frame-sync-delay-bits`, `fsl,clock-falling-edge`, `fsl,fsync-rising-edge`, `fsl,fsync-active-low`, `fsl,double-speed-clock`; required child fields: `reg`, `clocks`, `clock-names`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32-matrix`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-tsa.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-tsa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ucc-qmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ucc-qmc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ucc-qmc.yaml` defines the Devicetree binding contract for PowerQUICC QE QUICC Multichannel Controller (QMC). The QMC (QUICC Multichannel Controller) emulates up to 64 channels within one serial controller using the same TDM physical interface routed from TSA. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,mpc8321-ucc-qmc`, `fsl,qe-ucc-qmc`; required properties `compatible`, `reg`, `reg-names`, `interrupts`, `fsl,tsa-serial`, `#address-cells`, `#size-cells`. Maintainers: Herve Codina <herve.codina@bootlin.com>. Property contract: `compatible`: ordered items Required. `reg`: ordered items Required. `reg-names`: ordered items Required. `interrupts`: maxItems 1; UCC interrupt line in the QE interrupt controller Required. `#address-cells`: const `1` Required. `#size-cells`: const `0` Required. `fsl,tsa-serial`: ref /schemas/types.yaml#/definitions/phandle-array; ordered items; Should be a phandle/number pair. The phandle to TSA node and the TSA serial interface to use. Required. `fsl,soft-qmc`: ref /schemas/types.yaml#/definitions/string; Soft QMC firmware name to load. If this property is omitted, no firmware are used.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^channel@([0-9]|[1-5][0-9]|6[0-3])$` accepts child objects with properties `compatible`, `reg`, `fsl,operational-mode`, `fsl,reverse-data`, `fsl,tx-ts-mask`, `fsl,rx-ts-mask`, `fsl,framer`; required child fields: `reg`, `fsl,tx-ts-mask`, `fsl,rx-ts-mask`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint64`. It describes SoC infrastructure blocks consumed by platform drivers and by other Devicetree nodes through phandles or syscon-style references. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ucc-qmc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/fsl/cpm_qe/fsl,qe-ucc-qmc.yaml -->
