## sources/distributed-fs/ceph/src/rgw/rgw_multi_del.cc

Purpose: implements XML parsing for S3 multi-object delete requests and a concurrency scheduler for executing delete batches.

Important APIs/functions: `RGWMultiDelObject::xml_end()` extracts key, version id, optional ETag match, last-modified precondition, and size match. `RGWMultiDelDelete::xml_end()` parses quiet mode and collects objects. `RGWMultiDelXMLParser::alloc_obj()` maps XML elements. `rgw::multi_delete::dispatch()` runs per-item delete callbacks with controlled concurrency and versioned-bucket OLH handling.

Control flow: object XML validates required key, URL-decodes and parses last-modified time, and parses size with `strict_strtoll()`. Dispatch uses `ceph::async::spawn_throttle`. For unversioned buckets, all items run concurrently with `skip_update_olh=false`. For versioned buckets, items are grouped by object name; all but the last delete per key run first with `skip_update_olh=true`, then final deletes run with normal OLH update.

State and persistence: XML parser state is request-local. Delete persistence happens through the caller-provided `Exec` callback. Dispatch preserves request/result order through `Item::index`.

Dependencies/integration: depends on XML parser, async spawn throttle, Boost.Asio yield, strict number parsing, URL/time parsing, and RGW object keys.

Risks and test signals: `if_match` stores `c_str()` from an XML data string; lifetime depends on XML object storage and should be scrutinized. Grouping by key must preserve correctness for repeated deletes. Tests should cover quiet mode, invalid preconditions, versioned duplicate-key ordering, max_aio zero normalization, and on-dispatch callbacks.
