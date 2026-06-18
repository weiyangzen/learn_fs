# sources/distributed-fs/coda/coda-src/librepair/repio.cc

Purpose: implements serialization, parsing, and printing of directory repair operation lists used by Coda manual/automatic repair. It supports a binary transfer format (`repair_putdfile`, overloaded `repair_getdfile`) and an ASCII command format (`repair_parseline`, `repair_parsefile`, `repair_printline`, `repair_printfile`).

APIs and flow: binary output writes replica count, per-replica volume/repair counts, then each `struct repair` opcode, newline-terminated names, new names, and `REPAIR_MAX` network-order parameters. Binary input reverses that into allocated `listhdr` arrays. ASCII parsing recognizes create/remove/ACL/status/replica/rename opcodes, unquotes names via `urlquote`, decodes ACL rights, and grows replica/repair arrays one element at a time.

State and dependencies: depends on `repio.h`, `vice.h`, RPC2/PRS rights, and Coda assertions. It allocates caller-owned arrays and mutates parse input lines. Risks include unchecked `fwrite` paths, debug-looking `perror` calls on success paths, possible underflow when stripping newlines from empty `fgets` results, and no cleanup of partially allocated data on parse/read errors. Test signal is mostly indirect through repair tools and `restest.cc`; no local unit test covers malformed binary input.
