<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/dfdaemon.yaml -->
# sources/cloud-native/nydus/misc/dragonfly/dfdaemon.yaml

## Purpose

This YAML is a minimal Dragonfly dfdaemon configuration for local end-to-end tests with Nydus proxy-backed image access.

## Important APIs, Types, and Functions

It configures scheduler cluster ID, manager address, seed peer mode, upload/proxy ports, storage/log/cache directories, download socket path, dynamic config refresh, and console mode.

## Control Flow

Dragonfly dfdaemon reads this config at startup, connects to the local manager on port 65003, exposes proxy server port 4001, upload server port 4000, and a Unix download socket.

## State and Persistence Behavior

Runtime data is stored under `/tmp/dragonfly/storage`, `/tmp/dragonfly/cache/dfdaemon`, and `/tmp/dragonfly/logs/dfdaemon`.

## Dependencies and Integration Points

It integrates with the matching local Dragonfly manager and scheduler configs and with Nydus configs that point proxy URL/ping URL to `127.0.0.1:4001`.

## Risks and Test Signals

The config is local-test oriented and assumes writable `/tmp`, local manager availability, and no port conflicts. It is not hardened for production authentication or persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/dfdaemon.yaml -->
