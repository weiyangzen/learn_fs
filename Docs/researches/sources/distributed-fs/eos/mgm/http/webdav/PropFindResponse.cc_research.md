## sources/distributed-fs/eos/mgm/http/webdav/PropFindResponse.cc

Purpose: implements WebDAV PROPFIND XML responses for file/directory properties, directory listings, quotas, etags, and OwnCloud extension fields.

Important APIs/types/functions: global URI encode/decode helpers; `PropFindResponse::EncodeURI`; `BuildResponse`; `ParseRequestPropertyTypes`; `BuildResponseNode`. Properties include content length/type, modified/creation dates, resource type, display name, etag, quotas, OwnCloud id/size/permissions, checked-in/out, and allprop marker.

Control flow: `BuildResponse` parses namespaces and requested property types, optionally enforces OwnCloud sync-allow attribute for `oc:id`, builds a multistatus document, stats the request path after namespace mapping, and branches by `Depth`: `0` or file returns one node; `1` opens the directory and appends child nodes excluding version/atomic/hidden entries; `1,noroot`, `infinity`, and empty depth return not implemented. `BuildResponseNode` stats each path, hides hardlinks, URI-encodes hrefs, creates found and not-found propstat blocks, fills requested properties, and maps stat/access failures to response code.

State and persistence: reads EOS namespace state through `gOFS->_stat`, `XrdMgmOfsDirectory`, `Quota::GetIndividualQuota`, and `gOFS->acc_access`. Does not mutate filesystem state.

Dependencies and integration points: instantiated by `WebDAVHandler`; uses `NamespaceMap`, `XrdMgmOfsDirectory`, `Quota`, `Timing`, `Path`, `OwnCloud`, and RapidXML.

Risks and test signals: URI encode buffers are stack-sized to `3 * strlen`; OK for byte expansion but global encode tables use static initialization without synchronization. XML values rely on RapidXML value setting; confirm escaping behavior during print. Tests should cover depth variants, missing/inaccessible paths, hardlink hiding, quota properties, OwnCloud sync-block attribute, hidden prefixes, symlink stat failures, and path namespace mapping.
