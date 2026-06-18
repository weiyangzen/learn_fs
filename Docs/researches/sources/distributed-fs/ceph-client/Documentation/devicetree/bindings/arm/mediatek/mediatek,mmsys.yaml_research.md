<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mmsys.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mmsys.yaml

## Purpose
This binding describes MediaTek MMSYS/VDOSYS/VPPSYS system controllers that provide display clocks, routing, resets, GCE access, and graph outputs.

## Important APIs, Types, And Functions
The node name must match `syscon@...`. Compatible chains cover many MediaTek display system variants followed by `syscon`, including deprecated `mediatek,mt8195-mmsys`, MT7623 fallback through MT2701, and MT8195 VDOSYS0 compatibility. Properties include `reg`, `power-domains`, `mboxes`, `mediatek,gce-client-reg`, `#clock-cells`, `#reset-cells`, and an optional graph `port`.

## Control Flow
Validation requires compatible, reg, and clock cells. The graph `port` uses `anyOf` to require at least one endpoint among primary, secondary, and tertiary outputs.

## State And Persistence
The DT records display-system MMIO, clock/reset provider metadata, power domain, command-queue mailbox, and display graph connectivity. Runtime state is held by display, clock, reset, power, and GCE drivers.

## Dependencies And Integration Points
It depends on graph, mailbox, power-domain, and type schemas plus MediaTek GCE headers. It integrates with DRM display pipelines and system-controller users.

## Risks
Deprecated MT8195 compatible handling and multi-output graph modeling are the main traps. Wrong GCE register tuples can break command-queue programming.

## Test Signals
`dt_binding_check` validates graph and property shape. `dtbs_check`, DRM component bind, clock/reset registration, and display pipeline bring-up are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mmsys.yaml -->
