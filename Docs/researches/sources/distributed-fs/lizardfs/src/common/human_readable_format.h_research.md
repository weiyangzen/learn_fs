# sources/distributed-fs/lizardfs/src/common/human_readable_format.h

Purpose: declares user-facing formatting utilities.

Important APIs/types/functions: `convertToSi`, `convertToIec`, `ipToString`, `timeToString`, and `bpsToString`.

Control flow: callers pass raw numeric values and receive display strings.

State and persistence: none.

Dependencies and integration: includes `platform.h`, `<cstdint>`, `<ctime>`, and `<string>`. Used by reporting surfaces where raw counters need compact text.

Risks: units and rounding are fixed by implementation; callers needing locale-aware or exact formatting need a different API.

Test signals: implementation tests cover byte formatting; IP/time/bps are not directly tested in this subset.
