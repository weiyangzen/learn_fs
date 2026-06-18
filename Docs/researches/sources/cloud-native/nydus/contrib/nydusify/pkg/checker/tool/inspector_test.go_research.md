# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/inspector_test.go

Purpose: tests inspector JSON formatting, construction, success parsing, command failure propagation, and invalid JSON handling.

Important APIs and flow: `TestBlobInfoString` and `TestBlobInfoListString` assert JSON serialization. `TestNewInspector` validates binary path assignment. `TestInspectorInspect` uses temporary shell scripts to emit valid blob JSON, emit an error with nonzero exit, and emit invalid JSON. It also tests unsupported operation dispatch.

State and persistence: writes temporary executable scripts only. No real bootstrap or `nydus-image` dependency is used.

Dependencies and integration: confirms the wrapper can decode the expected `nydus-image inspect --request blobs` schema and exposes failures to callers.

Risks and test signals: strong unit signal around parsing and errors. It does not check exact CLI arguments, so a command order regression could pass if fake scripts ignore arguments.
