# sources/distributed-fs/ceph-client/include/trace/events/nilfs2.h

Purpose: Provides NILFS2 filesystem tracepoints for segment construction, transaction transitions, segment usage accounting, and metadata block operations. It is aimed at debugging the log-structured write path.

Important APIs/types/functions: Events include `nilfs2_collection_stage_transition`, `nilfs2_transaction_transition`, `nilfs2_segment_usage_check`, `nilfs2_segment_usage_allocated`, `nilfs2_segment_usage_freed`, `nilfs2_mdt_insert_new_block`, and `nilfs2_mdt_submit_block`. Fields include superblock device, collection stage, mode, transaction state, segment number, segment usage checks, inode numbers, block numbers, level, and mode flags.

Control flow: NILFS2 emits collection and transaction events as the segment constructor changes stages and transaction modes. Segment usage events fire when segments are checked, allocated, or freed. Metadata tracepoints track insertion/submission of metadata blocks.

State and persistence: The header stores no state. It observes in-memory NILFS2 transaction and segment metadata that corresponds to persistent log segments on disk.

Dependencies and integration points: Depends on tracepoints and NILFS2 structs supplied by including sources. It integrates with filesystem writeback, cleaner/segment usage management, and block I/O diagnostics.

Risks and test signals: Risks include mismatched symbolic stage/state names, incorrect segment identifiers, and tracing metadata after buffer lifetime changes. Test NILFS2 mount/write/fsync, cleaner activity, segment reuse, metadata updates, remount/recovery, and trace output under error injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/nilfs2.h` completely for this pass (229 lines, 5426 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/nilfs2.h_research.md`.
