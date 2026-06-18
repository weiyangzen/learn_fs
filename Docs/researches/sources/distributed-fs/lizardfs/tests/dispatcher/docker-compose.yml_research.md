# sources/distributed-fs/lizardfs/tests/dispatcher/docker-compose.yml

## Purpose
This compose file runs the dispatcher Flask service for CI or local distributed test scheduling.

## Important APIs, Types, and Functions
It defines one service, `flask`, built from the dispatcher directory, mapping host `${EXTERNAL_PORT}` to container `5000`, with `restart: unless-stopped`.

## Control Flow
`docker compose up` builds the local Dockerfile and starts the service. Agents can point `TESTS_DISPATCHER_URL` at the chosen external port.

## State and Persistence Behavior
No volumes are declared, so dispatcher state is container memory only and is lost on restart/recreate.

## Dependencies and Integration Points
It depends on Docker Compose variable substitution for `EXTERNAL_PORT` and the dispatcher Dockerfile.

## Risks and Edge Cases
Missing `EXTERNAL_PORT` prevents predictable port binding. Restarting the service during a run loses queues. The service is exposed without auth.

## Test Signals
Compose validation should include config rendering with `EXTERNAL_PORT`, container startup, and a simple push/next-test HTTP round trip.
