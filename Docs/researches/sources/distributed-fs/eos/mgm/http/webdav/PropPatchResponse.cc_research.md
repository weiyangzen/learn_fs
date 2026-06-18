## sources/distributed-fs/eos/mgm/http/webdav/PropPatchResponse.cc

Purpose: builds a dummy WebDAV PROPPATCH multistatus response acknowledging requested property set/remove operations.

Important APIs/types/functions: `PropPatchResponse::BuildResponse` parses namespaces, validates root `<propertyupdate>`, builds `<d:multistatus>`, copies custom namespace declarations, then emits `HTTP/1.1 200 OK` propstat entries for each property under DAV `set/prop` and `remove/prop`.

Control flow: no property persistence is performed. It echoes property names in response nodes and always marks them successful when present.

State and persistence: does not mutate EOS attributes or any property store.

Dependencies and integration points: instantiated by `WebDAVHandler` for PROPPATCH; uses `WebDAVResponse` namespace and XML helpers.

Risks and test signals: clients may believe properties were saved although response is fake. The `<d:href>` node is created but no value is set. Tests should cover set/remove XML, custom namespaces, malformed XML, and client compatibility expectations.
