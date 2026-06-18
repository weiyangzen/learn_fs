# sources/control-plane/mayastor/test/grpc/grpc_enums.js

Purpose: dynamically extracts enum constants from Mayastor protobuf descriptors for JavaScript gRPC tests.

Important APIs/types/functions: uses `@grpc/proto-loader`, `grpc.loadPackageDefinition`, and `path.join` to load `utils/dependencies/apis/io-engine/protobuf/mayastor.proto`; iterates loaded `mayastor` definitions and stores every enum variant name/number into `constants`.

Control flow: load proto synchronously with protobufjs include dir, flatten package definitions, detect entries whose `format` mentions `EnumDescriptorProto`, then export a name-to-number object.

State/persistence: in-memory constants object only.

Dependencies/integration: consumed by grpc JS tests to avoid hard-coding enum numeric values.

Risks: relies on internal descriptor shape (`ent.format` and `ent.type.value`) of grpc/proto-loader output. Duplicate enum variant names across enums would overwrite each other.

Test signals: JS tests using exported constants should match current protobuf enum values after proto changes.
