<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/debugfs.c

## Purpose

This optional module exposes Wilco EC debugfs controls. It provides raw mailbox command access plus convenience nodes for H1 GPIO status and generating a test EC event.

## Important APIs, Types, And Functions

`struct wilco_ec_debugfs` stores the EC pointer, debugfs directory, latest raw response, and formatting buffers. `parse_hex_sentence()` converts space-separated hex tokens to bytes. `raw_write()` parses a two-byte message type plus request bytes and calls `wilco_ec_mailbox()`. `raw_read()` returns the latest response as a hex dump once. `send_ec_cmd()`, `h1_gpio_get()`, and `test_event_set()` implement the simple debug attributes.

## Control Flow

The platform child `wilco-ec-debugfs` probes with the Wilco EC parent data, creates `/sys/kernel/debug/wilco_ec`, and adds `raw`, `h1_gpio`, and `test_event`. A write to `raw` immediately sends the mailbox transaction and stores the response for the next read. Remove recursively deletes the debugfs directory.

## State And Persistence

The module has a single global `debug_info` pointer and stores only the most recent raw response until read. It does not persist data. EC state may be changed by arbitrary raw commands.

## Dependencies And Integration Points

It depends on debugfs, the Wilco mailbox export, and the core-created platform child. The documented ABI is under `debugfs-wilco-ec`.

## Risks

The global `debug_info` means multiple Wilco EC instances would collide. Raw command access is intentionally unsafe and can send arbitrary EC mailbox messages. `raw_write()` and `raw_read()` share buffers without explicit locking, so concurrent debugfs users can race.

## Test Signals

Test debugfs directory creation/removal, valid and invalid hex parsing, short raw command rejection, raw response one-shot reads, H1 GPIO command status, test event generation, and concurrent access behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/debugfs.c -->
