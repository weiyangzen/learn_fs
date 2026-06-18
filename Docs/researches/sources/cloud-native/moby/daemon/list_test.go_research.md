## sources/cloud-native/moby/daemon/list_test.go

Purpose: Unit tests for core container listing behavior using an in-memory container view database.

Important helpers and tests: `TestMain` creates a temporary root. `setupContainerWithName` constructs a base container with a UUID, digest-derived image ID, running state, host config, image config, creation time, saves it to `containersReplica`, and reserves its name. `containerListContainsName` searches summary names. `TestContainerList` checks empty through 100-container cases and descending creation order. `TestContainerList_InvalidFilter` rejects unknown filters. `TestContainerList_NameFilter` validates regex and exact names with and without slash prefixes. `TestContainerList_LimitFilter` checks zero, negative, smaller, equal, and larger limits.

Control flow and state: Tests replace the view DB per case to avoid cross-contamination. Creation timestamps are separated by milliseconds so sort order is deterministic.

Dependencies and integration points: Exercises `Daemon.Containers`, `container.NewViewDB`, name reservation, filter parsing, and image refresh prerequisites. It avoids real image service calls by setting `Config.Image` equal to `ImageID`.

Risks covered: Protects ordering, name-filter slash normalization, accepted filter validation, and limit handling. Remaining filters such as ancestor, before/since, health, volumes, ports, network, size, and isolation are not exercised here.
