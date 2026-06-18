# sources/cloud-native/cri-o/server/rootless_unsupported.go

Purpose: non-Linux no-op implementation for rootless OCI spec adjustment.

Important APIs and functions: `makeOCIConfigurationRootless(g *generate.Generator)` exists for cross-platform compilation and does nothing.

Control flow: no mutations.

State and persistence: none.

Dependencies and integration: keeps platform-specific sandbox creation code buildable on non-Linux targets.

Risks: non-Linux rootless behavior is not handled here.

Test signals: compile-time coverage only.
