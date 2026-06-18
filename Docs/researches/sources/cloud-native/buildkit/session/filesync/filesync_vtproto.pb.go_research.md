<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_vtproto.pb.go -->
# sources/cloud-native/buildkit/session/filesync/filesync_vtproto.pb.go

Purpose: vtprotobuf optimized helpers for filesync `BytesMessage`.

Important APIs, types, and functions: implements clone, equality, marshal, size, and unmarshal methods for `BytesMessage`.

Control flow and state: generated code deep-copies data on clone, compares data and unknown fields, writes protobuf wire format, and parses byte fields while preserving unknown fields.

Dependencies and integration: used by fast protobuf paths for FileSend byte streams.

Risks and test signals: generated code should be regenerated from proto. Test byte round trips, clone independence, and stream integration with large chunked writes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_vtproto.pb.go -->
