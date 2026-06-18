## sources/distributed-fs/eos/mgm/commandmap/CommandMap.hh

Purpose: declares the `FsctlCommand` enum and lookup function for command dispatch. It is the typed command vocabulary for MGM FSctl string commands.

Important API/types: `enum class FsctlCommand` with `INVALID` plus command values including access, chmod/chown, event, stat/statvfs, symlink, txstate, and version. `lookupFsctl(const std::string&)` maps user/proc strings to enum values.

Integration: used by FSctl/proc command dispatch code. Risks include enum values that are documented “not used anymore” and values that must stay synchronized with `CommandMap.cc`. Tests should enforce string coverage for all active commands.
