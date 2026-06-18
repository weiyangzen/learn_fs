# Research: sources/cloud-native/moby/daemon/cluster/tasks.go

## sources/cloud-native/moby/daemon/cluster/tasks.go

Purpose: implements task list and inspect operations for the swarm backend.

Important APIs: `GetTasks` and `GetTask`. `GetTasks` builds a transform callback that resolves service filters and node filters to SwarmKit IDs, defaults runtime filtering to container plus empty runtime when no runtime filter is supplied, validates/builds task filters with `newListTasksFilters`, lists tasks through SwarmKit with a large receive limit, and converts each task with `convert.TaskFromGRPC`. `GetTask` resolves a single task with `getTask` and converts it.

State is remote SwarmKit task state. Dependencies include daemon internal filters, swarmbackend option types, cluster helper lookups, convert package, SwarmKit control client, and gRPC receive-size settings. Risks include mutation of filter args during transform, lookup failures for service/node names, runtime default behavior hiding non-container runtimes unless requested, and version/manager availability handled by `lockedManagerAction`. Tests are indirect.
