<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,l3bridge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,l3bridge.yaml

## Purpose
This binding describes the MStar/SigmaStar Armv7 L3 bridge register block used to flush a CPU-to-memory pipeline before DMA-capable devices run.

## Important APIs, Types, And Functions
It requires `compatible = "mstar,l3bridge"` and one `reg` range. The platform code uses this node to install a DMA barrier.

## Control Flow
Validation is strict: compatible and reg are required and additional properties are rejected.

## State And Persistence
The DT records persistent bridge registers. Runtime state is the platform-installed barrier and hardware flush side effects.

## Dependencies And Integration Points
It integrates with MStar platform code and DMA coherency/barrier handling.

## Risks
If the node is absent or the register range is wrong, DMA devices may observe stale memory due to missing pipeline flushes.

## Test Signals
`dtbs_check` validates the node. Runtime DMA stability on affected SoCs is the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,l3bridge.yaml -->
