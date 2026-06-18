# sources/distributed-fs/ceph/src/rgw/rgw_s3select.cc

## Purpose
`rgw_s3select.cc` implements the S3 Select operation for RGW. It creates the select RGW op, parses AWS SelectObjectContent XML, streams object data through the s3select engine for CSV/JSON and optionally Parquet, formats AWS event-stream responses with CRCs, tracks usage counters, and handles scan ranges and Trino-specific row-boundary shaping.

## Important APIs, Types, and Functions
`rgw::s3select::create_s3select_op()` returns `RGWSelectObj_ObjStore_S3`. `aws_response_handler` builds AWS event-stream messages: headers for Records, Cont, Progress, Stats, End, and errors; `create_message()` fills total length/header length/prelude CRC/message CRC; send methods write binary data via RGW formatter and set chunked transfer encoding.

`RGWSelectObj_ObjStore_S3::get_params()` reads the request body, detects Trino user-agent, and calls `handle_aws_cli_parameters()`. That parser extracts SQL expression, input/output serialization fields, compression type, progress flag, and scan range using tag-string extraction. `execute()` blocks disabled S3 Select, validates Parquet magic, invokes Parquet processing, or starts a GET/range request for CSV/JSON. `send_response_data()` dispatches to `csv_processing()`, `json_processing()`, or `parquet_processing()`.

`run_s3select_on_csv()`, `run_s3select_on_json()`, and `run_s3select_on_parquet()` configure the external s3select engine, execute it, send records/progress/errors, and update returned byte counters. `range_request()` reuses `RGWGetObj` range execution for Parquet and scan ranges. `shape_chunk_per_trino_requests()` trims scan-range chunks to row delimiters for Trino.

## Control Flow
The operation first reads XML parameters, then defers normal object reads to `RGWGetObj_ObjStore_S3`. Each returned data chunk arrives in `send_response_data()`. CSV/JSON chunks are fed to the select engine; emitted rows are wrapped in AWS event-stream Records frames. When processed bytes reach the target size or SQL LIMIT is reached, Stats and End frames are sent. Parquet reverses control: the Arrow-backed reader calls RGW range callbacks through `m_rgw_api`, and `parquet_processing()` accumulates buffers for those reads.

## State and Persistence Behavior
There is no object metadata persistence. Per-request state includes parsed XML fields, serialization delimiters, scan range, object size for processing, response buffers, byte counters stored into `s->s3select_usage`, chunk count, Parquet/JSON mode flags, and range-request scratch buffers. Responses are streamed over HTTP using chunked transfer encoding.

## Dependencies and Integration Points
The file depends on `RGWGetObj_ObjStore_S3`, request state/formatters, RGW range parsing, Ceph logging, Boost CRC, Boost string replacement, the external `s3select` engine, optional Arrow/Parquet support, and S3 REST error formatting. It integrates directly with GET object read callbacks and usage accounting.

## Risks
XML parsing is ad hoc string extraction and may mis-handle namespaces, missing sections, or repeated tags. Compression other than `NONE` is rejected. Regex/SQL/parser errors are mapped inconsistently between AWS event-stream errors and normal RGW XML errors. Some CSV paths update processed bytes with buffer length instead of shaped `len`, which can affect stats and termination. `parquet_processing()` appends `len` bytes from each buffer segment using the same offset/length, which is sensitive to multi-segment bufferlists. SQL LIMIT uses `-ENOENT` to stop fetching, which callers must treat as nonfatal.

## Test Signals
Tests should cover CSV, JSON DOCUMENT, unsupported JSON type, Parquet magic validation with and without Arrow, disabled config, empty objects, malformed XML, unsupported compression, progress frames, stats/end frames, event-stream CRC compatibility, scan ranges, Trino row-boundary shaping, SQL LIMIT early termination, range callbacks, usage counters, and chunked response setup.
