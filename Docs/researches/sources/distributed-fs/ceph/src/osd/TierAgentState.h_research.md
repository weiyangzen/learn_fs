# sources/distributed-fs/ceph/src/osd/TierAgentState.h

## Purpose
`TierAgentState.h` declares the state container used by `PrimaryLogPG` cache-tiering agent work. It tracks where the agent is scanning, what recent hit-set/temperature information it has, and which flush/evict modes are active.

## Important APIs, Types, And Functions
`TierAgentState` stores `position`, `started`, `start`, `delaying`, a power-of-two temperature histogram, histogram age, archived `HitSetRef` values keyed by time, recent clean objects, flush mode, evict mode, and `evict_effort`. It defines `flush_mode_t` values `FLUSH_MODE_IDLE`, `FLUSH_MODE_LOW`, and `FLUSH_MODE_HIGH`, plus `evict_mode_t` values `EVICT_MODE_IDLE`, `EVICT_MODE_SOME`, and `EVICT_MODE_FULL`. Helper methods stringify modes, test idleness, manage hit sets, and dump state.

## Control Flow
`PrimaryLogPG` agent logic mutates this structure as it chooses agent modes, loads hit sets, estimates object temperature, flushes dirty objects, and evicts clean or cold objects. `is_idle()` reports no agent work only when not delaying and both flush and evict modes are idle. Hit-set methods add archived sets, remove the oldest, or discard all on reset.

## State And Persistence Behavior
This type is in-memory state only. Persistent tiering inputs and effects are elsewhere: hit-set objects, object dirty/clean state, and flush/evict transactions. The dump method exposes current mode, effort, scan position, and histogram for diagnostics.

## Dependencies And Integration Points
The header depends on Ceph formatter, histogram, `hobject_t`, and `HitSet`. It is included by `PrimaryLogPG.h`, where `agent_state` is a scoped pointer and the agent methods consume its fields.

## Risks And Test Signals
Risk is mostly policy drift: wrong idle semantics can stall or overrun tier-agent work, and stale hit sets can bias eviction decisions. Tests should cover mode transitions in `PrimaryLogPG`, dump output, hit-set trimming, delayed state, and cache-tiering integration under full/nearfull pool conditions.
