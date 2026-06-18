<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-7k-8k.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-7k-8k.yaml

## Purpose
This schema catalogs Marvell Armada 7K/8K, CN913x, AP806/AP807/AP810, and related carrier/module root compatible chains.

## Important APIs, Types, And Functions
The binding validates many ordered chains, including pure SoC compatibles like `marvell,armada7020`, `marvell,armada-ap806-dual`, `marvell,armada-ap806`, board chains for Falcon and MACCHIATOBin, CN9130/9131/9132 fallback sequences, Alleycat5X carrier/module forms, and SolidRun CN913x products.

## Control Flow
`oneOf` enforces exactly one board or SoC chain. The order preserves board, module, SoC, CPU/AP, and family identity from most to least specific.

## State And Persistence
It stores root identity only. Multi-chip and carrier/module topology is represented through the compatible list rather than mutable state.

## Dependencies And Integration Points
It integrates with Marvell Armada 7K/8K platform code, DTS includes for AP/CP layouts, and board-specific matching.

## Risks
The multi-level fallback chains are error-prone. Missing an intermediate module or AP compatible can break shared initialization for carrier/module combinations.

## Test Signals
`dtbs_check` is the primary validation signal. Hardware boot on Armada/CN913x boards confirms that the selected compatible chain reaches the expected platform code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-7k-8k.yaml -->
