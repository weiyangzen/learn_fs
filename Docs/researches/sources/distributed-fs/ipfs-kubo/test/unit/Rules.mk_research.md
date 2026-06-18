## sources/distributed-fs/ipfs-kubo/test/unit/Rules.mk

Purpose: make fragment for unit-test report artifacts.

Important targets and control flow: includes `mk/header.mk`, adds `$(d)/gotest.json` and `$(d)/gotest.junit.xml` to `CLEAN`, defines `$(d)/gotest.junit.xml` as generated from `test/bin/gotestsum` and `$(d)/gotest.json`, then runs `gotestsum --no-color --junitfile $@ --raw-command cat $(@D)/gotest.json`.

State and persistence: consumes JSON test output and writes JUnit XML beside it; both artifacts are cleanable.

Dependencies and integration points: depends on the repository make system, `gotestsum`, and the `test_unit` pipeline that produces `gotest.json`.

Risks and test signals: failures indicate missing `gotestsum`, malformed JSON, or changed make directory variables. The target is a reporting bridge for CI systems expecting JUnit XML.
