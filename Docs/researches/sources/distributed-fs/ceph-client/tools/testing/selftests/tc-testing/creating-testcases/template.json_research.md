# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/template.json

## Purpose
Provides blank templates for authoring tc-testing JSON cases, including simple command cases and cases with accepted setup/teardown exit-code lists.

## Important APIs, Types, And Functions
Shows required schema fields: `id`, `name`, `category`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern`, `matchCount`, and `teardown`. The second template demonstrates command entries represented as arrays with the command string followed by acceptable exit codes.

## Control Flow
No meaningful test flow is encoded because values are placeholders. It documents how the runner interprets setup and teardown lists before and after command/verify phases.

## State And Persistence
No real state.

## Dependencies And Integration Points
Used by test authors creating new files under `tc-tests`.

## Risks
Placeholders must not be run as real tests. The schema shown is regex-oriented and does not cover plugin, scapy, or `matchJSON` fields except by implication from other examples.

## Test Signals
As documentation, the signal is that new tests copied from this template load successfully after placeholders are filled.
