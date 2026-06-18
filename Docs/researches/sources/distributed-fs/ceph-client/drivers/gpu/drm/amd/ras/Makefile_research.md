# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/Makefile

## Purpose

This Makefile is the top-level AMDGPU RAS build aggregator. It selects the RAS manager directory, adds include paths for `rascore` and the manager, and includes the subordinate Makefiles that append object files into `AMD_GPU_RAS_FILES`.

## Important APIs, Types, And Functions

The relevant variables are `AMD_GPU_RAS_MGR`, defaulting to `ras_mgr`; `RAS_LIBS`, containing the manager and `rascore`; and `AMD_RAS`, a list of included Makefiles resolved under `AMD_GPU_RAS_FULL_PATH`. It also appends include paths through `subdir-ccflags-y`.

## Control Flow, State, And Persistence

Build-time control flow is simple: if no manager override is supplied, use `ras_mgr`; compute two library Makefile paths; include them. It persists no runtime state, but it determines which RAS implementation objects enter the AMDGPU module.

## Dependencies And Integration Points

It depends on outer AMDGPU Kbuild variables `AMD_GPU_RAS_FULL_PATH` and `AMD_GPU_RAS_PATH`. It integrates with `ras_mgr/Makefile`, `rascore/Makefile`, and the parent driver Makefile that consumes `AMD_GPU_RAS_FILES`.

## Risks And Test Signals

Risks are incorrect path variables, missing include paths for cross-directory headers, and future manager overrides not matching the object layout. Test signals include kernel builds with RAS enabled, clean builds after directory renames, and object list inspection to confirm both manager and core RAS objects are present.
