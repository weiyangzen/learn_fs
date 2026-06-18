# sources/distributed-fs/ceph-client/fs/befs/io.h

Purpose: declares BeFS block-run read helper.

Important APIs/types/functions: `befs_bread_iaddr`.

Control flow: included by `datastream.c` and other BeFS code that reads allocation-group addressed blocks.

State and persistence: no state; returned buffer_heads represent disk cache state owned by callers.

Dependencies and integration: depends on BeFS address types from `befs.h`.

Risks: callers must release the buffer_head and pass host-endian inode addresses.

Test signals: compile and file-read coverage.
