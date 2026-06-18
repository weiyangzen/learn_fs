# File Research: sources/block-storage/mdadm/msg.h

## Role

`msg.h` declares the mdmon socket/message API shared by mdadm command code and mdmon implementation.

## API Surface

It declares message send/receive, acknowledgements, monitor connection/ping helpers, subarray block/unblock helpers, container block/unblock helpers, manager ping, mdmon flush, and `MSG_MAX_LEN`.

## Invariants

The header forward-declares `struct mdinfo` and `struct metadata_update`, keeping it lightweight. The implementation owns framing details in `msg.c`.
