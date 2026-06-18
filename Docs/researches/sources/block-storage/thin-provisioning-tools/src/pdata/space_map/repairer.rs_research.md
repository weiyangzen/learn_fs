# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/repairer.rs

Repairs leak-only space-map bitmap errors. `repair_space_map` rereads bitmap blocks identified by `BitmapLeak`, unpacks each bitmap, changes entries from `Small(1)` to `Small(0)` where expected refcount is zero, repacks, rewrites bitmap checksums, and writes all repaired blocks.

It assumes leaks are the only corruption class; reread or write failures abort with errors.
