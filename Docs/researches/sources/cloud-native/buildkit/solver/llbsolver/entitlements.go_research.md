<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/entitlements.go -->
## sources/cloud-native/buildkit/solver/llbsolver/entitlements.go

Purpose: loads and filters LLB entitlements stored on solver jobs/builders.

Important APIs and types: `keyEntitlements`, `supportedEntitlements(ents []string)`, and `loadEntitlements(b solver.Builder)`.

Control flow: `supportedEntitlements` maps string names to known BuildKit entitlement constants for network host, security insecure, and devices. `loadEntitlements` iterates all builder values under `keyEntitlements`, requires each to be an `entitlements.Set`, and merges configs into one set, merging when a previous non-nil config exists.

State and dependencies: no persistence; values are stored in solver job value maps elsewhere. Dependencies are `solver.Builder`, BuildKit `entitlements`, and `pkg/errors`.

Integration points: `llbBridge.loadResult`, `validateEntitlements`, and LLB loading use these values to permit or reject network/security/device behavior.

Risks and test signals: type assertions mean incorrect job value wiring fails the build. Merge behavior distinguishes nil config from non-nil config. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/entitlements.go -->
