# Research: sources/cloud-native/moby/daemon/cluster/filters.go

## sources/cloud-native/moby/daemon/cluster/filters.go

Purpose: converts daemon filter arguments into SwarmKit list request filters for nodes, tasks, secrets, and configs. It also validates accepted filter keys.

Important APIs are `newListNodesFilters`, `newListTasksFilters`, `newListSecretsFilters`, and `newListConfigsFilters`. Node filters support name, id, label, role, membership, and node.label; role and membership strings are uppercased and mapped to SwarmKit enums. Task filters support name, id, label, service, node, desired-state, internal `_up-to-date`, and runtime, with an optional transform callback used by `tasks.go` to resolve service/node names to IDs and add default runtimes. Secret and config filters accept name/id/label, with secrets also accepting `names`.

State is none; filter arguments may be mutated by the transform callback. Dependencies include daemon internal filters and SwarmKit API protobuf filter structs. Risks include enum string mismatch, API-visible validation errors for unsupported filters, and `convertKVStringsToMap` treating labels without `=` as keys with empty values. Tests cover accepted and rejected secret/config filter keys, while node/task enum paths are less directly tested here.
