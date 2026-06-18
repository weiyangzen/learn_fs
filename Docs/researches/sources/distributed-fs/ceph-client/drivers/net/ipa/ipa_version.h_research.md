# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_version.h

Purpose: Defines the enumerated IPA hardware versions, their paired GSI version comments, and execution-environment IDs shared across IPA/GSI register maps and driver logic.

Important APIs and types: `enum ipa_version` lists IPA versions from `IPA_VERSION_3_0` through `IPA_VERSION_5_5`, ending with `IPA_VERSION_COUNT`. `enum gsi_ee_id` defines AP, modem, microcontroller, and TrustZone execution environments as `GSI_EE_AP`, `GSI_EE_MODEM`, `GSI_EE_UC`, and `GSI_EE_TZ`.

Control flow and integration: Version values select IPA and GSI register maps, hardware data tables, feature branches such as table hash support and cache/register layout, and endpoint/route ownership behavior. Execution-environment IDs are embedded in register offsets and ownership comparisons throughout IPA/GSI code.

State and persistence: The header owns no runtime state. The enum ordering is a persistent internal ABI because comparisons such as `version < IPA_VERSION_5_0` encode feature boundaries.

Dependencies: Only depends on Linux types, but many IPA and GSI translation units depend on these definitions.

Risks: Adding a version requires updating string conversion, register-map selection, hardware data, feature gates, and any range comparisons. Incorrect enum ordering can silently break feature tests. GSI version comments are documentation only and must be kept aligned with platform data.

Test signals: Build all register-map references for each version; probe supported platforms; exercise version boundary logic around IPA v4.2 hash absence and IPA v5.0 cache/register changes.
