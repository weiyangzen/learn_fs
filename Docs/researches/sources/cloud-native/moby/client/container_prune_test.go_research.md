<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_prune_test.go -->
# sources/cloud-native/moby/client/container_prune_test.go

Purpose: validates container prune request filtering and result decoding.

Important coverage: daemon internal errors, `POST /containers/prune`, empty and populated `filters` JSON, dangling/until/label cases, and returned deleted IDs/space reclaimed.

Control flow and dependencies: table-driven mock callbacks inspect query values and return JSON prune reports.

State and risks: no persistence. This is high-signal because prune is destructive and filter mistakes can broaden deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_prune_test.go -->
