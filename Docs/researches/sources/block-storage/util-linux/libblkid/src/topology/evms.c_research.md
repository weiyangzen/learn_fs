# File Research: sources/block-storage/util-linux/libblkid/src/topology/evms.c

## Scope

Provides legacy EVMS topology probing.

## Behavior

- Detects EVMS devices by major number or driver name.
- Uses `EVMS_GET_STRIPE_INFO` ioctl to obtain stripe unit and width.
- Exports minimum I/O size and optimal I/O size in bytes.

## Dependencies And Risks

- Linux-specific fallback for old systems.
- Returns no topology for non-EVMS devices or ioctl failure.
