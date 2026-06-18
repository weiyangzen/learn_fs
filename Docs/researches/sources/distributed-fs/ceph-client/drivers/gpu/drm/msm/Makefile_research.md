# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/Makefile

## Purpose
Defines the MSM DRM build graph, including include paths, Adreno GPU objects, optional display-controller/output objects, generated register headers, and XML-to-C header generation rules.

## Important APIs, types, and functions
- `ccflags-y` adds source, generated, DPU, DSI, and DP include paths as needed.
- `adreno-y` lists core Adreno files from a2xx through a8xx, with optional debugfs and GPU state objects.
- `msm-display-*` object groups are gated by HDMI, MDP4, MDP5, DPU, MDSS, KMS, DP, HDMI HDCP, DSI, and DSI PHY configs.
- `msm-y` lists core GEM, GPU, fence, submit, syncobj, perf, IOMMU, trace, and KMS objects.
- Header generation rules invoke `registers/gen_header.py` for Adreno and display XML files, optionally with schema validation.
- `ADRENO_HEADERS` and `DISPLAY_HEADERS` define generated header dependencies for GPU and display objects.

## Control flow
Kbuild accumulates object lists based on Kconfig symbols, appends display objects into `msm-y` when KMS is enabled, links `msm.o` under `CONFIG_DRM_MSM`, and ensures relevant generated XML headers exist before compiling dependent objects. The `CONFIG_DRM_MSM_VALIDATE_XML` branch toggles generator validation flags.

## State and persistence
No runtime state. Generated headers under `$(obj)/generated` are build artifacts derived from XML register descriptions.

## Dependencies and integration points
Couples Kconfig selections to source compilation and generated register headers. Integrates with Python, rules-fd XML schema, freedreno register XMLs, and all MSM DRM subdirectories.

## Risks
Missing generated header dependencies can cause parallel build races. Include path changes can mask source/generated header mismatches. Object list omissions can break feature configs or leave Kconfig-enabled code unlinked. Validation depends on host Python/lxml support.

## Test signals
Build matrix coverage for GPU-only, KMS, HDMI, DP, DSI, DPU/MDP4/MDP5, debugfs, GPU state, and XML validation configs. Parallel builds are important to catch generated-header ordering issues.
