<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,merge.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,merge.yaml

### Purpose
This schema defines MediaTek MERGE blocks, which combine two slice-per-line inputs into one side-by-side output for split display pipelines.

### Important APIs, Types, And Functions
The node exposes SoC/fallback `compatible` strings, one `reg`, one interrupt, one power-domain reference, a defined set of clocks, optional `mediatek,gce-client-reg`, and graph `ports`. Ports describe one or more input endpoints and an output endpoint to the next display block.

### Control Flow
The schema validates compatible choices and resource cardinality. The functional data flow is represented by graph endpoints rather than code: inputs converge at MERGE and output continues downstream.

### State, Persistence, And Dependencies
The DT node persists the register, clock, power, interrupt, command-queue, and graph topology. Dependencies include MMSYS/VDOSYS routing, GCE bindings, graph schemas, and upstream slice-producing blocks.

### Integration Points
MediaTek DRM uses MERGE when dual/sliced pipelines must become a single stream before later blocks. It is relevant to high-resolution panels and display paths using split or DSC blocks.

### Risks
MERGE is topology-sensitive. A graph that omits one slice or points both endpoints to the same source can validate poorly at runtime even if schema constraints pass. Clock lists can differ by SoC generation.

### Test Signals
Use schema checks and board DTS graph validation. Runtime tests should exercise split-to-merged modes, command-queue programming, dual-pipeline atomic commits, and output correctness at high resolutions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,merge.yaml -->
