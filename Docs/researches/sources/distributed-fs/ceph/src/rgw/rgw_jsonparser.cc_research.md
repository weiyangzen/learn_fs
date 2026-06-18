# sources/distributed-fs/ceph/src/rgw/rgw_jsonparser.cc

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This standalone utility reads JSON from stdin with `JSONParser`, prints parsed nodes, drills into a `conditions` object, decodes the input as `RGWUserInfo`, and dumps it with `JSONFormatter`. It is developer/test tooling, not RGW server persistence. Dependencies are Ceph JSON/formatter helpers and RGW user types. Risks include continuing after parse errors, utility-level uncaught exception behavior, an unused `bufferlist`, and limited handling for large/malformed input. Tests should feed valid RGW user JSON, malformed JSON, missing-field decode failures, array conditions, and compare formatted output with `RGWUserInfo::dump()`.
