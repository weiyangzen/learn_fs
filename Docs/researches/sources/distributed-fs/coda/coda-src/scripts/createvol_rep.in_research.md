# sources/distributed-fs/coda/coda-src/scripts/createvol_rep.in

Purpose: creates a replicated Coda volume on the SCM across one to eight servers/partitions and updates VLDB/VRDB metadata.

Control flow: loads `server.conf`, requires current host to match `$vicedir/db/scm`, validates args and volume-name length, migrates old `VRList`/`maxgroupid` locations, dumps current VRDB to `VRList.new`, rejects existing replicated/nonreplicated names by querying each server's volume list, validates partitions, allocates or accepts a 0x7f-style group id, calls `volutil create_rep` for each replica, disables resolution for singly replicated volumes, rebuilds VLDB with `bldvldb.sh`, appends a padded eight-replica VRList entry, runs `volutil makevrdb`, swaps `VRList.new` into place with backup, and calls `volutil updatedb`.

State/persistence: creates actual server volumes, modifies `$vicedir/db/VRList`, `maxgroupid`, `files`, VRDB, VLDB, and temporary files under `/tmp`.

Dependencies, risks, tests: depends on `volutil`, `bldvldb.sh`, SCM identity files, server/partition listings, and shell/awk/sed parsing. Risks include no rollback after partial replica creation, unanchored regex lookups, `/tmp` predictable names, inconsistent `VRList` if `makevrdb` succeeds but moves fail, and lower/upper group id detection by prefix only. Test duplicate detection, multi-partition validation, partial create failure recovery, single-replica resolution disable, and VRList padding to eight replica slots.
