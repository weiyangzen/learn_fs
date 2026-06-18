<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,spi-bcm-qspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,spi-bcm-qspi.yaml

## Purpose
Devicetree binding schema for Broadcom SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `brcm,spi-bcm7425-qspi`, `brcm,spi-bcm7429-qspi`, `brcm,spi-bcm7435-qspi`, `brcm,spi-bcm7445-qspi`, `brcm,spi-bcm7216-qspi`, `brcm,spi-bcm7278-qspi`, and 5 more compatible strings. The schema description narrows this to: The Broadcom SPI controller is a SPI master found on various SOCs, including BRCMSTB (BCM7XXX), Cygnus, NSP and NS2. The Broadcom Master SPI hw IP consists of: MSPI : SPI master controller can read and write to a SPI slave device BSPI : Broadcom SPI in combination with the MSPI hw IP provides acceleration for flash reads and be configured to do single, double, quad lane io with 3-byte and 4-byte addressing support...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `native-endian`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/flag`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `reg`, `reg-names`, `interrupts`, `interrupt-names`; conditional branches include 2 `oneOf`; 4 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/flag`. Maintainer metadata routes binding review to Kamal Dasu <kdasu.kdev@gmail.com>, Rafał Miłecki <rafal@milecki.pl>.

## Risks and edge cases
missing required properties (`reg`, `reg-names`, `interrupts`, `interrupt-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/brcm,spi-bcm-qspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 4 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,spi-bcm-qspi.yaml -->
