## sources/distributed-fs/eos/mgm/http/webdav/WebDAVResponse.cc

Purpose: implements shared XML request parsing and RapidXML response-building helpers for WebDAV response classes.

Important APIs/types/functions: constructor copies/parses request body or supplies default allprop PROPFIND XML for empty body; `ParseNamespaces`; `GetNode`; `AllocateNode`; `AllocateAttribute`; `CloneNode`; `AllocateString`; `SetValue`.

Control flow: constructor parses XML into `mXMLRequestDocument` and logs parse errors without throwing. Namespace parsing records DAV and custom namespaces from root-level attributes. `GetNode` searches direct children matching known DAV/custom namespace prefixes.

State and persistence: owns request XML copy, parsed request document, response document, and namespace maps for one response object.

Dependencies and integration points: base for `PropFindResponse`, `PropPatchResponse`, and `LockResponse`; depends on RapidXML and common logging.

Risks and test signals: parse errors leave an empty/partial document and derived builders must detect missing root. Namespace parsing only scans top-level sibling nodes, not nested declarations. Tests should cover invalid XML, empty body, namespace prefixes, custom namespaces, and memory-pool lifetime after printing/clearing response document.
