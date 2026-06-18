# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsMsg.h

## Purpose
Defines `GetClientStatsMsg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetClientStats`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetClientStatsMsg` derives from `public SimpleInt64Msg` and uses `BaseType(NETMSGTYPE_GetClientStats)` or an equivalent base constructor. Constructors include `GetClientStatsMsg(int64_t cookie) : SimpleInt64Msg(NETMSGTYPE_GetClientStats, cookie)`; `GetClientStatsMsg() : SimpleInt64Msg(NETMSGTYPE_GetClientStats)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getCookieIP()`, `getValue()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `GetClientStatsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/SimpleInt64Msg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetClientStats`. Feature flags: `GETCLIENTSTATSMSG_FLAG_PERUSERSTATS`=1.

## Risks And Edge Cases
Feature flag mismatches change the expected wire layout.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetClientStats`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior.
