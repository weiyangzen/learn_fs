# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/matchall.json

Purpose: 22 tc-testing cases for the `matchall` classifier on ingress and egress, validating protocol selection, gact actions, classid handling, skip flags, chain deletion, and `filter get`.

APIs and control flow: Cases use the tc-testing schema (`id`, `category`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, regex/count, `teardown`) and execute `$TC filter add|get|show|del`, `$TC qdisc add|del`, and `$TC actions` for police objects. Setups create ingress/root state, the command mutates filters, verification matches tc output, and teardown deletes qdisc/action state.

State/dependencies: State is namespace-local kernel qdisc/filter/action state on dummy devices via `nsPlugin`. Police action index `199` is shared inside the flag-validation cases and must be cleaned.

Risks/test signals: Regexes depend on iproute2 text such as `gact action pass`, `ref 1 bind 1`, `skip_hw`, and `not_in_hw`. Expected exits include success, parser errors, and skip/action incompatibility failures. Positive cases expect one match; invalid and delete cases expect zero or preserved chain-specific matches.
