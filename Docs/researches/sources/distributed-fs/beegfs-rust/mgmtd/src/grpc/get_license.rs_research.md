<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_license.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_license.rs

Purpose: returns license certificate data and trial-serial persistence state over gRPC.

Important APIs/types/functions: `get_license()` calls `app.license().get_license_cert_data()`, reads `Config::TrialSerial` from SQLite, and builds `GetLicenseResponse` including a derived `trial_used` flag.

Control flow: if certificate data is available and is a trial certificate, the handler marks `trial_used` true when the stored trial serial exists and differs from the current serial. For non-trial or missing data it reports false.

State and persistence: read-only. It reads the license library's cached cert data and the DB config row storing a previously used trial serial.

Dependencies and integration points: used by management clients to inspect licensing. Integrates `license.rs`, protobuf license types, and DB config.

Risks: if the license library is unavailable or no cert is loaded, the helper returns an error. Trial-used semantics depend on serial persistence during startup in `lib.rs`.

Test signals: no direct tests. Coverage should include no library, invalid/no data, trial same serial, trial different serial, and non-trial certs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_license.rs -->
