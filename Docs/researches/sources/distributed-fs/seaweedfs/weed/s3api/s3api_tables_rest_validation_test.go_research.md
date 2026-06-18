<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_rest_validation_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_rest_validation_test.go

Purpose: tests validation and error mapping for S3 Tables REST namespace query parsing.

Important APIs/functions: tests call `buildListTablesRequest`, `buildGetTableRequest`, and `S3TablesApiServer.handleRestOperation` with invalid namespace values.

Control flow: table-driven cases supply uppercase, hyphenated, and slash-containing namespaces. Builder tests assert an error containing "invalid namespace". Handler test asserts HTTP 400 with AWS JSON error shape and `s3tables.ErrCodeInvalidRequest`.

State and persistence behavior: no persistent state. Requests are synthetic and mux vars are injected directly.

Dependencies and integration: uses gorilla/mux, httptest, JSON decoding, and `s3tables` error codes. It protects parser helpers in `s3api_tables.go`.

Risks: tests are narrow to namespace query validation; path namespace parsing, table-name validation, and ARN parsing have separate or missing coverage. Error-message substring assertions can drift with parser wording.

Test signals: passing tests mean invalid namespaces are rejected before hitting storage and are surfaced as client bad-request JSON errors, not internal errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_rest_validation_test.go -->
