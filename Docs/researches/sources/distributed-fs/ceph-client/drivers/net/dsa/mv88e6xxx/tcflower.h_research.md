# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcflower.h

## Purpose
Declares the mv88e6xxx tc flower offload entry points.

## Important APIs, Types, and Functions
Provides prototypes for `mv88e6xxx_cls_flower_add`, `mv88e6xxx_cls_flower_del`, and `mv88e6xxx_flower_teardown`.

## Control Flow and State
No runtime logic. State is managed by `tcflower.c` through allocated TCAM entries and `chip->tcam.entries`.

## Dependencies and Integration Points
Relies on DSA and flow offload types being visible through includers. Used by the main driver ops table and cleanup paths.

## Risks and Test Signals
Risks are prototype drift and missing declarations when TCAM/flower support changes. Test signals are builds with tc flower callbacks enabled and add/delete offload smoke tests.
