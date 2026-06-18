# sources/distributed-fs/coda/coda-src/al/prs.h

Purpose: Defines Protection Server (PRS) constants, CPS representation, and filesystem rights bit masks shared by AL and auth/server code.

Important APIs/types: `PRS_VERSION`, `PRS_MAXNAMELEN`, well-known group names `PRS_ANYUSERGROUP` and `PRS_ADMINGROUP`, `PRS_InternalCPS`, `PRS_ExternalCPS`, and rights constants `PRSFS_READ` through `PRSFS_ALL`.

Control flow and state model: `PRS_InternalCPS` is a flexible-array style structure where leading `InclEntries` are sorted included IDs and trailing `ExclEntries` are excluded IDs. `PRS_ExternalCPS` is an ASCII string representation starting with a count.

Persistence and integration: The definitions are consumed by AL, auth2, and server authorization code. Rights bits map directly onto directory privileges.

Risks and test signals: The one-element array idiom requires callers to allocate enough memory for all IDs. The header documents exclusion entries, but current `AL_GetInternalCPS` fills only inclusions from PDB CPS arrays.
