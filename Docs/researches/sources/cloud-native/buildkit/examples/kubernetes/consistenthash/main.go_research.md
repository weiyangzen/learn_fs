# Research: sources/cloud-native/buildkit/examples/kubernetes/consistenthash/main.go

## Purpose
Utility for selecting a BuildKit Kubernetes pod with consistent hashing.

## Important APIs, Types, and Functions
`xmain` reads stdin and argv; `doConsistentHash` builds a `hashring` and returns a node; `main` logs/exits.

## Control Flow
Reads pod names, validates a key, creates a ring from names, prints the selected pod.

## State and Persistence
No persistence; ring is rebuilt per invocation from live stdin.

## Dependencies and Integration Points
Depends on `serialx/hashring`, logrus, and pkg/errors. Pairs with `show-running-pods.sh` to route clients to stable BuildKit pods.

## Risks and Edge Cases
Empty/changing pod sets change routing; determinism only holds for the same node list.

## Test Signals
No direct tests; CLI behavior is small and library-backed.
