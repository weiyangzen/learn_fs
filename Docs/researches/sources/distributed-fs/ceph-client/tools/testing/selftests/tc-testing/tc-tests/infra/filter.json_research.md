# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/filter.json

Purpose: 3 negative infrastructure tests for filter-chain and shared-block validation: prio-0 chain deletion without soft lockup, empty `fw` filter rejection on shared block, and `flow` filter rejection without baseclass.

APIs and control flow: Uses `$TC filter add|delete|show` and `$TC qdisc add|del`. Each command is expected to fail with exit `2`, then verification checks residual chain state or confirms no invalid filter was installed.

State/dependencies: Temporary state is chain metadata and shared block classifier configuration. Requires `nsPlugin`, chain-aware filters, `fw`, `flow`, and shared-block support.

Risks/test signals: The soft-lockup regression is detected by non-hang plus output, not by a simple value. Shared-block failures depend on parser/kernel validation order. Expected matches are one chain line for the regression and zero `fw`/`flow` lines for rejected filters.
