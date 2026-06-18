# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runnetwork.go

Purpose: converts Dockerfile `RUN --network` mode into an LLB run option.

Important API: `dispatchRunNetwork(c)` maps parsed network mode to `llb.Network`.

Control flow: default mode returns nil, `none` maps to `pb.NetMode_NONE`, `host` maps to `pb.NetMode_HOST`, and unknown modes error.

State and persistence: none; network mode is encoded in the exec op.

Dependencies and integration: called by `dispatchRun`; depends on instruction parser and solver `pb` net modes.

Risks and test signals: risk is parser/dispatcher mode drift. RUN network frontend tests cover supported and unsupported modes.
