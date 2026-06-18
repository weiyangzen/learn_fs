## sources/distributed-fs/eos/mgm/http/webdav/WebDAVResponse.hh

Purpose: declares the abstract base class for WebDAV XML responses.

Important APIs/types/functions: inherits `eos::common::HttpResponse`; defines `NamespaceMap`, XML document members, namespace maps, constructor, pure virtual `BuildResponse`, and XML helper methods.

Control flow: derived response builders use base helpers to parse request XML and assemble response XML.

State and persistence: per-response XML documents and namespace maps only.

Dependencies and integration points: used by all WebDAV response types and returned through the common HTTP response interface.

Risks and test signals: because the class itself is an `HttpResponse`, derived `BuildResponse` often returns `this`; ownership expectations should be verified to prevent leaks or double deletes.
