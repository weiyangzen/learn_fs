## sources/distributed-fs/eos/mgm/http/webdav/LockResponse.cc

Purpose: builds a dummy WebDAV LOCK response with lock discovery information.

Important APIs/types/functions: `LockResponse::BuildResponse` parses namespaces, validates root XML, clones request lock properties into `<activelock>`, then appends fixed timeout, depth, locktoken, response headers, and XML body.

Control flow: request XML is parsed by base `WebDAVResponse`; build creates declaration, `<prop xmlns="DAV:">`, `<lockdiscovery>`, `<activelock>`, clones all child properties from the lockinfo root, and returns `this`.

State and persistence: no real lock is persisted. It returns a constant opaque lock token `00000000-0000-0000-0000-000000000000` and fixed `Second-604800` timeout/depth infinity.

Dependencies and integration points: instantiated by `WebDAVHandler` on `LOCK`; uses RapidXML helpers from `WebDAVResponse`.

Risks and test signals: because locking is not enforced, clients may believe a lock exists while EOS does not maintain lock state. Tests should cover malformed XML, empty root, cloned owner/scope/type fields, headers, and unlock behavior.
