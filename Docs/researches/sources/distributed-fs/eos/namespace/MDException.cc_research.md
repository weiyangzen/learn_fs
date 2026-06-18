## sources/distributed-fs/eos/namespace/MDException.cc

Purpose: Implements `MDStatus` construction and logging for namespace metadata operation status.

Important APIs and functions: `MDStatus::MDStatus(int, const std::string&)` stores errno and error text, logging at critical level for non-`ENOENT` errors and debug level for `ENOENT`.

Control flow: construction performs the only behavior: choose log severity based on errno, then leave `ok()` false because `err` is non-empty.

State and persistence: no durable persistence; status objects carry local errno and message for caller-side throwing or inspection.

Dependencies and integration: includes `MDException.hh`, common logging, and folly exception wrapper headers. Used by metadata services as a non-exception status channel.

Risks: constructing `MDStatus` for expected non-ENOENT failures emits critical logs, so high-volume paths should avoid using it for benign conditions. Empty error strings are the only `ok()` signal.

Test signals: verify log severity expectations, `ok/getError/getErrno`, and `throwIfNotOk` behavior through header implementation.
