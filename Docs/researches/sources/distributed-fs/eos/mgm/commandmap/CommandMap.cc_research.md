## sources/distributed-fs/eos/mgm/commandmap/CommandMap.cc

Purpose: implements string-to-enum lookup for MGM FSctl commands. A file-scope `std::map` is populated by a static initializer object.

Important behavior: `fsctlMapInit` inserts supported command strings such as `access`, `event`, `mkdir`, `stat`, `txstate`, and `version`. `lookupFsctl(cmd)` returns the matching `FsctlCommand` or `INVALID`.

State/dependencies: anonymous-namespace static map initialized before use in the translation unit. Risks include static initialization order only being safe because all access is through this file, omitted enum values (`schedule2balance`, `schedule2delete`) intentionally not mapped, and map mutability despite being effectively constant. Tests should cover known commands, unknown commands, and enum/map drift.
