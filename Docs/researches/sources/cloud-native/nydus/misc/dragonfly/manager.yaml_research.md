<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/manager.yaml -->
# sources/cloud-native/nydus/misc/dragonfly/manager.yaml

## Purpose

This YAML configures a minimal Dragonfly Manager for local E2E testing.

## Important APIs, Types, and Functions

It sets gRPC port 65003, REST address `:8080`, log/cache directories, JWT settings, MySQL connection parameters, Redis address, migration enablement, and console mode.

## Control Flow

Dragonfly Manager reads the config at startup, opens gRPC/REST endpoints, connects to local MySQL and Redis, and performs database migrations when enabled.

## State and Persistence Behavior

Logs/cache are under `/tmp/dragonfly`; persistent manager state is in MySQL database `manager` and Redis at localhost.

## Dependencies and Integration Points

It is paired with local scheduler and dfdaemon configs. Scheduler and dfdaemon use the manager gRPC address to register and coordinate.

## Risks and Test Signals

Credentials are fixed local-test values (`root`/`dragonfly`), JWT key is static, and ports may conflict. This is an E2E fixture, not a production config.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/manager.yaml -->
