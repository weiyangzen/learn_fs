# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convertllb.go

Purpose: implements the Dockerfile frontend `convertllb` subrequest by serializing a dispatch state's LLB graph into digest-addressed protobuf ops.

Important API: `(*dispatchState).ConvertLLB(ctx)` returns `*convertllb.Result`.

Control flow: marshals `ds.state`, initializes result maps and metadata/source fields, unmarshals each definition byte slice into `pb.Op`, computes its digest from bytes, and stores op by digest.

State and persistence: reads final dispatch state only; result is returned through gateway subrequest response.

Dependencies and integration: used by `DockerfileConvertLLB` in `convert.go` and by builder subrequest handling.

Risks and test signals: risks include marshal failures and protobuf unmarshal incompatibility. Subrequest tests and clients inspecting LLB output provide coverage.
