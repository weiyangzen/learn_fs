# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-ci.h

## Purpose
`ddbridge-ci.h` declares the attach/detach interface for Digital Devices bridge CI support.

## Important APIs, Types, And Functions
The header includes `ddbridge.h` for `struct ddb_port` and declares `int ddb_ci_attach(struct ddb_port *port, u32 bitrate);` plus `void ddb_ci_detach(struct ddb_port *port);`.

## Control Flow
The header has no executable control flow. Include guards prevent duplicate declarations. Runtime behavior is implemented in `ddbridge-ci.c`.

## State, Persistence, And Dependencies
No state is stored in the header. It depends on ddbridge core types and the caller-owned `ddb_port` lifetime. The `bitrate` argument is meaningful for CXD2099-backed CI attach and ignored by some other attach paths.

## Integration Points
Core ddbridge port initialization includes this header to attach CI handling for ports with internal, XO2, or Sony CI types, and teardown calls `ddb_ci_detach()` during device removal.

## Risks
The interface is intentionally small, so all ownership rules are implicit: callers must pass an initialized port with DVB adapter and I2C fields ready, and must detach before those resources disappear. Any signature change requires updates across ddbridge setup code.

## Test Signals
Compile coverage confirms declarations match implementation. Runtime validation follows `ddbridge-ci.c`: attach succeeds for CI-capable ports, detach releases EN50221/CXD2099 resources, and non-CI ports are rejected by callers or return errors cleanly.
