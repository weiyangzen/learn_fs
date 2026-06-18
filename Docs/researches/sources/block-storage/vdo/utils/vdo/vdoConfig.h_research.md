# File Research: sources/block-storage/vdo/utils/vdo/vdoConfig.h

Declares VDO formatting and configuration helper APIs.

Key details:
- Exposes recovery-journal initialization, full formatting, minimum-size calculation, layout initialization, UDS index block computation, geometry initialization, deterministic nonce/UUID formatting, force rebuild, and offline read-only marking.
- Notes that `initializeLayoutFromConfig()` is exposed for testing.
- Pulls in UDS `indexer.h`, VDO `encodings.h`, and core types.

Research relevance:
- This header is the main entry point for tools such as `vdoformat`, `vdocalculatesize`, `vdoforcerebuild`, and `vdoreadonly`.
