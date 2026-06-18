# sources/cloud-native/moby/integration/secret/secret_test.go

## Purpose
Integration coverage for Docker Swarm secret APIs and templated secrets. It tests inspect/list/filter/create/delete/update semantics, immutable data constraints, template rendering with referenced secrets/configs, tmpfs mount behavior, and name/ID resolution edge cases.

## Important APIs, Types, And Functions
Uses `swarm.NewSwarm`, `client.SecretCreate`, `SecretInspect`, `SecretList`, `SecretRemove`, `SecretUpdate`, `ConfigCreate`, service helpers from `integration/internal/swarm`, `stdcopy.StdCopy`, and containerd errdefs predicates. Helpers `createSecret` and `namesFromList` centralize secret creation and sorted name extraction.

## Control Flow
Each test creates a swarm-backed daemon and client. `TestSecretInspect` creates and inspects a secret and compares raw JSON unmarshalling. `TestSecretList` verifies empty list, creates labeled secrets, then applies name/id/label filters. `TestSecretsCreateAndDelete` checks duplicate conflict, removal, not-found errors, and labels. `TestSecretsUpdate` updates labels by full ID, full name, and ID prefix, then asserts data updates are rejected. `TestTemplatedSecret` creates referenced secret/config plus a templated secret using `golang` templating, creates a service mounting all references, waits for a running task, execs `cat` and `mount`, and checks rendered content plus tmpfs mount. `TestSecretCreateResolve` ensures removal resolves full ID before a secret whose name equals that ID, and does not resolve partial names as IDs.

## State And Persistence Behavior
Secret and config objects persist in swarm state during each test. Update behavior is constrained to labels; secret data is intentionally immutable. Service task mounts expose rendered secret content as tmpfs under `/run/secrets`.

## Dependencies And Integration Points
Depends on Swarm mode, secret/config API types, service scheduling, task exec, stdcopy stream decoding, errdefs classification, Linux tmpfs mounts, and polling for running tasks.

## Risks
Swarm scheduling and task startup introduce timing risk. Template rendering depends on referenced target names matching. The prefix-resolution test is subtle because it distinguishes full name, full ID, and partial ID rules.

## Test Signals
Signals include exact errdefs conflict/not-found/invalid-argument checks, sorted list equality, label value checks, rendered secret content equality, empty stderr, mount output containing tmpfs, and final list counts after resolution operations.
