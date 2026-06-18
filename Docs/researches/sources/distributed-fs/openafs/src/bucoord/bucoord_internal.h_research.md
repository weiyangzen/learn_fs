# sources/distributed-fs/openafs/src/bucoord/bucoord_internal.h

`bucoord_internal.h` declares internal cross-module functions and globals for the `backup` command implementation. It is broader than the public prototype header and covers command handlers, config parsing, dump/restore orchestration, text-database operations, tape host and volume set persistence, VLDB interaction, status management, regex, and globals.

Important API groups include status watcher/job/wait functions; command utility and command handler prototypes; config host operations; volume set and dump schedule CRUD/parsing; butc connection and dump/restore/tape commands; update/save functions for dump schedules, tape hosts, and volume sets; ubik backup database wrappers; VLDB/volume helpers; and globals `localauth`, `nobutcauth`, `tcell`, and `tokenExpires`.

There is no runtime control flow or persistence in the header, but it defines contracts for modules that read/write bucoord config text, interact with budb/ubik/vldb/butc, and manage status queues. Dependencies include many structs from generated `bc.h`, `budb`, `ubik_client`, `rx_connection`, `cmd`, socket, FILE, and status types.

Risks include a large shared namespace, duplicate declarations also present in `bucoord_prototypes.h`, pointer ownership ambiguity, historical regex prototypes, and difficulty enforcing module boundaries. Test signals are compile/link coverage across all bucoord objects, generated-header ordering, and warnings for prototype mismatches.
