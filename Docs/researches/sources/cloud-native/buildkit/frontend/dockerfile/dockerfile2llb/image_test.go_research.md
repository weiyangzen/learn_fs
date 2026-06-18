# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/image_test.go

Purpose: verifies that `clone` deep-copies mutable image config fields.

Important test coverage: exposed ports, env, cmd, entrypoint, volumes, labels, onbuild, shell, healthcheck test slice, and history are mutated in the clone and asserted unchanged in the source.

Control flow and state: constructs an in-memory `DockerOCIImage`, clones it, mutates nested values, and asserts original values.

Dependencies and integration: protects stage inheritance semantics in `convert.go`.

Risks and test signals: strong signal for currently known mutable fields. Future image config fields need test updates.
