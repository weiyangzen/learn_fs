# sources/distributed-fs/ceph/src/rgw/rgw_http_client.cc

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This source implements RGW's libcurl-backed HTTP transport: `rgw_http_req_data`, pooled `RGWCurlHandle` objects, `RGWHTTPClient::init_request()`, callback dispatch, `RGWHTTPManager` multi-handle scheduling, cancellation, pause/resume, request completion, and `RGWHTTP::send()`/`process()`. It is in-memory lifecycle state only, integrates with libcurl, Ceph threading/async completion, RGW errno mapping, and completion manager hooks. Main risks are cancellation/callback races, global curl lifecycle, SSL verification configuration, timeout behavior, request lock ordering, and `send_len` narrowing. Test signals include request success/failure mappings, SSL options, callback errors, cancellation, coroutine/blocking waits, pause/resume, timeout, handle reuse, and shutdown with live requests.
