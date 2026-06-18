## sources/distributed-fs/eos/mgm/bulk-request/BulkRequest.cc

Purpose: provides the static `BulkRequest::BULK_REQ_TYPE_TO_STRING_MAP`, mapping `PREPARE_STAGE`, `PREPARE_EVICT`, and `PREPARE_CANCEL` to stable string names. This backs `BulkRequest::bulkRequestTypeToString()` in the header.

Important behavior: there is no runtime control flow beyond static initialization. The map is used in logging, persistence error messages, and business-layer switch diagnostics. State is process-local and immutable after initialization.

Dependencies are limited to `BulkRequest.hh` and `<map>`. Risks are mostly enum drift: adding a new `BulkRequest::Type` without updating this map can make `bulkRequestTypeToString()` throw `std::out_of_range` in logging/error paths. Test signals should cover every enum value, unsupported/default behavior where relevant, and business-layer persistence for each type.
