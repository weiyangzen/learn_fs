<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/protoc-gen-go-fieldpath/generator.go -->
# sources/cloud-native/containerd/cmd/protoc-gen-go-fieldpath/generator.go

## Purpose
Generator logic for protoc plugin that emits Go field-path helper methods for protobuf messages.

## Important APIs, Types, And Functions
Defines `generator`, `newGenerator`, `genFieldMethod`, `isMessageField`, `isLabelsField`, `isAnyField`, `collectChildlen`, and `generate`.

## Control Flow
Walks protobuf messages, discovers child message fields, labels maps, and Any fields, then emits methods that join field paths and optionally unmarshal Any values for nested path resolution.

## State And Persistence
Writes generated Go code through `protogen.GeneratedFile`; no runtime persistence.

## Dependencies And Integration Points
protogen, protobuf descriptors, fieldpath helpers, fmt/string formatting imports.

## Risks And Test Signals
The function name `collectChildlen` is misspelled but internal. Generator correctness depends on descriptor shape; tested through generated-code compilation. Source size reviewed: 201 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/protoc-gen-go-fieldpath/generator.go -->
