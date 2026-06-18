<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ufoe.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ufoe.yaml

### Purpose
This binding documents MediaTek UFOe display compression blocks. UFOe compresses display streams before downstream output interfaces.

### Important APIs, Types, And Functions
The schema defines compatible strings, one `reg`, one interrupt, one power-domain reference, one clock, optional graph `ports`, and optional `mediatek,gce-client-reg`. The ports connect input from an upstream display block and output to the next block.

### Control Flow
The schema validates compatible/resource cardinality and graph port requirements when `ports` is present. Compression behavior is runtime driver/hardware behavior, not implemented in YAML.

### State, Persistence, And Dependencies
Persistent data is the DT node with MMIO, interrupt, power, clock, command-queue, and graph information. Dependencies include MMSYS, GCE, graph schemas, and downstream display interface bindings.

### Integration Points
UFOe integrates with MediaTek DRM as a compression component in display routes that require reduced bandwidth before DSI or other outputs.

### Risks
Compression blocks must match downstream capabilities. A route that enables UFOe toward an unsupported sink can fail modeset. Optional graph or GCE omissions can leave runtime behavior different from intended pipeline design.

### Test Signals
Run `dt_binding_check` and board graph validation. Runtime signals are component bind, compressed route modeset, command-queue programming, and display correctness on modes requiring UFOe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ufoe.yaml -->
