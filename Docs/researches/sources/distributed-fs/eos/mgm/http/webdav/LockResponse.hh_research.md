## sources/distributed-fs/eos/mgm/http/webdav/LockResponse.hh

Purpose: declares the WebDAV LOCK response builder.

Important APIs/types/functions: constructor takes request and `VirtualIdentity*`, stores identity, and calls base `WebDAVResponse`; `BuildResponse` overrides response construction.

Control flow: used by `WebDAVHandler` for LOCK methods.

State and persistence: stores client identity pointer but implementation does not use it for real lock state.

Dependencies and integration points: inherits `WebDAVResponse`; includes RapidXML, mapping, namespace, and identity dependencies.

Risks and test signals: identity pointer lifetime should match request handling. Since lock responses are dummy, compatibility tests with WebDAV clients are important.
