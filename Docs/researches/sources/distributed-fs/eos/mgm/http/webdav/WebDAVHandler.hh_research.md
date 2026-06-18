## sources/distributed-fs/eos/mgm/http/webdav/WebDAVHandler.hh

Purpose: declares the WebDAV protocol handler for EOS HTTP.

Important APIs/types/functions: private method enum, constructor taking `VirtualIdentity*`, static `Matches`, `HandleRequest`, `MkCol`, `Move`, `Copy`, and inline `ParseMethodString`.

Control flow: HTTP server can test `Matches` and then delegate WebDAV requests to `HandleRequest`.

State and persistence: inherits identity and response storage from `ProtocolHandler`; mutation methods persist through MGM operations in `.cc`.

Dependencies and integration points: depends on common `ProtocolHandler`, mapping, namespace macros, and HTTP request/response types.

Risks and test signals: method parsing is exact and case-sensitive. Tests should cover unsupported WebDAV methods and interaction with other protocol handlers.
