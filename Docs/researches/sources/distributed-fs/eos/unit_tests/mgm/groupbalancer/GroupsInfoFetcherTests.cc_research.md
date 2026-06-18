# sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupsInfoFetcherTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupsInfoFetcherTests.cc

Purpose: tests group status filtering behavior in `eosGroupsInfoFetcher`.

Important APIs and types: `eosGroupsInfoFetcher`, `GroupStatus`, and status predicates configured through the fetcher constructor or setter.

Control flow: the default test asserts default status acceptance. The drain-status test checks whether drain status is treated according to the configured predicate. The lambda-status test installs a custom lambda and verifies it controls validity.

State and persistence: predicate state is held in memory by the fetcher object. No external I/O is exercised.

Dependencies and integration: this is a boundary test for the component that feeds balancer engines with group data. Correct filtering determines which groups can act as sources or targets.

Risks and test signals: because tests are small, they mainly guard predicate plumbing rather than namespace-fetching behavior. Integration with real MGM group data is outside this file.
