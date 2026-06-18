# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_private.h

## Purpose
This private header defines the internal operation table used by the arm64 GIC guest library. It is shared only by GIC wrapper and implementation files.

## Important APIs, Types, and Functions
`struct gic_common_ops` contains function pointers for distributor/CPU initialization, IRQ enable/disable, IAR/EOIR/DIR access, EOI split mode, priority controls, active and pending state, interrupt configuration, and group assignment. It declares `extern const struct gic_common_ops gicv3_ops`.

## Control Flow
There is no executable control flow. The table shape determines which callbacks `gic.c` can dispatch after `gic_init()` selects an implementation.

## State, Dependencies, and Integration
This header creates a contract between generic `gic.c` and `gic_v3.c`. It deliberately avoids public exposure of implementation-specific register details; public callers use `gic.h` while internal files exchange this vtable.

## Risks and Test Signals
Adding a public GIC operation requires updating this table and every implementation. Mismatched signatures or missing `gicv3_ops` entries fail at compile time, while semantically wrong entries show up as guest interrupt test failures.
