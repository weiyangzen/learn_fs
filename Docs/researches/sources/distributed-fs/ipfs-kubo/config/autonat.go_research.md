# Research: sources/distributed-fs/ipfs-kubo/config/autonat.go

Purpose: Defines configuration for libp2p AutoNAT service mode and dialback throttling.

Important APIs/types/functions: `AutoNATServiceMode` enum values `Unset`, `Enabled`, `Disabled`, and `EnabledV1Only`; text marshal/unmarshal methods; `AutoNATConfig`; `AutoNATThrottleConfig`.

Control flow, state, and persistence: JSON/text decoding maps `""`, `"enabled"`, `"disabled"`, and `"legacy-v1"` to enum values. Unknown values error. Throttle config stores global/per-peer limits and an optional interval; semantics are applied by node construction, not this file.

Dependencies and integration points: Integrated into top-level `Config` and used by libp2p host/node setup. Low-power profile sets `ServiceMode` disabled.

Risks and test signals: `MarshalText` for unset returns nil bytes, which relies on encoding behavior for omitempty/defaults. Typoed modes fail during config decode. No direct tests in this subset.
