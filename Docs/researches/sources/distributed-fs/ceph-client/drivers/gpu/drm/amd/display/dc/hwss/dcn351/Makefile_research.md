# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/Makefile

## Purpose
The DCN351 Makefile lists the DCN351 hw sequencer objects and adds them to the AMD Display build.

## Important APIs, types, and functions
It defines `DCN351 = dcn351_hwseq.o dcn351_init.o`, expands that into `AMD_DAL_DCN351` under `$(AMDDALPATH)/dc/dcn351/`, and appends the result to `AMD_DISPLAY_FILES`.

## Control flow
There is no runtime control flow. Build-system control flow is the object list expansion that ensures both DCN351 implementation files are compiled and linked.

## State and persistence behavior
No runtime state is owned. Build state is limited to make variables contributing object files to the display driver.

## Dependencies and integration points
The file integrates the DCN351 directory into the broader AMD Display build system. The path prefix assumes the tree layout used by the surrounding display Makefiles.

## Risks and edge cases
If the object list or path prefix drifts from source layout, DCN351 symbols such as `dcn351_hw_sequencer_construct` or power-gating overrides will be missing at link time. Adding new DCN351 source files requires updating this list.

## Test signals
A successful kernel/display-driver build with DCN351 enabled is the primary signal. Link failures or missing constructor symbols indicate Makefile coverage issues.
