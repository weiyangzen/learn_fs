# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/proto/protoc_gen_hrpc.cc

Purpose: implements a protobuf compiler plugin that generates lightweight C++ HRPC service stubs. The generated stubs call `hdfs::RpcEngine::AsyncRpc` for each protobuf service method.

Important APIs and types: `StubGenerator` subclass of `google::protobuf::compiler::CodeGenerator`, `Generate`, `EmitService`, `EmitMethod`, and `main` invoking `PluginMain`.

Control flow: for every service in a `.proto` file, `Generate` opens `<proto-name>.hrpc.inl`, writes a generated class with a shared `RpcEngine`, and emits one inline method per protobuf method. Each generated method takes a request message, shared response message, and callback, then passes the raw method name to `AsyncRpc`.

State and persistence: no runtime persistence beyond generated source files emitted through `GeneratorContext`. The generated class stores a shared pointer to `RpcEngine`.

Dependencies and integration: depends on protobuf compiler APIs and local `protobuf/cpp_helpers.h` helpers such as `StripProto` and `ToCamelCase`. Its output is included by `namenode_operations.h`.

Risks and test signals: generator output is simple and method-name-sensitive; tests should diff generated stubs for expected methods after proto updates. It assumes service names are valid C++ class names and does not generate include guards or namespaces itself in this file, so consuming context matters.
