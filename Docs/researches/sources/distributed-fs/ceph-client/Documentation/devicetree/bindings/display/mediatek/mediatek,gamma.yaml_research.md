<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,gamma.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,gamma.yaml

### Purpose
This binding describes MediaTek GAMMA color-correction blocks. The block applies gamma lookup/transformation in the display pipeline before later stages such as DITHER or POSTMASK.

### Important APIs, Types, And Functions
The API includes SoC/fallback `compatible` entries, one `reg`, one interrupt, one power-domain reference, one clock, optional `mediatek,gce-client-reg`, and graph `ports`. `port@0` is the input, and `port@1` sends corrected pixels to the next pipeline block.

### Control Flow
The schema validates compatible fallback order and required resources. Port validation is declarative and ensures the graph has both input and output when topology is expressed.

### State, Persistence, And Dependencies
The persistent state is the DT node and graph. Dependencies include MMSYS sibling placement, display clock and power domains, interrupt controller routing, graph endpoint bindings, and optional GCE command-engine definitions.

### Integration Points
MediaTek DRM discovers the GAMMA component from this node and inserts it into the display route. GCE metadata allows command queue programming of gamma registers during atomic display updates.

### Risks
Color blocks can appear optional in topology, so missing endpoints may silently bypass expected processing. Incorrect compatible fallback can select wrong LUT capabilities. Bad GCE register offsets can affect runtime programming without schema-visible type errors.

### Test Signals
Use `dt_binding_check` plus DTS validation for required properties. Runtime signals are component bind, gamma LUT programming, visible color transform changes, and correct ordering relative to DITHER/POSTMASK in DRM pipeline dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,gamma.yaml -->
