# sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_controller.h

## Purpose
This private header declares the boundary between the CDX platform controller, its RPMsg transport, and MCDI response handling.

## Important APIs, Types, and Functions
It declares `cdx_rpmsg_post_probe()`, `cdx_rpmsg_pre_remove()`, `cdx_rpmsg_send()`, `cdx_rpmsg_read_resp()`, `cdx_setup_rpmsg()`, and `cdx_destroy_rpmsg()`.

## Control Flow
`cdx_controller.c` calls setup/destroy and receives post/pre remove callbacks from the RPMsg layer. `mcdi.c` sends requests through the `cdx_mcdi_ops.mcdi_request` callback implemented by `cdx_controller.c`, which delegates to `cdx_rpmsg_send()`.

## State and Persistence Behavior
The header owns no state. The prototypes define how `struct cdx_mcdi` state moves between platform-driver code and RPMsg callbacks.

## Dependencies and Integration Points
It includes public CDX bus types and MCDI helper declarations. It is shared by `cdx_controller.c` and `cdx_rpmsg.c`.

## Risks
The header declares `cdx_rpmsg_read_resp()`, but the listed source set does not define or use it, indicating stale API surface. Any future use would fail to link unless implemented.

## Test Signals
Build coverage should catch prototype/definition drift. Runtime coverage should confirm setup/destroy and post/pre callbacks are invoked in the expected RPMsg lifecycle order.
