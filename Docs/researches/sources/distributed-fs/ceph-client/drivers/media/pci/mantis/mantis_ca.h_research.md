# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ca.h

## Purpose
This header declares the Mantis Common Interface lifecycle API.

## Important APIs, Types, and Functions
It declares `mantis_ca_init(struct mantis_pci *mantis)` and `mantis_ca_exit(struct mantis_pci *mantis)`.

## Control Flow
There is no executable flow. Mantis core/card initialization calls `mantis_ca_init` when CA support is needed and calls `mantis_ca_exit` during teardown.

## State and Persistence Behavior
The header stores no state. The implementation allocates and frees `mantis->mantis_ca`, EN50221 state, waitqueues, and event-manager resources.

## Dependencies and Integration Points
It depends on `struct mantis_pci` being visible to includers through surrounding Mantis headers. It is part of the core object list and used by card drivers and HIF/CA integration.

## Risks
Callers must pair init and exit and must tolerate init failures. The header does not expose whether CA is optional for a given board.

## Test Signals
Build coverage, CA init/exit during probe/remove, and CAM insertion/removal tests validate the interface.
