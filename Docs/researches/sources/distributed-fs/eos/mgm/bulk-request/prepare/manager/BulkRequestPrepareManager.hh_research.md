## sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/BulkRequestPrepareManager.hh

Purpose: declares the template-method subclass that adds bulk-request management to `PrepareManager` without changing the base prepare workflow.

Important APIs: constructor, `setBulkRequestBusiness()`, `getBulkRequest()`, overrides for stage/cancel initialization, file addition, saving, and failure handling. The base hooks are protected except the retrieval/configuration methods.

State/integration: integrates prepare workflow with `BulkRequestBusiness` persistence. Risks include ownership transfer through `getBulkRequest()` and shared ownership of business layer. Tests should derive or instantiate with mock filesystem/business dependencies to assert hook behavior.
