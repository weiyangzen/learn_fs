# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_policy_types.h

## Purpose
`dml_top_policy_types.h` defines the small public policy-parameter surface used by DML21 top-level options. It currently provides tunables that influence display-mode policy decisions without changing the display configuration or SoC/IP bounding boxes.

## Important APIs, Types, And Data Shapes
The only exported type is `struct dml2_policy_parameters`. It contains `odm_combine_dispclk_threshold_khz`, a threshold for ODM combine policy decisions based on display clock, and `max_immediate_flip_latency`, a cap for immediate-flip latency policy. There are no functions, enums, or macros beyond the include guard.

## Control Flow And Integration
This header is included by `dml_top_types.h`, making policy parameters part of the broader top-level DML API surface. The exact structure is not heavily referenced in this subset, but policy concepts are reflected in `dml2_pmo_options`, mode support, and mode programming paths where ODM, immediate flip, p-state, DRR, and SubVP strategy are selected.

## State And Persistence Behavior
The policy structure is plain runtime configuration. It owns no memory and has no persistence behavior. Because it is a small scalar struct, callers can safely copy it by value, but absent defaults must be handled by initialization code outside this file.

## Dependencies
The file has no includes. It depends only on standard C integer types being available through includers or compiler defaults for `unsigned long` and `unsigned int`. Its main dependency is conceptual: consumers must interpret the units consistently as kHz and latency units expected by the policy code.

## Risks And Edge Cases
The structure has no validity flags, so zero can mean either "unset" or a real threshold depending on consumer interpretation. Unit ambiguity for `max_immediate_flip_latency` should be checked at call sites. As the policy surface grows, adding fields without explicit initialization in callers could change mode-selection behavior.

## Test Signals
Tests should verify default initialization, explicit ODM threshold behavior near the boundary value, and immediate-flip latency behavior when the cap is zero, below calculated latency, and above calculated latency. Compile-time integration through `dml_top_types.h` is also useful because this header intentionally stays minimal.
