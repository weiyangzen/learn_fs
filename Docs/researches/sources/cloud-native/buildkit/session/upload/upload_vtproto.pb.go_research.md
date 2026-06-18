## sources/cloud-native/buildkit/session/upload/upload_vtproto.pb.go

Purpose: generated vtprotobuf fast-path helpers for upload `BytesMessage`.

Important APIs/types/functions: implements clone, equality, marshal, sized-buffer marshal, size, and unmarshal methods for `BytesMessage`. Unmarshal parses wire type 2 for the `data` field and skips unknown fields.

Control flow: marshal allocates based on `SizeVT`, writes bytes field if present, and returns the produced slice. Unmarshal loops over protobuf wire data, appends decoded bytes to `Data`, and returns descriptive errors for invalid wire format.

State and persistence: operates only on message fields in memory.

Dependencies and integration points: complements standard protobuf generated code and may be used by optimized serializers in the session upload path.

Risks and test signals: stale generated code after proto changes is the main risk. Because upload messages are raw byte chunks, malformed length handling is important; generated unmarshal includes bounds checks. No vtproto-specific tests are in this subset.
