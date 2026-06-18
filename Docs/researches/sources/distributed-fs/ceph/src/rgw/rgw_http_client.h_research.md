# sources/distributed-fs/ceph/src/rgw/rgw_http_client.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header declares RGW's outbound HTTP client abstraction: configurable `RGWHTTPClient`, virtual receive/send callbacks, `RGWHTTPHeadersCollector`, buffer-backed `RGWHTTPTransceiver`, `RGWHTTPManager`, pause/resume states, and the `RGWHTTP` facade. It carries transient method/URL/header/body/timeout/SSL/user-info state and integrates with Ceph yield contexts, `bufferlist`, and I/O correlation ids. Risks include caller-owned buffer lifetime, exception behavior for missing headers, effective URL changes after initial parsing, and request object lifetime during callbacks. Tests should cover subclass dispatch, header case-insensitivity, body transceiving, timeouts, SSL flag propagation, cancellation, and process/wait behavior.
