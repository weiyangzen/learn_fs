<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,audsys.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,audsys.yaml

## Purpose
This schema describes MediaTek AUDSYS clock/system controller blocks and optional embedded audio-controller child nodes.

## Important APIs, Types, And Functions
The compatible list is either a supported AUDSYS variant followed by `syscon`, or the MT7623 backward-compatible chain through `mediatek,mt2701-audsys`, `syscon`. It requires `#clock-cells = <1>`, supports `reg`, and has an `audio-controller` child whose schema depends on the SoC.

## Control Flow
`allOf` conditionals attach specific sound binding `$ref`s for MT2701/MT7622, MT8183 audiosys, and MT8192 audsys. `additionalProperties: false` keeps the controller node strict.

## State And Persistence
The DT describes clock controller registers and optional audio hardware topology. Runtime state is in clock, syscon, and ASoC drivers.

## Dependencies And Integration Points
It depends on sound schemas, syscon, clock provider conventions, interrupt/power/clock phandles in child examples, and MediaTek clock ID headers.

## Risks
The MT8183 spelling split between `audiosys` and `audsys` and the MT7623 compatibility exception are easy to break. Missing `#clock-cells` prevents clock consumers from resolving.

## Test Signals
`dt_binding_check` validates conditional child refs. `dtbs_check`, clock provider registration, and ASoC card probing are runtime/integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,audsys.yaml -->
