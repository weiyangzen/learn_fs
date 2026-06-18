# sources/distributed-fs/ceph-client/rust/helpers/blk.c

## Purpose
Exposes block multiqueue request/private-data conversions to Rust drivers.

## APIs, Types, and Functions
`rust_helper_blk_mq_rq_to_pdu()` and `rust_helper_blk_mq_rq_from_pdu()` wrap the blk-mq PDU helpers.

## Control Flow, State, and Persistence
No local state is kept; conversions depend on blk-mq request allocation layout.

## Dependencies and Integration
Depends on `linux/blk-mq.h` and `linux/blkdev.h`, integrating Rust block drivers with blk-mq request-private storage.

## Risks and Test Signals
Risks are invalid PDU pointers, wrong tag-set command size, and lifetime assumptions after request completion. Test signals are Rust block queue tests and blk-mq request allocation/free stress.
