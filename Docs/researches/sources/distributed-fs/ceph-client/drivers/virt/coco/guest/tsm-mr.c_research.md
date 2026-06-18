# sources/distributed-fs/ceph-client/drivers/virt/coco/guest/tsm-mr.c

## Purpose
Provides a reusable sysfs binary-attribute generator for TSM measurement registers.

## APIs, Types, and Functions
Exports `tsm_mr_create_attribute_group()` and `tsm_mr_free_attribute_group()`. Internal `struct tm_context` owns the generated attribute group, MR bin attributes, source `struct tsm_measurements`, cache sync flag, and rwsem. File operations are `tm_digest_read()` and `tm_digest_write()`.

## Control Flow and State
Creation validates MR definitions, required callbacks, names, hash IDs, and duplicate generated names. It allocates one context and one combined attribute/name block. Read locks the context, refreshes live MRs on a stale cache by upgrading to write lock, copies the requested digest slice, and traces reads. Writes require a full-size write at offset zero, call provider `write()`, mark the cache stale, and trace. Freeing releases the generated bin-attribute array and context.

## Dependencies and Integration
Depends on `linux/tsm-mr.h`, crypto hash-name metadata, sysfs binary attributes, and tracepoints from `trace/events/tsm_mr.h`. TDX uses it for RTMR/MR exposure.

## Risks and Test Signals
Risks include provider freeing MR backing storage before removing the group, stale-cache semantics being global rather than per-MR, and write callbacks extending security-sensitive registers. Tests should validate invalid MR definitions, duplicate names, live refresh behavior, partial write rejection, tracepoints, and TDX group teardown.
