# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/ingress.json

## Purpose
Defines six TDC cases for the special `ingress` qdisc. It covers adding ingress, rejecting unsupported arguments, duplicate add behavior, deleting missing ingress instances, double deletion, and class display.

## Important APIs, Types, and Functions
The file uses the standard TDC JSON case schema. `cmdUnderTest` entries call `$TC qdisc add|del|show dev $DEV0 ingress` and related class show commands; expected failures are represented by nonzero `expExitCode` and matching error text.

## Control Flow
The harness prepares a network namespace device, runs each ingress operation, checks exit status, then verifies via `tc qdisc show` or class output. Negative cases intentionally execute commands on absent or duplicate ingress state to confirm kernel/iproute2 validation.

## State and Persistence Behavior
Ingress attaches to a fixed ingress hook on the device and cannot be stacked like ordinary classful qdiscs. Teardown removes it when created; missing-qdisc cases leave no intended state.

## Dependencies and Integration Points
Depends on kernel ingress qdisc support and the TDC namespace plugin. Integration points are the `tc` ingress parser, qdisc creation path, duplicate detector, delete path, and class dump path.

## Risks and Edge Cases
Because ingress is a singleton per device, ordering and teardown are critical. Error strings can vary between iproute2/kernel versions, and class show behavior for ingress may be easy to regress because it is not a normal classful scheduler.

## Test Signals
Expected signals are successful ingress creation, duplicate/missing deletes returning the configured failure code, unsupported argument rejection, and a non-empty class show for ingress.
