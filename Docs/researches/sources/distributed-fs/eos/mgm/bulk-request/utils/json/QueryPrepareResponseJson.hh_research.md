## sources/distributed-fs/eos/mgm/bulk-request/utils/json/QueryPrepareResponseJson.hh

Purpose: implements JSON serialization for `QueryPrepareResponse` using the common JsonCpp jsonifier base.

Important flow: `jsonify(QueryPrepareResponse*, stringstream&)` creates a root object with `request_id`, initializes `responses` as an array, serializes each file response through a private overload, and writes the JsonCpp value to the stream. Per-file JSON keys mirror the response fields: `path`, `path_exists`, `on_tape`, `online`, `requested`, `has_reqid`, `req_time`, and `error_text`.

State/dependencies: header-defined methods depend on `Json::Value` and `common::JsonCppJsonifier`. Risks include implementation in a header without `inline` keywords if included in multiple translation units, depending on how the build treats it. Tests should assert exact JSON keys/types and escaping for paths/errors.
