# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetClientStatsV2Msg.h

## Purpose
Defines `GetClientStatsV2Msg`, a BeeGFS node and target management query/request message using `NETMSGTYPE_GetClientStatsV2`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetClientStatsV2Msg` derives from `public NetMessageSerdes<GetClientStatsV2Msg>` and uses `BaseType(NETMSGTYPE_GetClientStatsV2)` or an equivalent base constructor. Constructors include `GetClientStatsV2Msg(uint128_t cookie) : BaseType(NETMSGTYPE_GetClientStatsV2), cookie(cookie)`; `GetClientStatsV2Msg() : BaseType(NETMSGTYPE_GetClientStatsV2)`. Serialization writes `cookie`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getCookieIP()`. Declared payload/backing members include `uint128_t cookie`.

## Control Flow
Sender-side code builds `GetClientStatsV2Msg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/net/message/SimpleInt64Msg.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetClientStatsV2`. Feature flags: `GETCLIENTSTATSMSG_FLAG_PERUSERSTATS`=1.

## Risks And Edge Cases
Feature flag mismatches change the expected wire layout.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetClientStatsV2`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior.
