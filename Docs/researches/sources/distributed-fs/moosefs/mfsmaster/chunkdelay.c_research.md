# sources/distributed-fs/moosefs/mfsmaster/chunkdelay.c

`chunkdelay.c` temporarily protects chunks from deletion after representation-changing operations such as COPY-to-EC or EC-to-COPY replication. It gives chunk state time to settle before allowing destructive cleanup and schedules extra chunk work when protection expires.

`chunk_prot` stores a `chunkid`, timestamp, and next pointer in a 4096-bucket hash table keyed by `chunkid ^ (chunkid >> 16)`. `ProtectionDelay` comes from `CHUNK_PROTECTION_SECONDS`. `chunk_group` batches up to 128 expired chunk IDs for follow-up jobs. Public functions are `chunk_delay_protect`, `chunk_delay_is_protected`, and `chunk_delay_init`.

`chunk_delay_protect` inserts or refreshes a timestamp. `chunk_delay_is_protected` returns true while the window is active and removes expired entries lazily. `chunk_delay_remove_old` scans ten buckets per timer tick, removes expired entries, batches their IDs, and calls `chunk_do_extra_job`. `chunk_delay_init` clears the table, loads config, registers a 10 ms scanner, and registers reload.

Protection state is volatile and not serialized, so restart clears all delay windows. Integration is with `chunks.c`, where chunks are protected after representation changes and the module is initialized from chunk startup. Dependencies are `clocks`, `chunks`, `main`, and `cfg`.

Risks include unchecked allocation, restart losing protection state, bad configuration making the delay too short or too long, and full-table cleanup latency depending on timer cadence. Test signals are protect/refresh behavior, expiry, lazy removal, scanner-triggered `chunk_do_extra_job`, config reload, and hash-collision handling.
