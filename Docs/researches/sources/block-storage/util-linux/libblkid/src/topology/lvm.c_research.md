# File Research: sources/block-storage/util-linux/libblkid/src/topology/lvm.c

## Scope

Provides legacy LVM topology probing via `lvdisplay`.

## Behavior

- Detects LVM devices by major number or driver name.
- Resolves the device name, forks `lvdisplay`, and parses `Stripes` and `Stripe size (KByte)` lines.
- Exports minimum I/O size and optimal I/O size in bytes.

## Dependencies And Risks

- Used only as fallback for old systems.
- Runs an external helper after dropping permissions.
- Produces no result for non-striped volumes or missing helper output.
