# sources/distributed-fs/ceph/src/mds/Mantle.h

## Purpose
Declares the Lua-based MDS balancer wrapper used to evaluate balancer policy scripts against per-rank metric maps.

## Important APIs, Types, And Functions
`Mantle` owns `lua_State *L`, constructs it, closes it in the destructor, and exposes `balance(script, whoami, metrics, my_targets)`. Output maps target ranks to double weights.

## Control Flow
Balancer code constructs a Mantle instance and calls `balance` for policy decisions. Implementation handles Lua script loading, metric publication, execution, and parsing.

## State And Persistence Behavior
Only the Lua VM pointer is stored. There is no encoded or durable state in this class.

## Dependencies And Integration Points
Depends on Lua headers, STL containers, and CephFS rank types. Integrates with MDS balancer policy execution and metrics collection.

## Risks
Raw `lua_State*` ownership is protected but copy operations are not explicitly disabled; accidental copies could double-close. Script runtime limits are not represented in the API.

## Test Signals
Construct/destroy lifecycle, no-copy usage expectations, successful balance calls, invalid script handling, and integration with balancer failure fallback.
