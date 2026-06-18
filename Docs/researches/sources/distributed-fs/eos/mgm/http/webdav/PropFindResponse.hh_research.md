## sources/distributed-fs/eos/mgm/http/webdav/PropFindResponse.hh

Purpose: declares PROPFIND response parsing and property generation support.

Important APIs/types/functions: `EOS_WEBDAV_HIDE_IN_PROPFIND_PREFIX`; extern encode tables and `dav_uri_decode`; `PropertyTypes` bitmask enum; constructor initializes encode tables; `BuildResponse`, `ParseRequestPropertyTypes`, `BuildResponseNode`, `MapRequestPropertyType`, and `EncodeURI`.

Control flow: `MapRequestPropertyType` converts DAV/OwnCloud property names to bit flags consumed by `BuildResponseNode`.

State and persistence: stores requested property bitmask and client identity pointer. Static encode table initialization is shared process state.

Dependencies and integration points: inherits `WebDAVResponse`; used by `WebDAVHandler`.

Risks and test signals: constructor's `initialized` flag is never set to true after initializing tables, so tables are rebuilt every construction; harmless but not intended. `ALLPROP_MARKER = 0xf000` overlaps extension bits and can make bit tests subtle; tests should cover allprop response differences.
