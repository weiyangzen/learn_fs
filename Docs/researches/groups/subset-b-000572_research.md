# Research Group subset-b-000572

This grouped report covers Linux Devicetree display and DMA binding schemas from the Ceph client source mirror. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5-dp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5-dp.yaml

## Purpose
This file is a Linux Devicetree binding schema for Samsung Exynos5250/Exynos5420 SoC Display Port. It validates nodes matched by `samsung,exynos5-dp`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/samsung/samsung,exynos5-dp.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `samsung,exynos5-dp`. Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `phys`, `phy-names`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `display-timings`, `interrupts`, `hpd-gpios`, `phys`, `phy-names`, `power-domains`, `interlaced`, `vsync-active-high`, `hsync-active-high`, `ports`, `samsung,hpd-gpios`, `samsung,ycbcr-coeff`, `samsung,dynamic-range`, `samsung,color-space`, `samsung,color-depth`, `samsung,link-rate`, `samsung,lane-count`. Referenced schemas: `/schemas/display/panel/display-timings.yaml#`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false, deprecated: true. The example instantiates `dp-controller@145b0000` and exercises the main required properties with 3 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. The schema preserves deprecated properties for legacy DTS compatibility while steering new users toward common bindings.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/display/panel/display-timings.yaml#, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, /schemas/types.yaml#/definitions/uint32, clock provider bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; deprecated properties must remain accepted long enough for old DTS files while new bindings avoid them; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5-dp.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5-dp.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5-dp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-decon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-decon.yaml

## Purpose
This file is a Linux Devicetree binding schema for Samsung Exynos5433 SoC Display and Enhancement Controller (DECON). It validates nodes matched by `samsung,exynos5433-decon`, `samsung,exynos5433-decon-tv`. Source description: DECON (Display and Enhancement Controller) is the Display Controller for the Exynos5433 series of SoCs which transfers the image data from a video memory buffer to an external LCD interface. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/samsung/samsung,exynos5433-decon.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `samsung,exynos5433-decon`, `samsung,exynos5433-decon-tv`. Required properties: `compatible`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `ports`, `reg`. Notable properties: `compatible`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `iommus`, `iommu-names`, `ports`, `power-domains`, `reg`, `samsung,disp-sysreg`. Referenced schemas: `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`. Validation keywords and constraints: additionalProperties: false. The example instantiates `display-controller@13800000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/ports, /schemas/types.yaml#/definitions/phandle, clock provider bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-decon.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-decon.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-decon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-mic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-mic.yaml

## Purpose
This file is a Linux Devicetree binding schema for Samsung Exynos5433 SoC Mobile Image Compressor (MIC). It validates nodes matched by `samsung,exynos5433-mic`. Source description: MIC (Mobile Image Compressor) resides between DECON and MIPI DSI. MIPI DSI is not capable of transferring high resoltuion frame data as DECON can send. MIC solves this problem by compressing the frame data by 1/2 before it is transferred through MIPI DSI. The compressed frame data must be uncompressed in the panel PCB. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/samsung/samsung,exynos5433-mic.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `samsung,exynos5433-mic`. Required properties: `compatible`, `clocks`, `clock-names`, `ports`, `reg`, `samsung,disp-syscon`. Notable properties: `compatible`, `clocks`, `clock-names`, `ports`, `power-domains`, `reg`, `samsung,disp-syscon`. Referenced schemas: `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`. Validation keywords and constraints: additionalProperties: false. The example instantiates `image-processor@13930000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/ports, /schemas/types.yaml#/definitions/phandle, clock provider bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-mic.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-mic.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos5433-mic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos7-decon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos7-decon.yaml

## Purpose
This file is a Linux Devicetree binding schema for Samsung Exynos7 SoC Display and Enhancement Controller (DECON). It validates nodes matched by `samsung,exynos7-decon`, `samsung,exynos7870-decon`. Source description: DECON (Display and Enhancement Controller) is the Display Controller for the Exynos7 series of SoCs which transfers the image data from a video memory buffer to an external LCD interface. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/samsung/samsung,exynos7-decon.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `samsung,exynos7-decon`, `samsung,exynos7870-decon`. Required properties: `compatible`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `port`, `reg`. Notable properties: `compatible`, `clocks`, `clock-names`, `display-timings`, `i80-if-timings`, `interrupts`, `interrupt-names`, `iommus`, `memory-region`, `port`, `power-domains`, `reg`. Referenced schemas: `../panel/display-timings.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false. The example instantiates `display-controller@13930000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. Memory-related properties can describe reserved framebuffer or device register ranges that persist from firmware into kernel boot. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, ../panel/display-timings.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/port, clock provider bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos7-decon.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos7-decon.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos7-decon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,fimd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,fimd.yaml

## Purpose
This file is a Linux Devicetree binding schema for Samsung S3C/S5P/Exynos SoC Fully Interactive Mobile Display (FIMD). It validates nodes matched by `samsung,s3c6400-fimd`, `samsung,s5pv210-fimd`, `samsung,exynos3250-fimd`, `samsung,exynos4210-fimd`, `samsung,exynos5250-fimd`, `samsung,exynos5420-fimd`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/samsung/samsung,fimd.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `samsung,s3c6400-fimd`, `samsung,s5pv210-fimd`, `samsung,exynos3250-fimd`, `samsung,exynos4210-fimd`, `samsung,exynos5250-fimd`, `samsung,exynos5420-fimd`. Required properties: `compatible`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `reg`. Notable properties: `compatible`, `clocks`, `clock-names`, `display-timings`, `i80-if-timings`, `iommus`, `iommu-names`, `interrupts`, `interrupt-names`, `power-domains`, `reg`, `samsung,invert-vden`, `samsung,invert-vclk`, `samsung,sysreg`. Referenced schemas: `../panel/display-timings.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false, patternProperties, allOf, if, then. The example instantiates `fimd@11c00000` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, ../panel/display-timings.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/port, clock provider bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,fimd.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,fimd.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,fimd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sharp,ls010b7dh04.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sharp,ls010b7dh04.yaml

## Purpose
This file is a Linux Devicetree binding schema for Sharp Memory LCD panels. It validates nodes matched by `sharp,ls010b7dh04`, `sharp,ls011b7dh03`, `sharp,ls012b7dd01`, `sharp,ls013b7dh03`, `sharp,ls013b7dh05`, `sharp,ls018b7dh02`, `sharp,ls027b7dh01`, `sharp,ls027b7dh01a`, and 2 more. Source description: Sharp Memory LCDs are a series of monochrome displays that operate over In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sharp,ls010b7dh04.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `sharp,ls010b7dh04`, `sharp,ls011b7dh03`, `sharp,ls012b7dd01`, `sharp,ls013b7dh03`, `sharp,ls013b7dh05`, `sharp,ls018b7dh02`, `sharp,ls027b7dh01`, `sharp,ls027b7dh01a`, `sharp,ls032b7dd02`, `sharp,ls044q7dh01`. Required properties: `compatible`, `reg`, `sharp,vcom-mode`. Notable properties: `compatible`, `reg`, `spi-max-frequency`, `sharp,vcom-mode`, `enable-gpios`, `pwms`. Referenced schemas: `/schemas/types.yaml#/definitions/string`, `panel/panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf, if, then. The example instantiates `spi` and exercises the main required properties. File-specific integration notes: Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/string, panel/panel-common.yaml#, /schemas/spi/spi-peripheral-props.yaml#, PWM bindings, SPI peripheral properties. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sharp,ls010b7dh04.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sharp,ls010b7dh04.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sharp,ls010b7dh04.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/simple-framebuffer.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/simple-framebuffer.yaml

## Purpose
This file is a Linux Devicetree binding schema for Simple Framebuffer. It validates nodes matched by `apple,simple-framebuffer`, `allwinner,simple-framebuffer`, `amlogic,simple-framebuffer`. Source description: A simple frame-buffer describes a frame-buffer setup by firmware or the bootloader, with the assumption that the display hardware has already been set up to scan out from the memory pointed to by the reg property. Since simplefb nodes represent runtime information they must be sub-nodes of the chosen node (*). Simplefb nodes must be named framebuffer@<address>. If the devicetree contains nodes for the display hardwar... In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/simple-framebuffer.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `apple,simple-framebuffer`, `allwinner,simple-framebuffer`, `amlogic,simple-framebuffer`. Required properties: `compatible`. Notable properties: `compatible`, `reg`, `memory-region`, `clocks`, `power-domains`, `width`, `height`, `stride`, `format`, `display`, `panel`, `allwinner,pipeline`, `amlogic,pipeline`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle`. Validation keywords and constraints: additionalProperties: false, patternProperties, allOf, if, then. The example instantiates `chosen` and exercises the main required properties. File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. Memory-related properties can describe reserved framebuffer or device register ranges that persist from firmware into kernel boot.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle, clock provider bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/simple-framebuffer.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/simple-framebuffer.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, boot handoff from simplefb/simpledrm to the real display driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/simple-framebuffer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7567.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7567.yaml

## Purpose
This file is a Linux Devicetree binding schema for Sitronix ST7567 Display Controller. It validates nodes matched by `sitronix,st7567`. Source description: Sitronix ST7567 is a driver and controller for monochrome In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sitronix,st7567.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `sitronix,st7567`. Required properties: `compatible`, `reg`, `width-mm`, `height-mm`, `panel-timing`. Notable properties: `compatible`, `reg`, `sitronix,inverted`, `width-mm`, `height-mm`, `panel-timing`. Referenced schemas: `panel/panel-common.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `i2c` and exercises the main required properties.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, panel/panel-common.yaml#. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7567.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7567.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7567.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7571.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7571.yaml

## Purpose
This file is a Linux Devicetree binding schema for Sitronix ST7571 Display Controller. It validates nodes matched by `sitronix,st7571`. Source description: Sitronix ST7571 is a driver and controller for 4-level gray In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sitronix,st7571.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `sitronix,st7571`. Required properties: `compatible`, `reg`, `reset-gpios`, `width-mm`, `height-mm`, `panel-timing`. Notable properties: `compatible`, `reg`, `sitronix,grayscale`, `sitronix,inverted`, `reset-gpios`, `width-mm`, `height-mm`, `panel-timing`. Referenced schemas: `panel/panel-common.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `i2c` and exercises the main required properties with 1 dt-bindings include(s).

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, panel/panel-common.yaml#, reset/GPIO bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7571.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7571.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7571.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7586.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7586.yaml

## Purpose
This file is a Linux Devicetree binding schema for Sitronix ST7586 Display Controller. It validates nodes matched by `lego,ev3-lcd`. Source description: Sitronix ST7586 is a driver and controller for 4-level gray In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sitronix,st7586.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `lego,ev3-lcd`. Required properties: `compatible`, `reg`, `a0-gpios`, `reset-gpios`. Notable properties: `compatible`, `reg`, `spi-max-frequency`, `a0-gpios`, `reset-gpios`, `rotation`. Referenced schemas: `panel/panel-common.yaml#`. Validation keywords and constraints: additionalProperties: false. The example instantiates `spi` and exercises the main required properties with 1 dt-bindings include(s).

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, panel/panel-common.yaml#, reset/GPIO bindings, SPI peripheral properties. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7586.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7586.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7586.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7735r.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7735r.yaml

## Purpose
This file is a Linux Devicetree binding schema for Sitronix ST7735R Display Panels. It validates nodes matched by `jianda,jd-t18003-t01`, `okaya,rh128128t`. Source description: This binding is for display panels using a Sitronix ST7715R or ST7735R In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sitronix,st7735r.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `jianda,jd-t18003-t01`, `okaya,rh128128t`. Required properties: `compatible`, `reg`, `dc-gpios`. Notable properties: `compatible`, `dc-gpios`, `backlight`, `reg`, `spi-max-frequency`, `reset-gpios`, `rotation`. Referenced schemas: `panel/panel-common.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `spi` and exercises the main required properties with 1 dt-bindings include(s).

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, panel/panel-common.yaml#, /schemas/spi/spi-peripheral-props.yaml#, reset/GPIO bindings, SPI peripheral properties. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7735r.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7735r.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7735r.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7920.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7920.yaml

## Purpose
This file is a Linux Devicetree binding schema for Sitronix ST7920 LCD Display Controllers. It validates nodes matched by `sitronix,st7920`. Source description: The Sitronix ST7920 is a controller for monochrome dot-matrix graphical LCDs, In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sitronix,st7920.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `sitronix,st7920`. Required properties: `compatible`, `reg`, `spi-max-frequency`. Notable properties: `compatible`, `reg`, `vdd-supply`, `reset-gpios`, `spi-max-frequency`. Referenced schemas: `/schemas/spi/spi-peripheral-props.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `spi` and exercises the main required properties with 1 dt-bindings include(s).

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/spi/spi-peripheral-props.yaml#, reset/GPIO bindings, SPI peripheral properties. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7920.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7920.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sitronix,st7920.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd-common.yaml

## Purpose
This file is a Linux Devicetree binding schema for Common properties for Solomon OLED Display Controllers. It is a reusable schema fragment consumed by concrete bindings rather than a standalone compatible match. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/solomon,ssd-common.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: none. Required properties: none. Notable properties: `reg`, `reset-gpios`, `dc-gpios`, `solomon,height`, `solomon,width`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/spi/spi-peripheral-props.yaml#`. Validation keywords and constraints: allOf. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: This is a reusable schema fragment rather than a concrete driver match table.

## Control Flow
Concrete schemas include this fragment with `$ref`/`allOf`; validation then flows through the shared rules defined here. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/spi/spi-peripheral-props.yaml#, reset/GPIO bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are schema drift from driver expectations or from existing in-tree DTS users.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd-common.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd-common.yaml` against in-tree DTS users, example-schema validation from the `examples` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd1307fb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd1307fb.yaml

## Purpose
This file is a Linux Devicetree binding schema for Solomon SSD1307 OLED Controller Framebuffer. It validates nodes matched by `solomon,ssd1305fb-i2c`, `solomon,ssd1306fb-i2c`, `solomon,ssd1307fb-i2c`, `solomon,ssd1309fb-i2c`, `sinowealth,sh1106`, `solomon,ssd1305`, `solomon,ssd1306`, `solomon,ssd1307`, and 1 more. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/solomon,ssd1307fb.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `solomon,ssd1305fb-i2c`, `solomon,ssd1306fb-i2c`, `solomon,ssd1307fb-i2c`, `solomon,ssd1309fb-i2c`, `sinowealth,sh1106`, `solomon,ssd1305`, `solomon,ssd1306`, `solomon,ssd1307`, `solomon,ssd1309`. Required properties: `compatible`, `reg`. Notable properties: `compatible`, `pwms`, `vbat-supply`, `solomon,page-offset`, `solomon,segment-no-remap`, `solomon,col-offset`, `solomon,com-seq`, `solomon,com-lrremap`, `solomon,com-invdir`, `solomon,com-offset`, `solomon,prechargep1`, `solomon,prechargep2`, `solomon,dclk-div`, `solomon,dclk-frq`, `solomon,lookup-table`, `solomon,area-color-enable`, `solomon,low-power`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint8-array`, `solomon,ssd-common.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf, if, then, deprecated: true. The example instantiates `i2c` and exercises the main required properties. File-specific integration notes: The schema preserves deprecated properties for legacy DTS compatibility while steering new users toward common bindings. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint8-array, solomon,ssd-common.yaml#, PWM bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; deprecated properties must remain accepted long enough for old DTS files while new bindings avoid them; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd1307fb.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd1307fb.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd1307fb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd132x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd132x.yaml

## Purpose
This file is a Linux Devicetree binding schema for Solomon SSD132x OLED Display Controllers. It validates nodes matched by `solomon,ssd1322`, `solomon,ssd1325`, `solomon,ssd1327`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/solomon,ssd132x.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `solomon,ssd1322`, `solomon,ssd1325`, `solomon,ssd1327`. Required properties: `compatible`, `reg`. Notable properties: `compatible`. Referenced schemas: `solomon,ssd-common.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf, if, then. The example instantiates `i2c` and exercises the main required properties. File-specific integration notes: Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, solomon,ssd-common.yaml#. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd132x.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd132x.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd132x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd133x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd133x.yaml

## Purpose
This file is a Linux Devicetree binding schema for Solomon SSD133x OLED Display Controllers. It validates nodes matched by `solomon,ssd1331`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/solomon,ssd133x.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `solomon,ssd1331`. Required properties: `compatible`, `reg`. Notable properties: `compatible`, `solomon,width`, `solomon,height`. Referenced schemas: `solomon,ssd-common.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `spi` and exercises the main required properties.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, solomon,ssd-common.yaml#. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd133x.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd133x.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/solomon,ssd133x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,display-subsystem.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,display-subsystem.yaml

## Purpose
This file is a Linux Devicetree binding schema for Unisoc DRM master device. It validates nodes matched by `sprd,display-subsystem`. Source description: The Unisoc DRM master device is a virtual device needed to list all DPU devices or other display interface nodes that comprise the graphics subsystem. Unisoc's display pipeline have several components as below description, multi display controllers and corresponding physical interfaces. For different display scenarios, dpu0 and dpu1 maybe binding to different encoder. E.g: dpu0 and dpu1 both binding to DSI for dual m... In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sprd/sprd,display-subsystem.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `sprd,display-subsystem`. Required properties: `compatible`, `ports`. Notable properties: `compatible`, `ports`. Referenced schemas: `/schemas/types.yaml#/definitions/phandle-array`. Validation keywords and constraints: additionalProperties: false. The example instantiates `display-subsystem` and exercises the main required properties. File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/phandle-array. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,display-subsystem.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,display-subsystem.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,display-subsystem.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dpu.yaml

## Purpose
This file is a Linux Devicetree binding schema for Unisoc Sharkl3 Display Processor Unit (DPU). It validates nodes matched by `sprd,sharkl3-dpu`. Source description: DPU (Display Processor Unit) is the Display Controller for the Unisoc SoCs which transfers the image data from a video memory buffer to an internal LCD interface. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sprd/sprd,sharkl3-dpu.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `sprd,sharkl3-dpu`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `port`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `iommus`, `port`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `example node` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dpu.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dpu.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dsi-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dsi-host.yaml

## Purpose
This file is a Linux Devicetree binding schema for Unisoc MIPI DSI Controller. It validates nodes matched by `sprd,sharkl3-dsi-host`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/sprd/sprd,sharkl3-dsi-host.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `sprd,sharkl3-dsi-host`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `ports`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `ports`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `ports` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dsi-host.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dsi-host.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/sprd/sprd,sharkl3-dsi-host.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-dsi.yaml

## Purpose
This file is a Linux Devicetree binding schema for STMicroelectronics STM32 DSI host controller. It validates nodes matched by `st,stm32-dsi`. Source description: The STMicroelectronics STM32 DSI controller uses the Synopsys DesignWare MIPI-DSI host controller. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/st,stm32-dsi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `st,stm32-dsi`. Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `ports`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `phy-dsi-supply`, `ports`. Referenced schemas: `dsi-controller.yaml#`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/media/video-interfaces.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `ports` and exercises the main required properties with 4 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dsi-controller.yaml#, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, clock provider bindings, reset/GPIO bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-dsi.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-dsi.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-ltdc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-ltdc.yaml

## Purpose
This file is a Linux Devicetree binding schema for STMicroelectronics STM32 lcd-tft display controller. It validates nodes matched by `st,stm32-ltdc`, `st,stm32mp251-ltdc`, `st,stm32mp255-ltdc`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/st,stm32-ltdc.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `st,stm32-ltdc`, `st,stm32mp251-ltdc`, `st,stm32mp255-ltdc`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `port`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `access-controllers`, `port`. Referenced schemas: `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false, allOf, if, then. The example instantiates `port` and exercises the main required properties with 3 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/port, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-ltdc.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-ltdc.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32-ltdc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32mp25-lvds.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32mp25-lvds.yaml

## Purpose
This file is a Linux Devicetree binding schema for STMicroelectronics STM32 LVDS Display Interface Transmitter. It validates nodes matched by `st,stm32mp255-lvds`. Source description: The STMicroelectronics STM32 LVDS Display Interface Transmitter handles the LVDS protocol: it maps the pixels received from the upstream Pixel-DMA (LTDC) onto the LVDS PHY. It is composed of three sub blocks: - LVDS host: handles the LVDS protocol (FPD / OpenLDI) and maps its input pixels onto the data lanes of the PHY - LVDS PHY: parallelize the data and drives the LVDS data lanes - LVDS wrapper: handles top-level s... In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/st,stm32mp25-lvds.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `st,stm32mp255-lvds`. Required properties: `compatible`, `#clock-cells`, `reg`, `clocks`, `clock-names`, `resets`, `ports`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `access-controllers`, `power-domains`, `ports`. Referenced schemas: `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false. The example instantiates `ports` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, clock provider bindings, reset/GPIO bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32mp25-lvds.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32mp25-lvds.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/st,stm32mp25-lvds.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ste,mcde.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ste,mcde.yaml

## Purpose
This file is a Linux Devicetree binding schema for ST-Ericsson Multi Channel Display Engine MCDE. It validates nodes matched by `ste,mcde`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/ste,mcde.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `ste,mcde`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `epod-supply`, `vana-supply`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `epod-supply`, `vana-supply`, `port`, `ranges`. Referenced schemas: `/schemas/graph.yaml#/properties/port`, `dsi-controller.yaml#`. Validation keywords and constraints: additionalProperties: false, unevaluatedProperties: false, patternProperties. The example instantiates `mcde@a0350000` and exercises the main required properties with 4 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/port, dsi-controller.yaml#, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ste,mcde.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ste,mcde.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ste,mcde.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-mipi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-mipi.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra MIPI pad calibration controller. It validates nodes matched by `nvidia,tegra114-mipi`, `nvidia,tegra124-mipi`, `nvidia,tegra132-mipi`, `nvidia,tegra210-mipi`, `nvidia,tegra186-mipi`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra114-mipi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra114-mipi`, `nvidia,tegra124-mipi`, `nvidia,tegra132-mipi`, `nvidia,tegra210-mipi`, `nvidia,tegra186-mipi`. Required properties: `compatible`, `reg`, `clocks`, `#nvidia,mipi-calibrate-cells`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false. The example instantiates `mipi@700e3000` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, clock provider bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-mipi.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-mipi.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-mipi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-tsec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-tsec.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra Security co-processor. It validates nodes matched by `nvidia,tegra114-tsec`, `nvidia,tegra124-tsec`, `nvidia,tegra210-tsec`. Source description: Tegra Security co-processor, an embedded security processor used In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra114-tsec.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra114-tsec`, `nvidia,tegra124-tsec`, `nvidia,tegra210-tsec`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `iommus`, `operating-points-v2`, `power-domains`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `tsec@54500000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-tsec.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-tsec.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra114-tsec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-dpaux.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-dpaux.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra DisplayPort AUX Interface. It validates nodes matched by `nvidia,tegra124-dpaux`, `nvidia,tegra210-dpaux`, `nvidia,tegra186-dpaux`, `nvidia,tegra194-dpaux`. Source description: The Tegra Display Port Auxiliary (DPAUX) pad controller manages two pins which can be assigned to either the DPAUX channel or to an I2C controller. When configured for DisplayPort AUX operation, the DPAUX controller can also be used to communicate with a DisplayPort device using the AUX channel. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra124-dpaux.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra124-dpaux`, `nvidia,tegra210-dpaux`, `nvidia,tegra186-dpaux`, `nvidia,tegra194-dpaux`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `i2c-bus`, `aux-bus`, `vdd-supply`. Referenced schemas: `/schemas/display/dp-aux-bus.yaml#`. Validation keywords and constraints: additionalProperties: false, patternProperties. The example instantiates `i2c-bus` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/display/dp-aux-bus.yaml#, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-dpaux.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-dpaux.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-dpaux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-sor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-sor.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra SOR Output Encoder. It validates nodes matched by `nvidia,tegra124-sor`, `nvidia,tegra210-sor`, `nvidia,tegra210-sor1`, `nvidia,tegra186-sor`, `nvidia,tegra186-sor1`, `nvidia,tegra194-sor`. Source description: The Serial Output Resource (SOR) can be used to drive HDMI, LVDS, eDP and DP outputs. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra124-sor.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra124-sor`, `nvidia,tegra210-sor`, `nvidia,tegra210-sor1`, `nvidia,tegra186-sor`, `nvidia,tegra186-sor1`, `nvidia,tegra194-sor`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `avdd-io-hdmi-dp-supply`, `vdd-hdmi-dp-pll-supply`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `avdd-io-hdmi-dp-supply`, `vdd-hdmi-dp-pll-supply`, `hdmi-supply`, `nvidia,interface`, `nvidia,ddc-i2c-bus`, `nvidia,hpd-gpio`, `nvidia,edid`, `nvidia,panel`, `nvidia,xbar-cfg`, `nvidia,dpaux`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/types.yaml#/definitions/uint32-array`. Validation keywords and constraints: additionalProperties: false, allOf, if, then. The example instantiates `example node` and exercises the main required properties with 3 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint8-array, /schemas/types.yaml#/definitions/uint32-array, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-sor.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-sor.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-sor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-vic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-vic.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra Video Image Composer. It validates nodes matched by `nvidia,tegra124-vic`, `nvidia,tegra210-vic`, `nvidia,tegra186-vic`, `nvidia,tegra194-vic`, `nvidia,tegra234-vic`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra124-vic.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra124-vic`, `nvidia,tegra210-vic`, `nvidia,tegra186-vic`, `nvidia,tegra194-vic`, `nvidia,tegra234-vic`. Required properties: none. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `iommus`, `interconnects`, `interconnect-names`, `dma-coherent`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-vic.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-vic.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra124-vic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dc.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra186 (and later) Display Controller. It validates nodes matched by `nvidia,tegra186-dc`, `nvidia,tegra194-dc`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra186-dc.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra186-dc`, `nvidia,tegra194-dc`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `nvidia,outputs`, `nvidia,head`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `iommus`, `interconnects`, `interconnect-names`, `nvidia,outputs`, `nvidia,head`. Referenced schemas: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/uint32, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dc.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dc.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-display.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-display.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra186 (and later) Display Hub. It validates nodes matched by `nvidia,tegra186-display`, `nvidia,tegra194-display`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra186-display.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra186-display`, `nvidia,tegra194-display`. Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `#address-cells`, `#size-cells`, `ranges`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `ranges`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false, patternProperties, allOf, if, then. The example instantiates `display-hub@15200000` and exercises the main required properties with 10 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-display.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-display.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-display.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dsi-padctl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dsi-padctl.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra MIPI DSI pad controller. It validates nodes matched by `nvidia,tegra186-dsi-padctl`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra186-dsi-padctl.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra186-dsi-padctl`. Required properties: none. Notable properties: `compatible`, `reg`, `resets`, `reset-names`. Referenced schemas: `/schemas/reset/reset.yaml`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `padctl@15880000` and exercises the main required properties with 1 dt-bindings include(s).

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/reset/reset.yaml, reset/GPIO bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dsi-padctl.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dsi-padctl.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra186-dsi-padctl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-csi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-csi.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra20 CSI controller. It validates nodes matched by `nvidia,tegra20-csi`, `nvidia,tegra30-csi`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-csi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-csi`, `nvidia,tegra30-csi`. Required properties: `compatible`, `reg`, `clocks`, `power-domains`, `#address-cells`, `#size-cells`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `avdd-dsi-csi-supply`, `power-domains`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/media/video-interfaces.yaml#`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false, unevaluatedProperties: false, patternProperties, allOf, if, then. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/graph.yaml#/properties/port, clock provider bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-csi.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-csi.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-csi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dc.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra Display Controller. It validates nodes matched by `nvidia,tegra20-dc`, `nvidia,tegra30-dc`, `nvidia,tegra114-dc`, `nvidia,tegra124-dc`, `nvidia,tegra210-dc`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-dc.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-dc`, `nvidia,tegra30-dc`, `nvidia,tegra114-dc`, `nvidia,tegra124-dc`, `nvidia,tegra210-dc`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `interconnect-names`, `interconnects`, `iommus`, `operating-points-v2`, `power-domains`, `memory-region`, `nvidia,head`, `nvidia,outputs`, `rgb`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint8-array`. Validation keywords and constraints: additionalProperties: false, allOf, if, then. The example instantiates `dc@54200000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. Memory-related properties can describe reserved framebuffer or device register ranges that persist from firmware into kernel boot.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint8-array, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dc.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dc.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dsi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dsi.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra Display Serial Interface. It validates nodes matched by `nvidia,tegra20-dsi`, `nvidia,tegra30-dsi`, `nvidia,tegra114-dsi`, `nvidia,tegra124-dsi`, `nvidia,tegra210-dsi`, `nvidia,tegra186-dsi`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-dsi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-dsi`, `nvidia,tegra30-dsi`, `nvidia,tegra114-dsi`, `nvidia,tegra124-dsi`, `nvidia,tegra210-dsi`, `nvidia,tegra186-dsi`. Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `operating-points-v2`, `power-domains`, `avdd-dsi-csi-supply`, `nvidia,mipi-calibrate`, `nvidia,ddc-i2c-bus`, `nvidia,hpd-gpio`, `nvidia,edid`, `nvidia,panel`, `nvidia,ganged-mode`. Referenced schemas: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint8-array`, `../dsi-controller.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf, if, then. The example instantiates `dsi@15300000` and exercises the main required properties with 4 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint8-array, ../dsi-controller.yaml#, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dsi.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dsi.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-epp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-epp.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra Encoder Pre-Processor. It validates nodes matched by `nvidia,tegra20-epp`, `nvidia,tegra30-epp`, `nvidia,tegra114-epp`, `nvidia,tegra124-epp`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-epp.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-epp`, `nvidia,tegra30-epp`, `nvidia,tegra114-epp`, `nvidia,tegra124-epp`. Required properties: none. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `reset-names`, `iommus`, `interconnects`, `interconnect-names`, `operating-points-v2`, `power-domains`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `epp@540c0000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-epp.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-epp.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-epp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr2d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr2d.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA 2D graphics engine. It validates nodes matched by `nvidia,tegra20-gr2d`, `nvidia,tegra30-gr2d`, `nvidia,tegra114-gr2d`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-gr2d.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-gr2d`, `nvidia,tegra30-gr2d`, `nvidia,tegra114-gr2d`. Required properties: none. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `reset-names`, `iommus`, `interconnects`, `interconnect-names`, `operating-points-v2`, `power-domains`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `gr2d@54140000` and exercises the main required properties with 3 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr2d.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr2d.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr2d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr3d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr3d.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA 3D graphics engine. It validates nodes matched by `nvidia,tegra20-gr3d`, `nvidia,tegra30-gr3d`, `nvidia,tegra114-gr3d`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-gr3d.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-gr3d`, `nvidia,tegra30-gr3d`, `nvidia,tegra114-gr3d`. Required properties: none. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `iommus`, `interconnects`, `interconnect-names`, `operating-points-v2`, `power-domains`, `power-domain-names`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false, allOf, if, then. The example instantiates `gr3d@54180000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr3d.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr3d.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-gr3d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-hdmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-hdmi.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra HDMI Output Encoder. It validates nodes matched by `nvidia,tegra20-hdmi`, `nvidia,tegra30-hdmi`, `nvidia,tegra114-hdmi`, `nvidia,tegra124-hdmi`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-hdmi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-hdmi`, `nvidia,tegra30-hdmi`, `nvidia,tegra114-hdmi`, `nvidia,tegra124-hdmi`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `pll-supply`, `vdd-supply`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `operating-points-v2`, `power-domains`, `hdmi-supply`, `vdd-supply`, `pll-supply`, `nvidia,ddc-i2c-bus`, `nvidia,hpd-gpio`, `nvidia,edid`, `nvidia,panel`, `port`. Referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false. The example instantiates `hdmi@54280000` and exercises the main required properties with 3 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint8-array, /schemas/graph.yaml#/properties/port, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-hdmi.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-hdmi.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-host1x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-host1x.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra host1x controller. It validates nodes matched by `nvidia,tegra20-host1x`, `nvidia,tegra30-host1x`, `nvidia,tegra114-host1x`, `nvidia,tegra124-host1x`, `nvidia,tegra210-host1x`, `nvidia,tegra186-host1x`, `nvidia,tegra194-host1x`, `nvidia,tegra234-host1x`. Source description: The host1x top-level node defines a number of children, each In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-host1x.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-host1x`, `nvidia,tegra30-host1x`, `nvidia,tegra114-host1x`, `nvidia,tegra124-host1x`, `nvidia,tegra210-host1x`, `nvidia,tegra186-host1x`, `nvidia,tegra194-host1x`, `nvidia,tegra234-host1x`. Required properties: `compatible`, `interrupts`, `interrupt-names`, `#address-cells`, `#size-cells`, `ranges`, `reg`, `clocks`, `clock-names`. Notable properties: `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `ranges`, `clocks`, `clock-names`, `resets`, `reset-names`, `iommus`, `interconnects`, `interconnect-names`, `operating-points-v2`, `power-domains`. Referenced schemas: none. Validation keywords and constraints: allOf, if, then. The example instantiates `host1x@50000000` and exercises the main required properties with 6 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-host1x.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-host1x.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-host1x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-isp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-isp.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra ISP processor. It validates nodes matched by `nvidia,tegra20-isp`, `nvidia,tegra30-isp`, `nvidia,tegra114-isp`, `nvidia,tegra124-isp`, `nvidia,tegra210-isp`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-isp.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-isp`, `nvidia,tegra30-isp`, `nvidia,tegra114-isp`, `nvidia,tegra124-isp`, `nvidia,tegra210-isp`. Required properties: none. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `reset-names`, `iommus`, `interconnects`, `interconnect-names`, `power-domains`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `isp@54100000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-isp.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-isp.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-isp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-mpe.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-mpe.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra Video Encoder. It validates nodes matched by `nvidia,tegra20-mpe`, `nvidia,tegra30-mpe`, `nvidia,tegra114-msenc`, `nvidia,tegra124-msenc`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-mpe.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-mpe`, `nvidia,tegra30-mpe`, `nvidia,tegra114-msenc`, `nvidia,tegra124-msenc`. Required properties: none. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `reset-names`, `iommus`, `interconnects`, `interconnect-names`, `operating-points-v2`, `power-domains`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `mpe@54040000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-mpe.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-mpe.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-mpe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-tvo.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-tvo.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra TV Encoder Output. It validates nodes matched by `nvidia,tegra20-tvo`, `nvidia,tegra30-tvo`, `nvidia,tegra114-tvo`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-tvo.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-tvo`, `nvidia,tegra30-tvo`, `nvidia,tegra114-tvo`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `operating-points-v2`, `power-domains`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `tvo@542c0000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-tvo.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-tvo.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-tvo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vi.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra Video Input controller. It validates nodes matched by `nvidia,tegra20-vi`, `nvidia,tegra114-vi`, `nvidia,tegra124-vi`, `nvidia,tegra210-vi`, `nvidia,tegra186-vi`, `nvidia,tegra194-vi`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-vi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-vi`, `nvidia,tegra114-vi`, `nvidia,tegra124-vi`, `nvidia,tegra210-vi`, `nvidia,tegra186-vi`, `nvidia,tegra194-vi`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `reset-names`, `iommus`, `interconnects`, `interconnect-names`, `operating-points-v2`, `power-domains`, `ranges`, `vip`, `ports`. Referenced schemas: `/schemas/display/tegra/nvidia,tegra20-vip.yaml`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false, patternProperties, allOf, if, then. The example instantiates `i2c` and exercises the main required properties with 4 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/display/tegra/nvidia,tegra20-vip.yaml, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vi.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vi.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vip.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vip.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra VIP (parallel video capture) controller. It validates nodes matched by `nvidia,tegra20-vip`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra20-vip.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra20-vip`. Required properties: `compatible`, `ports`. Notable properties: `compatible`, `ports`. Referenced schemas: `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: unevaluatedProperties: false. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vip.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vip.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra20-vip.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra210-csi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra210-csi.yaml

## Purpose
This file is a Linux Devicetree binding schema for NVIDIA Tegra CSI controller. It validates nodes matched by `nvidia,tegra210-csi`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tegra/nvidia,tegra210-csi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `nvidia,tegra210-csi`. Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `avdd-dsi-csi-supply`, `power-domains`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra210-csi.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra210-csi.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tegra/nvidia,tegra210-csi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am625-oldi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am625-oldi.yaml

## Purpose
This file is a Linux Devicetree binding schema for Texas Instruments AM625 OLDI Transmitter. It is a reusable schema fragment consumed by concrete bindings rather than a standalone compatible match. Source description: The AM625 TI Keystone OpenLDI transmitter (OLDI TX) supports serialized RGB In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/ti/ti,am625-oldi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: none. Required properties: `reg`, `clocks`, `clock-names`, `ti,oldi-io-ctrl`, `ports`. Notable properties: `reg`, `clocks`, `clock-names`, `ti,companion-oldi`, `ti,secondary-oldi`, `ti,oldi-io-ctrl`, `ports`. Referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. This is a reusable schema fragment rather than a concrete driver match table.

## Control Flow
Concrete schemas include this fragment with `$ref`/`allOf`; validation then flows through the shared rules defined here. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, clock provider bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am625-oldi.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am625-oldi.yaml` against in-tree DTS users, example-schema validation from the `examples` block, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am625-oldi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am65x-dss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am65x-dss.yaml

## Purpose
This file is a Linux Devicetree binding schema for Texas Instruments AM65x Display Subsystem. It validates nodes matched by `ti,am625-dss`, `ti,am62a7-dss`, `ti,am62l-dss`, `ti,am65x-dss`. Source description: The AM625 and AM65x TI Keystone Display SubSystem has two output ports and two video planes. In AM65x DSS, the first video port supports 1 OLDI TX and in AM625 DSS, the first video port output is internally routed to 2 OLDI TXes. The second video port supports DPI format. The first plane is full video plane with all features and the second is a "lite plane" without scaling support. The AM62L display subsystem has a s... In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/ti/ti,am65x-dss.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `ti,am625-dss`, `ti,am62a7-dss`, `ti,am62l-dss`, `ti,am65x-dss`. Required properties: `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `ports`. Notable properties: `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, `interrupts`, `power-domains`, `dma-coherent`, `ports`, `ti,am65x-oldi-io-ctrl`, `max-memory-bandwidth`, `oldi-transmitters`. Referenced schemas: `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/endpoint`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `ti,am625-oldi.yaml#`. Validation keywords and constraints: additionalProperties: false, patternProperties, allOf, if, then. The example instantiates `ports` and exercises the main required properties with 6 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, /schemas/graph.yaml#/properties/endpoint, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32, ti,am625-oldi.yaml#, clock provider bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am65x-dss.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am65x-dss.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,am65x-dss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,j721e-dss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,j721e-dss.yaml

## Purpose
This file is a Linux Devicetree binding schema for Texas Instruments J721E Display Subsystem. It validates nodes matched by `ti,j721e-dss`. Source description: The J721E TI Keystone Display SubSystem with four output ports and four video planes. There is two full video planes and two "lite planes" without scaling support. The video ports can be connected to the SoC's DPI pins or to integrated display bridges on the SoC. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/ti/ti,j721e-dss.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `ti,j721e-dss`. Required properties: `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `ports`. Notable properties: `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, `interrupts`, `interrupt-names`, `power-domains`, `dma-coherent`, `ports`, `max-memory-bandwidth`. Referenced schemas: `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false. The example instantiates `ports` and exercises the main required properties with 3 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, /schemas/types.yaml#/definitions/uint32, clock provider bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,j721e-dss.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,j721e-dss.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,j721e-dss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,k2g-dss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,k2g-dss.yaml

## Purpose
This file is a Linux Devicetree binding schema for Texas Instruments K2G Display Subsystem. It validates nodes matched by `ti,k2g-dss`. Source description: The K2G DSS is an ultra-light version of TI Keystone Display SubSystem. It has only one output port and video plane. The output is DPI. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/ti/ti,k2g-dss.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `ti,k2g-dss`. Required properties: `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `port`. Notable properties: `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`, `power-domains`, `port`, `max-memory-bandwidth`. Referenced schemas: `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false. The example instantiates `port` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/port, /schemas/types.yaml#/definitions/uint32, clock provider bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,k2g-dss.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,k2g-dss.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/ti/ti,k2g-dss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tilcdc/ti,am33xx-tilcdc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tilcdc/ti,am33xx-tilcdc.yaml

## Purpose
This file is a Linux Devicetree binding schema for TI LCD Controller, found on AM335x, DA850, AM18x and OMAP-L138. It validates nodes matched by `ti,am33xx-tilcdc`, `ti,da850-tilcdc`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/tilcdc/ti,am33xx-tilcdc.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `ti,am33xx-tilcdc`, `ti,da850-tilcdc`. Required properties: `compatible`, `interrupts`, `reg`, `port`. Notable properties: `compatible`, `reg`, `interrupts`, `port`, `ti,hwmods`, `max-bandwidth`, `max-width`, `max-pixelclock`, `blue-and-red-wiring`. Referenced schemas: `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false. The example instantiates `display-controller@4830e000` and exercises the main required properties. File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/port, /schemas/types.yaml#/definitions/string, /schemas/types.yaml#/definitions/uint32, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tilcdc/ti,am33xx-tilcdc.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tilcdc/ti,am33xx-tilcdc.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/tilcdc/ti,am33xx-tilcdc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/verisilicon,dc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/verisilicon,dc.yaml

## Purpose
This file is a Linux Devicetree binding schema for Verisilicon DC-series display controllers. It validates nodes matched by `thead,th1520-dc8200`. In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/verisilicon,dc.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `thead,th1520-dc8200`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `ports`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `ports`. Referenced schemas: `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false. The example instantiates `soc` and exercises the main required properties with 3 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/verisilicon,dc.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/verisilicon,dc.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/verisilicon,dc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xlnx/xlnx,zynqmp-dpsub.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xlnx/xlnx,zynqmp-dpsub.yaml

## Purpose
This file is a Linux Devicetree binding schema for Xilinx ZynqMP DisplayPort Subsystem. It validates nodes matched by `xlnx,zynqmp-dpsub-1.7`. Source description: The DisplayPort subsystem of Xilinx ZynqMP (Zynq UltraScale+ MPSoC) implements the display and audio pipelines based on the DisplayPort v1.2 standard. The subsystem includes multiple functional blocks as below: +------------------------------------------------------------+ +--------+ | +----------------+ +-----------+ | | DPDMA | --->| | --> | Video | Video +-------------+ | | 4x vid | | | | | Rendering | -+--> | | |... In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/xlnx/xlnx,zynqmp-dpsub.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `xlnx,zynqmp-dpsub-1.7`. Required properties: `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `resets`, `dmas`, `dma-names`, `phys`, `phy-names`, `ports`. Notable properties: `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `resets`, `dmas`, `dma-names`, `phys`, `phy-names`, `ports`. Referenced schemas: `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false. The example instantiates `display@fd4a0000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xlnx/xlnx,zynqmp-dpsub.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xlnx/xlnx,zynqmp-dpsub.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xlnx/xlnx,zynqmp-dpsub.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xylon,logicvc-display.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xylon,logicvc-display.yaml

## Purpose
This file is a Linux Devicetree binding schema for Xylon LogiCVC display controller. It validates nodes matched by `xylon,logicvc-3.02.a-display`, `xylon,logicvc-4.01.a-display`. Source description: The Xylon LogiCVC is a display controller that supports multiple layers. It is usually implemented as programmable logic and was optimized for use with Xilinx Zynq-7000 SoCs and Xilinx FPGAs. Because the controller is intended for use in a FPGA, most of the configuration of the controller takes place at logic configuration bitstream synthesis time. As a result, many of the device-tree bindings are meant to reflect th... In the kernel tree, this documents the persistent DT ABI for display, panel, framebuffer, graphics, or media pipeline nodes.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/display/xylon,logicvc-display.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `xylon,logicvc-3.02.a-display`, `xylon,logicvc-4.01.a-display`. Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `xylon,display-interface`, `xylon,display-colorspace`, `xylon,display-depth`, `xylon,row-stride`, `layers`, `port`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `memory-region`, `xylon,display-interface`, `xylon,display-colorspace`, `xylon,display-depth`, `xylon,row-stride`, `xylon,dithering`, `xylon,background-layer`, `xylon,layers-configurable`, `layers`, `port`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/graph.yaml#/properties/port`. Validation keywords and constraints: additionalProperties: false, patternProperties. The example instantiates `layers` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: Graph bindings define endpoint topology, so remote-endpoint correctness is part of the contract. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. Graph endpoint validation then checks the display/media pipeline links to bridges, panels, PHYs, or sibling controllers. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. Memory-related properties can describe reserved framebuffer or device register ranges that persist from firmware into kernel boot. For display/media bindings, endpoint graph links persist as the topology used to assemble DRM, V4L2, bridge, or panel pipelines.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/flag, /schemas/graph.yaml#/properties/port, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; incorrect graph endpoints break pipeline assembly without obvious schema errors in the peer node; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xylon,logicvc-display.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xylon,logicvc-display.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DRM/V4L2 graph walk or bridge/panel attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/xylon,logicvc-display.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/adi,axi-dmac.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/adi,axi-dmac.yaml

## Purpose
This file is a Linux Devicetree binding schema for Analog Devices AXI-DMAC DMA controller. It validates nodes matched by `adi,axi-dmac-1.00.a`. Source description: FPGA-based DMA controller designed for use with high-speed converter hardware. http://analogdevicesinc.github.io/hdl/library/axi_dmac/index.html In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/adi,axi-dmac.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `adi,axi-dmac-1.00.a`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `#dma-cells`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `adi,channels`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false, patternProperties, deprecated: true. The example instantiates `dma-controller@7c420000` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. The schema preserves deprecated properties for legacy DTS compatibility while steering new users toward common bindings. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; deprecated properties must remain accepted long enough for old DTS files while new bindings avoid them; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/adi,axi-dmac.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/adi,axi-dmac.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/adi,axi-dmac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun4i-a10-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun4i-a10-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Allwinner A10 DMA Controller. It validates nodes matched by `allwinner,sun4i-a10-dma`, `allwinner,suniv-f1c100s-dma`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/allwinner,sun4i-a10-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `allwinner,sun4i-a10-dma`, `allwinner,suniv-f1c100s-dma`. Required properties: `#dma-cells`, `compatible`, `reg`, `interrupts`, `clocks`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `example node` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun4i-a10-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun4i-a10-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun4i-a10-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun50i-a64-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun50i-a64-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Allwinner A64 DMA Controller. It validates nodes matched by `allwinner,sun20i-d1-dma`, `allwinner,sun50i-a64-dma`, `allwinner,sun50i-a100-dma`, `allwinner,sun50i-h6-dma`, `allwinner,sun50i-h616-dma`, `allwinner,sun55i-a523-dma`, `allwinner,sun55i-a523-mcu-dma`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/allwinner,sun50i-a64-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `allwinner,sun20i-d1-dma`, `allwinner,sun50i-a64-dma`, `allwinner,sun50i-a100-dma`, `allwinner,sun50i-h6-dma`, `allwinner,sun50i-h616-dma`, `allwinner,sun55i-a523-dma`, `allwinner,sun55i-a523-mcu-dma`. Required properties: `#dma-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `dma-channels`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf, if, then. The example instantiates `example node` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun50i-a64-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun50i-a64-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun50i-a64-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun6i-a31-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun6i-a31-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Allwinner A31 DMA Controller. It validates nodes matched by `allwinner,sun6i-a31-dma`, `allwinner,sun8i-a23-dma`, `allwinner,sun8i-a83t-dma`, `allwinner,sun8i-h3-dma`, `allwinner,sun8i-v3s-dma`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/allwinner,sun6i-a31-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `allwinner,sun6i-a31-dma`, `allwinner,sun8i-a23-dma`, `allwinner,sun8i-a83t-dma`, `allwinner,sun8i-h3-dma`, `allwinner,sun8i-v3s-dma`. Required properties: `#dma-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `resets`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `resets`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `example node` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun6i-a31-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun6i-a31-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/allwinner,sun6i-a31-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/altr,msgdma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/altr,msgdma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Altera mSGDMA IP core. It validates nodes matched by `altr,socfpga-msgdma`. Source description: Altera / Intel modular Scatter-Gather Direct Memory Access (mSGDMA) intellectual property (IP) In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/altr,msgdma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `altr,socfpga-msgdma`. Required properties: `compatible`, `reg`, `reg-names`, `interrupts`. Notable properties: `compatible`, `reg`, `reg-names`, `interrupts`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `example node` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/altr,msgdma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/altr,msgdma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/altr,msgdma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apm,xgene-storm-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apm,xgene-storm-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for APM X-Gene Storm SoC DMA. It validates nodes matched by `apm,xgene-storm-dma`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/apm,xgene-storm-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `apm,xgene-storm-dma`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `dma-coherent`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `dma@1f270000` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apm,xgene-storm-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apm,xgene-storm-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apm,xgene-storm-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apple,admac.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apple,admac.yaml

## Purpose
This file is a Linux Devicetree binding schema for Apple Audio DMA Controller (ADMAC). It validates nodes matched by `apple,t6000-admac`, `apple,t8103-admac`, `apple,t8112-admac`. Source description: Apple's Audio DMA Controller (ADMAC) is used to fetch and store audio samples on SoCs from the "Apple Silicon" family. The controller has been seen with up to 24 channels. Even-numbered channels are TX-only, odd-numbered are RX-only. Individual channels are coupled to fixed device endpoints. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/apple,admac.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `apple,t6000-admac`, `apple,t8103-admac`, `apple,t8112-admac`. Required properties: `compatible`, `reg`, `#dma-cells`, `dma-channels`, `interrupts`. Notable properties: `compatible`, `reg`, `dma-channels`, `interrupts`, `iommus`, `power-domains`, `resets`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `example node` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apple,admac.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apple,admac.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/apple,admac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,dma-350.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,dma-350.yaml

## Purpose
This file is a Linux Devicetree binding schema for Arm CoreLink DMA-350 Controller. It validates nodes matched by `arm,dma-350`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/arm,dma-350.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `arm,dma-350`. Required properties: `compatible`, `reg`, `interrupts`. Notable properties: `compatible`, `reg`, `interrupts`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,dma-350.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,dma-350.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,dma-350.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,pl330.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,pl330.yaml

## Purpose
This file is a Linux Devicetree binding schema for ARM PrimeCell PL330 DMA Controller. It validates nodes matched by `arm,pl330`. Source description: The ARM PrimeCell PL330 DMA controller can move blocks of memory contents In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/arm,pl330.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `arm,pl330`. Required properties: `compatible`, `reg`, `interrupts`. Notable properties: `compatible`, `reg`, `interrupts`, `arm,pl330-broken-no-flushp`, `arm,pl330-periph-burst`, `dma-coherent`, `iommus`, `power-domains`, `resets`, `reset-names`. Referenced schemas: `dma-controller.yaml#`, `/schemas/arm/primecell.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `dma-controller@12680000` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Memory/IOMMU properties affect DMA addressability, reserved boot buffers, or display scanout ownership.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, /schemas/arm/primecell.yaml#, reset/GPIO bindings, interrupt-controller bindings, power-domain providers, IOMMU bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,pl330.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,pl330.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm,pl330.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm-pl08x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm-pl08x.yaml

## Purpose
This file is a Linux Devicetree binding schema for ARM PrimeCell PL080 and PL081 and derivatives DMA controller. It validates nodes matched by `arm,pl080`, `arm,pl081`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/arm-pl08x.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `arm,pl080`, `arm,pl081`. Required properties: `reg`, `interrupts`, `clocks`, `clock-names`, `#dma-cells`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `lli-bus-interface-ahb1`, `lli-bus-interface-ahb2`, `mem-bus-interface-ahb1`, `mem-bus-interface-ahb2`, `memcpy-burst-size`, `memcpy-bus-width`, `resets`. Referenced schemas: `/schemas/arm/primecell.yaml#`, `dma-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `dma-controller@67000000` and exercises the main required properties with 3 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/arm/primecell.yaml#, dma-controller.yaml#, /schemas/types.yaml#/definitions/uint32, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm-pl08x.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm-pl08x.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/arm-pl08x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,at91sam9g45-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,at91sam9g45-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Atmel Direct Memory Access Controller (DMA). It validates nodes matched by `atmel,at91sam9g45-dma`, `atmel,at91sam9rl-dma`. Source description: The Atmel Direct Memory Access Controller (DMAC) transfers data from a source In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/atmel,at91sam9g45-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `atmel,at91sam9g45-dma`, `atmel,at91sam9rl-dma`. Required properties: `compatible`, `reg`, `interrupts`, `#dma-cells`, `clocks`, `clock-names`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `dma-controller@ffffec00` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,at91sam9g45-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,at91sam9g45-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,at91sam9g45-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,sama5d4-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,sama5d4-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Microchip AT91 Extensible Direct Memory Access Controller. It validates nodes matched by `atmel,sama5d4-dma`, `microchip,sama7g5-dma`, `microchip,sam9x60-dma`, `microchip,sam9x7-dma`, `microchip,lan9691-dma`, `microchip,sama7d65-dma`. Source description: The DMA Controller (XDMAC) is a AHB-protocol central direct memory access In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/atmel,sama5d4-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `atmel,sama5d4-dma`, `microchip,sama7g5-dma`, `microchip,sam9x60-dma`, `microchip,sam9x7-dma`, `microchip,lan9691-dma`, `microchip,sama7d65-dma`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#dma-cells`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `dma-controller@f0008000` and exercises the main required properties with 3 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,sama5d4-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,sama5d4-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/atmel,sama5d4-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,bcm2835-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,bcm2835-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for BCM2835 DMA controller. It validates nodes matched by `brcm,bcm2835-dma`. Source description: The BCM2835 DMA controller has 16 channels in total. Only the lower In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/brcm,bcm2835-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `brcm,bcm2835-dma`. Required properties: `compatible`, `reg`, `interrupts`, `#dma-cells`, `brcm,dma-channel-mask`. Notable properties: `compatible`, `reg`, `interrupts`, `interrupt-names`, `brcm,dma-channel-mask`. Referenced schemas: `dma-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `dma-controller@7e007000` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, /schemas/types.yaml#/definitions/uint32, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,bcm2835-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,bcm2835-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,bcm2835-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,iproc-sba.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,iproc-sba.yaml

## Purpose
This file is a Linux Devicetree binding schema for Broadcom SBA RAID engine. It validates nodes matched by `brcm,iproc-sba`, `brcm,iproc-sba-v2`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/brcm,iproc-sba.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `brcm,iproc-sba`, `brcm,iproc-sba-v2`. Required properties: `compatible`, `mboxes`. Notable properties: `compatible`, `mboxes`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `raid0` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,iproc-sba.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,iproc-sba.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/brcm,iproc-sba.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2m.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2m.yaml

## Purpose
This file is a Linux Devicetree binding schema for Cirrus Logic ep93xx SoC DMA controller. It validates nodes matched by `cirrus,ep9302-dma-m2m`, `cirrus,ep9307-dma-m2m`, `cirrus,ep9312-dma-m2m`, `cirrus,ep9315-dma-m2m`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/cirrus,ep9301-dma-m2m.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `cirrus,ep9302-dma-m2m`, `cirrus,ep9307-dma-m2m`, `cirrus,ep9312-dma-m2m`, `cirrus,ep9315-dma-m2m`. Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `dma-controller@80000100` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2m.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2m.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2m.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2p.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2p.yaml

## Purpose
This file is a Linux Devicetree binding schema for Cirrus Logic ep93xx SoC M2P DMA controller. It validates nodes matched by `cirrus,ep9302-dma-m2p`, `cirrus,ep9307-dma-m2p`, `cirrus,ep9312-dma-m2p`, `cirrus,ep9315-dma-m2p`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/cirrus,ep9301-dma-m2p.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `cirrus,ep9302-dma-m2p`, `cirrus,ep9307-dma-m2p`, `cirrus,ep9312-dma-m2p`, `cirrus,ep9315-dma-m2p`. Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `dma-controller@80000000` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2p.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2p.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/cirrus,ep9301-dma-m2p.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-common.yaml

## Purpose
This file is a Linux Devicetree binding schema for DMA Engine Common Properties. It is a reusable schema fragment consumed by concrete bindings rather than a standalone compatible match. Source description: Generic binding to provide a way for a driver using DMA Engine to In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/dma-common.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: none. Required properties: `#dma-cells`. Notable properties: `dma-channel-mask`, `dma-channels`, `dma-requests`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: none declared. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. This is a reusable schema fragment rather than a concrete driver match table.

## Control Flow
Concrete schemas include this fragment with `$ref`/`allOf`; validation then flows through the shared rules defined here. Required-property checks run first for the node contract. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint32. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-common.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-common.yaml` against in-tree DTS users, example-schema validation from the `examples` block, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-controller.yaml

## Purpose
This file is a Linux Devicetree binding schema for DMA Controller Common Properties. It is a reusable schema fragment consumed by concrete bindings rather than a standalone compatible match. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/dma-controller.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: none. Required properties: none. Notable properties: none. Referenced schemas: `dma-common.yaml#`. Validation keywords and constraints: allOf. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. This is a reusable schema fragment rather than a concrete driver match table.

## Control Flow
Concrete schemas include this fragment with `$ref`/`allOf`; validation then flows through the shared rules defined here. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-common.yaml#. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-controller.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-controller.yaml` against in-tree DTS users, example-schema validation from the `examples` block, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-router.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-router.yaml

## Purpose
This file is a Linux Devicetree binding schema for DMA Router Common Properties. It is a reusable schema fragment consumed by concrete bindings rather than a standalone compatible match. Source description: DMA routers are transparent IP blocks used to route DMA request In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/dma-router.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: none. Required properties: `#dma-cells`, `dma-masters`. Notable properties: `dma-masters`, `dma-requests`. Referenced schemas: `dma-common.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`. Validation keywords and constraints: allOf. No example block is provided, so coverage depends on external DTS users and schema validation of consumers. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. This is a reusable schema fragment rather than a concrete driver match table.

## Control Flow
Concrete schemas include this fragment with `$ref`/`allOf`; validation then flows through the shared rules defined here. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-common.yaml#, /schemas/types.yaml#/definitions/phandle-array. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-router.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-router.yaml` against in-tree DTS users, example-schema validation from the `examples` block, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/dma-router.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,edma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,edma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Freescale enhanced Direct Memory Access(eDMA) Controller. It validates nodes matched by `fsl,vf610-edma`, `fsl,imx7ulp-edma`, `fsl,imx8qm-edma`, `fsl,imx8ulp-edma`, `fsl,imx93-edma3`, `fsl,imx93-edma4`, `fsl,imx95-edma5`, `nxp,s32g2-edma`, and 2 more. Source description: The eDMA channels have multiplex capability by programmable memory-mapped registers. channels are split into two groups, called DMAMUX0 and DMAMUX1, specific DMA request source can only be multiplexed by any channel of certain group, DMAMUX0 or DMAMUX1, but not both. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/fsl,edma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `fsl,vf610-edma`, `fsl,imx7ulp-edma`, `fsl,imx8qm-edma`, `fsl,imx8ulp-edma`, `fsl,imx93-edma3`, `fsl,imx93-edma4`, `fsl,imx95-edma5`, `nxp,s32g2-edma`, `fsl,imx94-edma3`, `fsl,imx94-edma5`. Required properties: `#dma-cells`, `compatible`, `reg`, `interrupts`, `dma-channels`. Notable properties: `compatible`, `reg`, `interrupts`, `interrupt-names`, `dma-channels`, `clocks`, `clock-names`, `power-domains`, `big-endian`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf, if, then. The example instantiates `dma-controller@5a9f0000` and exercises the main required properties with 6 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,edma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,edma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,edma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Freescale Elo DMA Controller. It validates nodes matched by `fsl,mpc8313-dma`, `fsl,mpc8315-dma`, `fsl,mpc8323-dma`, `fsl,mpc8347-dma`, `fsl,mpc8349-dma`, `fsl,mpc8360-dma`, `fsl,mpc8377-dma`, `fsl,mpc8378-dma`, and 1 more. Source description: This is a little-endian 4-channel DMA controller, used in Freescale mpc83xx In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/fsl,elo-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `fsl,mpc8313-dma`, `fsl,mpc8315-dma`, `fsl,mpc8323-dma`, `fsl,mpc8347-dma`, `fsl,mpc8349-dma`, `fsl,mpc8360-dma`, `fsl,mpc8377-dma`, `fsl,mpc8378-dma`, `fsl,mpc8379-dma`. Required properties: `compatible`, `reg`. Notable properties: `compatible`, `reg`, `cell-index`, `ranges`, `interrupts`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false, patternProperties. The example instantiates `dma@82a8` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo3-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo3-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Freescale Elo3 DMA Controller. It validates nodes matched by `fsl,elo3-dma`. Source description: DMA controller which has same function as EloPlus except that Elo3 has 8 In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/fsl,elo3-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `fsl,elo3-dma`. Required properties: none. Notable properties: `compatible`, `reg`, `ranges`, `interrupts`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false, patternProperties. The example instantiates `dma@100300` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo3-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo3-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,elo3-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,eloplus-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,eloplus-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Freescale EloPlus DMA Controller. It validates nodes matched by `fsl,mpc8540-dma`, `fsl,mpc8541-dma`, `fsl,mpc8548-dma`, `fsl,mpc8555-dma`, `fsl,mpc8560-dma`, `fsl,mpc8572-dma`, `fsl,mpc8641-dma`. Source description: This is a 4-channel DMA controller with extended addresses and chaining, In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/fsl,eloplus-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `fsl,mpc8540-dma`, `fsl,mpc8541-dma`, `fsl,mpc8548-dma`, `fsl,mpc8555-dma`, `fsl,mpc8560-dma`, `fsl,mpc8572-dma`, `fsl,mpc8641-dma`. Required properties: none. Notable properties: `compatible`, `reg`, `cell-index`, `ranges`, `interrupts`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false, patternProperties. The example instantiates `dma@21300` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,eloplus-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,eloplus-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,eloplus-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Freescale Direct Memory Access (DMA) Controller for i.MX. It validates nodes matched by `fsl,imx1-dma`, `fsl,imx21-dma`, `fsl,imx27-dma`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/fsl,imx-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `fsl,imx1-dma`, `fsl,imx21-dma`, `fsl,imx27-dma`. Required properties: `compatible`, `reg`, `interrupts`, `#dma-cells`, `clocks`, `clock-names`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dma-channels`, `dma-requests`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `dma-controller@10001000` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-sdma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-sdma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Freescale Smart Direct Memory Access (SDMA) Controller for i.MX. It validates nodes matched by `fsl,imx50-sdma`, `fsl,imx51-sdma`, `fsl,imx53-sdma`, `fsl,imx6q-sdma`, `fsl,imx7d-sdma`, `fsl,imx6sx-sdma`, `fsl,imx6sl-sdma`, `fsl,imx8mp-sdma`, and 5 more. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/fsl,imx-sdma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `fsl,imx50-sdma`, `fsl,imx51-sdma`, `fsl,imx53-sdma`, `fsl,imx6q-sdma`, `fsl,imx7d-sdma`, `fsl,imx6sx-sdma`, `fsl,imx6sl-sdma`, `fsl,imx8mp-sdma`, `fsl,imx8mn-sdma`, `fsl,imx8mm-sdma`, and 3 more. Required properties: `compatible`, `reg`, `interrupts`, `fsl,sdma-ram-script-name`. Notable properties: `compatible`, `reg`, `interrupts`, `fsl,sdma-ram-script-name`, `gpr`, `fsl,sdma-event-remap`, `clocks`, `clock-names`, `iram`. Referenced schemas: `dma-controller.yaml#`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-matrix`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `example node` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, /schemas/types.yaml#/definitions/string, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32-matrix, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-sdma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-sdma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,imx-sdma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,mxs-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,mxs-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Freescale Direct Memory Access (DMA) Controller from i.MX23/i.MX28. It validates nodes matched by `fsl,imx6q-dma-apbh`, `fsl,imx6sx-dma-apbh`, `fsl,imx7d-dma-apbh`, `fsl,imx8dxl-dma-apbh`, `fsl,imx8mm-dma-apbh`, `fsl,imx8mn-dma-apbh`, `fsl,imx8mp-dma-apbh`, `fsl,imx8mq-dma-apbh`, and 6 more. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/fsl,mxs-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `fsl,imx6q-dma-apbh`, `fsl,imx6sx-dma-apbh`, `fsl,imx7d-dma-apbh`, `fsl,imx8dxl-dma-apbh`, `fsl,imx8mm-dma-apbh`, `fsl,imx8mn-dma-apbh`, `fsl,imx8mp-dma-apbh`, `fsl,imx8mq-dma-apbh`, `fsl,imx8qm-dma-apbh`, `fsl,imx8qxp-dma-apbh`, and 4 more. Required properties: `compatible`, `reg`, `#dma-cells`, `dma-channels`, `interrupts`. Notable properties: `compatible`, `reg`, `clocks`, `interrupts`, `interrupt-names`, `dma-channels`, `power-domains`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf, if, then. The example instantiates `dma-controller@80004000` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, interrupt-controller bindings, power-domain providers. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; changing DMA specifier cells or request limits is an ABI break for client nodes; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,mxs-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,mxs-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl,mxs-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl-qdma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl-qdma.yaml

## Purpose
This file is a Linux Devicetree binding schema for NXP Layerscape SoC qDMA Controller. It validates nodes matched by `fsl,ls1028a-qdma`, `fsl,ls1043a-qdma`, `fsl,ls1046a-qdma`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/fsl-qdma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `fsl,ls1028a-qdma`, `fsl,ls1043a-qdma`, `fsl,ls1046a-qdma`. Required properties: `compatible`, `reg`, `interrupts`, `interrupt-names`, `fsl,dma-queues`, `block-number`, `block-offset`, `status-sizes`, `queue-sizes`. Notable properties: `compatible`, `reg`, `interrupts`, `interrupt-names`, `dma-channels`, `fsl,dma-queues`, `block-number`, `block-offset`, `status-sizes`, `queue-sizes`, `big-endian`. Referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/flag`, `dma-controller.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf, if, then. The example instantiates `dma-controller@8390000` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/flag, dma-controller.yaml#, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; changing DMA specifier cells or request limits is an ABI break for client nodes; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl-qdma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl-qdma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/fsl-qdma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/ingenic,dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/ingenic,dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Ingenic SoCs DMA Controller. It validates nodes matched by `ingenic,jz4740-dma`, `ingenic,jz4725b-dma`, `ingenic,jz4755-dma`, `ingenic,jz4760-dma`, `ingenic,jz4760-bdma`, `ingenic,jz4760-mdma`, `ingenic,jz4760b-dma`, `ingenic,jz4760b-bdma`, and 5 more. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/ingenic,dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `ingenic,jz4740-dma`, `ingenic,jz4725b-dma`, `ingenic,jz4755-dma`, `ingenic,jz4760-dma`, `ingenic,jz4760-bdma`, `ingenic,jz4760-mdma`, `ingenic,jz4760b-dma`, `ingenic,jz4760b-bdma`, `ingenic,jz4760b-mdma`, `ingenic,jz4770-dma`, and 3 more. Required properties: `compatible`, `reg`, `interrupts`, `clocks`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `ingenic,reserved-channels`. Referenced schemas: `dma-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `example node` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, /schemas/types.yaml#/definitions/uint32, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/ingenic,dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/ingenic,dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/ingenic,dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/intel,ldma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/intel,ldma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Lightning Mountain centralized DMA controllers.. It validates nodes matched by `intel,lgm-cdma`, `intel,lgm-dma2tx`, `intel,lgm-dma1rx`, `intel,lgm-dma1tx`, `intel,lgm-dma0tx`, `intel,lgm-dma3`, `intel,lgm-toe-dma30`, `intel,lgm-toe-dma31`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/intel,ldma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `intel,lgm-cdma`, `intel,lgm-dma2tx`, `intel,lgm-dma1rx`, `intel,lgm-dma1tx`, `intel,lgm-dma0tx`, `intel,lgm-dma3`, `intel,lgm-toe-dma30`, `intel,lgm-toe-dma31`. Required properties: `compatible`, `reg`. Notable properties: `compatible`, `reg`, `dma-channels`, `dma-channel-mask`, `clocks`, `resets`, `reset-names`, `interrupts`, `intel,dma-poll-cnt`, `intel,dma-byte-en`, `intel,dma-drb`, `intel,dma-dburst-wr`. Referenced schemas: `dma-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `example node` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, /schemas/types.yaml#/definitions/uint32, clock provider bindings, reset/GPIO bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/intel,ldma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/intel,ldma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/intel,ldma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls1b-apbdma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls1b-apbdma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Loongson-1 APB DMA Controller. It validates nodes matched by `loongson,ls1a-apbdma`, `loongson,ls1c-apbdma`. Source description: Loongson-1 APB DMA controller provides 3 independent channels for In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/loongson,ls1b-apbdma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `loongson,ls1a-apbdma`, `loongson,ls1c-apbdma`. Required properties: `compatible`, `reg`, `interrupts`, `interrupt-names`, `#dma-cells`. Notable properties: `compatible`, `reg`, `interrupts`, `interrupt-names`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `dma-controller@1fd01160` and exercises the main required properties with 1 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; interrupt-name/count drift can disable completion, vsync, FIFO, or error handling paths.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls1b-apbdma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls1b-apbdma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls1b-apbdma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2k0300-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2k0300-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Loongson-2 Multi-Channel DMA controller. It validates nodes matched by `loongson,ls2k0300-dma`, `loongson,ls2k3000-dma`. Source description: The Loongson-2 Multi-Channel DMA controller is used for transferring data In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/loongson,ls2k0300-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `loongson,ls2k0300-dma`, `loongson,ls2k3000-dma`. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `#dma-cells`, `dma-channels`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`, `dma-channels`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf. The example instantiates `dma-controller@1612c000` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2k0300-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2k0300-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2k0300-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2x-apbdma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2x-apbdma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Loongson LS2X APB DMA controller. It is a reusable schema fragment consumed by concrete bindings rather than a standalone compatible match. Source description: The Loongson LS2X APB DMA controller is used for transferring data In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/loongson,ls2x-apbdma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: none. Required properties: `compatible`, `reg`, `interrupts`, `clocks`, `#dma-cells`. Notable properties: `compatible`, `reg`, `interrupts`, `clocks`. Referenced schemas: `dma-controller.yaml#`. Validation keywords and constraints: additionalProperties: false, allOf. The example instantiates `dma-controller@1fe00c00` and exercises the main required properties with 2 dt-bindings include(s). File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. This is a reusable schema fragment rather than a concrete driver match table.

## Control Flow
Concrete schemas include this fragment with `$ref`/`allOf`; validation then flows through the shared rules defined here. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, dma-controller.yaml#, clock provider bindings, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2x-apbdma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2x-apbdma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/loongson,ls2x-apbdma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,mmp-dma.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,mmp-dma.yaml

## Purpose
This file is a Linux Devicetree binding schema for Marvell MMP DMA controller. It validates nodes matched by `marvell,pdma-1.0`, `marvell,adma-1.0`, `marvell,pxa910-squ`. Source description: Marvell MMP SoCs may have two types of DMA controllers, peripheral and audio. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/marvell,mmp-dma.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `marvell,pdma-1.0`, `marvell,adma-1.0`, `marvell,pxa910-squ`. Required properties: `compatible`, `reg`, `interrupts`, `#dma-cells`. Notable properties: `compatible`, `reg`, `interrupts`, `asram`. Referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `dma-controller.yaml#`. Validation keywords and constraints: unevaluatedProperties: false, allOf, if, then, deprecated: true. The example instantiates `dma-controller@d4000000` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Interrupt count/name mismatches commonly produce probe failures or lost completion/error events. The schema preserves deprecated properties for legacy DTS compatibility while steering new users toward common bindings. Conditional branches change required properties or property shapes for specific compatibles, making compatible-specific tests important.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. `allOf` and conditional branches refine the base contract for SoC variants, bus mode, or child-node shape. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, /schemas/types.yaml#/definitions/phandle, dma-controller.yaml#, interrupt-controller bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; deprecated properties must remain accepted long enough for old DTS files while new bindings avoid them; compatible-specific conditionals can accidentally under-validate one SoC variant if not covered by examples or dtbs checks; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,mmp-dma.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,mmp-dma.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,mmp-dma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,orion-xor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,orion-xor.yaml

## Purpose
This file is a Linux Devicetree binding schema for Marvell XOR engine. It validates nodes matched by `marvell,armada-3700-xor`, `marvell,orion-xor`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/marvell,orion-xor.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `marvell,armada-3700-xor`, `marvell,orion-xor`. Required properties: `compatible`, `reg`. Notable properties: `compatible`, `reg`, `clocks`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false, patternProperties, deprecated: true. The example instantiates `xor@d0060900` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes. The schema preserves deprecated properties for legacy DTS compatibility while steering new users toward common bindings. Pattern properties admit structured child nodes or supply names while still constraining their schema.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; deprecated properties must remain accepted long enough for old DTS files while new bindings avoid them; changing DMA specifier cells or request limits is an ABI break for client nodes.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,orion-xor.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,orion-xor.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,orion-xor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,xor-v2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,xor-v2.yaml

## Purpose
This file is a Linux Devicetree binding schema for Marvell XOR v2 engines. It validates nodes matched by `marvell,armada-7k-xor`. In the kernel tree, this documents the persistent DT ABI for DMA controller or DMA routing nodes and the specifiers used by DMA clients.

## Important APIs, Types, and Schema Contracts
This is declarative schema code, so it defines no C/Python functions or classes. The important APIs are the Devicetree properties, compatible strings, referenced schema fragments, and validation keywords consumed by dt-schema and kernel subsystem drivers. `$id` is `http://devicetree.org/schemas/dma/marvell,xor-v2.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible contract: `marvell,armada-7k-xor`. Required properties: `compatible`, `reg`, `msi-parent`, `dma-coherent`. Notable properties: `compatible`, `reg`, `clocks`, `clock-names`, `msi-parent`, `dma-coherent`. Referenced schemas: none. Validation keywords and constraints: additionalProperties: false. The example instantiates `xor0@6a0000` and exercises the main required properties. File-specific integration notes: DMA client integration depends on stable channel/specifier cells and the shared dma-controller/dma-common schemas. Clock array order and `clock-names` are ABI-sensitive because drivers request resources by fixed names or indexes.

## Control Flow
dt-schema selects this schema through the `compatible` value and validates the node before DTS output is accepted. Required-property checks run first for the node contract. DMA clients later consume the advertised `#dma-cells`/request mapping through the OF DMA lookup path when drivers request channels. At runtime the matching kernel driver maps register resources from `reg`, requests clocks/resets/IRQs, and probes only if those resources line up with the schema contract. Example blocks, when present, act as executable validation fixtures for dt-schema and document intended node construction for board DTS authors.

## State and Persistence
The YAML file stores no runtime state and defines no executable persistence path. Its stateful effect is the Devicetree ABI it accepts: once a DTS using these properties ships in firmware or a board file, driver code and users rely on those property names, array orders, and child-node layouts. For DMA bindings, channel counts, request counts, and specifier cell formats persist as the contract between DMA providers and client nodes.

## Dependencies and Integration Points
Depends on Devicetree core meta-schema, clock provider bindings. Integration points are DTS board files, `make dt_binding_check`, `make dtbs_check`, matching kernel drivers, and any subsystem helpers that parse these properties.

## Risks
Key risks are missing or misordered required resources can make the driver fail probe even though the node still matches by compatible; strict property closure can reject legacy or vendor DTS properties unless intentionally modeled; changing DMA specifier cells or request limits is an ABI break for client nodes; clock-name drift between schema, DTS, and driver resource lookup is a common integration failure.

## Test Signals
Useful signals are `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,xor-v2.yaml`, `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,xor-v2.yaml` against in-tree DTS users, example-schema validation from the `examples` block, driver probe logs for nodes using the listed compatibles, DMA client channel request and transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/dma/marvell,xor-v2.yaml -->
