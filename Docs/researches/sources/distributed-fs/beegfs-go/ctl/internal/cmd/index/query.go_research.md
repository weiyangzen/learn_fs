
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/query.go

- Purpose: implements `index query` for SQL queries against single-level Hive Index databases.
- Important APIs: `newGenericQueryCmd`, `newQueryCmd`, and `runPythonQueryIndex`.
- Control flow/state: validates Hive Index configuration, forwards `--db-path` and `--sql-query`, appends output format `-Q` for non-table output, and executes `bee query-index`.
- Dependencies/integration: uses external Hive Index SQL/query engine, `bflag`, Viper output config, and logger.
- Risks/tests: raw SQL is forwarded without local validation; only last statement output is documented. No direct tests.
