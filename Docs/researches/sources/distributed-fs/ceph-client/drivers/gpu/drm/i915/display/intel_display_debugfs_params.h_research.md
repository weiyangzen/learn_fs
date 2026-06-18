# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs_params.h

## Purpose
`intel_display_debugfs_params.h` declares the display-parameter debugfs registration function. It is a narrow interface used by the broader display debugfs setup code.

## Important APIs, Types, And Functions
The header forward declares `struct intel_display` and declares `void intel_display_debugfs_params(struct intel_display *display)`. It has no stubs, because the implementation file itself is part of the debugfs build path that includes it.

## Control Flow And State
No state or control flow is defined here. The declared function creates debugfs files for `display->params` when invoked.

## Dependencies And Integration Points
The header is consumed by `intel_display_debugfs.c`. It intentionally avoids including `intel_display_core.h`, reducing include dependencies for callers that only need the declaration.

## Risks And Test Signals
Risk is limited to declaration/definition drift. Build coverage and debugfs file creation smoke tests are sufficient. Behavioral risks are in the `.c` implementation.
