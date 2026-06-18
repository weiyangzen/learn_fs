# sources/distributed-fs/lizardfs/src/master/personality.cc

## Purpose

`personality.cc` implements metadata server personality state: master versus shadow, with special validation and promotion behavior for HA-cluster-managed installations. The file was read as a complete 188-line implementation.

## Important APIs, Types, and Functions

Exports in namespace `metadataserver` are `getPersonality`, `setPersonality`, `registerFunctionCalledOnPromotion`, `promoteToMaster`, `personality_reload`, `promoteAutoToMaster`, `personality_validate`, `personality_init`, and `isMaster`. Static state includes `gPersonality` and `gChangePersonalityReloadFunctions`. Helpers parse `PERSONALITY`, command-line extra arguments, and the `ha-cluster-managed` mode.

## Control Flow

Initialization registers reload handling outside `METARESTORE`, validates mutually exclusive initial-personality arguments, and derives master/shadow state from either HA-managed command-line arguments or non-HA config. Reload refuses switching between HA-managed and non-HA-managed modes; in non-HA mode it permits shadow-to-master promotion but rejects master-to-shadow. Promotion logs, calls registered promotion hooks, then sets personality to master. `promoteAutoToMaster` only promotes a HA-managed shadow.

## State and Persistence Behavior

Personality is in-process global state. The persistent source of desired personality is the configuration file plus process command-line arguments. Promotion callbacks let services reconfigure event-loop behavior after a transition, but no durable promotion marker is written here.

## Dependencies and Integration Points

The module integrates with config (`cfg_get`, `cfg_filename`), command-line argument inspection, reload events, logging, and services that register promotion callbacks such as metalogger and tapeserver services.

## Risks and Edge Cases

`setPersonality` itself does not enforce the documented forbidden master-to-shadow transition; policy is enforced by higher-level reload/init code. HA-managed mode requires exact coordination between config and command-line option. Promotion callback order is registration order and callbacks are raw function pointers. Reload errors are logged but intentionally do not abort the running instance.

## Test Signals

Tests should cover config strings case-insensitively, invalid personalities, HA/non-HA mismatch exceptions, mutually exclusive initial options, shadow-to-master callback execution, forbidden master-to-shadow reload logging, and `promoteAutoToMaster` behavior.
