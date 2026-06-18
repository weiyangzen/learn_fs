# sources/distributed-fs/coda/coda-src/librepair/repio.h

Purpose: defines the repair operation wire/in-memory contract shared by librepair parsers, resolution code, and repair executors. `struct repair` carries an opcode, name, optional rename target, and five overloaded integer parameters.

Important types/APIs: opcodes cover file/directory/symlink/link creation, removal, positive/negative ACL updates, mode/owner/mtime changes, ASCII-only replica markers, and rename. `struct listhdr` groups repair operations per replica FID. Prototypes expose binary I/O, ASCII parsing, and printing.

State and integration: no state is stored in the header, but the constants and field overloading are a cross-module ABI. `resolve.cc` fills `listhdr` arrays; `repio.cc` serializes them; repair clients/servers interpret the opcode/parameter layout. Risks are typical of untagged unions: consumers must know which parameter indexes are meaningful for each opcode, and `MAXNAMELEN` is locally defined if absent. Test signals come from any parser/repair workflow that round-trips `listhdr` content.
