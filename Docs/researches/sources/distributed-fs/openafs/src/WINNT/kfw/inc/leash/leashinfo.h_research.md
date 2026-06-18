## sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leashinfo.h

Purpose: Defines resource/configuration identifiers used by Leash for time-host and default ticket-life settings.

Important APIs/types/functions: Defines `LSH_TIME_HOST = 1970` and `LSH_DEFAULT_TICKET_LIFE = 1971`.

Control flow: No executable logic. Consumers use these numeric IDs to load or store Leash settings/resources.

State and persistence: No state in the header. The IDs point to settings that are likely persisted by Leash configuration code elsewhere.

Dependencies and integration points: Integrated with Leash resource and configuration handling.

Risks: No include guard and very generic numeric constants can collide if included in broad resource contexts. Changing values breaks compatibility with existing resources/configuration.

Test signals: Resource compile tests and Leash configuration tests that read/write time-host and default lifetime by these IDs.
