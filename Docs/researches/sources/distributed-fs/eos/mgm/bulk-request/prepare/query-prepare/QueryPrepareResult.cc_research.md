## sources/distributed-fs/eos/mgm/bulk-request/prepare/query-prepare/QueryPrepareResult.cc

Purpose: implements the result wrapper returned by `PrepareManager::queryPrepare()`. It owns a `QueryPrepareResponse`, a finished flag, and a return code.

Important behavior: constructor initializes `mHasQueryPrepareFinished=false` and allocates an empty response. Getters expose the flag, shared response, and return code. Private setters are used by friend `PrepareManager`.

State/integration: no persistence; response is shared so callers can serialize it after query execution. Risks include `mReturnCode` not initialized in the constructor until `setReturnCode()` is called; current factory path sets it immediately after `doQueryPrepare()`. Tests should assert initial finished state, response allocation, and return-code setting through query manager.
