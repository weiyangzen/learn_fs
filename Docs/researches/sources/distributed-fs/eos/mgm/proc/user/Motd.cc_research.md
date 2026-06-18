# sources/distributed-fs/eos/mgm/proc/user/Motd.cc

Purpose: implements `ProcCommand::Motd()` for reading and, for admins, updating the MGM message-of-the-day file.

Important APIs and types: uses `mgm.motd`, `gOFS->MgmMetaLogDir`, `SymKey::Base64Decode`, POSIX `open`, `write`, `read`, and admin checks against root or admin UID/GID.

Control flow: builds the motd file path under the MGM meta log directory. If a base64 payload is supplied by root/admin, it decodes and writes it to the existing motd file. It then opens the motd file for reading and appends up to 64 KiB to stdout.

State and persistence: persists MOTD contents in the local file `${MgmMetaLogDir}/motd`. Reads are local filesystem reads.

Dependencies and integration: integrates with MGM stats and local deployment filesystem state rather than namespace metadata.

Risks: update opens with `O_WRONLY` only and does not create or truncate the file, so shorter updates may leave trailing content. It checks only zero bytes written, not partial writes. The read path sets `buffer[65535] = 0` regardless of bytes read and appends as a C string. Tests should cover admin-only update, invalid base64, missing motd file, shorter replacement content, partial-write handling, and maximum read length.
