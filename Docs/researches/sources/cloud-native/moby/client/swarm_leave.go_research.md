# sources/cloud-native/moby/client/swarm_leave.go

## Purpose
Implements leaving a swarm, optionally forcing removal when the daemon is a manager.

## APIs, Types, And Functions
`SwarmLeaveOptions` contains `Force`; `SwarmLeaveResult` is empty; `Client.SwarmLeave` posts to the daemon with a `force` query value when requested.

## Control Flow, State, And Integration
The method builds `force=1` only for forced leave and sends `POST /swarm/leave`. Successful calls mutate daemon swarm membership and may remove cluster participation state.

## Risks And Test Signals
Risks include accidentally omitting the force flag or using the wrong HTTP method. Integration is with node demotion/leave workflows and daemon swarm state cleanup.
