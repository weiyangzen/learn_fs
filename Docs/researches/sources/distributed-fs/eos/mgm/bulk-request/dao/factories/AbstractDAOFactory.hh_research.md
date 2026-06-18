## sources/distributed-fs/eos/mgm/bulk-request/dao/factories/AbstractDAOFactory.hh

Purpose: declares the abstract factory for persistence-layer DAOs. It currently has a single product: `getBulkRequestDAO()`.

Important API: `virtual std::unique_ptr<IBulkRequestDAO> getBulkRequestDAO() const = 0` plus virtual destructor.

State/integration: allows `BulkRequestBusiness` to remain independent of proc-directory persistence. Risks are minimal, but repeated factory calls may create independent DAO instances with shared external dependencies. Tests should use fake factories to isolate business logic and verify ownership transfer.
