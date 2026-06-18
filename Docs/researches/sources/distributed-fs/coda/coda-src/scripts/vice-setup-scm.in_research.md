# sources/distributed-fs/coda/coda-src/scripts/vice-setup-scm.in

Purpose: SCM-specific server setup step that initializes server identity metadata.

Control flow: loads `server.conf`, defaults `vicedir`, writes initial maximum replicated volume id `2130706432` (`0x7f000000`) to `$vicedir/db/maxgroupid`, determines the SCM hostname from exported `hn`, Linux `hostname -f`, or prompted domain plus short hostname, changes to `$vicedir/db`, prompts for a unique server id, appends `<hostname> <id>` to `servers`, and writes hostname to `$vicedir/db/scm`.

State/persistence: creates/overwrites `maxgroupid`, appends to `servers`, and writes `scm`.

Dependencies, risks, tests: depends on `codaconfedit`, hostname resolution, and interactive input. Risks include no validation that server id is numeric/range/unique despite prompt text, appending duplicates, and overwriting maxgroupid on rerun. Test fresh setup, rerun duplicate handling, non-Linux domain prompt, and correct exported `hn` propagation from `vice-setup`.
