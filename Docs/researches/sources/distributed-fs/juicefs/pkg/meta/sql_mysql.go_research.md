# sources/distributed-fs/juicefs/pkg/meta/sql_mysql.go

## Purpose

`sql_mysql.go` contains MySQL-specific registration and engine creation for the SQL metadata backend. It adapts MySQL duplicate-entry detection, password handling, and transaction isolation configuration before delegating the rest of metadata behavior to `newSQLMeta`/`dbMeta`.

## Important APIs, Types, And Functions

`isMySQLDuplicateEntryErr` recognizes `*mysql.MySQLError` number `1062` for unique-key conflicts. `recoveryMysqlPwd` recovers percent-decoded passwords in DSNs by parsing a synthetic URL around the password segment. `createMySQLEngine` parses the DSN, ensures `Params` exists, tries to set repeatable-read isolation through `transaction_isolation`, falls back to legacy `tx_isolation` when the first variable is unknown, pings the engine to verify the setting, and returns a ready xorm engine. `isUnknownTransactionIsolationErr` detects the fallback condition. `init` appends duplicate checking, installs the engine creator, and registers the `mysql` metadata scheme.

## Control Flow

MySQL engine creation starts with `mysql.ParseDSN(recoveryMysqlPwd(dsn))`. It then tries two possible system variable names because MySQL/MariaDB/TiDB variants differ. Each attempt creates an xorm engine, pings it, returns on success, closes it on failure, and only continues when the error says the chosen isolation variable is unknown. Any other ping failure is returned immediately.

## State And Persistence Behavior

This file does not define metadata tables directly. Its persistent effect is to force repeatable-read transaction isolation through DSN parameters before `dbMeta` begins using the engine. Duplicate-entry detection feeds shared retry and conflict logic in `sql.go` and `sql_bak.go`.

## Dependencies And Integration Points

It depends on `github.com/go-sql-driver/mysql`, xorm, and shared package globals `dupErrorCheckers`, `engineCreator`, and `Register`. `newSQLMeta` calls `engineCreator["mysql"]` when the driver is MySQL.

## Risks And Edge Cases

The DSN password recovery logic relies on locating the first colon and last at sign; unusual usernames or network addresses could make this brittle, though tests cover several special-character password cases. Setting isolation through connection parameters can fail for managed or proxy databases; the code only tolerates unknown variable names, not permission or unsupported value errors. MySQL duplicate-entry errors are also treated as retryable elsewhere, which can hide whether a conflict is expected or a real invariant violation.

## Test Signals

`TestRecoveryMysqlPwd` covers empty passwords and special characters including `@`, `|`, and `:` in encoded and direct forms. `TestMySQLClient` attempts end-to-end metadata testing against `root:@/dev` when the environment provides a database.
