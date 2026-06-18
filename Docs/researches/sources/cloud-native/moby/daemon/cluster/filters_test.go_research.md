# Research: sources/cloud-native/moby/daemon/cluster/filters_test.go

## sources/cloud-native/moby/daemon/cluster/filters_test.go

Purpose: verifies filter validation for list secrets and list configs. It focuses on accepted filter names and rejection of unsupported filter keys.

`TestNewListSecretsFilters` covers `name`, `id`, `label`, `names`, combined filters, and invalid `nonexist`. `TestNewListConfigsFilters` covers `name`, `id`, `label`, combined filters, and invalid `nonexist`. Control flow is direct loops over valid and invalid `filters.Args`.

State is none. Dependencies are daemon internal filters and the functions in `filters.go`. The tests signal that the API contract for these filters is intentionally narrow. Gaps include checking converted protobuf fields, label map conversion, node/task filters, enum validation, and transform callback behavior.
