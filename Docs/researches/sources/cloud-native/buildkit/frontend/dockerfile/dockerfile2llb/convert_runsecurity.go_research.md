# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runsecurity.go

Purpose: converts Dockerfile `RUN --security` mode into an LLB run option.

Important API: `dispatchRunSecurity(c)` maps insecure/sandbox modes to solver security enums.

Control flow: insecure returns `llb.Security(pb.SecurityMode_INSECURE)`, sandbox returns `llb.Security(pb.SecurityMode_SANDBOX)`, and unknown modes error.

State and persistence: none; security mode is stored in the exec op.

Dependencies and integration: called by `dispatchRun`; depends on instruction parser and solver `pb` security modes.

Risks and test signals: risk is feature-gating/security entitlement mismatch outside this function. RUN security integration tests provide coverage.
